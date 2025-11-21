#!/bin/bash

# Blue/Green Deployment Script for AKS
# This script manages zero-downtime deployments using blue/green strategy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ai-model-serving"
SERVICE_NAME="ai-model-service"
HEALTH_CHECK_RETRIES=5
HEALTH_CHECK_DELAY=10
REGISTRY="${CONTAINER_REGISTRY:-ghcr.io/imrohankataria/mlops-zero-downtime-ai-delivery}"

# Print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get current active deployment color
get_current_color() {
    kubectl get service $SERVICE_NAME -n $NAMESPACE \
        -o jsonpath='{.spec.selector.deployment}' 2>/dev/null || echo "blue"
}

# Function to determine target deployment color
get_target_color() {
    local current_color=$1
    if [ "$current_color" == "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Function to run health checks
run_health_checks() {
    local deployment_color=$1
    local service_url=$2
    
    log_info "Running health checks on $deployment_color deployment..."
    
    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        log_info "Health check attempt $i/$HEALTH_CHECK_RETRIES"
        
        # Check if pods are ready
        local ready_pods=$(kubectl get deployment ai-model-$deployment_color -n $NAMESPACE \
            -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired_pods=$(kubectl get deployment ai-model-$deployment_color -n $NAMESPACE \
            -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [ "$ready_pods" == "$desired_pods" ] && [ "$ready_pods" != "0" ]; then
            log_success "All $ready_pods pods are ready"
            
            # Additional health checks can be added here
            # For example: curl to health endpoint, response time checks, etc.
            
            return 0
        else
            log_warning "Waiting for pods to be ready ($ready_pods/$desired_pods)..."
            sleep $HEALTH_CHECK_DELAY
        fi
    done
    
    log_error "Health checks failed after $HEALTH_CHECK_RETRIES attempts"
    return 1
}

# Function to switch traffic
switch_traffic() {
    local target_color=$1
    
    log_info "Switching traffic to $target_color deployment..."
    
    kubectl patch service $SERVICE_NAME -n $NAMESPACE \
        -p "{\"spec\":{\"selector\":{\"deployment\":\"$target_color\"}}}"
    
    log_success "Traffic switched to $target_color deployment"
}

# Function to rollback
rollback() {
    local current_color=$1
    local previous_color=$(get_target_color $current_color)
    
    log_warning "Initiating rollback to $previous_color deployment..."
    
    switch_traffic $previous_color
    
    log_success "Rollback completed successfully"
}

# Main deployment function
deploy() {
    local image_tag=$1
    local model_version=$2
    
    if [ -z "$image_tag" ]; then
        log_error "Image tag is required"
        echo "Usage: $0 <image-tag> [model-version]"
        exit 1
    fi
    
    if [ -z "$model_version" ]; then
        model_version="v1.0.0"
    fi
    
    log_info "Starting blue/green deployment..."
    log_info "Image tag: $image_tag"
    log_info "Model version: $model_version"
    
    # Get current deployment color
    local current_color=$(get_current_color)
    log_info "Current active deployment: $current_color"
    
    # Determine target deployment color
    local target_color=$(get_target_color $current_color)
    log_info "Target deployment: $target_color"
    
    # Deploy to target environment
    log_info "Deploying to $target_color environment..."
    
    kubectl set image deployment/ai-model-$target_color \
        ai-model=$REGISTRY/ai-model:$image_tag \
        -n $NAMESPACE
    
    kubectl set env deployment/ai-model-$target_color \
        MODEL_VERSION=$model_version \
        -n $NAMESPACE
    
    # Wait for rollout
    log_info "Waiting for deployment rollout..."
    if kubectl rollout status deployment/ai-model-$target_color -n $NAMESPACE --timeout=300s; then
        log_success "Deployment rollout completed"
    else
        log_error "Deployment rollout failed"
        exit 1
    fi
    
    # Run health checks
    if run_health_checks $target_color "ai-model-$target_color.$NAMESPACE.svc.cluster.local"; then
        log_success "Health checks passed"
        
        # Switch traffic
        switch_traffic $target_color
        
        log_success "🎉 Deployment completed successfully!"
        log_info "Active deployment: $target_color"
        log_info "Standby deployment: $current_color (ready for instant rollback)"
        
    else
        log_error "Health checks failed"
        log_warning "Keeping traffic on $current_color deployment"
        log_info "You can manually rollback or retry the deployment"
        exit 1
    fi
}

# Script entry point
if [ "$1" == "deploy" ]; then
    shift
    deploy "$@"
elif [ "$1" == "rollback" ]; then
    current_color=$(get_current_color)
    rollback $current_color
elif [ "$1" == "status" ]; then
    current_color=$(get_current_color)
    log_info "Current active deployment: $current_color"
    kubectl get deployments -n $NAMESPACE -l app=ai-model
    kubectl get pods -n $NAMESPACE -l app=ai-model
else
    echo "Usage:"
    echo "  $0 deploy <image-tag> [model-version]  - Deploy new version"
    echo "  $0 rollback                             - Rollback to previous version"
    echo "  $0 status                               - Show deployment status"
    exit 1
fi

# Zero-Downtime AI Delivery: Blue/Green Deployment on AKS

This repository demonstrates a production-ready CI/CD pipeline for AI applications with zero-downtime deployments using blue/green deployment strategy on Azure Kubernetes Service (AKS).

## 🎯 Features

- **Automated CI/CD Pipeline**: GitHub Actions workflow for test → build → deploy → rollback
- **Blue/Green Deployments**: Zero-downtime deployments with instant rollback capability
- **Automated Health Checks**: Canary health-checks before switching traffic
- **Instant Rollback**: Automatic rollback on deployment failure
- **Container Registry**: GitHub Container Registry (GHCR) integration
- **Production-Ready**: Resource limits, health probes, and monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                           │
│  ┌──────┐   ┌───────┐   ┌────────┐   ┌──────────┐             │
│  │ Test │ → │ Build │ → │ Deploy │ → │ Rollback │             │
│  └──────┘   └───────┘   └────────┘   └──────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Azure Kubernetes Service (AKS)                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │                Load Balancer Service                 │     │
│  │            (Routes to Blue OR Green)                 │     │
│  └──────────────────────────────────────────────────────┘     │
│           ↓                              ↓                     │
│  ┌─────────────────┐          ┌─────────────────┐            │
│  │ Blue Deployment │          │ Green Deployment│            │
│  │   (Active)      │          │   (Standby)     │            │
│  │                 │          │                 │            │
│  │  ┌───┐ ┌───┐   │          │  ┌───┐ ┌───┐   │            │
│  │  │Pod│ │Pod│   │          │  │Pod│ │Pod│   │            │
│  │  └───┘ └───┘   │          │  └───┘ └───┘   │            │
│  │     ┌───┐      │          │     ┌───┐      │            │
│  │     │Pod│      │          │     │Pod│      │            │
│  │     └───┘      │          │     └───┘      │            │
│  └─────────────────┘          └─────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker installed locally
- Azure account with AKS cluster (for production deployment)
- GitHub account
- `kubectl` configured (for manual deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery.git
   cd mlops-zero-downtime-ai-delivery
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**:
   ```bash
   python -m pytest test_app.py -v
   ```

4. **Run locally**:
   ```bash
   python app.py
   ```

5. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:5000/health
   
   # Make a prediction
   curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"text": "This is a great product!"}'
   ```

### Docker Build

```bash
# Build the image
docker build -t ai-model:latest .

# Run the container
docker run -p 5000:5000 \
  -e MODEL_VERSION=v1.0.0 \
  -e DEPLOYMENT_COLOR=blue \
  ai-model:latest

# Test the container
curl http://localhost:5000/health
```

## 📋 CI/CD Pipeline

### Pipeline Stages

1. **Test**: Runs unit tests with pytest and generates coverage reports
2. **Build**: Builds Docker image and pushes to GitHub Container Registry
3. **Deploy**: Deploys to AKS using blue/green strategy with health checks
4. **Rollback**: Automatically rolls back on failure

### Workflow Triggers

- **Push to main**: Full CI/CD pipeline execution
- **Pull Request**: Test and build only
- **Manual Dispatch**: Manual deployment with color selection

### Health Check Process

The deployment includes a comprehensive health check system:

1. **Kubernetes Readiness Probes**: Checks if pods are ready to receive traffic
2. **Canary Health Checks**: 5 health checks with 10-second intervals
3. **Validation Checks**:
   - Service responding
   - Model loaded successfully
   - Prediction endpoint working
   - Response time within limits
   - Error rate acceptable

### Traffic Switching

Once health checks pass:
1. Service selector is updated to point to the new deployment
2. Kubernetes gradually shifts traffic to new pods
3. Old deployment remains running as standby
4. **Zero downtime** achieved!

## 🔄 Blue/Green Deployment Strategy

### How It Works

1. **Initial State**: Blue deployment is active, serving production traffic
2. **New Deployment**: Deploy new version to Green environment
3. **Health Checks**: Run automated health checks on Green
4. **Traffic Switch**: If checks pass, switch service to Green
5. **Standby**: Blue remains running for instant rollback if needed

### Manual Deployment

Use the deployment script for manual deployments:

```bash
# Deploy new version
./scripts/deploy.sh deploy <image-tag> [model-version]

# Check deployment status
./scripts/deploy.sh status

# Rollback to previous version
./scripts/deploy.sh rollback
```

### Example Deployment Flow

```bash
# Deploy version 1.0.0
./scripts/deploy.sh deploy v1.0.0

# Output:
# [INFO] Starting blue/green deployment...
# [INFO] Current active deployment: blue
# [INFO] Target deployment: green
# [INFO] Deploying to green environment...
# [SUCCESS] Deployment rollout completed
# [INFO] Running health checks...
# [SUCCESS] Health checks passed
# [INFO] Switching traffic to green deployment...
# [SUCCESS] Traffic switched to green deployment
# 🎉 Deployment completed successfully!
```

## ⚡ Hot vs Cold Swap Comparison

### Hot Swap (Blue/Green - This Approach)

**Advantages:**
- ✅ Zero downtime
- ✅ Instant rollback (just switch service back)
- ✅ Full environment testing before traffic switch
- ✅ No connection drops

**Cost:**
- 💰 2x resources during deployment (both environments running)
- 💰 Continuous standby environment cost

**Time:**
- ⏱️ ~2-5 minutes for deployment
- ⏱️ ~5 seconds for traffic switch
- ⏱️ <10 seconds for rollback

### Cold Swap (Rolling Update)

**Advantages:**
- ✅ Lower resource usage
- ✅ No extra standby environment

**Disadvantages:**
- ❌ Potential downtime during pod replacement
- ❌ Slower rollback (requires redeployment)
- ❌ Risk of mixed versions serving traffic

**Cost:**
- 💰 Lower - only single environment

**Time:**
- ⏱️ ~5-10 minutes for deployment
- ⏱️ ~30 seconds for rolling update
- ⏱️ ~5-10 minutes for rollback

### Cost Analysis (Example AKS Setup)

**Scenario**: 3-pod deployment, 2 vCPU, 4GB RAM per pod

**Blue/Green (Hot Swap)**:
- Running cost: 6 pods = ~$350/month
- Deployment window: 2x cost for 5 minutes
- Rollback: No additional cost (instant)
- **Total cost increase**: ~0.5% for 24 deployments/day

**Rolling Update (Cold Swap)**:
- Running cost: 3 pods = ~$175/month
- Deployment window: temporary extra pods
- Rollback: Full redeployment cost
- **Total cost increase**: ~0.2% for 24 deployments/day

**Recommendation**: For production AI models, **Hot Swap** is recommended despite the ~2x cost due to:
- Zero downtime guarantee
- Instant rollback capability
- Lower risk of customer impact
- Better for compliance requirements

## 🔐 Setup Instructions

### GitHub Secrets

Configure these secrets in your GitHub repository:

```
AZURE_CREDENTIALS         # Azure service principal credentials
AZURE_RESOURCE_GROUP      # Azure resource group name
AZURE_CLUSTER_NAME        # AKS cluster name
```

### Azure Setup

1. **Create AKS cluster**:
   ```bash
   az aks create \
     --resource-group myResourceGroup \
     --name myAKSCluster \
     --node-count 3 \
     --enable-addons monitoring \
     --generate-ssh-keys
   ```

2. **Configure kubectl**:
   ```bash
   az aks get-credentials \
     --resource-group myResourceGroup \
     --name myAKSCluster
   ```

3. **Deploy initial environment**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/deployment-blue.yaml
   kubectl apply -f k8s/service-blue-green.yaml
   kubectl apply -f k8s/service.yaml
   ```

## 📊 Monitoring and Observability

### Health Check Endpoints

- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe
- `GET /info` - Application information

### Kubernetes Resources

```bash
# Check deployment status
kubectl get deployments -n ai-model-serving

# Check pods
kubectl get pods -n ai-model-serving -l app=ai-model

# Check services
kubectl get services -n ai-model-serving

# View logs
kubectl logs -n ai-model-serving -l app=ai-model --tail=100
```

## 🧪 Testing

The repository includes comprehensive unit tests:

```bash
# Run all tests
python -m pytest test_app.py -v

# Run with coverage
python -m pytest test_app.py -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Coverage

- Health check endpoints
- Readiness probes
- Prediction endpoint with various inputs
- Error handling
- Input validation

## 🎬 Zero-Click Deploy Animation

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Developer pushes code                             │
│  ════════════════════════════                               │
│                                                             │
│  $ git push origin main                                    │
│  → GitHub Actions triggered automatically                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Automated Testing                                 │
│  ════════════════════════                                   │
│                                                             │
│  ✓ Unit tests passed (10/10)                              │
│  ✓ Coverage: 95%                                           │
│  Duration: 45 seconds                                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Container Build                                   │
│  ════════════════════════                                   │
│                                                             │
│  ✓ Docker image built                                      │
│  ✓ Pushed to GHCR                                          │
│  Tag: main-abc1234                                          │
│  Duration: 2 minutes                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Blue/Green Deployment                             │
│  ════════════════════════════════                           │
│                                                             │
│  Current: Blue (serving traffic)                            │
│  Target:  Green (deploying...)                             │
│                                                             │
│  ✓ Pods created (3/3)                                      │
│  ✓ Health checks passed (5/5)                             │
│  Duration: 2 minutes                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Traffic Switch                                    │
│  ════════════════════                                       │
│                                                             │
│  Blue:  ███░░░░░░░ 30% → 0%                               │
│  Green: ░░░███████ 70% → 100%                             │
│                                                             │
│  ✓ Traffic switched to Green                               │
│  ✓ Zero downtime achieved!                                 │
│  Duration: 5 seconds                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Complete ✨                                        │
│  ═══════════════════                                        │
│                                                             │
│  Current: Green (serving traffic)                           │
│  Standby: Blue (ready for instant rollback)                │
│                                                             │
│  Total Time: ~5 minutes                                     │
│  Downtime: 0 seconds                                        │
│  User Action Required: 0 clicks                             │
└─────────────────────────────────────────────────────────────┘
```

## 🛡️ Rollback Mechanism

### Automatic Rollback

If health checks fail, the pipeline automatically:
1. Detects the failure
2. Switches service back to previous deployment
3. Keeps the failed deployment for investigation
4. Notifies the team

### Manual Rollback

```bash
# Using deployment script
./scripts/deploy.sh rollback

# Or using kubectl directly
kubectl patch service ai-model-service -n ai-model-serving \
  -p '{"spec":{"selector":{"deployment":"blue"}}}'
```

Rollback time: **< 10 seconds**

## 📚 API Documentation

### Endpoints

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "model_version": "v1.0.0",
  "deployment_color": "blue",
  "timestamp": 1234567890
}
```

#### Readiness Check
```bash
GET /ready

Response:
{
  "status": "ready",
  "model_version": "v1.0.0",
  "deployment_color": "blue"
}
```

#### Predict
```bash
POST /predict
Content-Type: application/json

{
  "text": "This is a great product!"
}

Response:
{
  "success": true,
  "prediction": {
    "sentiment": "positive",
    "confidence": 0.85,
    "model_version": "v1.0.0"
  },
  "deployment_color": "blue"
}
```

#### Info
```bash
GET /info

Response:
{
  "app": "AI Model Serving API",
  "model_version": "v1.0.0",
  "deployment_color": "blue",
  "endpoints": {
    "health": "/health",
    "ready": "/ready",
    "predict": "/predict (POST)",
    "info": "/info"
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask and Gunicorn
- Deployed on Azure Kubernetes Service
- CI/CD powered by GitHub Actions
- Container registry: GitHub Container Registry (GHCR)

---

**Note**: This is a demonstration repository. In production, you would:
- Use real ML models (e.g., transformers, TensorFlow, PyTorch)
- Implement proper authentication and authorization
- Add comprehensive monitoring and logging (Prometheus, Grafana)
- Set up alerting (PagerDuty, Slack)
- Implement rate limiting and request validation
- Use production-grade secrets management (Azure Key Vault)
- Configure proper resource limits based on load testing
- Set up auto-scaling based on metrics

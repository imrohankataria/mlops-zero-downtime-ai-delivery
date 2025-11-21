"""
Simple AI Model Serving API
A Flask-based application that serves a pre-trained sentiment analysis model
"""
from flask import Flask, request, jsonify
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simulated model version (in production, this would be loaded from model registry)
MODEL_VERSION = os.getenv('MODEL_VERSION', 'v1.0.0')
DEPLOYMENT_COLOR = os.getenv('DEPLOYMENT_COLOR', 'blue')

# Simple in-memory model (in production, this would be a real ML model)
class SentimentModel:
    def __init__(self, version):
        self.version = version
        logger.info(f"Initialized model version: {version}")
    
    def predict(self, text):
        """Simple sentiment prediction (placeholder logic)"""
        # In production, this would use a real model like transformers
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'worst']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.6 + (positive_count * 0.1), 0.99)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.6 + (negative_count * 0.1), 0.99)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'model_version': self.version
        }

# Initialize model
model = SentimentModel(MODEL_VERSION)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Kubernetes readiness/liveness probes"""
    return jsonify({
        'status': 'healthy',
        'model_version': MODEL_VERSION,
        'deployment_color': DEPLOYMENT_COLOR,
        'timestamp': time.time()
    }), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe endpoint"""
    # In production, check if model is loaded and all dependencies are ready
    return jsonify({
        'status': 'ready',
        'model_version': MODEL_VERSION,
        'deployment_color': DEPLOYMENT_COLOR
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        
        if not text or len(text.strip()) == 0:
            return jsonify({
                'error': 'Text cannot be empty'
            }), 400
        
        # Make prediction
        result = model.predict(text)
        
        logger.info(f"Prediction made: {result}")
        
        return jsonify({
            'success': True,
            'prediction': result,
            'deployment_color': DEPLOYMENT_COLOR
        }), 200
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/info', methods=['GET'])
def info():
    """Get application information"""
    return jsonify({
        'app': 'AI Model Serving API',
        'model_version': MODEL_VERSION,
        'deployment_color': DEPLOYMENT_COLOR,
        'endpoints': {
            'health': '/health',
            'ready': '/ready',
            'predict': '/predict (POST)',
            'info': '/info'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting AI Model Serving API on port {port}")
    logger.info(f"Model Version: {MODEL_VERSION}, Deployment: {DEPLOYMENT_COLOR}")
    app.run(host='0.0.0.0', port=port)

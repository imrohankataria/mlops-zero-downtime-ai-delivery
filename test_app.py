"""
Unit tests for AI Model Serving API
"""
import unittest
import json
from app import app

class TestAIModelAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('model_version', data)
        self.assertIn('deployment_color', data)
    
    def test_ready_endpoint(self):
        """Test readiness probe endpoint"""
        response = self.app.get('/ready')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ready')
    
    def test_info_endpoint(self):
        """Test info endpoint"""
        response = self.app.get('/info')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('app', data)
        self.assertIn('model_version', data)
        self.assertIn('endpoints', data)
    
    def test_predict_positive_sentiment(self):
        """Test prediction with positive sentiment"""
        response = self.app.post('/predict',
                                data=json.dumps({'text': 'This is a great and wonderful product!'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['prediction']['sentiment'], 'positive')
        self.assertGreater(data['prediction']['confidence'], 0.5)
    
    def test_predict_negative_sentiment(self):
        """Test prediction with negative sentiment"""
        response = self.app.post('/predict',
                                data=json.dumps({'text': 'This is terrible and awful'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['prediction']['sentiment'], 'negative')
        self.assertGreater(data['prediction']['confidence'], 0.5)
    
    def test_predict_neutral_sentiment(self):
        """Test prediction with neutral sentiment"""
        response = self.app.post('/predict',
                                data=json.dumps({'text': 'This is a product'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['prediction']['sentiment'], 'neutral')
    
    def test_predict_missing_text(self):
        """Test prediction with missing text field"""
        response = self.app.post('/predict',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_predict_empty_text(self):
        """Test prediction with empty text"""
        response = self.app.post('/predict',
                                data=json.dumps({'text': ''}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()

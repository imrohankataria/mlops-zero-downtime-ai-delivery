# MLOps: Zero-Downtime AI Delivery 🚀

[![CI/CD Pipeline](https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery/actions/workflows/ci-cd-pipeline.yaml/badge.svg)](https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery/actions/workflows/ci-cd-pipeline.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready CI/CD pipeline for AI applications demonstrating **zero-downtime deployments** using blue/green deployment strategy on Azure Kubernetes Service (AKS).

## ✨ Key Features

🔄 **Blue/Green Deployments** - Zero-downtime deployments with instant rollback  
🤖 **GitHub Actions CI/CD** - Automated test → build → deploy → rollback pipeline  
🏥 **Automated Health Checks** - Canary health-checks before traffic switching  
⚡ **Instant Rollback** - Automatic rollback on deployment failure (< 10 seconds)  
📊 **Cost/Time Analysis** - Detailed comparison of hot vs cold swap strategies  
🎬 **Zero-Click Deploy** - Fully automated deployment process  

## 🏗️ Architecture Overview

```
GitHub Push → Tests → Build Docker Image → Deploy to Inactive Environment
                                         → Run Health Checks → Switch Traffic
                                         → Rollback on Failure
```

**Blue/Green Strategy:**
- Two identical production environments (Blue & Green)
- One serves live traffic while other is standby
- New deployments go to inactive environment
- Traffic switches only after health checks pass
- Instant rollback by switching back to previous environment

## 🚀 Quick Start

### Run Locally

```bash
# Clone repository
git clone https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery.git
cd mlops-zero-downtime-ai-delivery

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest test_app.py -v

# Start application
python app.py

# Test the API
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a great product!"}'
```

### Deploy to Production

The deployment happens automatically when you push to the `main` branch:

```bash
git push origin main
```

That's it! The CI/CD pipeline will:
1. ✅ Run all tests
2. 🏗️ Build Docker image
3. 🚀 Deploy to inactive environment
4. 🏥 Run health checks
5. 🔄 Switch traffic (zero downtime!)
6. 🎉 Done!

## 📊 Hot vs Cold Swap Comparison

### Hot Swap (Blue/Green) - ⭐ Recommended for Production

| Metric | Value |
|--------|-------|
| **Downtime** | 0 seconds ✅ |
| **Rollback Time** | < 10 seconds ⚡ |
| **Deployment Time** | ~5 minutes |
| **Resource Cost** | 2x during deployment 💰 |
| **Risk Level** | Low 🟢 |

### Cold Swap (Rolling Update)

| Metric | Value |
|--------|-------|
| **Downtime** | 5-30 seconds ⚠️ |
| **Rollback Time** | ~5 minutes 🐌 |
| **Deployment Time** | ~10 minutes |
| **Resource Cost** | 1x 💵 |
| **Risk Level** | Medium 🟡 |

**Winner**: Hot Swap for mission-critical AI applications where downtime is unacceptable.

## 🎬 Zero-Click Deploy Animation

```
Developer Push → [AUTOMATED] → Tests Pass → Build Image → Deploy Green
                                                        → Health Checks ✓
                                                        → Switch Traffic
                                                        → Complete! ✨
                                                        
Time: ~5 minutes | Downtime: 0 seconds | Clicks: 0
```

## 🛠️ Tech Stack

- **Application**: Python + Flask + Gunicorn
- **Containerization**: Docker (multi-stage builds)
- **Orchestration**: Kubernetes (AKS)
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (GHCR)
- **Deployment**: Blue/Green Strategy

## 📁 Repository Structure

```
.
├── app.py                          # Flask application
├── test_app.py                     # Unit tests
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── .github/
│   └── workflows/
│       └── ci-cd-pipeline.yaml    # CI/CD workflow
├── k8s/                           # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment-blue.yaml
│   ├── deployment-green.yaml
│   ├── service.yaml
│   └── service-blue-green.yaml
├── scripts/
│   └── deploy.sh                  # Deployment automation script
├── DEPLOYMENT_GUIDE.md            # Detailed deployment guide
└── README.md                      # This file
```

## 🔐 Setup

### Prerequisites

- Azure account with AKS cluster
- GitHub account
- Docker installed (for local testing)

### Configuration

1. **Fork this repository**

2. **Set up GitHub Secrets** (for production deployment):
   - `AZURE_CREDENTIALS` - Azure service principal
   - `AZURE_RESOURCE_GROUP` - Azure resource group
   - `AZURE_CLUSTER_NAME` - AKS cluster name

3. **Deploy initial infrastructure**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/deployment-blue.yaml
   kubectl apply -f k8s/service-blue-green.yaml
   kubectl apply -f k8s/service.yaml
   ```

## 📖 Documentation

For detailed documentation, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) which includes:

- Complete architecture diagrams
- Step-by-step deployment instructions
- Cost analysis and comparisons
- Rollback procedures
- API documentation
- Monitoring and observability
- Troubleshooting guide

## 🧪 Testing

```bash
# Run unit tests
python -m pytest test_app.py -v

# Run with coverage
python -m pytest test_app.py -v --cov=app --cov-report=html

# Load testing (requires locust)
locust -f tests/load_test.py --host=http://localhost:5000
```

## 🎯 Use Cases

This repository is perfect for:

- ✅ Machine Learning model serving in production
- ✅ Microservices requiring zero downtime
- ✅ Applications with strict SLA requirements
- ✅ Learning MLOps best practices
- ✅ Understanding blue/green deployments
- ✅ Setting up production-ready CI/CD pipelines

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

## 📧 Contact

Rohan Kataria - [@imrohankataria](https://github.com/imrohankataria)

Project Link: [https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery](https://github.com/imrohankataria/mlops-zero-downtime-ai-delivery)

---

**Made with ❤️ for the MLOps community**
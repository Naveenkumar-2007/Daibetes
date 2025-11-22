# Azure Deployment Guide - Complete Setup

## 🚀 Quick Start

This guide will help you deploy the Diabetes Health Predictor to Azure with automated CI/CD.

## Prerequisites

1. **GitHub Account** - Repository: `https://github.com/Naveenkumar-2007/Daibetes`
2. **Azure Account** - Sign up at https://portal.azure.com (free tier available)
3. **Firebase Project** - For database and authentication

## Step 1: Prepare Environment Variables

Create these secrets in Azure App Service Configuration:

```bash
GROQ_API_KEY=your_groq_api_key_here
FIREBASE_DATABASE_URL=https://diabetes-prediction-22082-default-rtdb.firebaseio.com
FIREBASE_API_KEY=your_firebase_api_key
SECRET_KEY=your-secure-secret-key-change-this
FLASK_ENV=production
```

## Step 2: Create Azure Web App

### Option A: Using Azure Portal (Recommended)

1. **Login**: Go to https://portal.azure.com
2. **Create Resource**: Click "Create a resource" → Search "Web App"
3. **Configure**:
   - **Resource Group**: Create new `diabetes-predictor-rg`
   - **Name**: `diabetes-predictor-ai` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: East US (or nearest)
   - **Pricing**: B1 Basic ($13/month) or F1 Free

4. **Review + Create**

### Option B: Using Azure CLI

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create --name diabetes-predictor-rg --location eastus

# Create app service plan
az appservice plan create \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group diabetes-predictor-rg \
  --plan diabetes-predictor-plan \
  --name diabetes-predictor-ai \
  --runtime "PYTHON|3.11"

# Configure startup command
az webapp config set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --startup-file "bash startup.sh"
```

## Step 3: Configure GitHub Secrets

1. **Get Azure Publish Profile**:
   - Go to Azure Portal → Your Web App
   - Click "Download publish profile"
   - Open the file and copy contents

2. **Add GitHub Secret**:
   - Go to GitHub: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste publish profile content
   - Click "Add secret"

## Step 4: Configure Environment Variables in Azure

Go to Azure Portal → Your Web App → Configuration → Application Settings:

```
GROQ_API_KEY = your_groq_api_key
FIREBASE_DATABASE_URL = https://diabetes-prediction-22082-default-rtdb.firebaseio.com
FIREBASE_API_KEY = your_firebase_key
SECRET_KEY = super-secret-key-change-this-in-production
FLASK_ENV = production
WEBSITES_PORT = 8000
SCM_DO_BUILD_DURING_DEPLOYMENT = true
WEBSITE_RUN_FROM_PACKAGE = 0
```

## Step 5: Push to GitHub (Automated Deployment)

```bash
# Check git status
git status

# Stage all changes
git add .

# Commit changes
git commit -m "feat: Azure deployment ready with CI/CD"

# Push to GitHub (triggers automated deployment)
git push origin main
```

## Step 6: Monitor Deployment

1. **GitHub Actions**:
   - Go to https://github.com/Naveenkumar-2007/Daibetes/actions
   - Watch the "Deploy to Azure Web App" workflow
   - Wait for ✅ success

2. **Azure Deployment Center**:
   - Azure Portal → Your Web App → Deployment Center
   - Check deployment logs
   - View build output

## Step 7: Access Your App

Your app will be available at:
```
https://diabetes-predictor-ai.azurewebsites.net
```

## 🔧 Troubleshooting

### Deployment Failed

**Check logs**:
```bash
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

**Common issues**:
- Missing environment variables
- Incorrect startup command
- Python version mismatch
- Port configuration

### App Not Starting

1. Check Application Insights in Azure Portal
2. View Log Stream: Azure Portal → Your Web App → Log stream
3. Check startup.sh has execution permissions

### Database Connection Issues

- Verify FIREBASE_DATABASE_URL is correct
- Check Firebase REST API is enabled
- Ensure Firebase rules allow read/write

## 📊 CI/CD Workflow

The GitHub Actions workflow automatically:

1. ✅ Checks out code
2. ✅ Sets up Python 3.11
3. ✅ Sets up Node.js 18
4. ✅ Installs Python dependencies
5. ✅ Installs frontend dependencies
6. ✅ Builds React production bundle
7. ✅ Copies build to Flask static folder
8. ✅ Creates deployment package
9. ✅ Deploys to Azure Web App

**Trigger**: Every push to `main` branch

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set up Firebase security rules
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set up authentication
- [ ] Enable Azure App Service authentication
- [ ] Set up monitoring and alerts

## 📈 Post-Deployment

1. **Test the app**: Visit your Azure URL
2. **Set up monitoring**: Enable Application Insights
3. **Configure alerts**: Set up Azure Monitor alerts
4. **Set up custom domain** (optional)
5. **Enable SSL certificate** (automatic with custom domain)

## 🛠️ Manual Deployment (If CI/CD fails)

```bash
# Build frontend
cd frontend
npm install
npm run build

# Copy to Flask
mkdir -p ../static/app
cp -r dist/* ../static/app/

# Deploy using ZIP
cd ..
zip -r deploy.zip static templates artifacts src flask_app.py auth.py firebase_config.py report_generator.py retrain_model.py requirements.txt startup.sh

# Upload using Azure CLI
az webapp deployment source config-zip \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --src deploy.zip
```

## 📞 Support

- **Azure Issues**: https://portal.azure.com → Support
- **GitHub Issues**: https://github.com/Naveenkumar-2007/Daibetes/issues
- **Documentation**: https://docs.microsoft.com/azure/app-service/

## 🎯 Next Steps

1. Monitor first deployment
2. Test all features
3. Set up custom domain
4. Configure email for password reset
5. Set up backup strategy
6. Enable auto-scaling (if needed)

---

**Deployment Status**: Ready for Azure ✅
**CI/CD**: GitHub Actions configured ✅
**Production Build**: Optimized ✅

# 🚀 Azure Deployment Guide - Diabetes Health Predictor

## ✅ Deployment Status
- **App URL**: https://diabetes-predictor-ai.azurewebsites.net
- **Resource Group**: diabetes-predictor-rg
- **Region**: East US
- **Runtime**: Python 3.11 (Linux)
- **Tier**: Basic B1

## 📋 Prerequisites Configured

### 1. Azure Resources ✅
- Web App: `diabetes-predictor-ai`
- App Service Plan: `diabetes-predictor-plan`
- Resource Group: `diabetes-predictor-rg`

### 2. GitHub Secrets ✅
- `AZURE_CREDENTIALS` - Service Principal for Azure CLI authentication
- `AZURE_WEBAPP_PUBLISH_PROFILE` - Publishing credentials (backup)

### 3. Environment Variables ⚠️ REQUIRED
Set these in Azure Portal > App Service > Configuration > Application settings:

```bash
# Required for deployment
SCM_DO_BUILD_DURING_DEPLOYMENT=true
WEBSITE_RUN_FROM_PACKAGE=0
ENABLE_ORYX_BUILD=true
POST_BUILD_COMMAND=pip install --no-cache-dir Flask-CORS==4.0.0
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PORT=8000

# Application secrets (CRITICAL - ADD THESE!)
GROQ_API_KEY=<your_groq_api_key>
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
```

## 🔧 Quick Setup Commands

### Set Azure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    GROQ_API_KEY="<your_groq_api_key>" \
    GOOGLE_CLIENT_ID="<your_google_client_id>" \
    GOOGLE_CLIENT_SECRET="<your_google_client_secret>"
```

### Manual Deployment (if needed)
```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Copy frontend to static
rm -rf static/app
mkdir -p static/app
cp -r frontend/dist/* static/app/

# Deploy to Azure
az webapp up \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11" \
  --sku B1
```

## 🔐 Google OAuth Setup

### 1. Create OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Application type: Web application

### 2. Configure Authorized Origins
```
http://localhost:5000
http://localhost:5173
https://diabetes-predictor-ai.azurewebsites.net
```

### 3. Configure Redirect URIs
```
http://localhost:5000/login
http://localhost:5173/login
https://diabetes-predictor-ai.azurewebsites.net/login
https://diabetes-predictor-ai.azurewebsites.net/api/login/google
```

### 4. Add Credentials to Azure
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    GOOGLE_CLIENT_ID="<your_client_id>.apps.googleusercontent.com" \
    GOOGLE_CLIENT_SECRET="<your_client_secret>"
```

## 📦 Firebase Setup

### 1. Download Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Project Settings > Service Accounts
3. Generate New Private Key
4. Save as `firebase-service-account.json`

### 2. Upload to Azure (if needed)
Use Azure Portal or Kudu console to upload the firebase-service-account.json file

## 🔄 CI/CD Pipeline

### Automated Deployment
- **Trigger**: Push to `main` branch
- **Workflow**: `.github/workflows/azure-deploy.yml`
- **Process**:
  1. Build React frontend (Node 20)
  2. Build Python backend (Python 3.11)
  3. Create deployment package
  4. Deploy to Azure using ZIP Deploy
  5. Restart app and verify

### Monitor Deployment
```bash
# Watch deployment logs
az webapp log tail --resource-group diabetes-predictor-rg --name diabetes-predictor-ai

# Check app status
az webapp show --resource-group diabetes-predictor-rg --name diabetes-predictor-ai --query state

# View recent deployments
az webapp deployment list --resource-group diabetes-predictor-rg --name diabetes-predictor-ai
```

## 🐛 Troubleshooting

### Application Not Starting
```bash
# Check logs
az webapp log tail --resource-group diabetes-predictor-rg --name diabetes-predictor-ai

# Restart app
az webapp restart --resource-group diabetes-predictor-rg --name diabetes-predictor-ai
```

### Module Import Errors
- Ensure `POST_BUILD_COMMAND` is set in App Settings
- Verify requirements.txt includes all dependencies
- Check that Oryx build is enabled

### Google Sign-In Not Working
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Check authorized origins and redirect URIs in Google Cloud Console
- Ensure frontend is using correct client ID

### Template Not Found Errors
- Verify `templates/` directory is included in deployment
- Check that frontend build was copied to `static/app/`

## 📊 Key Features Configured

✅ Flask-CORS properly installed and configured
✅ ML model with feature engineering (10 features)
✅ Google OAuth 2.0 Sign-In
✅ Firebase integration for user management
✅ React frontend with Vite
✅ Professional CI/CD pipeline
✅ Health monitoring and logging
✅ Auto-restart on deployment

## 🔗 Useful Links

- **Application**: https://diabetes-predictor-ai.azurewebsites.net
- **Kudu Console**: https://diabetes-predictor-ai.scm.azurewebsites.net
- **Azure Portal**: https://portal.azure.com/#view/WebsitesExtension/WebsiteMenuBlade/~/Configuration/resourceId/%2Fsubscriptions%2F%3Csubscription-id%3E%2FresourceGroups%2Fdiabetes-predictor-rg%2Fproviders%2FMicrosoft.Web%2Fsites%2Fdiabetes-predictor-ai
- **GitHub Actions**: https://github.com/Naveenkumar-2007/Daibetes/actions

## 📝 Next Steps

1. ✅ Set up Google OAuth credentials
2. ✅ Add environment variables to Azure
3. ✅ Upload Firebase service account key
4. 🔄 Push to GitHub to trigger deployment
5. ✅ Verify application is running
6. ✅ Test Google Sign-In functionality
7. ✅ Test diabetes prediction feature

---
**Last Updated**: November 23, 2025
**Status**: Production Ready ✅

# 🚀 Azure Deployment Guide for Diabetes Predictor

## Prerequisites
- Azure Account with active subscription
- Azure CLI installed (`az --version` to check)
- Docker installed locally
- Git repository pushed to GitHub

## Deployment Options

### Option 1: Azure App Service with Docker (Recommended)

#### Step 1: Prepare Environment Variables
Create a `.env.production` file:
```env
GROQ_API_KEY=your_groq_api_key_here
FIREBASE_DATABASE_URL=https://diabetes-prediction-22082-default-rtdb.firebaseio.com
SECRET_KEY=your_secure_secret_key_here
FLASK_ENV=production
```

#### Step 2: Login to Azure
```bash
az login
az account set --subscription "Your-Subscription-Name"
```

#### Step 3: Create Resource Group
```bash
az group create \
  --name diabetes-predictor-rg \
  --location eastus
```

#### Step 4: Create Azure Container Registry (ACR)
```bash
az acr create \
  --resource-group diabetes-predictor-rg \
  --name diabetesacr \
  --sku Basic \
  --admin-enabled true
```

#### Step 5: Get ACR Credentials
```bash
az acr credential show --name diabetesacr
```
Save the username and password.

#### Step 6: Build and Push Docker Image
```bash
# Login to ACR
az acr login --name diabetesacr

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Build and tag Docker image
docker build -t diabetesacr.azurecr.io/diabetes-predictor:latest .

# Push to ACR
docker push diabetesacr.azurecr.io/diabetes-predictor:latest
```

#### Step 7: Create App Service Plan
```bash
az appservice plan create \
  --name diabetes-plan \
  --resource-group diabetes-predictor-rg \
  --is-linux \
  --sku B1
```

#### Step 8: Create Web App
```bash
az webapp create \
  --resource-group diabetes-predictor-rg \
  --plan diabetes-plan \
  --name diabetes-predictor-ai \
  --deployment-container-image-name diabetesacr.azurecr.io/diabetes-predictor:latest
```

#### Step 9: Configure Container Registry Credentials
```bash
az webapp config container set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --docker-custom-image-name diabetesacr.azurecr.io/diabetes-predictor:latest \
  --docker-registry-server-url https://diabetesacr.azurecr.io \
  --docker-registry-server-user <ACR_USERNAME> \
  --docker-registry-server-password <ACR_PASSWORD>
```

#### Step 10: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    GROQ_API_KEY="your_groq_api_key" \
    FIREBASE_DATABASE_URL="https://diabetes-prediction-22082-default-rtdb.firebaseio.com" \
    SECRET_KEY="your_secure_secret_key" \
    WEBSITES_PORT=8080 \
    FLASK_ENV=production
```

#### Step 11: Enable Logging
```bash
az webapp log config \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --docker-container-logging filesystem
```

#### Step 12: Restart and Monitor
```bash
# Restart app
az webapp restart \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

# Stream logs
az webapp log tail \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg
```

---

### Option 2: GitHub Actions CI/CD (Automated)

#### Step 1: Setup GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_CREDENTIALS` - Azure service principal JSON
- `GROQ_API_KEY` - Your Groq API key
- `FIREBASE_DATABASE_URL` - Firebase database URL
- `SECRET_KEY` - Flask secret key

#### Step 2: Create Azure Service Principal
```bash
az ad sp create-for-rbac \
  --name "diabetes-predictor-sp" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/diabetes-predictor-rg \
  --sdk-auth
```
Copy the entire JSON output and add it as `AZURE_CREDENTIALS` secret.

#### Step 3: Push to GitHub
```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Build frontend
2. Build Docker image
3. Push to ACR
4. Deploy to Azure App Service

---

### Option 3: Azure Web App (Direct Python Deployment)

#### Step 1: Create Web App (Python Runtime)
```bash
az webapp up \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11" \
  --sku B1 \
  --location eastus
```

#### Step 2: Configure Startup Command
```bash
az webapp config set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 600 flask_app:app"
```

#### Step 3: Set Environment Variables (same as Option 1, Step 10)

---

## Post-Deployment Configuration

### 1. Configure Custom Domain (Optional)
```bash
az webapp config hostname add \
  --webapp-name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --hostname yourdomain.com
```

### 2. Enable HTTPS Only
```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

### 3. Configure CORS
```bash
az webapp cors add \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --allowed-origins "*"
```

### 4. Scale Up (if needed)
```bash
az appservice plan update \
  --name diabetes-plan \
  --resource-group diabetes-predictor-rg \
  --sku P1V2
```

---

## Troubleshooting

### Check Application Logs
```bash
az webapp log tail \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg
```

### SSH into Container
```bash
az webapp ssh \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg
```

### Check Deployment Status
```bash
az webapp deployment list-publishing-profiles \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg
```

### Common Issues

1. **App not starting**: Check environment variables and logs
2. **502 Bad Gateway**: Check if port 8080 is exposed and gunicorn is running
3. **Module not found**: Rebuild Docker image with all dependencies
4. **Firebase connection**: Verify `firebase-service-account.json` is in container

---

## Access Your Application

Your app will be available at:
```
https://diabetes-predictor-ai.azurewebsites.net
```

---

## Cost Optimization

- **B1 Basic**: ~$13/month - Good for testing
- **P1V2 Premium**: ~$73/month - Production ready
- **Free Tier**: 60 minutes/day - For development only

---

## Monitoring

### Enable Application Insights
```bash
az monitor app-insights component create \
  --app diabetes-predictor-insights \
  --location eastus \
  --resource-group diabetes-predictor-rg \
  --application-type web

az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="<INSTRUMENTATION_KEY>"
```

---

## Backup and Disaster Recovery

```bash
az webapp config backup create \
  --resource-group diabetes-predictor-rg \
  --webapp-name diabetes-predictor-ai \
  --backup-name initial-backup \
  --container-url "<STORAGE_CONTAINER_URL_WITH_SAS>"
```

---

## Deployment Checklist

- [ ] Azure account setup
- [ ] Environment variables configured
- [ ] Frontend built (`npm run build`)
- [ ] Docker image tested locally
- [ ] ACR created and image pushed
- [ ] App Service created
- [ ] Environment variables set in Azure
- [ ] HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Application Insights enabled (optional)
- [ ] Backup configured (optional)
- [ ] Test all features (login, predict, reports)
- [ ] Monitor logs for errors

---

## Quick Deploy Script

Save this as `deploy-to-azure.sh`:

```bash
#!/bin/bash

# Configuration
RG="diabetes-predictor-rg"
ACR_NAME="diabetesacr"
APP_NAME="diabetes-predictor-ai"
PLAN_NAME="diabetes-plan"
LOCATION="eastus"

echo "🚀 Starting Azure Deployment..."

# Build frontend
echo "📦 Building frontend..."
cd frontend && npm install && npm run build && cd ..

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $ACR_NAME.azurecr.io/diabetes-predictor:latest .

# Login to Azure
echo "🔐 Logging into Azure..."
az login

# Create resources
echo "🏗️ Creating Azure resources..."
az group create --name $RG --location $LOCATION
az acr create --resource-group $RG --name $ACR_NAME --sku Basic --admin-enabled true

# Push image
echo "📤 Pushing Docker image..."
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/diabetes-predictor:latest

# Create and configure app
echo "🌐 Creating web app..."
az appservice plan create --name $PLAN_NAME --resource-group $RG --is-linux --sku B1
az webapp create --resource-group $RG --plan $PLAN_NAME --name $APP_NAME \
  --deployment-container-image-name $ACR_NAME.azurecr.io/diabetes-predictor:latest

# Get ACR credentials
CREDS=$(az acr credential show --name $ACR_NAME --query "{username:username, password:passwords[0].value}" -o tsv)
ACR_USER=$(echo $CREDS | cut -f1)
ACR_PASS=$(echo $CREDS | cut -f2)

# Configure container
az webapp config container set \
  --name $APP_NAME --resource-group $RG \
  --docker-custom-image-name $ACR_NAME.azurecr.io/diabetes-predictor:latest \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $ACR_USER \
  --docker-registry-server-password $ACR_PASS

echo "✅ Deployment complete!"
echo "🌍 Your app: https://$APP_NAME.azurewebsites.net"
```

Run with: `chmod +x deploy-to-azure.sh && ./deploy-to-azure.sh`

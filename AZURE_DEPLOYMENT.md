# Azure Deployment Guide for Diabetes Health Predictor

## Prerequisites
1. Azure Account (free tier available)
2. GitHub Account
3. Azure CLI installed locally

## Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Diabetes Health Predictor with Azure CI/CD"

# Add remote (already done)
git remote add origin https://github.com/Naveenkumar-2007/Daibetes.git

# Push to GitHub
git push -u origin main
```

## Step 2: Create Azure Web App

### Option A: Using Azure Portal (Recommended)

1. **Login to Azure Portal**: https://portal.azure.com

2. **Create Web App**:
   - Click "Create a resource"
   - Search for "Web App"
   - Click "Create"

3. **Configure Web App**:
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new "diabetes-predictor-rg"
   - **Name**: `diabetes-predictor-ai` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.12
   - **Operating System**: Linux
   - **Region**: Choose nearest (e.g., East US)
   - **Pricing Plan**: F1 (Free) or B1 (Basic $13/month)

4. **Click "Review + Create"**, then **"Create"**

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name diabetes-predictor-rg --location eastus

# Create App Service Plan
az appservice plan create --name diabetes-predictor-plan --resource-group diabetes-predictor-rg --sku B1 --is-linux

# Create Web App
az webapp create --resource-group diabetes-predictor-rg --plan diabetes-predictor-plan --name diabetes-predictor-ai --runtime "PYTHON:3.12"
```

## Step 3: Configure Environment Variables in Azure

1. Go to your Web App in Azure Portal
2. Navigate to **Settings** → **Configuration**
3. Click **"+ New application setting"** for each variable:

```
GROQ_API_KEY=your_groq_key_here
FIREBASE_API_KEY=your_firebase_key
FIREBASE_PROJECT_ID=diabetes-prediction-22082
FIREBASE_CLIENT_EMAIL=your_firebase_email
FIREBASE_STORAGE_BUCKET=your_bucket
FIREBASE_DATABASE_URL=your_database_url
FIREBASE_SERVICE_ACCOUNT_JSON=your_base64_encoded_json
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
SMTP_FROM_EMAIL=your_email
SMTP_HOST=smtp.gmail.com
SMTP_PASSWORD=your_app_password
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email
SECRET_KEY=your_secret_key_here
```

4. Click **"Save"** at the top

## Step 4: Setup GitHub Actions CI/CD

1. **Get Azure Publish Profile**:
   - In Azure Portal, go to your Web App
   - Click **"Get publish profile"** (top menu)
   - Download the `.PublishSettings` file
   - Open it and copy the entire XML content

2. **Add to GitHub Secrets**:
   - Go to your GitHub repo: https://github.com/Naveenkumar-2007/Daibetes
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **"New repository secret"**
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste the entire publish profile XML
   - Click **"Add secret"**

3. **Update Azure App Name** (if different):
   - Edit `.github/workflows/azure-deploy.yml`
   - Change `AZURE_WEBAPP_NAME: diabetes-predictor-ai` to your app name

## Step 5: Deploy!

```bash
# Add all files
git add .

# Commit
git commit -m "Add Azure deployment configuration"

# Push to trigger deployment
git push origin main
```

## Step 6: Monitor Deployment

1. **GitHub Actions**:
   - Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
   - Watch the deployment workflow

2. **Azure Portal**:
   - Go to your Web App → **Deployment** → **Deployment Center**
   - View deployment logs

## Step 7: Access Your App

Once deployed, your app will be available at:
```
https://diabetes-predictor-ai.azurewebsites.net
```

## Troubleshooting

### Check Logs
```bash
# Stream logs
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# Or in Azure Portal:
# Web App → Monitoring → Log stream
```

### Common Issues

1. **App won't start**:
   - Check if `gunicorn` is in requirements.txt ✅
   - Verify Procfile exists ✅
   - Check environment variables are set

2. **Database connection issues**:
   - Verify Firebase credentials in Configuration
   - Check FIREBASE_SERVICE_ACCOUNT_JSON is properly base64 encoded

3. **Google OAuth not working**:
   - Add Azure URL to Google Cloud Console:
     - Authorized JavaScript origins: `https://diabetes-predictor-ai.azurewebsites.net`
     - Authorized redirect URIs: `https://diabetes-predictor-ai.azurewebsites.net/api/login/google`

## Cost Optimization

- **Free Tier (F1)**: Limited, good for testing
- **Basic Tier (B1)**: $13/month, recommended for production
- **Enable Auto-scaling**: Settings → Scale up → Configure rules

## Continuous Deployment

Every push to `main` branch will automatically:
1. Build the application
2. Run tests (if configured)
3. Deploy to Azure
4. Zero downtime deployment

## Security Best Practices

1. ✅ Environment variables stored in Azure (not in code)
2. ✅ GitHub Secrets for deployment credentials
3. ✅ HTTPS enabled by default on Azure
4. ⚠️ Consider Azure Key Vault for sensitive data

## Monitoring & Analytics

1. **Application Insights** (Recommended):
   - Web App → Monitoring → Application Insights
   - Enable for detailed performance tracking

2. **Alerts**:
   - Set up alerts for errors, high CPU, memory usage

## Next Steps

1. Configure custom domain (optional)
2. Setup SSL certificate (free with Let's Encrypt)
3. Enable Application Insights
4. Configure backup and disaster recovery
5. Setup staging environment

## Support

- Azure Documentation: https://docs.microsoft.com/azure/app-service/
- GitHub Actions: https://docs.github.com/actions
- Issues: https://github.com/Naveenkumar-2007/Daibetes/issues

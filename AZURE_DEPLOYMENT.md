# 🚀 Azure Deployment Guide - Diabetes Health Predictor

Complete guide to deploy your Flask + React application to Azure with automated CI/CD pipeline.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ **Azure Account** ([Sign up for free](https://azure.microsoft.com/free/))
- ✅ **GitHub Account** (where your code is hosted)
- ✅ **Azure CLI** (optional, for command-line deployment)
- ✅ **All environment variables ready** (Firebase, GROQ API, etc.)

---

## 🎯 Quick Start (5 Steps)

### Step 1: Create Azure Web App

#### Option A: Azure Portal (Easiest) ⭐

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → Search **"Web App"** → Click **"Create"**
3. Fill in the details:
   ```
   Subscription: Your Azure subscription
   Resource Group: Create new → "diabetes-predictor-rg"
   Name: diabetes-predictor-ai (must be globally unique)
   Publish: Code
   Runtime stack: Python 3.11
   Operating System: Linux
   Region: East US (or nearest to you)
   Pricing Plan: B1 Basic (recommended) or F1 Free
   ```
4. Click **"Review + Create"** → **"Create"**
5. Wait 2-3 minutes for deployment to complete

#### Option B: Azure CLI (Advanced)

```bash
# Login to Azure
az login

# Create resource group
az group create --name diabetes-predictor-rg --location eastus

# Create App Service Plan
az appservice plan create \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --sku B1 \
  --is-linux

# Create Web App with Python 3.11
az webapp create \
  --resource-group diabetes-predictor-rg \
  --plan diabetes-predictor-plan \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11"
```

---

### Step 2: Configure Environment Variables

Environment variables are **CRITICAL** for your app to work.

1. In Azure Portal, go to your Web App
2. Navigate to: **Settings** → **Configuration** → **Application settings**
3. Click **"+ New application setting"** for each variable below:

#### Required Environment Variables:

```bash
# AI/ML Services
GROQ_API_KEY=gsk_your_groq_api_key_here

# Firebase Configuration
FIREBASE_API_KEY=AIzaSy...
FIREBASE_PROJECT_ID=diabetes-prediction-22082
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@....iam.gserviceaccount.com
FIREBASE_STORAGE_BUCKET=diabetes-prediction-22082.appspot.com
FIREBASE_DATABASE_URL=https://diabetes-prediction-22082.firebaseio.com
FIREBASE_SERVICE_ACCOUNT_JSON=<base64_encoded_service_account_json>

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Email Configuration (SMTP)
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com

# Flask Security
SECRET_KEY=generate-a-strong-random-secret-key-here

# Python Settings (Auto-configured)
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

4. Click **"Save"** (top of page)
5. Click **"Continue"** when warned about app restart

> 💡 **Tip**: To generate a strong SECRET_KEY:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### Step 3: Get Azure Publish Profile

This is needed for GitHub Actions to deploy automatically.

1. In Azure Portal, go to your Web App
2. Click **"Get publish profile"** button (top toolbar)
3. A `.PublishSettings` XML file will download
4. Open the file in a text editor
5. **Copy the entire XML content** (Ctrl+A, Ctrl+C)

---

### Step 4: Configure GitHub Secrets

1. Go to your GitHub repository: `https://github.com/Naveenkumar-2007/Daibetes`
2. Click **Settings** (top right)
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Create a secret:
   - **Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value**: Paste the entire XML content from Step 3
6. Click **"Add secret"**

---

### Step 5: Deploy Your Application

#### Method 1: Automatic Deployment (CI/CD) ✅

The CI/CD pipeline is already configured! Just push your code:

```bash
# Make sure you're on main branch
git checkout main

# Add all files
git add .

# Commit changes
git commit -m "Deploy to Azure with CI/CD"

# Push to GitHub (triggers deployment automatically)
git push origin main
```

**What happens next:**
1. ✅ GitHub Actions starts automatically
2. ✅ Builds Python backend
3. ✅ Builds React frontend
4. ✅ Combines frontend with Flask
5. ✅ Deploys to Azure
6. ✅ Health check verifies deployment

**Monitor the deployment:**
- Go to your GitHub repo → **Actions** tab
- Watch the "Deploy to Azure Web App" workflow
- Wait 5-10 minutes for first deployment

#### Method 2: Manual Deployment (Using Azure CLI)

```bash
# Login to Azure
az login

# Deploy from local directory
az webapp up \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11" \
  --sku B1
```

---

## 🔍 Verify Deployment

1. **Check Azure Portal:**
   - Go to your Web App → **Overview**
   - Look for: "Status: Running"
   - Click on the URL: `https://diabetes-predictor-ai.azurewebsites.net`

2. **Check Application Logs:**
   ```bash
   # View live logs
   az webapp log tail \
     --resource-group diabetes-predictor-rg \
     --name diabetes-predictor-ai
   ```

3. **Test Endpoints:**
   ```bash
   # Test homepage
   curl https://diabetes-predictor-ai.azurewebsites.net
   
   # Should return 200 or 302
   ```

---

## 🐛 Troubleshooting

### Issue: "Application Error" or 500 Error

**Solution:**
1. Check logs in Azure Portal:
   - Web App → **Monitoring** → **Log stream**
2. Verify all environment variables are set correctly
3. Check if `requirements.txt` has all dependencies

### Issue: Frontend not loading

**Solution:**
1. Ensure GitHub Actions completed successfully
2. Check if `static/app/` folder has files:
   ```bash
   az webapp ssh
   ls -la /home/site/wwwroot/static/app/
   ```

### Issue: Firebase/Database errors

**Solution:**
1. Verify Firebase credentials in Configuration
2. Check `FIREBASE_SERVICE_ACCOUNT_JSON` is valid base64
3. Test Firebase connection locally first

### Issue: Slow cold starts

**Solution:**
- Upgrade to B1 or higher pricing tier (F1 has cold start delays)
- In Azure Portal: **Scale up (App Service plan)** → Select B1 Basic

---

## 🔄 Update/Redeploy Application

After making code changes:

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "Fix: Updated prediction model"

# Push to trigger auto-deployment
git push origin main
```

GitHub Actions will automatically:
- ✅ Build your changes
- ✅ Run tests (if configured)
- ✅ Deploy to Azure
- ✅ Verify deployment

---

## 🎛️ CI/CD Pipeline Configuration

Your workflow file: `.github/workflows/azure-deploy.yml`

**Key features:**
- ✅ Builds Python 3.11 backend
- ✅ Builds React 20.x frontend
- ✅ Combines frontend with Flask
- ✅ Runs tests (if available)
- ✅ Deploys to Azure
- ✅ Post-deployment health check
- ✅ Detailed deployment summary

**Environment variables in workflow:**
```yaml
env:
  AZURE_WEBAPP_NAME: diabetes-predictor-ai  # Change this to your app name
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'
```

---

## 📊 Monitoring & Maintenance

### Enable Application Insights (Recommended)

1. In Azure Portal, go to your Web App
2. Left sidebar: **Monitoring** → **Application Insights**
3. Click **"Turn on Application Insights"**
4. Select **"Create new"** or use existing resource
5. Click **"Apply"**

Benefits:
- 📈 Performance monitoring
- 🐛 Error tracking
- 📊 Usage analytics
- 🔍 Request tracing

### View Logs

**Real-time logs:**
```bash
az webapp log tail --resource-group diabetes-predictor-rg --name diabetes-predictor-ai
```

**Download logs:**
```bash
az webapp log download --resource-group diabetes-predictor-rg --name diabetes-predictor-ai
```

**In Azure Portal:**
- Web App → **Monitoring** → **Log stream**

---

## 💰 Cost Management

### Free Tier (F1)
- **Cost**: $0/month
- **Limitations**: 
  - 60 CPU minutes/day
  - 1 GB RAM
  - Cold starts (slow first load)
  - No custom domains

### Basic Tier (B1) - Recommended
- **Cost**: ~$13/month
- **Benefits**:
  - Always on (no cold starts)
  - 1.75 GB RAM
  - Custom domains
  - Better performance

### To change pricing tier:
1. Azure Portal → Your Web App
2. **Settings** → **Scale up (App Service plan)**
3. Select desired tier
4. Click **"Apply"**

---

## 🔒 Security Best Practices

### 1. Use Azure Key Vault (Production)

Instead of storing secrets in Application Settings:

```bash
# Create Key Vault
az keyvault create \
  --name diabetes-kv-unique \
  --resource-group diabetes-predictor-rg \
  --location eastus

# Add secret
az keyvault secret set \
  --vault-name diabetes-kv-unique \
  --name "GROQ-API-KEY" \
  --value "your-secret-value"

# Grant Web App access
az webapp identity assign \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai
```

### 2. Enable HTTPS Only

```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

### 3. Configure CORS (if needed)

In `flask_app.py`:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://yourdomain.com"])
```

---

## 🚀 Performance Optimization

### 1. Enable Caching

In Azure Portal:
- Web App → **Settings** → **Configuration**
- Add: `MPLCONFIGDIR=/tmp/matplotlib`

### 2. Optimize Startup

Ensure `startup.sh` is configured:
```bash
#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 flask_app:app
```

### 3. Use CDN for Static Files (Advanced)

For production, serve `static/` files via Azure CDN for faster loading.

---

## 📱 Custom Domain Setup (Optional)

### 1. Add Custom Domain

```bash
# Add custom domain
az webapp config hostname add \
  --resource-group diabetes-predictor-rg \
  --webapp-name diabetes-predictor-ai \
  --hostname yourdomain.com
```

### 2. Configure DNS

Add CNAME record in your DNS provider:
```
CNAME: www → diabetes-predictor-ai.azurewebsites.net
```

### 3. Enable SSL

Azure provides free SSL certificates:
1. Web App → **Settings** → **Custom domains**
2. Click your domain → **Add binding**
3. Select **Azure managed certificate** (free)
4. Click **"Add"**

---

## 🔄 Backup & Disaster Recovery

### Create Backup

```bash
# Create storage account
az storage account create \
  --name diabetesbackup \
  --resource-group diabetes-predictor-rg \
  --location eastus

# Configure backup
az webapp config backup create \
  --resource-group diabetes-predictor-rg \
  --webapp-name diabetes-predictor-ai \
  --backup-name InitialBackup \
  --container-url <storage-container-url>
```

---

## 🧪 Testing CI/CD Pipeline

To test the pipeline without deploying:

1. Create a test branch:
```bash
git checkout -b test-deployment
```

2. Modify `.github/workflows/azure-deploy.yml`:
```yaml
on:
  push:
    branches:
      - main
      - test-deployment  # Add this
```

3. Push and watch Actions tab:
```bash
git push origin test-deployment
```

---

## 📝 Useful Commands Cheat Sheet

```bash
# View app logs
az webapp log tail -g diabetes-predictor-rg -n diabetes-predictor-ai

# Restart app
az webapp restart -g diabetes-predictor-rg -n diabetes-predictor-ai

# View app settings
az webapp config appsettings list -g diabetes-predictor-rg -n diabetes-predictor-ai

# Update app setting
az webapp config appsettings set \
  -g diabetes-predictor-rg \
  -n diabetes-predictor-ai \
  --settings KEY=VALUE

# SSH into app
az webapp ssh -g diabetes-predictor-rg -n diabetes-predictor-ai

# View deployment history
az webapp deployment list -g diabetes-predictor-rg -n diabetes-predictor-ai

# Scale app
az appservice plan update \
  -g diabetes-predictor-rg \
  -n diabetes-predictor-plan \
  --sku B2
```

---

## 🆘 Getting Help

### Azure Support
- **Documentation**: https://docs.microsoft.com/azure/app-service/
- **Support**: Azure Portal → **Help + support**
- **Community**: https://stackoverflow.com/questions/tagged/azure-web-app-service

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 502/503 errors | Check logs, verify startup command, increase timeout |
| Static files not loading | Check `web.config`, verify build process |
| Firebase errors | Verify credentials, check network access |
| Memory issues | Upgrade to B1 or higher tier |
| Slow performance | Enable Application Insights, check database queries |

---

## ✅ Post-Deployment Checklist

- [ ] Application loads successfully
- [ ] Login/authentication works
- [ ] Predictions are generating
- [ ] Reports can be generated
- [ ] Email notifications working (if configured)
- [ ] All environment variables set
- [ ] HTTPS enabled
- [ ] Application Insights configured
- [ ] Logs are accessible
- [ ] Backup configured (for production)
- [ ] Custom domain configured (if needed)
- [ ] Cost alerts set up

---

## 🎉 Success!

Your Diabetes Health Predictor is now live on Azure!

**Next Steps:**
1. Test all features thoroughly
2. Monitor logs for any errors
3. Share your application URL
4. Set up monitoring alerts
5. Configure backups for production

**Live URL:** `https://diabetes-predictor-ai.azurewebsites.net`

---

## 📚 Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [Flask on Azure](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Python Web App Tutorial](https://docs.microsoft.com/azure/app-service/tutorial-python-postgresql-app)

---

**Need help?** Open an issue on GitHub or contact your team lead!
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

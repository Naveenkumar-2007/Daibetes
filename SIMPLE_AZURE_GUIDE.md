# 🎯 Simple Azure Deployment - Step by Step Guide

## Quick Start for Windows Users

### Method 1: One-Click PowerShell Deployment (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X` → Select "Windows PowerShell (Admin)"

2. **Navigate to project folder**
   ```powershell
   cd C:\Users\navee\Downloads\Diabetes-Risk-predictor-main\Diabetes-Risk-predictor-main
   ```

3. **Run deployment script**
   ```powershell
   .\deploy-to-azure.ps1
   ```

4. **Follow prompts:**
   - Login to Azure when browser opens
   - Enter your GROQ_API_KEY
   - Press Enter for default Firebase URL
   - Press Enter to generate SECRET_KEY automatically

5. **Wait 10-15 minutes** for deployment to complete

6. **Access your app** at: `https://diabetes-predictor-ai.azurewebsites.net`

---

## Method 2: Azure Portal (Manual - No Command Line)

### Step 1: Prepare Your Application

1. **Build Frontend Locally**
   ```powershell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. **Zip the entire project**
   - Right-click project folder → Send to → Compressed (zipped) folder

### Step 2: Login to Azure Portal

1. Go to: https://portal.azure.com
2. Sign in with your Microsoft account

### Step 3: Create Web App

1. Click **"Create a resource"**
2. Search for **"Web App"** → Click **Create**
3. Fill in details:
   - **Subscription**: Choose your subscription
   - **Resource Group**: Click "Create new" → Enter: `diabetes-predictor-rg`
   - **Name**: `diabetes-predictor-ai` (must be globally unique)
   - **Publish**: Docker Container
   - **Operating System**: Linux
   - **Region**: East US (or nearest)
   - **Pricing Plan**: B1 Basic (or higher)
4. Click **"Next: Docker"**

### Step 4: Configure Docker

1. **Options**: Single Container
2. **Image Source**: Docker Hub
3. **Access Type**: Public
4. **Image and tag**: `python:3.11-slim` (temporary - we'll change this)
5. Click **"Review + Create"** → **Create**

### Step 5: Configure Environment Variables

1. Once created, go to your Web App resource
2. In left menu, click **"Configuration"** under Settings
3. Click **"+ New application setting"** and add these:

   | Name | Value |
   |------|-------|
   | `GROQ_API_KEY` | `your_groq_api_key_here` |
   | `FIREBASE_DATABASE_URL` | `https://diabetes-prediction-22082-default-rtdb.firebaseio.com` |
   | `SECRET_KEY` | `generate-random-32-character-string` |
   | `WEBSITES_PORT` | `8080` |
   | `FLASK_ENV` | `production` |
   | `PYTHONUNBUFFERED` | `1` |

4. Click **"Save"** at the top

### Step 6: Deploy Using ZIP

Since we can't easily build Docker from portal, let's use ZIP deployment:

1. Go to **"Deployment Center"** in left menu
2. Choose **"Local Git"** or **"External Git"**
3. Or use **FTP/FTPS** to upload files

**Better Option: Use VS Code Extension**

1. Install "Azure App Service" extension in VS Code
2. Right-click your folder → **"Deploy to Web App"**
3. Select your Azure subscription and web app
4. Confirm deployment

### Step 7: Enable Logging

1. Go to **"App Service logs"** in left menu
2. Enable:
   - **Application Logging**: File System, Level: Information
   - **Deployment Logging**: On
   - **Detailed Error Messages**: On
3. Click **"Save"**

### Step 8: View Logs

1. Go to **"Log stream"** in left menu
2. Monitor for startup messages
3. Wait 2-3 minutes for app to fully start

---

## Method 3: Using Azure CLI (Command Line)

### Prerequisites
- Install Azure CLI: https://aka.ms/installazurecliwindows
- Install Docker Desktop: https://www.docker.com/products/docker-desktop

### Quick Commands

```powershell
# Login
az login

# Create everything
az group create --name diabetes-predictor-rg --location eastus

# Create App Service Plan
az appservice plan create `
  --name diabetes-plan `
  --resource-group diabetes-predictor-rg `
  --is-linux `
  --sku B1

# Create Web App with Python
az webapp create `
  --resource-group diabetes-predictor-rg `
  --plan diabetes-plan `
  --name diabetes-predictor-ai `
  --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set `
  --resource-group diabetes-predictor-rg `
  --name diabetes-predictor-ai `
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 600 flask_app:app"

# Set environment variables
az webapp config appsettings set `
  --resource-group diabetes-predictor-rg `
  --name diabetes-predictor-ai `
  --settings `
    GROQ_API_KEY="your_key" `
    FIREBASE_DATABASE_URL="your_firebase_url" `
    SECRET_KEY="your_secret" `
    FLASK_ENV=production

# Deploy code (from project root)
az webapp up `
  --resource-group diabetes-predictor-rg `
  --name diabetes-predictor-ai `
  --runtime "PYTHON:3.11"
```

---

## Method 4: GitHub Actions (Automatic CI/CD)

### Setup Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/diabetes-predictor.git
   git push -u origin main
   ```

2. **Get Azure Publish Profile**
   - Go to your Web App in Azure Portal
   - Click **"Get publish profile"** at the top
   - Save the downloaded file

3. **Add GitHub Secret**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click **"New repository secret"**
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste entire content of publish profile file
   - Click **"Add secret"**

4. **The workflow file is already configured!**
   - File: `.github/workflows/azure-docker-deploy.yml`
   - It will automatically deploy on every push to main branch

5. **Push to trigger deployment**
   ```bash
   git push origin main
   ```

6. **Monitor deployment**
   - Go to GitHub repo → Actions tab
   - Watch the deployment progress

---

## Troubleshooting

### App not starting?
```powershell
# View logs
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# Restart app
az webapp restart --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

### Check app status
```powershell
az webapp show `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --query state
```

### SSH into container
```powershell
az webapp ssh --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

### Common Issues

1. **"Application Error"**: Check logs, verify environment variables set correctly
2. **"502 Bad Gateway"**: App taking too long to start, wait 2-3 minutes
3. **"Module not found"**: Requirements.txt missing dependencies
4. **"Cannot connect to Firebase"**: Check FIREBASE_DATABASE_URL is correct

---

## Cost Estimate

| Tier | Monthly Cost | CPU | RAM | Storage |
|------|-------------|-----|-----|---------|
| **Free (F1)** | $0 | Shared | 1 GB | 1 GB |
| **Basic (B1)** | ~$13 | 1 Core | 1.75 GB | 10 GB |
| **Standard (S1)** | ~$70 | 1 Core | 1.75 GB | 50 GB |
| **Premium (P1V2)** | ~$73 | 1 Core | 3.5 GB | 250 GB |

**Recommended**: Start with B1 Basic for testing, upgrade to S1 or P1V2 for production.

---

## Next Steps After Deployment

1. ✅ Test login functionality
2. ✅ Test prediction feature
3. ✅ Test report generation and download
4. ✅ Test mobile responsiveness
5. ✅ Configure custom domain (optional)
6. ✅ Enable Application Insights for monitoring
7. ✅ Set up automatic backups

---

## Quick Access Links

- **Your App**: https://diabetes-predictor-ai.azurewebsites.net
- **Azure Portal**: https://portal.azure.com
- **Resource Group**: Search "diabetes-predictor-rg" in portal
- **Deployment Center**: Web App → Deployment Center
- **Logs**: Web App → Log stream

---

## Delete Everything (Cleanup)

```powershell
az group delete --name diabetes-predictor-rg --yes --no-wait
```

This removes ALL resources and stops billing.

---

## Support

If you encounter issues:
1. Check logs first: `az webapp log tail -n diabetes-predictor-ai -g diabetes-predictor-rg`
2. Restart app: `az webapp restart -n diabetes-predictor-ai -g diabetes-predictor-rg`
3. Verify environment variables in Portal → Configuration
4. Check Firebase connection in logs
5. Ensure all dependencies in requirements.txt

**Your deployment is complete!** 🎉

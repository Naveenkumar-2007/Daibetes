# 🚀 GitHub Actions CI/CD Setup Guide

## Quick Fix for "Publish profile is invalid" Error

The error you're seeing occurs when:
1. The publish profile doesn't match the Azure Web App name
2. The publish profile is for a different slot
3. The publish profile has expired or been regenerated

## ✅ Solution Steps

### Step 1: Get Fresh Publish Profile

#### Option A: Using PowerShell Script (Recommended)
```powershell
# Run this script in PowerShell
.\get-publish-profile.ps1
```

#### Option B: Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Web App: **diabetes-predictor-ai**
3. Click **"Get publish profile"** (top menu bar)
4. Save the downloaded XML file
5. Open it with a text editor and copy **entire contents**

#### Option C: Azure CLI
```bash
# Login to Azure
az login

# Get publish profile
az webapp deployment list-publishing-profiles \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --xml
```

### Step 2: Add to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Set up the secret:
   - **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value:** Paste the **entire XML content** from the publish profile
5. Click **"Add secret"**

### Step 3: Verify Web App Name

Make sure the app name in your workflow matches Azure:

**In `.github/workflows/azure-deploy.yml`:**
```yaml
env:
  AZURE_WEBAPP_NAME: diabetes-predictor-ai  # Must match your Azure Web App
```

**Check in Azure Portal:**
- Go to your Web App
- The name should be: **diabetes-predictor-ai**
- If different, update the workflow file

### Step 4: Test Deployment

```bash
# Commit changes
git add .
git commit -m "Fix Azure deployment configuration"

# Push to trigger deployment
git push origin main
```

## 🔍 What Was Fixed

### 1. Updated GitHub Workflow (`.github/workflows/azure-deploy.yml`)
- ✅ Added `slot-name: 'production'` to specify deployment slot
- ✅ Added `clean: true` to ensure clean deployment
- ✅ Improved package verification to catch missing files early
- ✅ Better error handling and logging

### 2. Created `.deployment` File
- Configures Azure to build during deployment
- Ensures proper deployment mode

### 3. Improved `startup.sh`
- Added error checking and validation
- Better logging for troubleshooting
- Uses `exec` to replace shell with Gunicorn process
- Added `--preload` for faster startup

## 📋 Common Issues and Solutions

### Issue 1: "Failed to set resource details"
**Cause:** Publish profile doesn't match the web app name or slot

**Solution:**
1. Re-download publish profile from Azure Portal
2. Verify app name matches in workflow file
3. Update GitHub secret with new profile

### Issue 2: "Deployment Failed"
**Cause:** Multiple possible causes

**Solution:**
```bash
# Check Azure logs
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# Or via portal
# Portal → Web App → Monitoring → Log stream
```

### Issue 3: Application Not Starting
**Cause:** Missing dependencies or configuration

**Solution:**
1. Verify all environment variables are set in Azure Portal
2. Check Application Insights or Log Stream
3. Ensure `startup.sh` is executable

### Issue 4: 502 Bad Gateway
**Cause:** Application crash or startup failure

**Solution:**
```bash
# SSH into container (if enabled)
az webapp ssh --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# Check logs
tail -f /home/LogFiles/*.log
```

## 🔧 Environment Configuration

Make sure these are set in Azure Portal → Configuration → Application Settings:

### Critical Variables:
```bash
GROQ_API_KEY=your_key_here
FIREBASE_API_KEY=your_key_here
FIREBASE_PROJECT_ID=diabetes-prediction-22082
SECRET_KEY=your_secret_key_here
```

### Optional but Recommended:
```bash
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_app_password
WEBSITES_PORT=8000
WEBSITES_CONTAINER_START_TIME_LIMIT=600
```

## 📊 Monitoring Deployment

### GitHub Actions
- View runs: `https://github.com/YOUR-USERNAME/YOUR-REPO/actions`
- Check build logs for errors
- Verify artifact upload/download

### Azure Portal
- Log Stream: Portal → Web App → Monitoring → Log stream
- Metrics: Portal → Web App → Monitoring → Metrics
- Diagnose: Portal → Web App → Diagnose and solve problems

## 🎯 Deployment Checklist

Before pushing to trigger deployment:

- [ ] Fresh publish profile downloaded from Azure
- [ ] `AZURE_WEBAPP_PUBLISH_PROFILE` secret updated in GitHub
- [ ] App name in workflow matches Azure (diabetes-predictor-ai)
- [ ] All environment variables set in Azure Portal
- [ ] Frontend built locally (optional, GitHub Actions will build)
- [ ] All required files present (flask_app.py, requirements.txt, etc.)
- [ ] `.deployment` file exists
- [ ] `startup.sh` has correct configuration

## 🚀 Deploy Now

```bash
# Verify configuration
.\verify-azure-config.ps1

# If all checks pass, deploy:
git add .
git commit -m "Deploy with fixed Azure configuration"
git push origin main
```

## 📞 Still Having Issues?

1. **Run verification script:**
   ```powershell
   .\verify-azure-config.ps1
   ```

2. **Check GitHub Actions logs:**
   - Look for specific error messages
   - Verify artifact was created successfully

3. **Check Azure logs:**
   ```bash
   az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
   ```

4. **Verify publish profile:**
   - Open the XML file
   - Confirm `msdeploySite` matches your app name
   - Check that credentials haven't been rotated

## 🎉 Success Indicators

After successful deployment, you should see:

1. ✅ GitHub Actions workflow completes without errors
2. ✅ Green checkmark on commit in GitHub
3. ✅ App accessible at: `https://diabetes-predictor-ai.azurewebsites.net`
4. ✅ Health check returns 200 OK
5. ✅ Azure logs show "Gunicorn starting"

---

**Last Updated:** November 23, 2025

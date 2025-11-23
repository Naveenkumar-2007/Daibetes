# 🚀 Quick Fix Guide - Azure Deployment Error

## Problem
```
Error: Deployment Failed, Error: Publish profile is invalid for app-name and slot-name provided.
Warning: Failed to set resource details: Failed to get app runtime OS
```

## ✅ Solution (5 Minutes)

### Step 1: Get Fresh Publish Profile

**Option A: Using PowerShell (Recommended)**
```powershell
.\get-publish-profile-enhanced.ps1
```
This will automatically retrieve and copy the publish profile to clipboard.

**Option B: Azure Portal**
1. Go to: https://portal.azure.com
2. Find your app: **diabetes-predictor-ai**
3. Click **"Download publish profile"** (top menu)
4. Open the XML file and copy ALL contents

### Step 2: Add to GitHub Secrets

1. Go to: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions
2. If `AZURE_WEBAPP_PUBLISH_PROFILE` exists:
   - Click the **pencil icon** to edit
   - Click **"Update secret"**
3. If it doesn't exist:
   - Click **"New repository secret"**
4. Set:
   - **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value:** Paste the ENTIRE XML content
5. Click **"Add secret"** or **"Update secret"**

### Step 3: Deploy

```bash
git add .
git commit -m "Fix: Azure deployment configuration"
git push origin main
```

### Step 4: Monitor

- **GitHub Actions:** https://github.com/Naveenkumar-2007/Daibetes/actions
- **Azure Portal:** https://portal.azure.com → Your Web App → Log Stream

---

## 🔧 What Was Fixed

### 1. **Updated `.github/workflows/azure-deploy.yml`**
   - ✅ Added `slot-name: 'production'` 
   - ✅ Added `clean: true` for clean deployments
   - ✅ Improved error checking and validation

### 2. **Created `.deployment` file**
   - Tells Azure how to deploy your app
   - Enables build during deployment

### 3. **Improved `startup.sh`**
   - Better error handling
   - Validates required files exist
   - More detailed logging

### 4. **Added Helper Scripts**
   - `verify-azure-config.ps1` - Check configuration before deploying
   - `get-publish-profile-enhanced.ps1` - Easy publish profile retrieval

---

## 📋 Pre-Deployment Checklist

Run this to verify everything:
```powershell
.\verify-azure-config.ps1
```

Manual check:
- [ ] Publish profile downloaded from Azure
- [ ] `AZURE_WEBAPP_PUBLISH_PROFILE` added/updated in GitHub Secrets
- [ ] App name in workflow matches Azure: `diabetes-predictor-ai`
- [ ] All environment variables set in Azure Portal
- [ ] `.deployment` file exists
- [ ] `startup.sh` exists

---

## 🐛 Still Not Working?

### Check 1: Verify App Name
In `.github/workflows/azure-deploy.yml`:
```yaml
env:
  AZURE_WEBAPP_NAME: diabetes-predictor-ai  # Must match Azure exactly
```

### Check 2: Verify Secret
- Secret name must be EXACTLY: `AZURE_WEBAPP_PUBLISH_PROFILE`
- Value must include the entire XML (starts with `<?xml...>`)
- No extra spaces or line breaks

### Check 3: Check Azure Status
```powershell
az webapp show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

### Check 4: View Azure Logs
```powershell
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

Or in Azure Portal:
- Your Web App → Monitoring → Log stream

---

## 📞 Common Errors

### Error: "slot-name provided doesn't exist"
**Fix:** Make sure workflow has `slot-name: 'production'`

### Error: "Failed to get app runtime OS"
**Fix:** This is a warning, usually safe to ignore. Verify deployment completed.

### Error: 502 Bad Gateway after deployment
**Fix:** 
1. Check Azure logs for startup errors
2. Verify all environment variables set
3. Check `startup.sh` is executable

### Error: Application never starts
**Fix:**
1. Verify `flask_app.py` exists
2. Check `requirements.txt` is valid
3. View logs in Azure Portal

---

## ✅ Success Indicators

After deployment succeeds:
- ✅ GitHub Actions shows green checkmark
- ✅ App accessible at: https://diabetes-predictor-ai.azurewebsites.net
- ✅ Azure logs show: "Starting Gunicorn on port 8000"
- ✅ No errors in Log Stream

---

## 📚 Additional Resources

- **Full Guide:** `GITHUB_ACTIONS_FIX.md`
- **Azure Deployment:** `AZURE_DEPLOYMENT.md`
- **Verification:** Run `.\verify-azure-config.ps1`

---

**Last Updated:** November 23, 2025
**Next Step:** Run `.\get-publish-profile-enhanced.ps1` and add to GitHub Secrets

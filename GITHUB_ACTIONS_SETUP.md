# 🚀 GitHub Actions Deployment Guide

## Complete Setup in 5 Steps

### Step 1: Create Azure Resources (One-Time Setup)

Open PowerShell and run:

```powershell
# Login to Azure
az login

# Create resource group
az group create --name diabetes-predictor-rg --location eastus

# Create App Service Plan
az appservice plan create `
  --name diabetes-plan `
  --resource-group diabetes-predictor-rg `
  --is-linux `
  --sku B1

# Create Web App
az webapp create `
  --resource-group diabetes-predictor-rg `
  --plan diabetes-plan `
  --name diabetes-predictor-ai `
  --runtime "PYTHON:3.11"
```

**Note**: Change `diabetes-predictor-ai` if the name is taken. Must be globally unique.

---

### Step 2: Create Azure Service Principal

This allows GitHub to access your Azure account:

```powershell
# Get your subscription ID
az account show --query id --output tsv

# Create service principal (replace <SUBSCRIPTION_ID>)
az ad sp create-for-rbac `
  --name "diabetes-predictor-github" `
  --role contributor `
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/diabetes-predictor-rg `
  --sdk-auth
```

**Copy the ENTIRE JSON output** - you'll need it in Step 4!

Example output:
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "xxx",
  "tenantId": "xxx",
  ...
}
```

---

### Step 3: Push Your Code to GitHub

#### If you haven't initialized Git yet:

```powershell
# Initialize Git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Diabetes Predictor"

# Create GitHub repository (do this on github.com or use gh CLI)
# Then connect to remote:
git remote add origin https://github.com/Naveenkumar-2007/Daibetes.git

# Push to GitHub
git push -u origin main
```

#### If you already have a Git repository:

```powershell
# Add changes
git add .

# Commit
git commit -m "Add Azure deployment configuration"

# Push
git push origin main
```

---

### Step 4: Configure GitHub Secrets

1. **Go to your GitHub repository**: https://github.com/Naveenkumar-2007/Daibetes

2. **Click**: `Settings` (top menu)

3. **Click**: `Secrets and variables` → `Actions` (left sidebar)

4. **Click**: `New repository secret` button

5. **Add these 4 secrets**:

#### Secret 1: AZURE_CREDENTIALS
- **Name**: `AZURE_CREDENTIALS`
- **Value**: Paste the ENTIRE JSON from Step 2
- Click `Add secret`

#### Secret 2: GROQ_API_KEY
- **Name**: `GROQ_API_KEY`
- **Value**: Your Groq API key from https://console.groq.com
- Click `Add secret`

#### Secret 3: FIREBASE_DATABASE_URL
- **Name**: `FIREBASE_DATABASE_URL`
- **Value**: `https://diabetes-prediction-22082-default-rtdb.firebaseio.com`
- Click `Add secret`

#### Secret 4: SECRET_KEY
- **Name**: `SECRET_KEY`
- **Value**: Generate with PowerShell:
  ```powershell
  -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
  ```
- Copy the output and use as value
- Click `Add secret`

**Verify all 4 secrets are added:**
- ✅ AZURE_CREDENTIALS
- ✅ GROQ_API_KEY
- ✅ FIREBASE_DATABASE_URL
- ✅ SECRET_KEY

---

### Step 5: Trigger Deployment

#### Option A: Push to GitHub (Automatic)

```powershell
# Make any change (or create empty commit)
git commit --allow-empty -m "Trigger deployment"
git push origin main
```

#### Option B: Manual Trigger

1. Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
2. Click: `Deploy to Azure App Service` (or `Deploy to Azure with Docker`)
3. Click: `Run workflow` button
4. Click: `Run workflow` (green button)

---

## 📊 Monitor Deployment

### Watch the deployment progress:

1. Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
2. Click on the latest workflow run
3. Watch each step complete (takes 5-10 minutes)

### Check deployment logs in Azure:

```powershell
az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

---

## ✅ Verify Deployment Success

### 1. Check if app is running:

```powershell
az webapp show `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --query state
```

Should return: `"Running"`

### 2. Test the URL:

Open browser: https://diabetes-predictor-ai.azurewebsites.net

You should see the login page!

### 3. Check logs for errors:

```powershell
az webapp log tail -n diabetes-predictor-ai -g diabetes-predictor-rg
```

Look for:
- ✅ `Connected to Firebase Realtime Database`
- ✅ `Model loaded successfully`
- ✅ `Groq LLM initialized successfully`
- ✅ `Running on http://0.0.0.0:8000`

---

## 🔄 How Auto-Deployment Works

After setup, **every time you push to GitHub**:

1. ✅ GitHub Actions automatically triggers
2. ✅ Frontend builds (`npm run build`)
3. ✅ Code deploys to Azure
4. ✅ Environment variables configured
5. ✅ App restarts automatically
6. ✅ New version is live in 5-10 minutes

**You never need to manually deploy again!**

---

## 🔧 Workflow Files

Two workflow options (both work):

### Option 1: Simple Python Deployment (Recommended)
**File**: `.github/workflows/azure-deploy-simple.yml`
- Deploys Python app directly
- Faster (~5 minutes)
- Easier to debug

### Option 2: Docker Deployment
**File**: `.github/workflows/azure-docker-deploy.yml`
- Builds Docker container
- Slower (~10 minutes)
- More portable

**Default**: Both are configured. Simple deployment runs first.

To disable one, rename the file:
```powershell
# Disable Docker deployment
git mv .github/workflows/azure-docker-deploy.yml .github/workflows/azure-docker-deploy.yml.disabled
git commit -m "Disable Docker workflow"
git push
```

---

## 🐛 Troubleshooting

### ❌ "Web App does not exist"
**Fix**: Create the web app first (Step 1)

### ❌ "Azure login failed"
**Fix**: Verify `AZURE_CREDENTIALS` secret is correct JSON from Step 2

### ❌ "Deployment succeeded but app shows 502"
**Fix**: Wait 2-3 minutes, app is starting. Check logs:
```powershell
az webapp log tail -n diabetes-predictor-ai -g diabetes-predictor-rg
```

### ❌ "Module not found" error
**Fix**: Verify all dependencies in `requirements.txt`

### ❌ "Firebase connection failed"
**Fix**: Check `FIREBASE_DATABASE_URL` secret is set correctly

### ❌ Workflow shows "secret not found"
**Fix**: Verify all 4 secrets added in Step 4

---

## 📝 Update App Settings Manually

If you need to change environment variables:

```powershell
az webapp config appsettings set `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --settings `
    GROQ_API_KEY="new_key_here" `
    SECRET_KEY="new_secret_here"

# Restart to apply
az webapp restart -n diabetes-predictor-ai -g diabetes-predictor-rg
```

---

## 🔍 View GitHub Actions Logs

1. Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
2. Click on workflow run
3. Click on job name (e.g., "build-and-deploy")
4. Expand steps to see detailed logs

---

## 💰 Cost Summary

| Service | Tier | Cost |
|---------|------|------|
| App Service | B1 | ~$13/month |
| GitHub Actions | Free tier | 2000 min/month free |
| **Total** | | **~$13/month** |

**Free tier notes**:
- GitHub Actions: 2000 minutes/month free (plenty for this)
- Each deployment: ~5 minutes
- You can deploy ~400 times/month for free

---

## 🎯 Quick Reference

### Deploy new version:
```powershell
git add .
git commit -m "Your update message"
git push origin main
```

### View logs:
```powershell
az webapp log tail -n diabetes-predictor-ai -g diabetes-predictor-rg
```

### Restart app:
```powershell
az webapp restart -n diabetes-predictor-ai -g diabetes-predictor-rg
```

### Check status:
```powershell
az webapp show -n diabetes-predictor-ai -g diabetes-predictor-rg --query state
```

### Access app:
```
https://diabetes-predictor-ai.azurewebsites.net
```

---

## ✅ Deployment Checklist

Before first deployment:
- [ ] Azure resources created (Step 1)
- [ ] Service principal created (Step 2)
- [ ] Code pushed to GitHub (Step 3)
- [ ] All 4 secrets configured (Step 4)
- [ ] Workflow triggered (Step 5)
- [ ] Deployment succeeded in GitHub Actions
- [ ] App URL loads successfully
- [ ] Login works
- [ ] Predictions work
- [ ] Reports generate correctly

---

## 🎉 Success!

Your diabetes predictor is now:
- ✅ Deployed to Azure
- ✅ Auto-deploys on every push
- ✅ Fully configured with environment variables
- ✅ Running in production mode
- ✅ Accessible at your Azure URL

**Your app**: https://diabetes-predictor-ai.azurewebsites.net

**GitHub Actions**: https://github.com/Naveenkumar-2007/Daibetes/actions

**Next push to main branch will automatically deploy!** 🚀

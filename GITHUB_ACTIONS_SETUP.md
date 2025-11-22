# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions for automated Azure deployment.

## Overview

The CI/CD pipeline automatically:
1. ✅ Builds the Python backend
2. ✅ Builds the React frontend
3. ✅ Combines them together
4. ✅ Deploys to Azure
5. ✅ Runs health checks

## Prerequisites

Before setting up GitHub Actions, ensure:
- ✅ Azure Web App is created
- ✅ You have the Azure publish profile
- ✅ Your code is pushed to GitHub

## Step-by-Step Setup

### 1. Get Azure Publish Profile

**Option A: Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Web App
3. Click **"Get publish profile"** in the top toolbar
4. Save the downloaded `.PublishSettings` file
5. Open it in a text editor and copy all contents

**Option B: Azure CLI**
```bash
az webapp deployment list-publishing-profiles \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --xml > publish-profile.xml
```

### 2. Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In the left sidebar: **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Add the secret:
   - **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value:** Paste the entire XML content from publish profile
6. Click **"Add secret"**

### 3. Update Workflow Configuration

Edit `.github/workflows/azure-deploy.yml`:

```yaml
env:
  AZURE_WEBAPP_NAME: your-app-name-here  # Change this!
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'
```

Replace `your-app-name-here` with your actual Azure Web App name.

### 4. Verify Workflow File

Ensure your workflow file has the correct structure:

```yaml
name: Deploy to Azure Web App

on:
  push:
    branches:
      - main  # Triggers on push to main
  workflow_dispatch:  # Allows manual trigger

jobs:
  build:
    # Build steps...
  
  deploy:
    needs: build
    # Deploy steps...
```

### 5. Test the Pipeline

#### Automatic Trigger (Recommended)
```bash
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

#### Manual Trigger
1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **"Deploy to Azure Web App"** workflow
4. Click **"Run workflow"** button
5. Select branch: `main`
6. Click **"Run workflow"**

### 6. Monitor Deployment

1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. Watch the progress in real-time
4. Check each step for success ✅ or failure ❌

Expected workflow stages:
```
📥 Checkout code
🐍 Set up Python
📦 Install Python dependencies
🧪 Run tests
📦 Set up Node.js
📦 Install frontend dependencies
🏗️ Build React frontend
📋 Copy frontend to Flask static
📊 Build Summary
📦 Upload artifact
📥 Download artifact
🚀 Deploy to Azure
🔍 Health check
```

## Troubleshooting

### Issue: Workflow doesn't start

**Possible causes:**
- Workflow file not in `.github/workflows/` directory
- Invalid YAML syntax
- Branch name doesn't match trigger

**Solution:**
```bash
# Check workflow file location
ls -la .github/workflows/

# Validate YAML syntax
cat .github/workflows/azure-deploy.yml | python -c "import sys, yaml; yaml.safe_load(sys.stdin)"

# Verify branch
git branch --show-current
```

### Issue: Build fails - Python dependencies

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
- Ensure all packages in `requirements.txt` are valid
- Check for typos in package names
- Verify package versions exist on PyPI

### Issue: Build fails - Frontend

**Error:** `npm ERR! Cannot find module...`

**Solution:**
```bash
# Regenerate package-lock.json
cd frontend
rm package-lock.json
npm install
git add package-lock.json
git commit -m "Update package-lock.json"
git push
```

### Issue: Deployment fails - Publish profile invalid

**Error:** `Error: Publish profile is invalid`

**Solution:**
1. Download a fresh publish profile from Azure
2. Verify you copied the ENTIRE XML content
3. Check for any extra spaces or characters
4. Re-add the secret in GitHub

### Issue: Deployment succeeds but app doesn't work

**Possible causes:**
- Missing environment variables in Azure
- Database/API connection issues
- Static files not served correctly

**Solution:**
1. Check Azure Portal → Configuration → Application settings
2. View Azure logs:
   ```bash
   az webapp log tail -g diabetes-predictor-rg -n diabetes-predictor-ai
   ```
3. Verify all environment variables are set

### Issue: Health check fails

**Error:** `Application might not be responding`

**Solution:**
- Wait 2-3 minutes for app to fully start
- Check if app is running in Azure Portal
- Restart the app:
  ```bash
  az webapp restart -g diabetes-predictor-rg -n diabetes-predictor-ai
  ```

## Workflow Customization

### Run tests before deployment

Add to build job:
```yaml
- name: Run tests
  run: |
    pytest tests/ -v
```

### Deploy to staging first

Create a staging slot:
```yaml
deploy-staging:
  needs: build
  steps:
    - name: Deploy to staging
      uses: azure/webapps-deploy@v3
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        slot-name: staging
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_STAGING }}
```

### Add approval gate

```yaml
deploy:
  needs: build
  environment:
    name: 'Production'
    url: ${{ steps.deploy.outputs.webapp-url }}
  # Requires manual approval in GitHub
```

### Notify on deployment

Add Slack/Discord notification:
```yaml
- name: Notify Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {"text": "✅ Deployed to Azure successfully!"}
```

## Security Best Practices

### 1. Never commit secrets
```bash
# Add to .gitignore
*.PublishSettings
publish-profile.xml
.env
```

### 2. Rotate publish profiles regularly

Regenerate every 90 days:
```bash
az webapp deployment list-publishing-profiles \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --xml > new-profile.xml
```

### 3. Use least privilege

Only grant necessary permissions to service principals.

### 4. Enable branch protection

1. GitHub Repository → **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable: "Require status checks to pass before merging"
4. Select: "Deploy to Azure Web App"

## Monitoring Workflow

### GitHub Actions Dashboard

View all workflows:
- Repository → **Actions** tab
- See success/failure rates
- Download logs for debugging

### Set up notifications

1. GitHub Profile → **Settings** → **Notifications**
2. Enable: "Actions - Workflow run failures"
3. Choose notification method (email/web)

### Workflow badges

Add to README.md:
```markdown
[![Deploy to Azure](https://github.com/USERNAME/REPO/actions/workflows/azure-deploy.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/azure-deploy.yml)
```

## Useful Commands

```bash
# Check workflow status
gh run list --workflow=azure-deploy.yml

# View latest run
gh run view

# Download logs
gh run download RUN_ID

# Re-run failed job
gh run rerun RUN_ID

# Cancel running workflow
gh run cancel RUN_ID
```

## Next Steps

✅ **Workflow is set up!**

Consider adding:
- [ ] Automated tests (pytest, jest)
- [ ] Code quality checks (flake8, eslint)
- [ ] Security scanning (Snyk, Dependabot)
- [ ] Performance testing
- [ ] Staging environment
- [ ] Blue-green deployment
- [ ] Rollback automation

---

**Need help?**
- GitHub Actions Docs: https://docs.github.com/actions
- Azure Deploy Action: https://github.com/Azure/webapps-deploy
- Troubleshooting: Check `AZURE_DEPLOYMENT.md`

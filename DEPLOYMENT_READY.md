# 🚀 Quick Deployment Guide

## ✅ All Fixes Applied

Your Diabetes Health Predictor application has been configured with:

1. ✅ **GROQ API Key** - AI chatbot functionality
2. ✅ **Pinecone API Key** - Vector database for RAG chatbot
3. ✅ **Updated .env file** - Local development ready
4. ✅ **GitHub Actions workflow** - Automated Azure deployment
5. ✅ **Requirements updated** - pinecone-client added

---

## 🎯 Deployment Steps

### Step 1: Configure GitHub Secrets

Run the automated setup script:

```powershell
cd "c:\Users\navee\Downloads\Diabetes-Risk-predictor-main\Diabetes-Risk-predictor-main"
.\setup-github-secrets.ps1
```

This will automatically configure all required secrets in your GitHub repository.

**Or manually add secrets** by following: `GITHUB_SECRETS_SETUP.md`

### Step 2: Add Azure Credentials

Create Azure service principal for GitHub Actions:

```powershell
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "diabetes-predictor-github" `
  --role contributor `
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/diabetes-predictor-rg `
  --sdk-auth
```

Copy the JSON output and add it as `AZURE_CREDENTIALS` secret in GitHub:
- Go to: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions
- Click "New repository secret"
- Name: `AZURE_CREDENTIALS`
- Value: Paste the JSON output

### Step 3: Deploy to Azure

Push your changes to trigger deployment:

```powershell
git add .
git commit -m "Configure Pinecone and GROQ API keys for deployment"
git push origin main
```

### Step 4: Monitor Deployment

1. Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
2. Click on the running "Deploy to Azure Web App" workflow
3. Watch the deployment progress

### Step 5: Access Your Application

Once deployment completes (5-10 minutes):

**🌐 Application URL**: https://diabetes-predictor-ai.azurewebsites.net

---

## 🧪 Test Locally First

Before deploying, test locally:

```powershell
# Activate virtual environment (if using one)
# .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python flask_app.py
```

Visit: http://localhost:5000

---

## 🔧 What Was Fixed

### 1. Application Error
**Problem**: Application showing error due to missing API keys
**Solution**: 
- Added GROQ_API_KEY to .env
- Added PINECONE_API_KEY to .env
- Updated environment configuration

### 2. Chatbot Integration
**Problem**: RAG chatbot needs Pinecone for vector database
**Solution**:
- Added `pinecone-client==3.0.3` to requirements.txt
- Configured PINECONE_API_KEY in environment
- Ready for vector embeddings storage

### 3. Azure Deployment
**Problem**: Need automated deployment with environment variables
**Solution**:
- Created `.github/workflows/azure-deploy.yml`
- Configured all secrets in GitHub Actions
- Automated build, deployment, and configuration

### 4. Configuration Management
**Problem**: Need easy secret management
**Solution**:
- Created `setup-github-secrets.ps1` automation script
- Created `GITHUB_SECRETS_SETUP.md` documentation
- All secrets properly documented

---

## 🔍 Troubleshooting

### If Application Still Shows Error:

1. **Check environment variables in Azure**:
   ```powershell
   az webapp config appsettings list `
     --name diabetes-predictor-ai `
     --resource-group diabetes-predictor-rg
   ```

2. **Restart the web app**:
   ```powershell
   az webapp restart `
     --name diabetes-predictor-ai `
     --resource-group diabetes-predictor-rg
   ```

3. **View application logs**:
   ```powershell
   az webapp log tail `
     --name diabetes-predictor-ai `
     --resource-group diabetes-predictor-rg
   ```

### If Chatbot Doesn't Work:

1. Verify GROQ_API_KEY is set correctly
2. Verify PINECONE_API_KEY is set correctly
3. Check Flask application logs for errors
4. Test API endpoint: https://diabetes-predictor-ai.azurewebsites.net/api/chatbot

---

## 📊 Configured Services

Your application now has:

| Service | Purpose | Status |
|---------|---------|--------|
| **GROQ AI** | AI-powered health analysis and chatbot | ✅ Configured |
| **Pinecone** | Vector database for RAG chatbot | ✅ Configured |
| **Firebase** | User authentication and data storage | ✅ Configured |
| **Google OAuth** | Social login | ✅ Configured |
| **SMTP Email** | Password reset and notifications | ✅ Configured |

---

## 📞 Support

If you encounter issues:

1. Check GitHub Actions logs for deployment errors
2. Verify all secrets are correctly set
3. Ensure Azure Web App is running
4. Check application logs in Azure Portal

**Repository**: https://github.com/Naveenkumar-2007/Daibetes
**Application**: https://diabetes-predictor-ai.azurewebsites.net

---

## ✨ What's Next?

After successful deployment:

1. ✅ Test all application features
2. ✅ Try the AI chatbot with health questions
3. ✅ Create a test diabetes prediction
4. ✅ Verify email notifications work
5. ✅ Test Google OAuth login

**🎉 Your Diabetes Health Predictor is ready to help users!**

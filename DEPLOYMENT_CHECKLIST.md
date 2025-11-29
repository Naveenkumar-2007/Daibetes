# 🚀 Production Deployment Checklist

## ✅ Pre-Deployment Tasks

### 1. Code Quality
- [x] Remove all test files
- [x] Clean __pycache__ directories
- [x] Update .gitignore
- [x] Remove unused code
- [x] Commit all changes
- [x] Push to GitHub

### 2. Environment Setup
- [ ] Create `.env` file with production values
- [ ] Set `GROQ_API_KEY`
- [ ] Set `FIREBASE_DATABASE_URL`
- [ ] Set `FIREBASE_PROJECT_ID`
- [ ] Set `GOOGLE_CLIENT_ID` (optional)
- [ ] Set `GOOGLE_CLIENT_SECRET` (optional)
- [ ] Set `APP_BASE_URL` to production URL

### 3. Firebase Configuration
- [ ] Create Firebase project
- [ ] Enable Realtime Database
- [ ] Configure database rules (see DEPLOYMENT.md)
- [ ] Download service account key
- [ ] Rename to `firebase-service-account.json`
- [ ] Add to `.gitignore` (already done)
- [ ] **NEVER commit firebase-service-account.json to git!**

### 4. Frontend Build
- [ ] Navigate to `frontend/` directory
- [ ] Run `npm install`
- [ ] Run `npm run build`
- [ ] Verify `frontend/dist/` folder created
- [ ] Test build locally

### 5. Dependencies
- [ ] Verify `requirements.txt` is up to date
- [ ] Test install: `pip install -r requirements.txt`
- [ ] Check for security vulnerabilities: `pip check`
- [ ] Update packages if needed

## 🌐 Deployment Options

### Option A: Azure Web Apps (Recommended)

#### Step 1: Install Azure CLI
```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### Step 2: Login
```bash
az login
```

#### Step 3: Create Resources
```bash
# Create resource group
az group create --name diabetes-predictor-rg --location eastus

# Create app service plan
az appservice plan create \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group diabetes-predictor-rg \
  --plan diabetes-predictor-plan \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11" \
  --startup-file "startup_azure.sh"
```

#### Step 4: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    GROQ_API_KEY="your_groq_key_here" \
    FIREBASE_DATABASE_URL="your_firebase_url" \
    FIREBASE_PROJECT_ID="your_project_id" \
    APP_BASE_URL="https://diabetes-predictor-ai.azurewebsites.net"
```

#### Step 5: Upload Firebase Service Account
```bash
# Convert JSON to string and upload
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    FIREBASE_SERVICE_ACCOUNT="$(cat firebase-service-account.json | jq -c .)"
```

#### Step 6: Deploy Code
```bash
# Method 1: Git deployment
az webapp deployment source config-local-git \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

git remote add azure <deployment_url_from_above>
git push azure main

# Method 2: ZIP deployment (faster)
zip -r deploy.zip . -x "*.git*" "*node_modules*" "*__pycache__*"
az webapp deployment source config-zip \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --src deploy.zip
```

#### Step 7: Enable HTTPS
```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

#### Step 8: View Logs
```bash
# Stream logs
az webapp log tail \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai

# Download logs
az webapp log download \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --log-file azure-logs.zip
```

### Option B: Heroku

```bash
# Install Heroku CLI (if not installed)
npm install -g heroku

# Login
heroku login

# Create app
heroku create diabetes-predictor-ai

# Set environment variables
heroku config:set GROQ_API_KEY="your_key"
heroku config:set FIREBASE_DATABASE_URL="your_url"
heroku config:set FIREBASE_PROJECT_ID="your_project_id"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Option C: Docker

```bash
# Build image
docker build -t diabetes-predictor .

# Test locally
docker run -p 5000:5000 \
  -e GROQ_API_KEY="your_key" \
  -e FIREBASE_DATABASE_URL="your_url" \
  diabetes-predictor

# Push to Docker Hub
docker tag diabetes-predictor yourusername/diabetes-predictor:latest
docker push yourusername/diabetes-predictor:latest

# Deploy to cloud (Azure Container Instances)
az container create \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor \
  --image yourusername/diabetes-predictor:latest \
  --dns-name-label diabetes-predictor \
  --ports 5000 \
  --environment-variables \
    GROQ_API_KEY="your_key" \
    FIREBASE_DATABASE_URL="your_url"
```

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
curl https://diabetes-predictor-ai.azurewebsites.net/health
```

Expected:
```json
{
  "status": "healthy",
  "message": "Application is running",
  "database": "connected",
  "ai": "connected"
}
```

### 2. Test Chatbot
```bash
curl -X POST https://diabetes-predictor-ai.azurewebsites.net/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "What is diabetes?"}'
```

### 3. Test Prediction
```bash
curl -X POST https://diabetes-predictor-ai.azurewebsites.net/predict \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 45,
    "sex": "Male",
    "contact": "1234567890",
    "address": "Test",
    "pregnancies": 0,
    "glucose": 140,
    "bloodPressure": 85,
    "skinThickness": 20,
    "insulin": 200,
    "bmi": 28.5,
    "diabetesPedigreeFunction": 0.5
  }'
```

### 4. Manual Testing
- [ ] Visit production URL
- [ ] Create user account
- [ ] Login successfully
- [ ] Make a prediction
- [ ] Generate a report
- [ ] Download PDF
- [ ] Test chatbot
- [ ] Test admin panel (if admin)
- [ ] Test chatbot training (admin only)
- [ ] Logout and login again
- [ ] Test password reset
- [ ] Test Google OAuth (if configured)

## 🔧 Monitoring Setup

### Azure Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app diabetes-predictor-insights \
  --location eastus \
  --resource-group diabetes-predictor-rg

# Get instrumentation key
az monitor app-insights component show \
  --app diabetes-predictor-insights \
  --resource-group diabetes-predictor-rg \
  --query instrumentationKey

# Configure in Web App
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your_key"
```

### Enable Auto-Scaling (Optional)
```bash
az monitor autoscale create \
  --resource-group diabetes-predictor-rg \
  --resource diabetes-predictor-ai \
  --resource-type Microsoft.Web/sites \
  --name autoscale-rule \
  --min-count 1 \
  --max-count 5 \
  --count 2
```

## 🔒 Security Hardening

### 1. HTTPS Only
```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

### 2. Custom Domain (Optional)
```bash
# Add custom domain
az webapp config hostname add \
  --resource-group diabetes-predictor-rg \
  --webapp-name diabetes-predictor-ai \
  --hostname www.yourdomain.com

# Enable managed SSL certificate (free)
az webapp config ssl bind \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

### 3. API Key Rotation
- [ ] Set reminders to rotate API keys every 90 days
- [ ] Update GROQ_API_KEY
- [ ] Update Firebase service account
- [ ] Update Google OAuth credentials

### 4. Firebase Security Rules
```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null",
    "users": {
      "$user_id": {
        ".read": "$user_id === auth.uid || root.child('users').child(auth.uid).child('role').val() === 'admin'",
        ".write": "$user_id === auth.uid || root.child('users').child(auth.uid).child('role').val() === 'admin'"
      }
    }
  }
}
```

## 📊 Performance Optimization

### 1. Enable Caching
```bash
az webapp config set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --always-on true
```

### 2. Scale Up (if needed)
```bash
# Upgrade to Premium tier
az appservice plan update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-plan \
  --sku P1V2
```

## 🐛 Troubleshooting

### View Application Logs
```bash
# Azure
az webapp log tail --resource-group diabetes-predictor-rg --name diabetes-predictor-ai

# Heroku
heroku logs --tail --app diabetes-predictor-ai
```

### Common Issues

#### 1. "Module not found" error
- Check `requirements.txt` is complete
- Ensure all dependencies are installed
- Verify Python version matches runtime.txt

#### 2. Firebase connection failed
- Verify `FIREBASE_DATABASE_URL` is correct
- Check service account JSON is valid
- Ensure database rules allow access

#### 3. Chatbot not responding
- Verify `GROQ_API_KEY` is set and valid
- Check API quota and rate limits
- View logs for specific error messages

#### 4. Frontend 404 errors
- Ensure `frontend/dist/` was built and deployed
- Check Flask is serving static files correctly
- Verify React routing configuration

## ✅ Final Checklist

- [ ] Application deployed successfully
- [ ] All environment variables configured
- [ ] HTTPS enabled
- [ ] Health check passing
- [ ] Manual testing completed
- [ ] Chatbot working
- [ ] Predictions working
- [ ] Reports generating correctly
- [ ] Admin panel accessible
- [ ] Monitoring enabled
- [ ] Logs accessible
- [ ] Documentation updated
- [ ] Team notified

## 🎉 Go Live!

Once all checklist items are complete:

1. ✅ Share production URL with stakeholders
2. ✅ Monitor logs for first 24 hours
3. ✅ Set up uptime monitoring (e.g., UptimeRobot)
4. ✅ Create backups of database
5. ✅ Document any deployment-specific configurations

---

**Production URL:** https://diabetes-predictor-ai.azurewebsites.net

**Deployed:** [DATE]
**Developer:** Naveenkumar Chapala
**Status:** ✅ Production Ready

---

## 📞 Support

Issues? Contact:
- 📧 Email: naveenkumarchapala02@gmail.com
- 🐛 GitHub: https://github.com/Naveenkumar-2007/Daibetes/issues

---

**© 2025 Diabetes Risk Predictor - Production Deployment Complete**

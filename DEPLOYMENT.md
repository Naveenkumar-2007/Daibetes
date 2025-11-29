# 🚀 Deployment Guide - Diabetes Risk Predictor

## 📋 Pre-Deployment Checklist

### ✅ Required Files
- [x] `flask_app.py` - Main application
- [x] `requirements.txt` - Python dependencies
- [x] `runtime.txt` - Python version
- [x] `Dockerfile` - Container configuration
- [x] `startup.sh` - Linux startup script
- [x] `startup_azure.sh` - Azure startup script
- [x] `.env.example` - Environment template
- [x] `frontend/dist/` - Built React app

### ✅ Environment Variables
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
FIREBASE_DATABASE_URL=https://xxx.firebaseio.com
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com (optional)
GOOGLE_CLIENT_SECRET=GOCSPX-xxx (optional)
APP_BASE_URL=https://your-app.azurewebsites.net
```

### ✅ Firebase Setup
1. Create Firebase project at https://console.firebase.google.com
2. Enable Realtime Database
3. Set database rules (see below)
4. Download service account key
5. Rename to `firebase-service-account.json`

---

## 🔥 Firebase Database Rules

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
    },
    "predictions": {
      ".read": "auth != null",
      ".write": "auth != null",
      "$prediction_id": {
        ".read": "auth != null",
        ".write": "data.child('user_id').val() === auth.uid || root.child('users').child(auth.uid).child('role').val() === 'admin'"
      }
    }
  }
}
```

---

## 🌐 Deployment Options

### Option 1: Azure Web Apps (Recommended)

#### 1. Install Azure CLI
```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### 2. Login to Azure
```bash
az login
```

#### 3. Create Resource Group
```bash
az group create --name diabetes-predictor-rg --location eastus
```

#### 4. Create App Service Plan
```bash
az appservice plan create \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --sku B1 \
  --is-linux
```

#### 5. Create Web App
```bash
az webapp create \
  --resource-group diabetes-predictor-rg \
  --plan diabetes-predictor-plan \
  --name diabetes-predictor-ai \
  --runtime "PYTHON:3.11" \
  --startup-file "startup_azure.sh"
```

#### 6. Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    GROQ_API_KEY="your_groq_key" \
    FIREBASE_DATABASE_URL="your_firebase_url" \
    FIREBASE_PROJECT_ID="your_project_id" \
    APP_BASE_URL="https://diabetes-predictor-ai.azurewebsites.net"
```

#### 7. Upload Firebase Service Account
```bash
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings \
    FIREBASE_SERVICE_ACCOUNT="$(cat firebase-service-account.json | jq -c .)"
```

#### 8. Deploy Code
```bash
# Method 1: Git Deployment
az webapp deployment source config-local-git \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

git remote add azure <deployment_url>
git push azure main

# Method 2: ZIP Deployment
zip -r deploy.zip . -x "*.git*" "*node_modules*" "*__pycache__*"
az webapp deployment source config-zip \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --src deploy.zip
```

#### 9. Enable HTTPS
```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

---

### Option 2: Docker Deployment

#### 1. Build Docker Image
```bash
docker build -t diabetes-predictor .
```

#### 2. Test Locally
```bash
docker run -p 5000:5000 \
  -e GROQ_API_KEY="your_key" \
  -e FIREBASE_DATABASE_URL="your_url" \
  diabetes-predictor
```

#### 3. Push to Docker Hub
```bash
docker tag diabetes-predictor yourusername/diabetes-predictor:latest
docker push yourusername/diabetes-predictor:latest
```

#### 4. Deploy to Cloud
```bash
# Azure Container Instances
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

---

### Option 3: Heroku

#### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
choco install heroku-cli

# Ubuntu
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Login & Create App
```bash
heroku login
heroku create diabetes-predictor-ai
```

#### 3. Set Environment Variables
```bash
heroku config:set GROQ_API_KEY="your_key"
heroku config:set FIREBASE_DATABASE_URL="your_url"
heroku config:set FIREBASE_PROJECT_ID="your_project_id"
```

#### 4. Deploy
```bash
git push heroku main
```

---

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
curl https://diabetes-predictor-ai.azurewebsites.net/health
```

Expected response:
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
    "address": "Test Address",
    "pregnancies": 0,
    "glucose": 140,
    "bloodPressure": 85,
    "skinThickness": 20,
    "insulin": 200,
    "bmi": 28.5,
    "diabetesPedigreeFunction": 0.5
  }'
```

---

## 🔧 Monitoring & Maintenance

### Azure Logs
```bash
# Stream logs
az webapp log tail \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai

# Download logs
az webapp log download \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai
```

### Performance Monitoring
```bash
# Enable Application Insights
az monitor app-insights component create \
  --app diabetes-predictor-insights \
  --location eastus \
  --resource-group diabetes-predictor-rg

# Link to Web App
az webapp config appsettings set \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your_key"
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` or `firebase-service-account.json`
- ✅ Use Azure Key Vault for secrets
- ✅ Rotate API keys regularly

### 2. HTTPS Only
```bash
az webapp update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --https-only true
```

### 3. Custom Domain (Optional)
```bash
# Add custom domain
az webapp config hostname add \
  --resource-group diabetes-predictor-rg \
  --webapp-name diabetes-predictor-ai \
  --hostname www.yourdomain.com

# Enable SSL
az webapp config ssl bind \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-ai \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

---

## 📊 Scaling

### Manual Scaling
```bash
az appservice plan update \
  --resource-group diabetes-predictor-rg \
  --name diabetes-predictor-plan \
  --sku P1V2
```

### Auto-Scaling
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

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Module Not Found
```bash
# Ensure requirements.txt is up to date
pip freeze > requirements.txt
```

#### 2. Firebase Connection Failed
- Check `FIREBASE_DATABASE_URL` is correct
- Verify service account JSON is valid
- Ensure database rules allow access

#### 3. Chatbot Not Responding
- Check `GROQ_API_KEY` is set
- Verify API key is valid
- Check Groq API quota

#### 4. Frontend 404 Errors
- Ensure `frontend/dist/` exists
- Run `npm run build` in frontend folder
- Check Flask serves static files correctly

---

## 📱 Frontend Build

```bash
cd frontend
npm install
npm run build
cd ..
```

Ensure `frontend/dist/` is included in deployment.

---

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Firebase service account uploaded
- [ ] Frontend built and included
- [ ] HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Auto-scaling enabled (optional)
- [ ] Error tracking configured
- [ ] Performance monitoring active

---

## 🆘 Support

For deployment issues:
1. Check Azure/Heroku logs
2. Verify environment variables
3. Test locally first
4. Check Firebase connection
5. Verify API keys are valid

---

**Deployment URL:** https://diabetes-predictor-ai.azurewebsites.net  
**Developer:** Naveenkumar Chapala  
**Email:** naveenkumarchapala02@gmail.com

**© 2025 Diabetes Risk Predictor - Production Ready**

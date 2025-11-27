# GitHub Actions Secrets Configuration Guide

## 🔐 Required GitHub Secrets

To deploy your Diabetes Health Predictor to Azure, you need to configure the following secrets in your GitHub repository.

### Navigation: Settings → Secrets and variables → Actions → New repository secret

---

## 1️⃣ Azure Credentials

### `AZURE_CREDENTIALS`
Your Azure service principal credentials in JSON format.

**How to get it:**
```powershell
# Login to Azure
az login

# Create service principal (replace with your values)
az ad sp create-for-rbac --name "diabetes-predictor-github" `
  --role contributor `
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/diabetes-predictor-rg `
  --sdk-auth
```

Copy the entire JSON output and paste it as the secret value.

---

## 2️⃣ AI Service Keys

### `GROQ_API_KEY`
```
gsk_YOUR_GROQ_API_KEY_HERE
```
**Note**: Use your actual GROQ API key from the .env file

### `PINECONE_API_KEY`
```
pcsk_YOUR_PINECONE_API_KEY_HERE
```
**Note**: Use your actual Pinecone API key from the .env file

---

## 3️⃣ Firebase Configuration

### `FIREBASE_API_KEY`
```
AIzaSyDQ70lgR3Vk5ykOWyUxKBQ3J-6p4dMKlxw
```

### `FIREBASE_PROJECT_ID`
```
diabetes-prediction-22082
```

### `FIREBASE_PRIVATE_KEY_ID`
```
1c0d23452f1e5b0edb51e3a8a10cef1725d0f678
```

### `FIREBASE_CLIENT_EMAIL`
```
firebase-adminsdk-fbsvc@diabetes-prediction-22082.iam.gserviceaccount.com
```

### `FIREBASE_CLIENT_ID`
```
110065795734752942444
```

### `FIREBASE_AUTH_DOMAIN`
```
diabetes-prediction-22082.firebaseapp.com
```

### `FIREBASE_DATABASE_URL`
```
https://diabetes-prediction-22082.firebaseio.com
```

### `FIREBASE_STORAGE_BUCKET`
```
diabetes-prediction-22082.appspot.com
```

### `FIREBASE_SERVICE_ACCOUNT_JSON`
```
ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiZGlhYmV0ZXMtcHJlZGljdGlvbi0yMjA4MiIsCiAgInByaXZhdGVfa2V5X2lkIjogIjFjMGQyMzQ1MmYxZTViMGVkYjUxZTNhOGExMGNlZjE3MjVkMGY2NzgiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQ2cwZ1VWZDBIOVl0Q1BcbitNeW5iNkJCL0trWlZFVmhJRWpQSkU1WjdWT21CajFtcEIxbTRTSG9ZdmF1WW9KNldTQ0xPSjJvd2QwTE5LV3dcbjg1V1JaSkZTa0NLVll0eVpSTTZMNlE2aExTY2c4R3ZKeGFTSGUxRDUzUGxNVlBLNDR3Q3NhRWRhNmwrME9mUUpcblJuVXhwbFM3UVJHSytWNWtpclc3YkF2b1dSVTJidHZjM0hUL1dCWU5tNVNoTHgxbGMyVHJPaWQvQTdsdy9VTm9cbmVQN0xqN2ZNMnRZSjFJbFRPc0s4SEN3UEIxK0pjTk85TVJWK2Rkekp0TXJ0OEpRemFqNS9teFNzQ1VuQzl2cW9cbkpnaDU3V0ZXblViOFYzaUhBeUtFYWVjbDdBTDA4NWgvV0Vva2FGOTI5enZXM2pKMnViM0RDQmNWdkFwMXFPdEZcbnlBNkt6R05oQWdNQkFBRUNnZ0VBR2kxRlZaS2xZNlN2ZFJmVzNCUXYzajNObW9sY2g2dzFIYjUzb0d5Z2RvQkNcbmcxQUlWeVFqSEV2cmdrUVhuK21kQWZ4VHNWSG85SGQ3MXRzM1I4UzZZTm1FUDVPcGU2czNBWkFNYVJETDh6RWZcbkltY3cyanFvMmhydFcwN2llVlM5MmRKWmR3TjZVNEF4YUVjWE1WODFJSXU5V3NVdlo2Y3FZSmo4TVRRNjN6S1hcbk9oVUdQM1h1ZEpaVmJjaUpGcXAwUEhCTlV0dE52YUZmSGdtRXdlOGZGaHFUU0RNTVNWR3dzTWwyZEFNRzNLV0hcbkF1OCs2VkJFb1h1aW9BK3RYeVZpM2VLZjNrTXRnRDdncGxXa21mRjhFakhQeFIzV3RZZVRLcklLS3JLdjIrYjFcbmJOVG1FSVB1MXZzUWhsRVlDK01aeGhEeXJjWmk3TWVoaksza2xIQmJyd0tCZ1FETEVPR2xvL3lxaFlaaExnQnFcblpuWEN2MFVkZUxHWFRhMVF4NEd3aUdoSzQzdlFRdVVCOHpuYXpaODNiRE1yUncxZi9RdXU0bE9FMUNwbTMreTNcbllyRC96QWdVNlltS3psclJmdi9mNEh5QU9LVkdUUWg5OHJPVTZka0drWExGeVh2YnhCbDU1SVI1NHA5ZjQzeFpcbk9kcUtaRnowOEl3b1dyaDVmY3RvY3lBWkp3S0JnUURLdmZ1WUVNZFVZb3IxbXB5NHdETGFCNmk3RjA3Mm1FenJcbkJnZm54SGlHeityVGplNmtKdWFMTnlPRlZWYm1wUzN1dXRrc3FqMmhlNzVrWmVPVEh3OHVrWFlLQzdFeklkeURcbnB3OW83N0FwZmJsZVVMRjd1bmtUd2tEOXBlTkM1Q1pRMURJVndBMWhpem5vemZkZlI1NllCcU5YRVZuYzl6Um1cbk5PZGVSU2FrTndLQmdRQ1JtU01SYndrbEF1UWRIYXl5blpCbCtGcUlEUmZZa3B0b1JnUVpIVlVhRFEyamY3TlBcbnVLT00zTTRDSVJSM1BWUzd0R1lDR01rbGZqS0EzS0dQdzdXQlV6dWdNdXFwbWRmSVNqVVF3cGJDSU50d0VwKzZcbkhxRGdidU5yTURLSTJqUnltS0pqb1pQVENNaVpLalRvalBERE5iN282T2kxcm9hQ3BjMklzTE1kRlFLQmdRQzBcbktsWXRVU1BCa255SU8yaHdLYVJHNnExLzdQdW4yYm5vMVFnclp3WHdUMDRQeDc0OU03Q0dJRzY1YXhmNWlPb2pcbmp2bTFYbWU4WEJuYVlFejNEWS9SUTBTUk1zaTZkcW5lZUpRU0hZWC9xUkVVaGtMaWY5aGV2YTVCZWF4V1lpYkdcbmgzc21wdTk5TWxzNHplZTVUUXpiYm5LeXllR0FvbEYzVGlZWk9QeFl5d0tCZ0VzdHBUWmd5d3N1bEcrVFQ5NUFcbllncjhWaTB4aHNvc2dXWW9xeDFnN05wZDdFLzl0bFdmQzhWeDgyTFNKWEtrcGVhcWxXNmZtS21OeXNsZUpTUktcblFaYi9kSHdHTXl5S3UrVlRHdzYrK0NRVlNnSmVjek1qZ2V5TEJxaXNKck9wNWI0OVJCZE91MmlPT3llS1pBSXdcbm52TjZTc1RXN0FyVCtiR2dVK0g2azVCbVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLWZic3ZjQGRpYWJldGVzLXByZWRpY3Rpb24tMjIwODIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTEwMDY1Nzk1NzM0NzUyOTQyNDQ0IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay1mYnN2YyU0MGRpYWJldGVzLXByZWRpY3Rpb24tMjIwODIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K
```

---

## 4️⃣ Application Secrets

### `SECRET_KEY`
```
^=qpGud8yaY\dn`e<yY0!C*3V+p.Fkq0
```

---

## 5️⃣ Google OAuth

### `GOOGLE_CLIENT_ID`
```
YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
```
**Note**: Use your actual Google OAuth Client ID from the .env file

### `GOOGLE_CLIENT_SECRET`
```
GOCSPX-YOUR_GOOGLE_CLIENT_SECRET_HERE
```
**Note**: Use your actual Google OAuth Client Secret from the .env file

---

## 6️⃣ Email Configuration (SMTP)

### `SMTP_FROM_EMAIL`
```
Diabetes Predictor <naveenkumarchapala123@gmail.com>
```

### `SMTP_HOST`
```
smtp.gmail.com
```

### `SMTP_PASSWORD`
```
txop cwxf hysc orxl
```

### `SMTP_PORT`
```
587
```

### `SMTP_USE_TLS`
```
true
```

### `SMTP_USERNAME`
```
naveenkumarchapala123@gmail.com
```

---

## 📋 Quick Setup Script

Run this PowerShell script to add all secrets at once (requires GitHub CLI):

```powershell
# Install GitHub CLI if not already installed: winget install GitHub.cli

# Login to GitHub
gh auth login

# Set repository (replace with your repo)
$REPO = "Naveenkumar-2007/Daibetes"

# Add all secrets
# Get actual values from .env file
$GROQ_KEY = (Get-Content .env | Select-String 'GROQ_API_KEY="(.*)"').Matches.Groups[1].Value
gh secret set GROQ_API_KEY -b $GROQ_KEY -R $REPO
$PINECONE_KEY = (Get-Content .env | Select-String 'PINECONE_API_KEY="(.*)"').Matches.Groups[1].Value
gh secret set PINECONE_API_KEY -b $PINECONE_KEY -R $REPO
gh secret set FIREBASE_API_KEY -b "AIzaSyDQ70lgR3Vk5ykOWyUxKBQ3J-6p4dMKlxw" -R $REPO
gh secret set FIREBASE_PROJECT_ID -b "diabetes-prediction-22082" -R $REPO
gh secret set FIREBASE_PRIVATE_KEY_ID -b "1c0d23452f1e5b0edb51e3a8a10cef1725d0f678" -R $REPO
gh secret set FIREBASE_CLIENT_EMAIL -b "firebase-adminsdk-fbsvc@diabetes-prediction-22082.iam.gserviceaccount.com" -R $REPO
gh secret set FIREBASE_CLIENT_ID -b "110065795734752942444" -R $REPO
gh secret set FIREBASE_AUTH_DOMAIN -b "diabetes-prediction-22082.firebaseapp.com" -R $REPO
gh secret set FIREBASE_DATABASE_URL -b "https://diabetes-prediction-22082.firebaseio.com" -R $REPO
gh secret set FIREBASE_STORAGE_BUCKET -b "diabetes-prediction-22082.appspot.com" -R $REPO
gh secret set SECRET_KEY -b "^=qpGud8yaY\dn\`e<yY0!C*3V+p.Fkq0" -R $REPO
$GOOGLE_ID = (Get-Content .env | Select-String 'GOOGLE_CLIENT_ID="(.*)"').Matches.Groups[1].Value
gh secret set GOOGLE_CLIENT_ID -b $GOOGLE_ID -R $REPO
$GOOGLE_SECRET = (Get-Content .env | Select-String 'GOOGLE_CLIENT_SECRET="(.*)"').Matches.Groups[1].Value
gh secret set GOOGLE_CLIENT_SECRET -b $GOOGLE_SECRET -R $REPO
gh secret set SMTP_FROM_EMAIL -b "Diabetes Predictor <naveenkumarchapala123@gmail.com>" -R $REPO
gh secret set SMTP_HOST -b "smtp.gmail.com" -R $REPO
gh secret set SMTP_PASSWORD -b "txop cwxf hysc orxl" -R $REPO
gh secret set SMTP_PORT -b "587" -R $REPO
gh secret set SMTP_USE_TLS -b "true" -R $REPO
gh secret set SMTP_USERNAME -b "naveenkumarchapala123@gmail.com" -R $REPO

# Add Firebase Service Account JSON (multiline)
$FIREBASE_JSON = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiZGlhYmV0ZXMtcHJlZGljdGlvbi0yMjA4MiIsCiAgInByaXZhdGVfa2V5X2lkIjogIjFjMGQyMzQ1MmYxZTViMGVkYjUxZTNhOGExMGNlZjE3MjVkMGY2NzgiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQ2cwZ1VWZDBIOVl0Q1BcbitNeW5iNkJCL0trWlZFVmhJRWpQSkU1WjdWT21CajFtcEIxbTRTSG9ZdmF1WW9KNldTQ0xPSjJvd2QwTE5LV3dcbjg1V1JaSkZTa0NLVll0eVpSTTZMNlE2aExTY2c4R3ZKeGFTSGUxRDUzUGxNVlBLNDR3Q3NhRWRhNmwrME9mUUpcblJuVXhwbFM3UVJHSytWNWtpclc3YkF2b1dSVTJidHZjM0hUL1dCWU5tNVNoTHgxbGMyVHJPaWQvQTdsdy9VTm9cbmVQN0xqN2ZNMnRZSjFJbFRPc0s4SEN3UEIxK0pjTk85TVJWK2Rkekp0TXJ0OEpRemFqNS9teFNzQ1VuQzl2cW9cbkpnaDU3V0ZXblViOFYzaUhBeUtFYWVjbDdBTDA4NWgvV0Vva2FGOTI5enZXM2pKMnViM0RDQmNWdkFwMXFPdEZcbnlBNkt6R05oQWdNQkFBRUNnZ0VBR2kxRlZaS2xZNlN2ZFJmVzNCUXYzajNObW9sY2g2dzFIYjUzb0d5Z2RvQkNcbmcxQUlWeVFqSEV2cmdrUVhuK21kQWZ4VHNWSG85SGQ3MXRzM1I4UzZZTm1FUDVPcGU2czNBWkFNYVJETDh6RWZcbkltY3cyanFvMmhydFcwN2llVlM5MmRKWmR3TjZVNEF4YUVjWE1WODFJSXU5V3NVdlo2Y3FZSmo4TVRRNjN6S1hcbk9oVUdQM1h1ZEpaVmJjaUpGcXAwUEhCTlV0dE52YUZmSGdtRXdlOGZGaHFUU0RNTVNWR3dzTWwyZEFNRzNLV0hcbkF1OCs2VkJFb1h1aW9BK3RYeVZpM2VLZjNrTXRnRDdncGxXa21mRjhFakhQeFIzV3RZZVRLcklLS3JLdjIrYjFcbmJOVG1FSVB1MXZzUWhsRVlDK01aeGhEeXJjWmk3TWVoaksza2xIQmJyd0tCZ1FETEVPR2xvL3lxaFlaaExnQnFcblpuWEN2MFVkZUxHWFRhMVF4NEd3aUdoSzQzdlFRdVVCOHpuYXpaODNiRE1yUncxZi9RdXU0bE9FMUNwbTMreTNcbllyRC96QWdVNlltS3psclJmdi9mNEh5QU9LVkdUUWg5OHJPVTZka0drWExGeVh2YnhCbDU1SVI1NHA5ZjQzeFpcbk9kcUtaRnowOEl3b1dyaDVmY3RvY3lBWkp3S0JnUURLdmZ1WUVNZFVZb3IxbXB5NHdETGFCNmk3RjA3Mm1FenJcbkJnZm54SGlHeityVGplNmtKdWFMTnlPRlZWYm1wUzN1dXRrc3FqMmhlNzVrWmVPVEh3OHVrWFlLQzdFeklkeURcbnB3OW83N0FwZmJsZVVMRjd1bmtUd2tEOXBlTkM1Q1pRMURJVndBMWhpem5vemZkZlI1NllCcU5YRVZuYzl6Um1cbk5PZGVSU2FrTndLQmdRQ1JtU01SYndrbEF1UWRIYXl5blpCbCtGcUlEUmZZa3B0b1JnUVpIVlVhRFEyamY3TlBcbnVLT00zTTRDSVJSM1BWUzd0R1lDR01rbGZqS0EzS0dQdzdXQlV6dWdNdXFwbWRmSVNqVVF3cGJDSU50d0VwKzZcbkhxRGdidU5yTURLSTJqUnltS0pqb1pQVENNaVpLalRvalBERE5iN282T2kxcm9hQ3BjMklzTE1kRlFLQmdRQzBcbktsWXRVU1BCa255SU8yaHdLYVJHNnExLzdQdW4yYm5vMVFnclp3WHdUMDRQeDc0OU03Q0dJRzY1YXhmNWlPb2pcbmp2bTFYbWU4WEJuYVlFejNEWS9SUTBTUk1zaTZkcW5lZUpRU0hZWC9xUkVVaGtMaWY5aGV2YTVCZWF4V1lpYkdcbmgzc21wdTk5TWxzNHplZTVUUXpiYm5LeXllR0FvbEYzVGlZWk9QeFl5d0tCZ0VzdHBUWmd5d3N1bEcrVFQ5NUFcbllncjhWaTB4aHNvc2dXWW9xeDFnN05wZDdFLzl0bFdmQzhWeDgyTFNKWEtrcGVhcWxXNmZtS21OeXNsZUpTUktcblFaYi9kSHdHTXl5S3UrVlRHdzYrK0NRVlNnSmVjek1qZ2V5TEJxaXNKck9wNWI0OVJCZE91MmlPT3llS1pBSXdcbm52TjZTc1RXN0FyVCtiR2dVK0g2azVCbVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLWZic3ZjQGRpYWJldGVzLXByZWRpY3Rpb24tMjIwODIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTEwMDY1Nzk1NzM0NzUyOTQyNDQ0IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay1mYnN2YyU0MGRpYWJldGVzLXByZWRpY3Rpb24tMjIwODIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"
gh secret set FIREBASE_SERVICE_ACCOUNT_JSON -b $FIREBASE_JSON -R $REPO

Write-Host "✅ All secrets configured successfully!" -ForegroundColor Green
```

---

## 🚀 Deployment Steps

### 1. Configure Azure Credentials

First, you need to create Azure credentials for GitHub Actions:

```powershell
# Login to Azure
az login

# Get your subscription ID
az account show --query id -o tsv

# Create service principal
az ad sp create-for-rbac --name "diabetes-predictor-github" `
  --role contributor `
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/diabetes-predictor-rg `
  --sdk-auth
```

Copy the JSON output and add it as `AZURE_CREDENTIALS` secret in GitHub.

### 2. Add All Secrets

Either:
- **Option A**: Use the PowerShell script above
- **Option B**: Manually add each secret via GitHub UI (Settings → Secrets → Actions)

### 3. Push to GitHub

```powershell
git add .
git commit -m "Configure deployment with Pinecone and GROQ API keys"
git push origin main
```

### 4. Monitor Deployment

- Go to your GitHub repository
- Click on **Actions** tab
- Watch the "Deploy to Azure Web App" workflow

### 5. Verify Deployment

After deployment completes, visit:
```
https://diabetes-predictor-ai.azurewebsites.net
```

---

## 🔍 Troubleshooting

### If deployment fails:

1. **Check GitHub Actions logs**
   - Go to Actions tab → Click on failed workflow
   - Expand each step to see error messages

2. **Check Azure Application Logs**
   ```powershell
   az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
   ```

3. **Verify all secrets are set**
   ```powershell
   gh secret list -R Naveenkumar-2007/Daibetes
   ```

4. **Test locally first**
   ```powershell
   # Ensure .env is configured
   python flask_app.py
   ```

---

## 📞 Support

If you encounter issues:
1. Check the deployment logs in GitHub Actions
2. Verify all API keys are valid
3. Ensure Azure Web App is running
4. Check environment variables in Azure Portal

**Application URL**: https://diabetes-predictor-ai.azurewebsites.net

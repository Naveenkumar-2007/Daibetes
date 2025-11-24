# ⚡ GitHub Actions Quick Start

## 🎯 Super Fast Setup (5 Minutes)

### Option 1: Automated Script (EASIEST)

```powershell
cd C:\Users\navee\Downloads\Diabetes-Risk-predictor-main\Diabetes-Risk-predictor-main
.\setup-github-actions.ps1
```

This script will:
- ✅ Create Azure resources
- ✅ Generate service principal
- ✅ Collect all secrets
- ✅ Save secrets to file
- ✅ (Optional) Push to GitHub

**Then**: Copy secrets from `github-secrets.txt` to GitHub → Done!

---

### Option 2: Manual (10 Minutes)

#### 1. Create Azure Resources
```powershell
az login
az group create --name diabetes-predictor-rg --location eastus
az appservice plan create --name diabetes-plan --resource-group diabetes-predictor-rg --is-linux --sku B1
az webapp create --resource-group diabetes-predictor-rg --plan diabetes-plan --name diabetes-predictor-ai --runtime "PYTHON:3.11"
```

#### 2. Create Service Principal
```powershell
az ad sp create-for-rbac --name "diabetes-github" --role contributor --scopes /subscriptions/<YOUR_SUB_ID>/resourceGroups/diabetes-predictor-rg --sdk-auth
```
**Save the JSON output!**

#### 3. Add GitHub Secrets
Go to: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions

Add 4 secrets:
- `AZURE_CREDENTIALS` → JSON from step 2
- `GROQ_API_KEY` → Your Groq key
- `FIREBASE_DATABASE_URL` → Firebase URL
- `SECRET_KEY` → Random 32-char string

#### 4. Push to GitHub
```powershell
git add .
git commit -m "Setup Azure deployment"
git push origin main
```

---

## 📋 Required GitHub Secrets

| Secret Name | Where to Get | Example |
|-------------|-------------|---------|
| **AZURE_CREDENTIALS** | `az ad sp create-for-rbac` | JSON object |
| **GROQ_API_KEY** | https://console.groq.com | `gsk_xxxxx` |
| **FIREBASE_DATABASE_URL** | Firebase Console | `https://...firebaseio.com` |
| **SECRET_KEY** | Generate random | 32 characters |

---

## 🚀 Trigger Deployment

### Auto-trigger (on every push):
```powershell
git add .
git commit -m "Your changes"
git push origin main
```

### Manual trigger:
1. Go to: https://github.com/Naveenkumar-2007/Daibetes/actions
2. Click "Deploy to Azure App Service"
3. Click "Run workflow"

---

## 📊 Monitor Deployment

### GitHub Actions:
https://github.com/Naveenkumar-2007/Daibetes/actions

### Azure Logs:
```powershell
az webapp log tail -n diabetes-predictor-ai -g diabetes-predictor-rg
```

### Check Status:
```powershell
az webapp show -n diabetes-predictor-ai -g diabetes-predictor-rg --query state
```

---

## ✅ Verify Success

Your app: https://diabetes-predictor-ai.azurewebsites.net

Should see:
- ✅ Login page loads
- ✅ Can register/login
- ✅ Predictions work
- ✅ Reports generate
- ✅ Dates show correctly

---

## 🔧 Useful Commands

### Restart app:
```powershell
az webapp restart -n diabetes-predictor-ai -g diabetes-predictor-rg
```

### Update environment variable:
```powershell
az webapp config appsettings set -n diabetes-predictor-ai -g diabetes-predictor-rg --settings GROQ_API_KEY="new_key"
```

### Delete everything:
```powershell
az group delete -n diabetes-predictor-rg --yes
```

---

## 🐛 Troubleshooting

### Workflow fails at "Azure Login"
- ❌ Secret `AZURE_CREDENTIALS` missing or invalid
- ✅ Re-run service principal creation

### App shows 502 Bad Gateway
- ⏳ Wait 2-3 minutes (app starting)
- 📋 Check logs: `az webapp log tail ...`

### "Module not found"
- 📦 Check `requirements.txt` complete
- 🔄 Restart app

---

## 📚 Full Documentation

- **Setup Guide**: `GITHUB_ACTIONS_SETUP.md`
- **General Deployment**: `AZURE_DEPLOYMENT.md`
- **Quick Reference**: `DEPLOYMENT_SUMMARY.md`

---

## 💡 Pro Tips

1. **Test locally first**: Ensure app runs on http://localhost:5000
2. **Check secrets**: All 4 must be added to GitHub
3. **Watch first deployment**: Monitor GitHub Actions carefully
4. **Check logs**: If issues, logs show the problem
5. **Be patient**: First deployment takes 5-10 minutes

---

## 🎉 Success Checklist

- [ ] Azure resources created
- [ ] Service principal created
- [ ] 4 GitHub secrets added
- [ ] Code pushed to GitHub
- [ ] Workflow completed successfully
- [ ] App URL loads
- [ ] All features work

**You're done! Every push now auto-deploys!** 🚀

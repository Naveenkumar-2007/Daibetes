# Google OAuth Configuration Fix

## Problem
Google OAuth authentication is failing because the Azure domain is not authorized in Google Cloud Console.

## Solution Steps

### 1. Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project (or create one if you haven't)

### 2. Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. If not configured:
   - Choose **External** user type
   - Fill in required fields:
     - App name: `Diabetes Health Predictor`
     - User support email: Your email
     - Developer contact: Your email
   - Click **Save and Continue**
3. Add scopes (click **Add or Remove Scopes**):
   - `userinfo.email`
   - `userinfo.profile`
   - `openid`
4. Click **Save and Continue**
5. Add test users if in testing mode (your email)
6. Click **Save and Continue**

### 3. Create/Update OAuth 2.0 Client ID
1. Go to **APIs & Services** → **Credentials**
2. If you don't have a Web application credential:
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Choose **Web application**
3. Configure the OAuth client:

#### **Authorized JavaScript origins** - Add BOTH:
```
https://diabetes-predictor-ai.azurewebsites.net
http://localhost:5000
```

#### **Authorized redirect URIs** - Add BOTH:
```
https://diabetes-predictor-ai.azurewebsites.net/api/login/google
http://localhost:5000/api/login/google
```

4. Click **Save**
5. Copy the **Client ID** and **Client Secret**

### 4. Update Azure App Settings
Run these commands in PowerShell:

```powershell
# Replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET with actual values
az webapp config appsettings set `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --settings `
    GOOGLE_CLIENT_ID="YOUR_CLIENT_ID" `
    GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### 5. Restart the Azure Web App
```powershell
az webapp restart --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

### 6. Test Google Login
1. Visit: https://diabetes-predictor-ai.azurewebsites.net/login
2. Click the **"Sign in with Google"** button
3. You should see the Google OAuth popup
4. Sign in with your Google account
5. You should be redirected to the dashboard

## Common Issues

### Issue 1: "redirect_uri_mismatch" error
**Cause:** The redirect URI in Google Console doesn't match exactly.

**Fix:** Make sure the URI is EXACTLY:
```
https://diabetes-predictor-ai.azurewebsites.net/api/login/google
```
(Note: No trailing slash, must include `/api/login/google`)

### Issue 2: "unauthorized_client" error
**Cause:** The OAuth client ID is not configured correctly or domain is not authorized.

**Fix:** 
1. Verify the domain is in **Authorized JavaScript origins**
2. Verify the Client ID in Azure matches Google Console
3. Wait 5 minutes for Google to propagate changes

### Issue 3: Google button doesn't appear
**Cause:** Google OAuth is disabled or Client ID is missing.

**Fix:**
1. Verify `GOOGLE_CLIENT_ID` is set in Azure
2. Check browser console for errors (F12)
3. Make sure the login page loads without errors

### Issue 4: 401 Unauthorized after Google login
**Cause:** Session not being created properly.

**Fix:**
1. Check that `SECRET_KEY` is set in Azure
2. Verify Firebase is initialized correctly
3. Check Azure logs for errors

## Verification Checklist
- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 Client ID created
- [ ] Authorized JavaScript origins added (Azure domain)
- [ ] Authorized redirect URIs added (Azure domain + /api/login/google)
- [ ] Client ID copied to Azure settings
- [ ] Client Secret copied to Azure settings
- [ ] Azure Web App restarted
- [ ] Google login button appears on login page
- [ ] Google OAuth popup opens
- [ ] Successfully redirects after login

## Next Steps After Google OAuth Works
Once Google authentication is working:
1. Test ML predictions (`/predict`)
2. Test report generation
3. Test graph visualizations
4. Verify LLM reports (AI-generated insights)

## Current Status
- ✅ Backend OAuth code implemented
- ✅ Frontend Google button implemented
- ✅ Azure credentials set (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
- ❌ **Google Console not configured** (JavaScript origins & redirect URIs)
- ❌ 401 errors occurring (likely due to missing Google Console config)

## Important Notes
1. **Wait 5-10 minutes** after changing Google Console settings for changes to propagate
2. Clear browser cache if button still doesn't work
3. Test in incognito mode to avoid session issues
4. Check browser console (F12) for detailed error messages

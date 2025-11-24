# Quick Testing Guide - Authentication

## Before Testing
1. Ensure backend is running: `python flask_app.py`
2. Ensure frontend is running: `cd frontend && npm run dev`
3. Open browser to `http://localhost:5173` (or your frontend URL)

## Test Scenarios

### ✅ Scenario 1: Login with Valid Credentials
**Steps:**
1. Go to Login page
2. Enter username: `admin` 
3. Enter password: `admin123`
4. Click "Sign In"

**Expected:** Login successful, redirect to dashboard

---

### ✅ Scenario 2: Login with Invalid Password
**Steps:**
1. Go to Login page
2. Enter username: `admin`
3. Enter password: `wrongpassword`
4. Click "Sign In"

**Expected:** Error message "Invalid username or password"

---

### ✅ Scenario 3: Register New User
**Steps:**
1. Go to Register page
2. Enter name: `John Doe`
3. Enter email: `johndoe@example.com`
4. Enter password: `password123`
5. Confirm password: `password123`
6. Check terms checkbox
7. Click "Create Account"

**Expected:** Account created, auto-login, redirect to dashboard

---

### ✅ Scenario 4: Register with Existing Email
**Steps:**
1. Go to Register page
2. Enter email: `192425151.simats@saveetha.com` (already registered)
3. Fill other fields
4. Click "Create Account"

**Expected:** Error "Email already registered"

---

### ✅ Scenario 5: Password Too Short
**Steps:**
1. Go to Register page
2. Enter password: `123`
3. Tab to next field

**Expected:** Red text "Password must be at least 6 characters"

---

### ✅ Scenario 6: Password Mismatch
**Steps:**
1. Go to Register page
2. Enter password: `password123`
3. Enter confirm: `password456`
4. Tab to next field

**Expected:** Red text "Passwords do not match"

---

### ✅ Scenario 7: Empty Fields
**Steps:**
1. Go to Login page
2. Leave username empty
3. Click "Sign In"

**Expected:** Browser validation error (field required)

---

### ✅ Scenario 8: Invalid Email Format
**Steps:**
1. Go to Register page
2. Enter email: `notanemail`
3. Click "Create Account"

**Expected:** Error "Please enter a valid email address"

---

## Feature Checklist

### Login Page
- ✅ Username/email input field
- ✅ Password input field with visibility toggle
- ✅ "Remember me" checkbox
- ✅ "Forgot password" link
- ✅ Client-side validation
- ✅ Error messages with animation
- ✅ Loading state during login
- ✅ Link to register page

### Register Page
- ✅ Full name input field
- ✅ Email input field
- ✅ Password input with visibility toggle
- ✅ Confirm password with visibility toggle
- ✅ Real-time password validation
- ✅ Real-time password match checking
- ✅ Email format validation
- ✅ Terms checkbox
- ✅ Error messages with animation
- ✅ Loading state during registration
- ✅ Link to login page
- ✅ Auto-login after successful registration

### Backend API
- ✅ `/api/login` - POST endpoint
- ✅ `/api/register` - POST endpoint
- ✅ `/api/session` - GET endpoint
- ✅ Session management
- ✅ Password hashing
- ✅ Duplicate email check
- ✅ Duplicate username check

## Common Issues & Quick Fixes

### Issue: "Unable to connect to server"
**Fix:** Check if backend is running on port 5000

### Issue: "Email already registered"
**Fix:** Use a different email or login with existing account

### Issue: Login works but doesn't redirect
**Fix:** Check browser console for navigation errors

### Issue: Session not persisting
**Fix:** 
- Clear browser cookies
- Check if backend session is configured correctly
- Ensure `withCredentials: true` in API calls

## Browser Developer Tools

### Check Network Tab
1. Open Developer Tools (F12)
2. Go to Network tab
3. Try to login/register
4. Look for:
   - `/api/login` or `/api/register` request
   - Status code (should be 200 for success)
   - Response data
   - Any CORS errors

### Check Console
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for:
   - API errors
   - JavaScript errors
   - Authentication logs

### Check Application/Storage Tab
1. Open Developer Tools (F12)
2. Go to Application (Chrome) or Storage (Firefox)
3. Check Cookies
4. Look for session cookie

## Success Indicators

✅ **Login Success:**
- No error messages
- Redirects to `/dashboard`
- User data appears in session
- Navigation shows logged-in state

✅ **Register Success:**
- No error messages
- Account created in database
- Auto-login completes
- Redirects to `/dashboard`

## Need More Help?

Check the detailed documentation in `AUTHENTICATION_FIX.md`

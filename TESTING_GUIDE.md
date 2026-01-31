# 🧪 Complete Testing Guide - Rental Management System

## ✅ Pre-Test Checklist

### Server Status
- [ ] **Backend:** http://localhost:8000 (FastAPI)
- [ ] **Frontend:** http://localhost:3000 (Next.js)
- [ ] **Database:** MySQL running

### Test Accounts Available
```
ADMIN:    admin@rental.com    / Admin@123
VENDOR:   vendor@rental.com   / Vendor@123
CUSTOMER: customer@rental.com / Customer@123
```

---

## 🧪 Test Suite

### TEST 1: Authentication & Error Handling ⭐ CRITICAL

**Purpose:** Verify the error handling fix works

#### 1.1 Test Invalid Login (Should Show Proper Error)
1. Open http://localhost:3000/login
2. Enter email: `test@test.com`
3. Enter password: `wrongpassword`
4. Click "Sign In"

**✅ Expected:** Toast notification with error message (NOT red React error screen)  
**❌ If you see:** Red error screen → ERROR NOT FIXED

#### 1.2 Test Valid Login (Admin)
1. Open http://localhost:3000/login
2. Enter email: `admin@rental.com`
3. Enter password: `Admin@123`
4. Click "Sign In"

**✅ Expected:** 
- Success toast notification
- Redirect to `/admin/dashboard`
- No console errors

#### 1.3 Test Valid Login (Vendor)
1. Logout (if logged in)
2. Login with: `vendor@rental.com / Vendor@123`

**✅ Expected:**
- Success toast
- Redirect to `/vendor/dashboard`

#### 1.4 Test Valid Login (Customer)
1. Logout (if logged in)
2. Login with: `customer@rental.com / Customer@123`

**✅ Expected:**
- Success toast  
- Redirect to `/browse`

---

### TEST 2: Navigation & Pages

#### 2.1 Test Browse Page (Customer)
1. Login as customer
2. Should auto-redirect to `/browse`

**✅ Expected:**
- Products grid (might be empty - that's OK)
- Filter dropdown works
- Search box present
- No errors in console

#### 2.2 Test Admin Dashboard
1. Login as admin
2. Should redirect to `/admin/dashboard`

**✅ Expected:**
- Stats cards display (revenue, users, etc.)
- User management table visible
- No React errors

#### 2.3 Test Vendor Dashboard
1. Login as vendor
2. Should redirect to `/vendor/dashboard`

**✅ Expected:**
- Vendor stats display
- Quick action buttons
- No errors

---

### TEST 3: Error Boundaries

**Purpose:** Ensure all API errors are handled gracefully

#### 3.1 Test Network Error Handling
1. Stop the backend server (Ctrl+C in backend terminal)
2. Try to login or browse products

**✅ Expected:**
- Toast error message (e.g., "Network Error")
- No red React error screen
- App remains functional

#### 3.2 Restart Backend
1. Restart backend: `cd backend && uvicorn main:app --reload`
2. Wait for it to start
3. Try operations again

**✅ Expected:** All functions work normally

---

### TEST 4: Protected Routes

#### 4.1 Test Unauthorized Access
1. Logout (if logged in)
2. Try to visit: http://localhost:3000/admin/dashboard

**✅ Expected:**
- Redirect to `/login`
- No errors

#### 4.2 Test Wrong Role Access
1. Login as customer
2. Try to visit: http://localhost:3000/admin/dashboard

**✅ Expected:**
- Error toast OR redirect
- No React crash

---

### TEST 5: Console Check (CRITICAL)

**Open Browser Console (F12)**

#### 5.1 Check for Errors
Look for:
- ❌ Red errors about "Objects are not valid as React child"
- ❌ Hydration errors
- ❌ Unhandled promise rejections

**✅ Expected:** 
- No red errors
- Some warnings are OK (yellow)
- Info logs are OK (blue)

#### 5.2 Network Tab
1. Open Network tab
2. Try logging in
3. Check `/login` API call

**✅ Expected:**
- Status: 200 (success) or 422 (validation error)
- Response is JSON
- Error responses don't crash the app

---

## 🎯 Success Criteria

### Must Pass ✅
- [ ] Login shows proper error messages (not React errors)
- [ ] All valid logins work and redirect correctly
- [ ] No "Objects are not valid" errors anywhere
- [ ] Console is clean (no red errors)
- [ ] All pages load without crashing

### Good to Have ✅
- [ ] Error messages are user-friendly
- [ ] Toasts appear and disappear correctly
- [ ] Navigation is smooth
- [ ] Protected routes work correctly

---

## 🐛 If You Find Issues

### Issue: Red React Error Screen
**Root Cause:** Object being rendered  
**Action:** Take screenshot and share

### Issue: Blank Page
**Root Cause:** Console error  
**Action:** Open F12, check Console tab, share error

### Issue: "Network Error" Toast
**Root Cause:** Backend not running  
**Action:** Check backend terminal, restart if needed

### Issue: Redirect Loop
**Root Cause:** Auth state issue  
**Action:** Clear localStorage, refresh page

---

## 📸 What to Test First

**PRIORITY 1 (MUST TEST):**
1. ✅ Login with wrong credentials → Should show error toast
2. ✅ Login with correct credentials → Should work
3. ✅ Check browser console → Should be clean

**PRIORITY 2 (SHOULD TEST):**
4. ✅ Navigate between pages
5. ✅ Test protected routes
6. ✅ Logout and login again

**PRIORITY 3 (NICE TO TEST):**
7. ✅ All three user roles
8. ✅ Network error handling
9. ✅ Various page features

---

## ⚡ Quick Test (2 minutes)

**Fastest way to verify the fix:**

1. Open http://localhost:3000/login
2. Enter: `wrong@email.com` / `wrongpass`
3. Click Sign In

**✅ PASS:** See error toast (gray/red notification)  
**❌ FAIL:** See red React error screen

If PASS → Login with real credentials and explore!  
If FAIL → Take screenshot and let me know!

---

## 🎉 Test Complete Checklist

Once you finish testing, check these off:

- [ ] Login error handling works
- [ ] Valid logins redirect correctly  
- [ ] Console is error-free
- [ ] No React rendering errors
- [ ] All three user types can login
- [ ] Pages load successfully
- [ ] Navigation works
- [ ] Logout works

**When all checked:** Application is working! 🚀

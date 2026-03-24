# Testing Checklist - Agent Chat History Fix

## ✅ Completed Steps
- [x] Cleaned target directory (`mvn clean`)
- [x] Recompiled project with updated files (`mvn compile`)
- [x] Verified source files contain "Agent Chat History"
- [x] Verified target files contain updated code
- [x] Started server on http://localhost:8080

## 🧪 Testing Steps

### Step 1: Clear Browser Cache
**IMPORTANT: Do this first!**
- Open browser DevTools (F12)
- Right-click refresh button → "Empty Cache and Hard Reload"
- OR: Press Ctrl+Shift+Delete → Clear cache → Reload page
- OR: Open in Incognito/Private window

### Step 2: Test Quote Flow
1. Navigate to: http://localhost:8080
2. Fill out quote form:
   - Age: 30
   - Coverage: $500,000
   - Health: Excellent
3. Click "Get My Quote"

**Expected Results:**
- ✅ "Agent Chat History" widget appears (bottom-right)
- ✅ Widget button says "Agent Chat History" (NOT "Quote Agent")
- ✅ Widget auto-expands after 1 second
- ✅ Inside widget: "Agent Chat History" as header
- ✅ "Quote Agent" section header appears inside
- ✅ Quote agent chat messages display
- ✅ No tabs visible

### Step 3: Test Application Flow
1. Click "Apply Now"
2. Fill out application form:
   - Name: Test User
   - Email: test@example.com
   - Phone: 555-0123
   - Address: 123 Test St
3. Click "Submit Application"

**Expected Results:**
- ✅ Underwriting processing card appears
- ✅ Widget opens (if it was closed)
- ✅ A visual separator line appears in the widget
- ✅ "UNDERWRITING AGENT" label appears in separator
- ✅ Underwriting agent chat messages appear BELOW quote agent chat
- ✅ Widget auto-scrolls to bottom to show new content
- ✅ "New" badge appears on widget button
- ✅ Both Quote Agent and Underwriting Agent chats are visible when you scroll
- ✅ Processing card disappears after ~1.5 seconds

### Step 4: Verify Persistence
1. Scroll through the widget chat history
2. Verify you can see:
   - Quote Agent section header
   - All quote agent messages
   - Separator line
   - Underwriting Agent label
   - All underwriting agent messages
3. Close the widget (click X or button)
4. Reopen the widget (click button)

**Expected Results:**
- ✅ All chat history is still there
- ✅ Nothing disappeared
- ✅ You can scroll through entire history

## 🐛 If Issues Persist

### Issue: Widget still shows old design with tabs
**Solution:**
```powershell
# Hard refresh in browser
Ctrl+Shift+F5

# Or clear browser cache completely:
# Chrome: Settings → Privacy → Clear browsing data → Cached images and files
# Edge: Settings → Privacy → Choose what to clear → Cached data and files
```

### Issue: Changes not visible
**Check these:**
1. Server is running (check terminal for "Started LifeInsuranceApplication")
2. Accessing correct URL: http://localhost:8080
3. Check target files have changes:
   ```powershell
   Select-String -Path "target\classes\static\js\app.js" -Pattern "Agent Chat History"
   ```
4. Clear browser cache completely

### Issue: Widget disappears or behaves strangely
**Check browser console (F12):**
- Look for JavaScript errors (red text)
- Check Network tab - ensure app.js and style.css load successfully
- Verify files are not being cached (should see 200, not 304)

## 📋 What Should NOT Happen
- ❌ NO tabs in the widget
- ❌ NO "Quote Agent" / "Underwriting Agent" tab buttons
- ❌ Underwriting chat should NOT disappear
- ❌ Widget should NOT show only one agent at a time

## 📋 What SHOULD Happen
- ✅ Single continuous timeline
- ✅ "Agent Chat History" as widget title
- ✅ Quote Agent section first
- ✅ Separator line with "UNDERWRITING AGENT" label
- ✅ Underwriting Agent section below
- ✅ All content scrollable in one view
- ✅ Content persists - never disappears

## 🎯 Success Criteria
All chat interactions from both agents are visible in a single, scrollable timeline that never disappears.

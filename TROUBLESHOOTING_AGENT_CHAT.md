# Troubleshooting Agent Chat Tab Switching

## What Was Fixed

### Issue
The underwriting agent tab was not automatically switching when the underwriting process completed.

### Changes Made

1. **Improved Tab Switching Logic** - Inline implementation in the underwriting handler:
   - Directly manipulates the DOM instead of relying on function call
   - Ensures tab classes are updated (`active` class)
   - Explicitly shows/hides the correct chat bodies
   - Added proper timing with `sleep()` calls

2. **Better Timing Sequence**:
   ```javascript
   await sleep(100);  // Wait for DOM updates
   // Expand widget
   await sleep(400);  // Wait for expansion animation
   // Switch tabs (inline code)
   // Show underwriting chat
   ```

3. **Enhanced Debug Logging**:
   - Added console.log statements to track tab switching
   - Logs element discovery and display changes
   - Open browser DevTools (F12) to see logs

## How to Test

1. **Start the application**:
   ```powershell
   mvn spring-boot:run
   ```

2. **Open browser DevTools** (F12) before testing

3. **Test Flow**:
   - Fill out quote form and submit
   - Verify Quote Agent tab appears in floating widget
   - Fill out application form and submit
   - Watch console logs during underwriting processing
   - **Expected**: Widget should automatically switch to "Underwriting Agent" tab

4. **Check Console Logs**:
   Look for these messages:
   ```
   Switching to agent tab: underwriting
   Found tabs: 2
   Activated tab: underwriting
   Quote chat element: found
   UW chat element: found
   Hiding quote chat
   Showing UW chat
   ```

## Manual Testing Steps

If automatic switching doesn't work, try:

1. **Check if tab is visible**:
   - Open DevTools → Elements tab
   - Find the underwriting tab button: `<button class="agent-tab" data-agent="underwriting">`
   - Check if `style="display: none;"` is still set
   - It should be `style="display: flex;"` after underwriting starts

2. **Manually click the tab**:
   - Click on "Underwriting Agent" tab
   - Verify it switches to show underwriting chat
   - This confirms the tab functionality works

3. **Check chat content**:
   - Look for element with id `underwriting-agent-chat`
   - Verify it has content (chat messages)
   - Check if it has `style="display: none;"` or `style="display: block;"`

## Common Issues & Solutions

### Issue 1: Tab Not Visible
**Symptom**: "Underwriting Agent" tab never appears
**Solution**: 
- Check if `data.underwritingResult.agentTrace` exists
- Verify the backend is returning agent trace data
- Check console for errors

### Issue 2: Tab Visible But Not Active
**Symptom**: Tab shows but quote agent tab stays active
**Solution**:
- Check browser console for the debug logs
- Verify timing - may need to increase sleep durations
- Clear browser cache and hard refresh (Ctrl+F5)

### Issue 3: Widget Doesn't Expand
**Symptom**: Widget stays minimized
**Solution**:
- Check if `toggleAgentChat()` is being called
- Manually click the widget button
- Check for JavaScript errors in console

### Issue 4: Chat Content Not Showing
**Symptom**: Tab switches but content is empty
**Solution**:
- Check if `parseAgentTraceToChat()` is working
- Verify agent trace has proper format
- Check if innerHTML is being set correctly

## Debugging Code Snippets

Add these in browser console while testing:

```javascript
// Check if widget exists
document.getElementById('floating-agent-chat')

// Check if tabs exist
document.querySelectorAll('.agent-tab')

// Check chat bodies
document.getElementById('quote-agent-chat')
document.getElementById('underwriting-agent-chat')

// Force switch to underwriting tab
switchAgentTab('underwriting')

// Check current tab display styles
console.log('Quote:', document.getElementById('quote-agent-chat')?.style.display);
console.log('UW:', document.getElementById('underwriting-agent-chat')?.style.display);
```

## If Still Not Working

1. **Hard refresh** the page (Ctrl+F5)
2. **Clear browser cache** completely
3. **Restart the Spring Boot application**
4. **Check for JavaScript errors** in console (F12)
5. **Verify files are copied** to target directory:
   ```powershell
   Get-Item target/classes/static/js/app.js | Select-Object LastWriteTime
   ```

## Expected Behavior

✅ After submitting application:
1. Underwriting processing card appears
2. "Underwriting Agent" tab becomes visible in widget
3. Widget expands (if collapsed)
4. Widget automatically switches to "Underwriting Agent" tab
5. Underwriting chat content is visible
6. "New" badge appears on widget button
7. Processing card disappears after 1.5 seconds

## Contact
If issues persist, provide:
- Browser console logs
- Screenshot of the widget
- Network tab showing API responses
- Any error messages

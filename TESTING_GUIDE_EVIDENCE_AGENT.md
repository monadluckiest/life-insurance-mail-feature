# TESTING GUIDE: Complex Path with Evidence Collection

## ✅ What's Fixed

### 1. **Agent Chat History Display**
- All underwriting reasons now display in Agent Chat History widget
- Manual Review reasons clearly shown
- Evidence Agent trace displayed
- Manual Underwriting Agent trace displayed

### 2. **Complete Flow Integration**
- Underwriting Agent flags cases → Evidence Agent → Manual UW Agent
- All agent traces appear sequentially in the chat widget
- Manual Review Pending card shows AI recommendation

## 🧪 How to Test the Evidence Agent

### Test Case 1: High Coverage (Triggers Financial Review)
**Input:**
```
Age: 45
Coverage Amount: $750,000
Health Status: Excellent
```

**Expected Behavior:**
1. ✅ Quote Agent calculates premium
2. ⚠️ Underwriting Agent flags: "High Coverage Amount: $750,000 exceeds $500,000 threshold"
3. 📋 Evidence Agent requests Financial Review evidence
4. ⏳ Simulates 5-second collection delay
5. 🩺 Manual UW Agent analyzes evidence
6. 📊 Shows "Manual Review Pending" card with AI recommendation

**What You'll See in Agent Chat History:**
```
QUOTE AGENT
🤖 Quote Agent: Initializing autonomous agent...
💭 Agent Reasoning: Invoking risk_analysis_tool...
✅ Result: Monthly Premium: $XX.XX

UNDERWRITING AGENT  
⚠️ Rules Engine: Flagged - High Coverage Amount ($750,000)
🔍 Decision: MANUAL_REVIEW required (1 risk factor)
📋 Next Step: Evidence Agent will request medical documentation

EVIDENCE AGENT
📋 Evidence Agent: Initiating evidence collection for APP-XXX
📋 Evidence Type Required: Financial Review
📋 Sending Financial Review request to provider...
⏳ Waiting for provider response (Demo: 5 second simulation)...
✅ Financial Review Received from provider
📄 Evidence Summary: XXX characters of data received
📋 Evidence Agent: Ready for Manual Underwriting Review

MANUAL UNDERWRITING AGENT
🩺 Manual UW Agent: Analyzing evidence for APP-XXX
📊 Extracting key risk factors...
📊 Risk Rating: STANDARD
💡 Recommendation: Approve at Standard Rates
📝 Generated detailed summary for human underwriter review
🩺 Manual UW Agent: Analysis complete - Ready for human decision
```

### Test Case 2: Medical Condition (Triggers APS Request)
**Input:**
```
Age: 55
Coverage Amount: $500,000
Health Status: Hypertension
```

**Expected Behavior:**
1. ✅ Quote Agent calculates premium
2. ⚠️ Underwriting Agent flags 2 risk factors:
   - "Age Factor: 55 years exceeds standard risk threshold"
   - "Medical Condition Detected: Hypertension"
3. 📋 Evidence Agent requests APS (Attending Physician Statement)
4. ⏳ Simulates 5-second collection delay
5. 📄 Returns mock APS document with physician notes
6. 🩺 Manual UW Agent analyzes APS:
   - Extracts: "Condition well-controlled", "Patient compliant"
   - Risk Rating: MODERATE
   - Recommendation: APPROVE_WITH_CONDITIONS (+50% premium)
7. 📊 Shows detailed summary for human underwriter

**What You'll See:**
- All 4 agent traces in chat widget
- Manual Review Pending card showing:
  - Application number
  - Risk factors flagged
  - Evidence type: APS
  - AI recommendation with conditions
  - "What Happens Next" information

### Test Case 3: Multiple Risk Factors (Most Complex)
**Input:**
```
Age: 58
Coverage Amount: $2,000,000
Health Status: Diabetes
```

**Expected Behavior:**
1. ✅ Quote Agent calculates premium
2. ⚠️ Underwriting Agent flags 3 risk factors:
   - "High Coverage Amount: $2,000,000"
   - "Age Factor: 58 years"
   - "Medical Condition: Diabetes"
3. 📋 Evidence Agent collects APS
4. 🩺 Manual UW Agent provides detailed analysis
5. 📊 Manual Review Pending with comprehensive summary

## 🎬 Step-by-Step Testing Instructions

### Step 1: Verify Servers Running
```bash
# Python Agent Server
# Should see: "Uvicorn running on http://0.0.0.0:8000"

# Java Spring Boot Server  
# Should see: "Started LifeInsuranceApplication in X seconds"
```

### Step 2: Open Browser
1. Navigate to: http://localhost:8080
2. Open Developer Tools (F12)
3. Go to Network tab, check "Disable cache"

### Step 3: Start Test Flow
1. **Get Quote:**
   - Enter: Age 55, $2,000,000, Hypertension
   - Click "Get Instant Quote"
   - ✅ Quote Agent trace appears in widget

2. **Submit Application:**
   - Fill in applicant details
   - Click "Submit Application"
   - ✅ Underwriting Agent trace appears
   - ⚠️ Watch for "MANUAL_REVIEW" flags

3. **Watch Evidence Collection:**
   - ⏳ 5-second delay simulation
   - ✅ Evidence Agent trace appears
   - 📋 Shows evidence collection progress

4. **View Manual UW Analysis:**
   - 🩺 Manual UW Agent trace appears
   - 📊 Shows risk analysis
   - 💡 Displays recommendation

5. **Check Manual Review Card:**
   - Application details
   - Risk factors listed
   - AI recommendation displayed
   - "What Happens Next" information

## 📊 What to Look For

### In Browser Console:
```javascript
console.log('🔍 Complex Path: Manual Review Required', data)
```

### In Java Logs:
```
🔍 Underwriting Agent: Application flagged for MANUAL REVIEW
📋 Triggering Evidence Collection Agent...
🩺 Triggering Manual Underwriting Agent...
✅ Complex Path Complete: Evidence collected and analyzed
```

### In Python Logs:
```
> Entering new AgentExecutor chain...
Invoking: `aps_request_tool`...
Invoking: `evidence_analysis_tool`...
> Finished chain.
```

### In Agent Chat Widget:
- 4 distinct sections with separators
- Each agent's reasoning visible
- Tools used by each agent
- Final decisions and recommendations

## 🐛 Troubleshooting

### If Evidence Agent Doesn't Show:
1. Check Python logs for errors
2. Verify endpoint: http://localhost:8000/agent/request-evidence
3. Check Java logs for "Triggering Evidence Collection Agent"

### If Manual UW Agent Doesn't Show:
1. Ensure evidence was received (check application.evidenceReceived)
2. Verify endpoint: http://localhost:8000/agent/manual-underwrite
3. Check Java logs for "Triggering Manual Underwriting Agent"

### If Chat Widget Empty:
1. Hard refresh browser (Ctrl+Shift+F5)
2. Clear browser cache
3. Check DevTools Console for JavaScript errors

## 🎯 Success Criteria

✅ All 4 agent traces visible in sequential order
✅ Reasons for manual review clearly displayed
✅ 5-second evidence collection delay observed
✅ Manual Review Pending card appears
✅ AI recommendation displayed with risk rating
✅ No JavaScript errors in console
✅ All agent reasoning visible

## 📝 Notes

- **Happy Path** (Age < 50, Coverage < $500k, Excellent health):
  - Goes straight to payment
  - Only 2 agents: Quote + Underwriting (Auto-approved)

- **Complex Path** (Age > 50 OR Coverage > $500k OR Medical condition):
  - Requires manual review
  - 4 agents: Quote + Underwriting + Evidence + Manual UW
  - Shows "Manual Review Pending" card
  - Does NOT proceed to payment

- **Evidence Collection**:
  - 5-second delay is intentional (demo of real-world wait)
  - Mock APS documents are realistic
  - Financial Review for high coverage amounts

- **Manual UW Analysis**:
  - Extracts key findings from evidence
  - Calculates risk scores
  - Provides specific recommendations
  - Generates summary for human underwriter

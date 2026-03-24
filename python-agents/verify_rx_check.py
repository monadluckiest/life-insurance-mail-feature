
import sys
import os

# Add parent directory to path so we can import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.underwriting import run_underwriting_agent

def run_test(name, age, health, coverage, risk_expected):
    print(f"\n--- Testing Case: {name} ({health}) ---")
    input_data = {
        "applicationNumber": f"TEST-{name}",
        "quote": {
            "age": age,
            "healthStatus": health,
            "coverageAmount": coverage,
            "isSmoker": False
        }
    }
    
    result = run_underwriting_agent(input_data)
    
    print(f"Decision: {result.get('decision')}")
    print(f"Reason: {result.get('reason')}")
    
    # Check trace for Rx Tool usage
    rx_tool_used = False
    rx_risk_found = False
    
    for log in result.get('agentTrace', []):
        if "prescription_check_tool" in str(log) or "PrescriptionCheck" in str(log):
            rx_tool_used = True
        if "Risk found" in str(log) or "High Risk" in str(log):
            rx_risk_found = True
            
    print(f"Rx Tool Used: {rx_tool_used}")
    
    if risk_expected:
        if result.get('decision') in ["REJECTED", "REFER", "MANUAL_REVIEW"]:
            print("✅ Result matches expected High Risk outcome.")
        else:
            print("❌ FAILED: Expected High Risk outcome, got Approved.")
    else:
        if result.get('decision') == "APPROVED":
            print("✅ Result matches expected Low Risk outcome.")
        else:
            print(f"❌ FAILED: Expected Approved, got {result.get('decision')}")

print("=== Verifying Prescription Check Integration ===")

# Case 1: High Risk (Triggers Mock Rx Logic via Name 'Risk' or Health 'Poor')
# This exactly matches the User's failed test case
run_test("Mona Risk", 67, "Poor", 100000, risk_expected=True)

# Case 2: Low Risk (Clean)
run_test("Jane Doe", 30, "Excellent", 100000, risk_expected=False)

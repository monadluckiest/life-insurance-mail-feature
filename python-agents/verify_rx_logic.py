
import sys
import os

# Add parent directory to path so we can import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.underwriting import run_underwriting_agent

def run_test(name, age, health, coverage, risk_expected):
    print(f"\n--- Testing Case: {name} ({health}) ---")
    input_data = {
        "applicationNumber": f"TEST-{name}",
        "applicantName": name,
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
    print(f"Full Result: {result}")
    
    # Check trace for Rx Tool usage
    rx_tool_used = False
    rx_risk_found = False
    
    for log in result.get('agentTrace', []):
        print(f"LOG: {log}")

print("=== Verifying Improved Rx Logic ===")

# Case 1: Deterministic "Mona Risk" (High Risk Trigger)
# Should return High Risk Meds due to name trigger
run_test("Mona Risk", 45, "Fair", 100000, risk_expected=True)

# Case 2: Deterministic "John Diabetes" (Diabetes Trigger)
run_test("John Diabetes", 50, "Good", 100000, risk_expected=True)

# Case 3: Probabilistic High Risk (Age 65 + Poor Health)
# Should trigger high probability of meds -> Rejection
run_test("Senior Poor", 65, "Poor", 100000, risk_expected=True)

# Case 4: Probabilistic Low Risk (Age 25 + Excellent Health)
# Should generally be clean
run_test("Young Healthy", 25, "Excellent", 100000, risk_expected=False)

# Case 5: Probabilistic Medium/High Risk (Age 60 + Fair Health)
# Might trigger meds (Statin/BP) -> Could be Risk if count > 2 or high risk med
run_test("Old Fair", 60, "Fair", 100000, risk_expected=True)


import sys
import os

# Add the current directory to the path so we can import agents
sys.path.append(os.path.join(os.getcwd(), 'python-agents'))

from agents.underwriting import run_underwriting_agent

def test_smoker_rejection():
    print("Testing Smoker Rejection Scenario...")
    
    # Payload for Smoker, Fair Health, 1M Coverage
    payload = {
        "applicationNumber": "TEST-APP-001",
        "quote": {
            "age": 35,
            "healthStatus": "Fair",
            "coverageAmount": 1000000,
            "isSmoker": True
        }
    }
    
    result = run_underwriting_agent(payload)
    
    print("\n--- Result ---")
    print(f"Decision: {result.get('decision')}")
    print(f"Reason: {result.get('reason')}")
    
    if result.get('decision') == 'REJECTED' and "Smoker" in result.get('reason'):
        print("\n✅ TEST PASSED: Application was correctly rejected due to smoker status.")
    else:
        print("\n❌ TEST FAILED: Application was NOT rejected as expected.")
        print(f"Actual Decision: {result.get('decision')}")

if __name__ == "__main__":
    test_smoker_rejection()

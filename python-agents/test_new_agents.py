import requests
import json

BASE_URL = "http://localhost:8000"

def test_needs_analysis():
    print("\n--- Testing Needs Analysis Agent ---")
    payload = {
        "age": 35,
        "dependents": 2,
        "isSmoker": "No"
    }
    try:
        response = requests.post(f"{BASE_URL}/agent/needs-analysis", json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ Status:", data.get("status"))
        print("   Recommended Coverage:", data.get("recommended_coverage"))
        print("   Reasoning:", json.dumps(data.get("reasoning"), indent=2))
    except Exception as e:
        print("❌ Failed:", str(e))

def test_policy_servicing():
    print("\n--- Testing Policy Servicing Agent ---")
    payload = {
        "policyNumber": "POL-123456789",
        "newAddress": "123 New Street, Cloud City, CA 90210"
    }
    try:
        response = requests.post(f"{BASE_URL}/agent/policy-servicing", json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ Status:", data.get("status"))
        print("   Updated Address:", data.get("updatedAddress"))
        print("   Confirmation Document Preview:\n", data.get("confirmationDocument")[:100], "...")
    except Exception as e:
        print("❌ Failed:", str(e))

if __name__ == "__main__":
    test_needs_analysis()
    test_policy_servicing()

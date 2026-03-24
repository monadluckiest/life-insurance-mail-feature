import requests
import time
import json

BASE_URL = "http://localhost:8080/api"

def verify_happy_path():
    print("🚀 Starting End-to-End Verification: Happy Path")
    
    # 1. Calculate Quote
    print("\n1️⃣  Requesting Quote (Age: 30, Coverage: 500k, Health: Excellent)...")
    quote_payload = {
        "age": 30,
        "coverageAmount": 500000,
        "healthStatus": "Excellent"
    }
    
    try:
        quote_res = requests.post(f"{BASE_URL}/quotes/calculate", json=quote_payload)
        quote_res.raise_for_status()
        quote_data = quote_res.json()
        print(f"✅ Quote Received: ${quote_data['monthlyPremium']}/mo (Quote ID: {quote_data['quoteId']})")
        
        quote_id = quote_data['quoteId']
        
        # 2. Submit Application
        print("\n2️⃣  Submitting Application (Triggering Instant UW)...")
        app_payload = {
            "quoteId": quote_id,
            "applicantName": "John Doe",
            "applicantEmail": "john@example.com",
            "applicantPhone": "+15550199123",
            "applicantAddress": "123 Main St, Springfield" 
        }
        
        app_res = requests.post(f"{BASE_URL}/applications/submit", json=app_payload)
        app_res.raise_for_status()
        app_data = app_res.json()
        
        print(f"✅ Application Response: {json.dumps(app_data, indent=2)}")
        
        # Verify Approval
        uw_result = app_data.get("underwritingResult", {})
        decision = uw_result.get("decision")
        
        if decision == "APPROVED":
            print("\n🎉 SUCCESS: Application was INSTANTLY APPROVED by Python Agent!")
        else:
            print(f"\n❌ FAILURE: Application Decision was {decision}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        try:
            print(f"Response Content: {e.response.text}")
        except:
            pass

if __name__ == "__main__":
    # Wait a bit for Java app to fully startup if run immediately
    time.sleep(2) 
    verify_happy_path()

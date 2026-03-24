import requests

# 1. First Get a Quote to get a Quote ID
quote_url = "http://localhost:8080/api/quotes/calculate"
quote_data = {
    "age": 45,
    "coverageAmount": 500000,
    "healthStatus": "Good",
    "isSmoker": False
}
print("Getting Quote...")
try:
    q_resp = requests.post(quote_url, json=quote_data)
    q_resp.raise_for_status()
    quote = q_resp.json()
    quote_id = quote['quoteId']
    print(f"Got Quote ID: {quote_id}")
    
    # 2. Submit Application with Insulin
    submit_url = "http://localhost:8080/api/applications/submit"
    app_data = {
        "quoteId": quote_id,
        "applicantName": "Java Test User",
        "applicantEmail": "test@example.com",
        "applicantPhone": "15551234567",
        "applicantAddress": "123 Test St",
        "applicantMedications": "insulin"
    }
    
    print(f"Submitting Application with Meds...")
    s_resp = requests.post(submit_url, json=app_data)
    s_resp.raise_for_status()
    
    result = s_resp.json()
    print("Submission Result:")
    import json
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"Test Failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Error Details: {e.response.text}")

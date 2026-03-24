import requests

url = "http://localhost:8000/agent/underwrite"
data = {
    "applicationNumber": "TEST-123",
    "applicantName": "Test User",
    "applicantMedications": "insulin, metformin",
    "quote": {
        "age": 45,
        "coverageAmount": 500000,
        "healthStatus": "Good",
        "isSmoker": False
    }
}

print(f"Sending request to {url} with meds: {data['applicantMedications']}")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    import json
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

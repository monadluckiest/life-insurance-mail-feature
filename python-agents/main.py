import sys
import io

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.quote import run_quote_agent
from agents.underwriting import run_underwriting_agent
from agents.policy_issuance import run_policy_issuance_agent
from agents.evidence import run_evidence_agent
from agents.manual_underwriting import run_manual_underwriting_agent
from agents.needs_analysis import run_needs_analysis_agent
from agents.policy_servicing import run_policy_servicing_agent

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "UP"}

class QuoteRequest(BaseModel):
    age: int
    coverageAmount: float
    healthStatus: str
    isSmoker: bool = False

class UnderwritingRequest(BaseModel):
    applicationNumber: str
    applicantName: str = "Unknown"
    applicantMedications: str | None = None
    quote: QuoteRequest

class PolicyIssuanceRequest(BaseModel):
    applicationNumber: str
    policyHolderName: str
    coverageAmount: float
    monthlyPremium: float

class EvidenceRequest(BaseModel):
    applicationNumber: str
    applicantName: str
    evidenceType: str
    healthStatus: str
    age: int

class ManualUnderwritingRequest(BaseModel):
    applicationNumber: str
    applicantName: str
    evidenceData: str
    age: int
    coverageAmount: float
    healthStatus: str

class NeedsAnalysisRequest(BaseModel):
    age: int
    dependents: int
    isSmoker: str

class PolicyServicingRequest(BaseModel):
    policyNumber: str
    newAddress: str

@app.post("/agent/quote")
async def quote_endpoint(request: QuoteRequest):
    try:
        result = run_quote_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/underwrite")
async def underwriting_endpoint(request: UnderwritingRequest):
    try:
        # Convert nested pydantic model to dict
        data = request.dict()
        print(f"DEBUG: Received Underwriting Request: {data}")
        print(f"DEBUG: Applicant Meds: {data.get('applicantMedications')}")
        result = run_underwriting_agent(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/issue-policy")
async def policy_issuance_endpoint(request: PolicyIssuanceRequest):
    try:
        result = run_policy_issuance_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/request-evidence")
async def evidence_endpoint(request: EvidenceRequest):
    try:
        result = run_evidence_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/manual-underwrite")
async def manual_underwriting_endpoint(request: ManualUnderwritingRequest):
    try:
        result = run_manual_underwriting_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/needs-analysis")
async def needs_analysis_endpoint(request: NeedsAnalysisRequest):
    try:
        result = run_needs_analysis_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/policy-servicing")
async def policy_servicing_endpoint(request: PolicyServicingRequest):
    try:
        result = run_policy_servicing_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

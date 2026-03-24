
import random
import time
from langchain.tools import tool
try:
    from langchain_core.pydantic_v1 import BaseModel, Field
except ImportError:
    from pydantic.v1 import BaseModel, Field # Fallback


# --- QUOTE AGENT TOOLS ---

class RiskAnalysisInput(BaseModel):
    age: int = Field(description="Age of the applicant")
    health_status: str = Field(description="Health status (Excellent, Good, Fair, Poor)")

@tool("risk_analysis_tool", args_schema=RiskAnalysisInput)
def risk_analysis_tool(age: int, health_status: str) -> dict:
    """Analyzes the risk factors based on age and health status to determine premium multipliers."""
    # Simulation delay
    time.sleep(0.5)
    
    # Logic moved from monolithic function to tool
    age_factor = 1.0
    if age < 25: age_factor = 1.5
    elif age < 35: age_factor = 1.2
    elif age < 45: age_factor = 1.3
    elif age < 55: age_factor = 1.5
    else: age_factor = 2.0
    
    health_factor = 1.0
    status_lower = health_status.lower()
    if status_lower == "excellent": health_factor = 0.8
    elif status_lower == "good": health_factor = 1.0
    elif status_lower == "fair": health_factor = 1.3
    elif status_lower == "poor": health_factor = 1.8
    else: health_factor = 1.5 # Default risk
    
    return {
        "age_factor": age_factor,
        "health_factor": health_factor,
        "base_rate": 0.0005,
        "description": f"Risk factors calculated: Age Factor {age_factor}, Health Factor {health_factor}"
    }

class PremiumCalculatorInput(BaseModel):
    coverage_amount: float = Field(description="Total coverage amount requested")
    age_factor: float = Field(description="Age risk factor")
    health_factor: float = Field(description="Health risk factor")
    base_rate: float = Field(description="Base premium rate")

@tool("premium_calculator_tool", args_schema=PremiumCalculatorInput)
def premium_calculator_tool(coverage_amount: float, age_factor: float, health_factor: float, base_rate: float) -> dict:
    """Calculates the final monthly and annual premium based on risk factors."""
    time.sleep(0.5)
    
    monthly_premium = coverage_amount * base_rate * age_factor * health_factor
    monthly_premium = round(monthly_premium, 2)
    annual_premium = monthly_premium * 12
    
    return {
        "monthly_premium": monthly_premium,
        "annual_premium": annual_premium
    }

# --- UNDERWRITING AGENT TOOLS ---

class CreditCheckInput(BaseModel):
    applicant_name: str = Field(description="Name of applicant (optional context)")

@tool("credit_check_tool", args_schema=CreditCheckInput)
def credit_check_tool(applicant_name: str = "Unknown") -> dict:
    """Simulates a call to a Credit Bureau (Equifax/TransUnion) to get a credit score."""
    time.sleep(1.0)
    score = random.randint(700, 850) # Happy path bias
    passed = score > 650
    return {
        "credit_score": score,
        "passed": passed,
        "status": "Excellent" if score > 750 else "Good"
    }

class MIBCheckInput(BaseModel):
    health_status: str = Field(description="Self-reported health status")

@tool("mib_check_tool", args_schema=MIBCheckInput)
def mib_check_tool(health_status: str) -> dict:
    """Simulates a call to the Medical Information Bureau (MIB) to verify medical history."""
    time.sleep(1.0)
    # Logic: Excellent/Good is clean, others might flag review
    is_clean = health_status.lower() in ["excellent", "good"]
    return {
        "mib_status": "Clean" if is_clean else "Review Required",
        "passed": is_clean
    }

class PrescriptionCheckInput(BaseModel):
    applicant_name: str = Field(description="Name of applicant")
    health_status: str = Field(description="Self-reported health status")

@tool("prescription_check_tool", args_schema=PrescriptionCheckInput)
def prescription_check_tool(applicant_name: str, health_status: str, age: int = 35) -> dict:
    """Simulates a call to a Pharmacy Benefit Manager (Rx check). Checks for life-saving meds and multiple pharmacies.
    Input 'age' is optional but recommended for better simulation.
    """
    time.sleep(1.0)
    
    rx_history = []
    pharmacy_count = 1
    risk_found = False
    details = []

    # --- SIMULATION DATA ---
    COMMON_MEDS = {
        "LOW_RISK": ["Amoxicillin (Antibiotic)", "Ibuprofen (Pain)", "Loratadine (Allergy)"],
        "MED_RISK": ["Atorvastatin (Cholesterol)", "Lisinopril (Hypertension)", "Omeprazole (GERD)", "Levothyroxine (Thyroid)"],
        "HIGH_RISK": ["Metformin (Diabetes)", "Insulin (Diabetes)", "Clopidogrel (Heart)", "Furosemide (Heart Failure)", "Albuterol (Asthma)"]
    }
    
    name_lower = applicant_name.lower()
    health_lower = health_status.lower()
    
    # --- 1. DETERMINISTIC TRIGGERS (For Demo Control) ---
    if "risk" in name_lower:
        rx_history.extend(["Metformin (Diabetes)", "Lisinopril (Hypertension)", "Atorvastatin (Cholesterol)"])
        pharmacy_count = 3
        risk_found = True
        details.append("Detected high-risk trigger in name.")
        
    elif "diabetes" in name_lower:
        rx_history.extend(["Metformin (Diabetes)", "Insulin Glargine"])
        risk_found = True
        details.append("Detected Diabetes trigger.")
        
    elif "heart" in name_lower or "cardio" in name_lower:
        rx_history.extend(["Clopidogrel (Heart)", "Atorvastatin (Cholesterol)"])
        risk_found = True
        details.append("Detected Cardiac trigger.")
        
    # --- 2. PROBABILISTIC LOGIC (Based on Age & Health) ---
    else:
        # Base probability of having ANY meds
        med_prob = 0.1
        if health_lower == "good": med_prob = 0.3
        elif health_lower == "fair": med_prob = 0.7
        elif health_lower == "poor": med_prob = 0.95
        
        # Age multiplier
        if age > 40: med_prob += 0.1
        if age > 50: med_prob += 0.2
        if age > 60: med_prob += 0.2
        
        # Determine if we add meds
        if random.random() < med_prob:
            # How many?
            num_meds = 1
            if health_lower == "fair": num_meds = 2
            elif health_lower == "poor": num_meds = random.randint(3, 5)
            
            # Which types?
            if health_lower in ["excellent", "good"]:
                 # Mostly low/med risk
                 pool = COMMON_MEDS["LOW_RISK"] + COMMON_MEDS["MED_RISK"]
            elif health_lower == "fair":
                # Med risk
                pool = COMMON_MEDS["MED_RISK"]
                pharmacy_count = random.randint(1, 2)
            else: # Poor
                # High risk
                pool = COMMON_MEDS["HIGH_RISK"] + COMMON_MEDS["MED_RISK"]
                pharmacy_count = random.randint(2, 4)
                risk_found = True
            
            # Select unique meds
            selected = random.sample(pool, min(num_meds, len(pool)))
            rx_history.extend(selected)
            
            if health_lower == "fair" and age > 50:
                # Force at least one maintenance med for Fair/Old
                if not any(m in COMMON_MEDS["MED_RISK"] for m in rx_history):
                    rx_history.append("Atorvastatin (Cholesterol)")

    # Final Risk Evaluation
    if len(rx_history) > 2 or pharmacy_count > 2:
        risk_found = True
        details.append(f"High prescription count ({len(rx_history)}) or pharmacy usage ({pharmacy_count}).")
        
    for med in rx_history:
        if "Diabetes" in med or "Heart" in med:
            risk_found = True
            details.append(f"High risk medication detected: {med}")

class MedRiskAnalysisInput(BaseModel):
    medication_list: list[str] = Field(description="List of medications to analyze")

@tool("medication_risk_analyzer_tool", args_schema=MedRiskAnalysisInput)
def medication_risk_analyzer_tool(medication_list: list[str]) -> dict:
    """Analyzes a list of medications and returns their risk categories and implications."""
    time.sleep(1.0)
    
    analysis = []
    overall_risk = "LOW"
    
    RISK_MAP = {
        "Metformin": "MED - Diabetes Management",
        "Insulin": "HIGH - Insulin Dependent Diabetes",
        "Lisinopril": "LOW - Hypertension (Common)",
        "Atorvastatin": "LOW - Cholesterol (Common)",
        "Clopidogrel": "HIGH - Heart Condition / Stroke Risk",
        "Furosemide": "HIGH - Heart Failure / Edema",
        "Albuterol": "MED - Asthma",
        "Amoxicillin": "LOW - Infection (Temporary)",
        "Ibuprofen": "LOW - Pain Management"
    }
    
    high_risk_count = 0
    med_risk_count = 0
    
    for med in medication_list:
        found = False
        med_lower = med.lower()
        for key, value in RISK_MAP.items():
            if key.lower() in med_lower:
                risk_level = value.split(" - ")[0]
                if risk_level == "HIGH": high_risk_count += 1
                if risk_level == "MED": med_risk_count += 1
                analysis.append(f"{med}: {value}")
                found = True
                break
        if not found:
            analysis.append(f"{med}: UNKNOWN - Requires Manual Review")
            med_risk_count += 1
            
    if high_risk_count > 0:
        overall_risk = "HIGH"
    elif med_risk_count >= 2:
        overall_risk = "MODERATE"
        
    return {
        "analysis_details": analysis,
        "overall_risk_assessment": overall_risk,
        "recommendation": "DECLINE" if overall_risk == "HIGH" else "REFER" if overall_risk == "MODERATE" else "APPROVE"
    }



# --- POLICY ISSUANCE AGENT TOOLS ---

class PolicyDocumentGeneratorInput(BaseModel):
    policy_holder_name: str = Field(description="Name of the policy holder")
    coverage_amount: float = Field(description="Coverage amount in dollars")
    monthly_premium: float = Field(description="Monthly premium amount")

@tool("policy_document_generator_tool", args_schema=PolicyDocumentGeneratorInput)
def policy_document_generator_tool(policy_holder_name: str, coverage_amount: float, monthly_premium: float) -> dict:
    """Generates policy document details including terms and conditions."""
    time.sleep(0.8)
    
    annual_premium = monthly_premium * 12
    term_years = 20
    
    document_details = {
        "policy_holder": policy_holder_name,
        "coverage": f"${coverage_amount:,.2f}",
        "monthly_premium": f"${monthly_premium:.2f}",
        "annual_premium": f"${annual_premium:.2f}",
        "term": f"{term_years} years",
        "benefits": [
            f"Death benefit of ${coverage_amount:,.2f} to named beneficiaries",
            "Guaranteed renewable for term duration",
            "30-day grace period for premium payments",
            "Cash value accumulation (if whole life)",
            "Accelerated death benefit rider available"
        ],
        "terms": [
            "Premiums must be paid monthly to maintain coverage",
            "Policy becomes effective upon first premium payment",
            "Beneficiaries must be designated and kept up-to-date",
            "Claims must be submitted within 180 days",
            "Suicide exclusion applies for first 2 years"
        ]
    }
    
    return document_details

class PolicyValidationInput(BaseModel):
    policy_holder_name: str = Field(description="Name to validate")
    coverage_amount: float = Field(description="Coverage amount to validate")
    monthly_premium: float = Field(description="Premium to validate")

@tool("policy_validation_tool", args_schema=PolicyValidationInput)
def policy_validation_tool(policy_holder_name: str, coverage_amount: float, monthly_premium: float) -> dict:
    """Validates policy details to ensure they meet company standards and regulations."""
    time.sleep(0.5)
    
    validation_results = {
        "name_valid": len(policy_holder_name) > 0,
        "coverage_valid": 50000 <= coverage_amount <= 5000000,
        "premium_valid": monthly_premium > 0,
        "overall_valid": True
    }
    
    # Check all validations
    validation_results["overall_valid"] = all([
        validation_results["name_valid"],
        validation_results["coverage_valid"],
        validation_results["premium_valid"]
    ])
    
    if validation_results["overall_valid"]:
        validation_results["message"] = "Policy details validated successfully. Ready for issuance."
    else:
        validation_results["message"] = "Validation failed. Please review policy details."
    
    return validation_results


# --- EVIDENCE COLLECTION AGENT TOOLS ---

class APSRequestInput(BaseModel):
    applicant_name: str = Field(description="Name of applicant")
    health_condition: str = Field(description="Reported health condition requiring APS")

@tool("aps_request_tool", args_schema=APSRequestInput)
def aps_request_tool(applicant_name: str, health_condition: str) -> dict:
    """Requests Attending Physician Statement (APS) from healthcare provider for medical underwriting."""
    time.sleep(2.0)  # Simulate request processing
    
    return {
        "request_status": "SENT",
        "provider": "Primary Care Physician",
        "condition": health_condition,
        "estimated_response_time": "3-5 business days (Demo: instant)",
        "request_id": f"APS-{random.randint(10000, 99999)}",
        "message": f"APS request sent for {applicant_name} regarding {health_condition}"
    }


class MedicalRecordsInput(BaseModel):
    applicant_name: str = Field(description="Name of applicant")
    record_type: str = Field(description="Type of medical records needed")

@tool("medical_records_tool", args_schema=MedicalRecordsInput)
def medical_records_tool(applicant_name: str, record_type: str) -> dict:
    """Requests detailed medical records from healthcare facilities."""
    time.sleep(1.5)
    
    return {
        "request_status": "SUBMITTED",
        "facility": "Regional Medical Center",
        "record_type": record_type,
        "estimated_response_time": "5-7 business days (Demo: instant)",
        "request_id": f"MR-{random.randint(10000, 99999)}",
        "message": f"Medical records request submitted for {applicant_name}"
    }


# --- MANUAL UNDERWRITING AGENT TOOLS ---

class EvidenceAnalysisInput(BaseModel):
    evidence_text: str = Field(description="Medical evidence text to analyze")
    focus_area: str = Field(description="Specific area to focus on (e.g., 'blood pressure', 'medications')")

@tool("evidence_analysis_tool", args_schema=EvidenceAnalysisInput)
def evidence_analysis_tool(evidence_text: str, focus_area: str = "general") -> dict:
    """Analyzes medical evidence and extracts key risk factors and clinical findings."""
    time.sleep(1.0)
    
    # Extract key terms
    key_findings = []
    evidence_lower = evidence_text.lower()
    
    if "controlled" in evidence_lower or "stable" in evidence_lower:
        key_findings.append("Condition is well-controlled")
    
    if "medication" in evidence_lower:
        key_findings.append("Currently on medication regimen")
    
    if "compliant" in evidence_lower:
        key_findings.append("Patient compliant with treatment")
    
    if "non-smoker" in evidence_lower or "non smoker" in evidence_lower:
        key_findings.append("Non-smoker status confirmed")
    
    if "hospitalization" in evidence_lower:
        key_findings.append("⚠️ Hospitalization history noted")
    
    # Determine severity
    severity = "MILD"
    if "moderate" in evidence_lower:
        severity = "MODERATE"
    elif "severe" in evidence_lower or "critical" in evidence_lower:
        severity = "SEVERE"
    
    return {
        "key_findings": key_findings,
        "severity": severity,
        "evidence_quality": "GOOD",
        "summary": f"Analyzed evidence with focus on {focus_area}. Found {len(key_findings)} key factors.",
        "requires_specialist_review": severity == "SEVERE"
    }


class RiskAssessmentInput(BaseModel):
    age: int = Field(description="Applicant age")
    health_findings: str = Field(description="Summary of health findings")
    coverage_amount: float = Field(description="Requested coverage amount")

@tool("risk_assessment_tool", args_schema=RiskAssessmentInput)
def risk_assessment_tool(age: int, health_findings: str, coverage_amount: float) -> dict:
    """Calculates comprehensive risk rating based on age, health, and coverage amount."""
    time.sleep(0.8)
    
    # Calculate risk score (0-100)
    risk_score = 50  # Base score
    
    # Age adjustments
    if age < 30:
        risk_score -= 10
    elif age > 55:
        risk_score += 15
    elif age > 65:
        risk_score += 25
    
    # Health findings adjustments
    findings_lower = health_findings.lower()
    if "controlled" in findings_lower or "stable" in findings_lower:
        risk_score -= 5
    if "severe" in findings_lower or "critical" in findings_lower:
        risk_score += 20
    if "compliant" in findings_lower:
        risk_score -= 3
    if "hospitalization" in findings_lower:
        risk_score += 10
    
    # Coverage amount adjustments
    if coverage_amount > 1000000:
        risk_score += 5
    if coverage_amount > 2000000:
        risk_score += 10
    
    # Determine rating
    if risk_score < 40:
        rating = "PREFERRED"
        table_rating = "Preferred rates available"
    elif risk_score < 60:
        rating = "STANDARD"
        table_rating = "Standard rates apply"
    elif risk_score < 75:
        rating = "SUBSTANDARD"
        table_rating = "Table B (+50% premium)"
    else:
        rating = "HIGH_RISK"
        table_rating = "Table D (+100% premium) or decline"
    
    return {
        "risk_score": risk_score,
        "risk_rating": rating,
        "table_rating": table_rating,
        "mortality_adjustment": f"{max(0, risk_score - 50)}% above standard",
        "recommendation": "APPROVE" if risk_score < 75 else "CONDITIONAL" if risk_score < 85 else "DECLINE",
        "confidence": "HIGH" if abs(risk_score - 50) > 15 else "MODERATE"
    }

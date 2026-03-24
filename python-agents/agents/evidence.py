import time
from datetime import datetime

def run_evidence_agent(input_data):
    """
    Evidence Collection Agent
    Requests and simulates receipt of medical evidence (APS, Medical Records)
    """
    app_number = input_data.get('applicationNumber')
    applicant_name = input_data.get('applicantName')
    evidence_type = input_data.get('evidenceType', 'APS')
    health_status = input_data.get('healthStatus', '')
    age = input_data.get('age', 0)
    
    trace = []
    
    trace.append(f"📋 Evidence Agent: Initiating evidence collection for {app_number}")
    trace.append(f"📋 Applicant: {applicant_name}")
    trace.append(f"📋 Evidence Type Required: {evidence_type}")
    print(trace[-1])
    
    # --- NEW AGENTIC LOGIC (Azure OpenAI + Tools) ---
    try:
        from llm_service import get_llm
        from agent_tools import aps_request_tool, medical_records_tool
        from callbacks import AgentTraceCallbackHandler
        from langchain.agents import create_openai_tools_agent, AgentExecutor
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        trace_handler = AgentTraceCallbackHandler()
        llm = get_llm()
        
        if llm:
            trace_handler.trace.append("📋 Evidence Agent (Azure OpenAI): Initializing Evidence Collection...")
            
            # Define Tools
            tools = [aps_request_tool, medical_records_tool]
            
            # Define Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an Evidence Collection Specialist for life insurance underwriting. "
                           "Your job is to request and collect medical evidence from healthcare providers. "
                           "Use 'aps_request_tool' to request Attending Physician Statement when medical conditions are present. "
                           "Use 'medical_records_tool' to request detailed medical records if needed. "
                           "Provide a summary of evidence collection status."),
                ("user", "Application {app_num}: Collect evidence for {name}. "
                         "Age: {age}, Health Status: {health}, Evidence Type: {ev_type}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create Agent
            agent = create_openai_tools_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Execute Agent
            agent_result = agent_executor.invoke(
                {
                    "app_num": app_number,
                    "name": applicant_name,
                    "age": age,
                    "health": health_status,
                    "ev_type": evidence_type
                },
                config={"callbacks": [trace_handler]}
            )
            
            trace_handler.trace.append(f"📋 Evidence Agent: Collection Complete")
            
            # Simulate evidence received
            evidence_data = generate_mock_evidence(evidence_type, applicant_name, health_status, age)
            
            return {
                "applicationNumber": app_number,
                "evidenceRequested": True,
                "evidenceReceived": True,
                "evidenceType": evidence_type,
                "evidenceData": evidence_data,
                "collectionDate": datetime.now().isoformat(),
                "agentStatus": "Evidence Collection Complete",
                "agentTrace": trace_handler.get_trace()
            }
            
    except Exception as e:
        import traceback
        error_msg = f"Evidence Agent Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        trace.append(f"⚠️ Evidence Agent: Using fallback collection process")
    
    # --- FALLBACK LOGIC ---
    trace.append(f"📋 Sending {evidence_type} request to healthcare provider...")
    trace.append(f"⏳ Waiting for provider response (Demo: 5 second simulation)...")
    
    # Simulate 5-second wait for evidence collection
    time.sleep(5)
    
    trace.append(f"✅ {evidence_type} Received from provider")
    
    # Generate mock evidence data
    evidence_data = generate_mock_evidence(evidence_type, applicant_name, health_status, age)
    
    trace.append(f"📄 Evidence Summary: {len(evidence_data)} characters of medical data received")
    trace.append(f"📋 Evidence Agent: Ready for Manual Underwriting Review")
    
    return {
        "applicationNumber": app_number,
        "evidenceRequested": True,
        "evidenceReceived": True,
        "evidenceType": evidence_type,
        "evidenceData": evidence_data,
        "collectionDate": datetime.now().isoformat(),
        "agentStatus": "Evidence Collection Agent Complete",
        "agentTrace": trace
    }


def generate_mock_evidence(evidence_type, name, health_status, age):
    """Generate realistic mock medical evidence"""
    
    if evidence_type == "APS":
        return f"""
ATTENDING PHYSICIAN STATEMENT (APS)
======================================

Patient Name: {name}
Date of Birth: {datetime.now().year - age}/03/15
Date of Examination: {datetime.now().strftime('%Y-%m-%d')}

MEDICAL HISTORY:
- Primary Diagnosis: {health_status}
- Current Medications: Lisinopril 10mg daily (if Hypertension)
- Last Visit: {datetime.now().strftime('%Y-%m-%d')}
- Blood Pressure: 138/88 mmHg (controlled with medication)
- BMI: 27.3 (slightly overweight)
- Smoking Status: Non-smoker
- Alcohol Use: Occasional, social

PHYSICIAN NOTES:
Patient has been under my care for the past 3 years. Current condition is well-managed 
with medication. Patient is compliant with treatment plan and maintains regular follow-up 
appointments. No hospitalizations in the past 5 years. Overall prognosis is good with 
continued medication adherence.

Risk Assessment: MODERATE - Condition is controlled and stable

Physician Signature: Dr. James Mitchell, MD
License #: MED-{age}789
Date: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    elif evidence_type == "Financial Review":
        return f"""
FINANCIAL UNDERWRITING REVIEW
======================================

Applicant Name: {name}
Age: {age}
Review Date: {datetime.now().strftime('%Y-%m-%d')}

FINANCIAL JUSTIFICATION:
- Annual Income: $250,000 (estimated)
- Net Worth: $1.2M (estimated)
- Existing Coverage: $500,000
- Requested Coverage: Large amount requiring verification

UNDERWRITING NOTES:
High coverage amount requires additional financial documentation to establish 
insurable interest. Applicant's financial profile suggests ability to maintain 
premium payments. Recommend approval pending income verification.

Risk Assessment: STANDARD - Financial capacity appears adequate

Analyst: Financial UW Team
Date: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    else:
        return f"Medical evidence for {name} collected on {datetime.now().strftime('%Y-%m-%d')}"

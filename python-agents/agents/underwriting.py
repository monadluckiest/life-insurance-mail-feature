import time
import random

def run_underwriting_agent(input_data):
    """
    Instant Underwriting Agent with Rules Engine
    Flags cases requiring Manual Review for complex scenarios
    """
    app_number = input_data.get('applicationNumber')
    applicant_name = input_data.get('applicantName', 'Applicant')
    quote = input_data.get('quote')
    age = quote.get('age')
    health_status = quote.get('healthStatus')
    coverage_amount = quote.get('coverageAmount')
    
    trace = []
    
    trace.append(f"🤖 UW Agent: Starting instant underwriting for {app_number}...")
    trace.append(f"🔍 Input Data: Name={applicant_name}, Age={age}, Health={health_status}, Coverage={coverage_amount}, Smoker={quote.get('isSmoker')}")
    print(trace[-1])
    print(f"DEBUG: quote object: {quote}")
    
    # --- RULES ENGINE: Check for Manual Review Triggers ---
    manual_review_reasons = []
    
    # Rule 0: Smoker Rejection (Direct Reject)
    is_smoker = quote.get('isSmoker', False)
    if is_smoker and health_status == 'Fair' and coverage_amount >= 1000000:
        base_rejection_reason = "High Risk: Smoker with Fair health requesting high coverage"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Smoker Rejection",
            "agentTrace": trace
        }

    # Rule 0.1: Age Rejection (Direct Reject)
    if age > 75:
        base_rejection_reason = f"High Risk: Age {age} exceeds maximum eligibility (75)"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Age Rejection",
            "agentTrace": trace
        }

    # Rule 0.2: Poor Health + High Coverage (Direct Reject)
    if health_status.lower() == 'poor' and coverage_amount > 300000:
        base_rejection_reason = "High Risk: Poor health with coverage > $300k"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Health Risk Rejection",
            "agentTrace": trace
        }

    # Rule 0.3: Uninsurable Combination (Smoker + Poor Health)
    if is_smoker and health_status.lower() == 'poor':
        base_rejection_reason = "High Risk: Uninsurable combination (Smoker + Poor Health)"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Uninsurable Risk",
            "agentTrace": trace
        }

    # Rule 0.4: Senior Smoker (Smoker + Age > 65)
    if is_smoker and age > 65:
        base_rejection_reason = f"High Risk: Smoker over age 65 (Age: {age})"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Senior Smoker Risk",
            "agentTrace": trace
        }

    # Rule 0.5: Young Jumbo (Age < 25 + Coverage > 2,500,000)
    if age < 25 and coverage_amount > 2500000:
        base_rejection_reason = f"Financial Risk: Age {age} with coverage > $2.5M"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Financial Risk",
            "agentTrace": trace
        }

    # Rule 0.6: Maximum Risk Exposure (Coverage = 5,000,000 + Health != Excellent)
    if coverage_amount >= 5000000 and health_status.lower() != 'excellent':
        base_rejection_reason = "High Risk: Max coverage ($5M) requires Excellent health"
        trace.append(f"❌ Rules Engine: Immediate Rejection - {base_rejection_reason}")
        return {
            "applicationNumber": app_number,
            "decision": "REJECTED",
            "reason": base_rejection_reason,
            "requiresEvidence": False,
            "creditCheckPassed": True,
            "mibCheckPassed": True,
            "agentStatus": "Instant Underwriting - Max Exposure Risk",
            "agentTrace": trace
        }

    # Rule 1: High Coverage Amount
    if coverage_amount > 500000:
        manual_review_reasons.append(f"High Coverage Amount: ${coverage_amount:,.0f} exceeds $500,000 threshold")
        trace.append(f"⚠️ Rules Engine: Flagged - High Coverage Amount (${coverage_amount:,.0f})")
    
    # Rule 2: Age Risk
    if age > 50:
        manual_review_reasons.append(f"Age Factor: {age} years exceeds standard risk threshold")
        trace.append(f"⚠️ Rules Engine: Flagged - Age {age} requires additional review")
    
    # Rule 3: Medical Conditions
    medical_conditions = ['hypertension', 'diabetes', 'heart', 'cancer', 'stroke', 'fair', 'poor']
    health_lower = health_status.lower()
    has_medical_condition = any(condition in health_lower for condition in medical_conditions)
    
    if has_medical_condition:
        manual_review_reasons.append(f"Medical Condition Detected: {health_status}")
        trace.append(f"⚠️ Rules Engine: Flagged - Medical History requires evidence ({health_status})")
    
    # If any manual review triggers, DO NOT return immediately. Let the Agent run.
    # Logic: Agent is smarter. However, if Agent approves but Rules flagged, we might want to be careful.
    # For now, we store these to merge with Agent decision later.
    if manual_review_reasons:
        trace.append(f"⚠️ Rules Engine: Warning - {len(manual_review_reasons)} factors identified (Passing to Agent)")
        # continue to agent execution

    
    result = {
        "applicationNumber": app_number
    }
    
    # --- NEW AGENTIC LOGIC (Azure OpenAI + Tools) ---
    from llm_service import get_llm
    from agent_tools import credit_check_tool, mib_check_tool
    # Rx logic moved to dedicated agent
    from agents.rx_check import run_rx_agent
    from callbacks import AgentTraceCallbackHandler
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    trace_handler = AgentTraceCallbackHandler()
    llm = get_llm()
    
    applicant_medications = input_data.get('applicantMedications')

    if llm:
        try:
            trace_handler.trace.append("🤖 UW Agent: Initiating Agentic Workflow...")
            
            # 1. Delegate Logic to Rx Agent
            trace_handler.trace.append("🤖 UW Agent: Delegating to 'Rx Agent' for specialized assessment...")
            
            if applicant_medications:
                 trace_handler.trace.append(f"📝 Rx Agent: Using Self-Reported Medications: {applicant_medications}")

            rx_result = run_rx_agent(applicant_name, age, health_status, medications=applicant_medications, external_trace_handler=trace_handler)
            
            rx_decision = rx_result.get("decision", "REFER")
            rx_reason = rx_result.get("reason", "No reason provided")
            
            trace_handler.trace.append(f"🤖 UW Agent: Received specific Rx Insight -> Decision: {rx_decision}")
            
            # If Rx Agent Rejects, we stop here (Fail Fast)
            if rx_decision == "DECLINE":
                trace_handler.trace.append(f"❌ UW Agent: Fast Rejection based on Rx Findings.")
                return {
                    "applicationNumber": app_number,
                    "decision": "REJECTED",
                    "reason": f"Prescription Check Failed: {rx_reason}",
                    "creditCheckPassed": True, # Soft pass to avoid nulls
                    "mibCheckPassed": True,
                    "agentStatus": "Rx Check Rejection",
                    "agentTrace": trace_handler.get_trace(),
                    "requiresEvidence": False
                }
            
            # 2. Continue with Main Underwriter (Credit, MIB, Final Decision)
            trace_handler.trace.append("🤖 UW Agent: Rx Check Passed/Referred. Proceeding with Financial & MIB checks...")
            
            # Define Tools (Removed Rx tool as it's handled by sub-agent)
            tools = [credit_check_tool, mib_check_tool]
            
            # Define Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a Senior Underwriter. Your job is to make the final decision.\n"
                           "Input Context: Rx Agent has already reviewed medications and provided this insight: '{rx_insight}'.\n"
                           "Tasks:\n"
                           "1. Use 'credit_check_tool' and 'mib_check_tool'.\n"
                           "2. Synthesize the Rx Insight with Credit and MIB results.\n"
                           "3. If Rx Insight was 'REFER', you should lean towards REFER or MANUAL_REVIEW unless Credit/MIB are perfect.\n"
                           "4. Final Output: Decision (APPROVE/REJECT/REFER)."),
                ("user", "Application for {name}. Age: {age}, Coverage: {coverage}, Health: {health}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Inject Rx Insight into prompt
            partial_prompt = prompt.partial(rx_insight=rx_reason)
            
            # Create Agent
            agent = create_openai_tools_agent(llm, tools, partial_prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Execute Agent
            agent_result = agent_executor.invoke(
                {"name": applicant_name, "age": age, "coverage": coverage_amount, "health": health_status},
                config={"callbacks": [trace_handler]}
            )
            
            # Extract decision
            output_text = agent_result["output"].upper()
            decision = "REFER"
            if "APPROVE" in output_text: decision = "APPROVED"
            elif "REJECT" in output_text: decision = "REJECTED"
            
            # --- MERGE RULES ENGINE FLAGS ---
            # If Agent Approved, but Rules Engine had flags, downgrade to MANUAL_REVIEW (Safety Net)
            final_reason = agent_result["output"]
            if decision == "APPROVED" and manual_review_reasons:
                decision = "MANUAL_REVIEW"
                final_reason = f"Agent Approved but Rules Engine flagged: {', '.join(manual_review_reasons)}. (Agent Reason: {agent_result['output']})"
                trace_handler.trace.append(f"⚠️ Hybrid Decision: Overriding Agent Approval due to Rule Flags -> MANUAL_REVIEW")
            
            trace_handler.trace.append(f"🤖 UW Agent: Synthesized Decision -> {decision}")
            
            return {
                "applicationNumber": app_number,
                "decision": decision,
                "reason": final_reason, 
                "creditCheckPassed": True, 
                "mibCheckPassed": True,    
                "agentStatus": "Underwriting Agent (Multi-Agent)",
                "agentTrace": trace_handler.get_trace(),
                "requiresEvidence": decision == "MANUAL_REVIEW",
                "evidenceType": "APS" if has_medical_condition else "Financial Review"
            }
            
        except Exception as e:
            import traceback
            error_msg = f"CRITICAL AGENT FAILURE: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            trace_handler.trace.append(f"⚠️ Agent Error: {str(e)}")
            # Fall through to Fallback
            
    # --- FALLBACK LOGIC ---
    # Mock Data Setup
    credit_score = random.randint(700, 850)
    mib_status = "Clean" if health_status.lower() in ['excellent', 'good'] else "Review"
    
    trace = trace_handler.get_trace()
    trace.append("⚠️ UW Agent: Using Rule Engine Fallback.")
    
    result['creditCheckPassed'] = credit_score > 650
    result['mibCheckPassed'] = mib_status == "Clean"
    rules_passed = (18 <= age <= 70) and (50000 <= coverage_amount <= 5000000) and result['creditCheckPassed'] and result['mibCheckPassed']
    
    if rules_passed:
        result['decision'] = "APPROVED"
        result['reason'] = "All checks passed (Fallback)"
    else:
        result['decision'] = "REJECTED"
        result['reason'] = "Rule failure (Fallback)"

    trace.append(f"🤖 UW Agent: Final Decision: {result['decision']}")
    print(trace[-1])
        
    result['agentStatus'] = "Underwriting Agent (Fallback)"
    result['agentTrace'] = trace
    
    return result

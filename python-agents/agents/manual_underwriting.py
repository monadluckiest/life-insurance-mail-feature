import time

def run_manual_underwriting_agent(input_data):
    """
    Manual Underwriting Agent
    Analyzes medical evidence and provides risk assessment for human underwriter
    """
    app_number = input_data.get('applicationNumber')
    applicant_name = input_data.get('applicantName')
    evidence_data = input_data.get('evidenceData', '')
    age = input_data.get('age', 0)
    coverage_amount = input_data.get('coverageAmount', 0)
    health_status = input_data.get('healthStatus', '')
    
    trace = []
    
    trace.append(f"🩺 Manual UW Agent: Analyzing evidence for {app_number}")
    trace.append(f"🩺 Applicant: {applicant_name}, Age: {age}")
    print(trace[-1])
    
    # --- NEW AGENTIC LOGIC (Azure OpenAI + Tools) ---
    try:
        from llm_service import get_llm
        from agent_tools import evidence_analysis_tool, risk_assessment_tool
        from callbacks import AgentTraceCallbackHandler
        from langchain.agents import create_openai_tools_agent, AgentExecutor
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        trace_handler = AgentTraceCallbackHandler()
        llm = get_llm()
        
        if llm:
            trace_handler.trace.append("🩺 Manual UW Agent (Azure OpenAI): Initializing Evidence Analysis...")
            
            # Define Tools
            tools = [evidence_analysis_tool, risk_assessment_tool]
            
            # Define Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a Senior Manual Underwriter reviewing complex life insurance applications. "
                           "Your job is to analyze medical evidence and provide a detailed risk assessment. "
                           "Use 'evidence_analysis_tool' to extract key findings from medical documents. "
                           "Use 'risk_assessment_tool' to calculate risk ratings based on evidence. "
                           "Provide a clear recommendation (APPROVE with conditions, APPROVE standard, or REJECT) "
                           "with detailed justification for the human underwriter to review."),
                ("user", "Application {app_num}: Review evidence for {name}, Age {age}, "
                         "Coverage ${coverage:,.0f}, Health: {health}.\n\nEvidence:\n{evidence}"),
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
                    "coverage": coverage_amount,
                    "health": health_status,
                    "evidence": evidence_data[:500]  # Truncate for LLM
                },
                config={"callbacks": [trace_handler]}
            )
            
            # Parse recommendation
            output_text = agent_result["output"]
            recommendation = extract_recommendation(output_text)
            
            trace_handler.trace.append(f"🩺 Manual UW Agent: Analysis Complete")
            trace_handler.trace.append(f"📊 Recommendation: {recommendation['decision']}")
            
            return {
                "applicationNumber": app_number,
                "recommendation": recommendation['decision'],
                "riskRating": recommendation['risk_rating'],
                "underwriterSummary": output_text,
                "keyFindings": recommendation['key_findings'],
                "conditions": recommendation['conditions'],
                "agentStatus": "Manual Underwriting Analysis Complete",
                "agentTrace": trace_handler.get_trace()
            }
            
    except Exception as e:
        import traceback
        error_msg = f"Manual UW Agent Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        trace.append(f"⚠️ Manual UW Agent: Using fallback analysis")
    
    # --- FALLBACK LOGIC ---
    trace.append(f"🩺 Analyzing medical evidence...")
    time.sleep(2)  # Simulate analysis time
    
    trace.append(f"📊 Extracting key risk factors from APS...")
    
    # Parse evidence for key terms
    key_findings = []
    risk_rating = "STANDARD"
    
    if "controlled" in evidence_data.lower() or "stable" in evidence_data.lower():
        key_findings.append("✅ Condition is well-controlled with medication")
        risk_rating = "STANDARD"
    
    if "compliant" in evidence_data.lower():
        key_findings.append("✅ Patient compliant with treatment plan")
    
    if "non-smoker" in evidence_data.lower():
        key_findings.append("✅ Non-smoker status")
    
    if "moderate" in evidence_data.lower():
        risk_rating = "MODERATE"
        key_findings.append("⚠️ Moderate risk assessment from physician")
    
    if age > 55:
        key_findings.append("⚠️ Age factor: Additional mortality risk")
    
    if coverage_amount > 1000000:
        key_findings.append("ℹ️ High coverage amount: $" + f"{coverage_amount:,.0f}")
    
    trace.append(f"📋 Identified {len(key_findings)} key findings")
    trace.append(f"📊 Risk Rating: {risk_rating}")
    
    # Generate recommendation
    recommendation = "APPROVE_WITH_CONDITIONS"
    conditions = []
    
    if risk_rating == "MODERATE":
        conditions.append("Table Rating: +50% premium increase recommended")
        conditions.append("Annual health review required")
        recommendation = "APPROVE_WITH_CONDITIONS"
        trace.append(f"💡 Recommendation: Approve with Modified Terms")
    else:
        recommendation = "APPROVE_STANDARD"
        trace.append(f"💡 Recommendation: Approve at Standard Rates")
    
    # Create summary for human underwriter
    underwriter_summary = f"""
MANUAL UNDERWRITING SUMMARY
{'='*50}

Applicant: {applicant_name}
Age: {age} | Coverage: ${coverage_amount:,.0f}
Health Status: {health_status}

KEY FINDINGS:
{chr(10).join('  ' + finding for finding in key_findings)}

RISK ASSESSMENT:
Risk Rating: {risk_rating}
The medical evidence shows a {risk_rating.lower()} risk profile. 
{'The condition appears well-managed with medication and regular monitoring.' if 'controlled' in evidence_data.lower() else 'Additional risk factors identified requiring modified terms.'}

RECOMMENDATION FOR UNDERWRITER:
{recommendation.replace('_', ' ')}
{'Premium adjustment recommended based on risk factors.' if conditions else 'Standard rates approved based on evidence review.'}

{'CONDITIONS:' if conditions else ''}
{chr(10).join('  • ' + cond for cond in conditions)}

This case is ready for final human underwriter approval.
"""
    
    trace.append(f"📝 Generated detailed summary for human underwriter review")
    trace.append(f"🩺 Manual UW Agent: Analysis complete - Ready for human decision")
    
    return {
        "applicationNumber": app_number,
        "recommendation": recommendation,
        "riskRating": risk_rating,
        "underwriterSummary": underwriter_summary,
        "keyFindings": key_findings,
        "conditions": conditions if conditions else None,
        "agentStatus": "Manual Underwriting Agent Complete - Awaiting Human Approval",
        "agentTrace": trace
    }


def extract_recommendation(output_text):
    """Extract structured recommendation from LLM output"""
    output_upper = output_text.upper()
    
    decision = "APPROVE_STANDARD"
    if "REJECT" in output_upper:
        decision = "REJECT"
    elif "CONDITION" in output_upper or "TABLE" in output_upper or "MODIFIED" in output_upper:
        decision = "APPROVE_WITH_CONDITIONS"
    elif "APPROVE" in output_upper:
        decision = "APPROVE_STANDARD"
    
    risk_rating = "STANDARD"
    if "HIGH RISK" in output_upper:
        risk_rating = "HIGH"
    elif "MODERATE" in output_upper:
        risk_rating = "MODERATE"
    elif "SUBSTANDARD" in output_upper:
        risk_rating = "SUBSTANDARD"
    
    return {
        "decision": decision,
        "risk_rating": risk_rating,
        "key_findings": ["AI-generated findings based on evidence"],
        "conditions": ["Premium adjustment may apply"] if "CONDITION" in output_upper else []
    }

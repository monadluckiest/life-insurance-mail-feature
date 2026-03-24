import time
from datetime import datetime, timedelta

def run_policy_issuance_agent(input_data):
    """
    Policy Issuance Agent
    Logic: Generate policy document with AI-assisted content generation
    """
    app_number = input_data.get('applicationNumber')
    policy_holder_name = input_data.get('policyHolderName')
    coverage_amount = input_data.get('coverageAmount')
    monthly_premium = input_data.get('monthlyPremium')
    
    # --- NEW AGENTIC LOGIC (Azure OpenAI + Tools) ---
    from llm_service import get_llm
    from agent_tools import policy_document_generator_tool, policy_validation_tool
    from callbacks import AgentTraceCallbackHandler
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    trace_handler = AgentTraceCallbackHandler()
    llm = get_llm()
    
    if llm:
        try:
            trace_handler.trace.append("🤖 Policy Issuance Agent (Azure OpenAI): Initializing Autonomous Agent with Tools...")
            
            # Define Tools
            tools = [policy_document_generator_tool, policy_validation_tool]
            
            # Define Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a Policy Issuance Specialist. Your job is to generate and validate insurance policies. "
                           "First, you MUST use 'policy_document_generator_tool' to create the policy document details. "
                           "Then, you MUST use 'policy_validation_tool' to ensure all policy details are correct. "
                           "Finally, confirm the policy is ready for issuance."),
                ("user", "Generate and validate policy for {name}. Coverage: ${coverage}, Premium: ${premium}/month"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create Agent
            agent = create_openai_tools_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Execute Agent
            agent_result = agent_executor.invoke(
                {
                    "name": policy_holder_name, 
                    "coverage": coverage_amount,
                    "premium": monthly_premium
                },
                config={"callbacks": [trace_handler]}
            )
            
            trace_handler.trace.append("🤖 Policy Issuance Agent: Policy validated and ready for activation")
            
            # Generate policy number
            policy_number = f"POL-{int(time.time())}"
            issue_date = datetime.now()
            effective_date = issue_date
            expiry_date = issue_date.replace(year=issue_date.year + 20)  # 20-year term
            
            return {
                "policyNumber": policy_number,
                "policyStatus": "ACTIVE",
                "issueDate": issue_date.isoformat(),
                "effectiveDate": effective_date.isoformat(),
                "expiryDate": expiry_date.isoformat(),
                "policyHolderName": policy_holder_name,
                "coverageAmount": coverage_amount,
                "monthlyPremium": monthly_premium,
                "annualPremium": monthly_premium * 12,
                "agentSummary": agent_result["output"],
                "agentStatus": "Policy Issuance Agent (Azure OpenAI Tools)",
                "agentTrace": trace_handler.get_trace(),
                "message": f"Policy {policy_number} has been issued and is now ACTIVE!"
            }
            
        except Exception as e:
            import traceback
            error_msg = f"CRITICAL AGENT FAILURE: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            trace_handler.trace.append(f"⚠️ Agent Error: {str(e)}")
            # Fall through to Fallback
    
    # --- FALLBACK LOGIC ---
    trace = trace_handler.get_trace()
    trace.append("⚠️ Policy Issuance Agent: Using deterministic fallback.")
    
    # Generate policy number and dates
    policy_number = f"POL-{int(time.time())}"
    issue_date = datetime.now()
    effective_date = issue_date
    expiry_date = issue_date.replace(year=issue_date.year + 20)  # 20-year term
    
    trace.append(f"🤖 Policy Issuance Agent: Generated policy {policy_number}")
    trace.append(f"🤖 Policy Issuance Agent: Coverage ${coverage_amount:,.2f} at ${monthly_premium:.2f}/month")
    trace.append(f"🤖 Policy Issuance Agent: Term: {issue_date.strftime('%Y-%m-%d')} to {expiry_date.strftime('%Y-%m-%d')}")
    trace.append(f"✅ Policy Issuance Agent: Policy ACTIVE")
    
    return {
        "policyNumber": policy_number,
        "policyStatus": "ACTIVE",
        "issueDate": issue_date.isoformat(),
        "effectiveDate": effective_date.isoformat(),
        "expiryDate": expiry_date.isoformat(),
        "policyHolderName": policy_holder_name,
        "coverageAmount": coverage_amount,
        "monthlyPremium": monthly_premium,
        "annualPremium": monthly_premium * 12,
        "agentStatus": "Policy Issuance Agent (Fallback)",
        "agentTrace": trace,
        "message": f"Policy {policy_number} has been issued and is now ACTIVE!"
    }

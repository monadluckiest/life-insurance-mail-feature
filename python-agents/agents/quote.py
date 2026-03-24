import time

def run_quote_agent(input_data):
    """
    Quote Generation Agent
    Logic: Base Rate * Age Factor * Amount
    """
    age = input_data.get('age')
    coverage_amount = input_data.get('coverageAmount')
    coverage_amount = input_data.get('coverageAmount')
    health_status = input_data.get('healthStatus')
    is_smoker = input_data.get('isSmoker', False)
    
    # --- IMMEDIATE REJECTION LOGIC ---
    rejection_reason = None
    
    # Rule 0: Smoker Rejection (Direct Reject)
    if is_smoker and health_status == 'Fair' and coverage_amount >= 1000000:
        rejection_reason = "High Risk: Smoker with Fair health requesting high coverage"

    # Rule 0.1: Age Rejection (Direct Reject)
    elif age > 75:
        rejection_reason = f"High Risk: Age {age} exceeds maximum eligibility (75)"

    # Rule 0.2: Poor Health + High Coverage (Direct Reject)
    elif health_status and health_status.lower() == 'poor' and coverage_amount > 300000:
        rejection_reason = "High Risk: Poor health with coverage > $300k"
        
    # Rule 0.3: Uninsurable Combination (Smoker + Poor Health)
    elif is_smoker and health_status and health_status.lower() == 'poor':
        rejection_reason = "High Risk: Uninsurable combination (Smoker + Poor Health)"

    # Rule 0.4: Senior Smoker (Smoker + Age > 65)
    elif is_smoker and age > 65:
        rejection_reason = f"High Risk: Smoker over age 65 (Age: {age})"

    # Rule 0.5: Young Jumbo (Age < 25 + Coverage > 2,500,000)
    elif age < 25 and coverage_amount > 2500000:
        rejection_reason = f"Financial Risk: Age {age} with coverage > $2.5M"

    # Rule 0.6: Maximum Risk Exposure (Coverage = 5,000,000 + Health != Excellent)
    elif coverage_amount >= 5000000 and health_status and health_status.lower() != 'excellent':
        rejection_reason = "High Risk: Max coverage ($5M) requires Excellent health"

    if rejection_reason:
        return {
            "monthlyPremium": 0,
            "annualPremium": 0,
            "coverageAmount": coverage_amount,
            "age": age,
            "healthStatus": health_status,
            "isSmoker": is_smoker,
            "isEligible": False,
            "rejectionReason": rejection_reason,
            "agentStatus": "Quote Agent (Rejected)",
            "agentTrace": [f"❌ Quote Rejected: {rejection_reason}"]
        }

    # --- NEW AGENTIC LOGIC (Azure OpenAI + Tools) ---
    from llm_service import get_llm
    from agent_tools import risk_analysis_tool, premium_calculator_tool
    from callbacks import AgentTraceCallbackHandler
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    trace_handler = AgentTraceCallbackHandler()
    llm = get_llm()
    
    if llm:
        try: 
            trace_handler.trace.append("🤖 Quote Agent (Azure OpenAI): Initializing Autonomous Agent with Tools...")
            
            # Define Tools
            tools = [risk_analysis_tool, premium_calculator_tool]
            
            # Define Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an intelligent Quote Agent. Your goal is to calculate the life insurance premium. "
                           "First, you MUST use 'risk_analysis_tool' to determine the risk factors. "
                           "Then, you MUST use 'premium_calculator_tool' to get the final price. "
                           "Finally, respond with the final monthly and annual premium amounts."),
                ("user", "Calculate premium for Age: {age}, Health: {health}, Coverage: {coverage}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create Agent
            agent = create_openai_tools_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Execute Agent
            result = agent_executor.invoke(
                {"age": age, "health": health_status, "coverage": coverage_amount},
                config={"callbacks": [trace_handler]}
            )
            
            trace_handler.trace.append("🤖 Quote Agent: Agent execution complete. Synthesizing response.")
            
            # Extract premium values from tool outputs in the trace
            monthly_premium = None
            annual_premium = None
            
            # Parse the trace to find the premium_calculator_tool output
            for i, trace_line in enumerate(trace_handler.trace):
                if "premium_calculator_tool" in trace_line:
                    # Look ahead for the Output line (usually 2 lines after the tool name)
                    for j in range(i + 1, min(i + 4, len(trace_handler.trace))):
                        if "Output:" in trace_handler.trace[j]:
                            try:
                                # Extract the dictionary from the output line
                                import ast
                                output_str = trace_handler.trace[j].replace("   Output: ", "").strip()
                                output_dict = ast.literal_eval(output_str)
                                if isinstance(output_dict, dict):
                                    monthly_premium = output_dict.get('monthly_premium')
                                    annual_premium = output_dict.get('annual_premium')
                                    print(f"✅ Extracted premiums from agent: Monthly=${monthly_premium}, Annual=${annual_premium}")
                                    break
                            except Exception as parse_error:
                                print(f"⚠️ Failed to parse tool output: {parse_error}")
                    if monthly_premium is not None:
                        break
            
            # If we couldn't extract from trace, use fallback calculation
            if monthly_premium is None or annual_premium is None:
                print("⚠️ Could not extract premium from agent output, using fallback calculation")
                base_rate = 0.0005
                age_factor = 2.0 if age >= 55 else (1.5 if age < 25 else 1.0) 
                if health_status.lower() == "excellent": 
                    health_factor = 0.8
                else: 
                    health_factor = 1.0
                
                monthly_premium = round(coverage_amount * base_rate * age_factor * health_factor, 2)
                annual_premium = monthly_premium * 12
            
            return {
                "monthlyPremium": monthly_premium,
                "annualPremium": annual_premium,
                "coverageAmount": coverage_amount,
                "age": age,
                "healthStatus": health_status,
                "isSmoker": is_smoker,
                "agentStatus": "Quote Agent (Azure OpenAI Tools)",
                "agentTrace": trace_handler.get_trace()
            }
            
        except Exception as e:
            import traceback
            error_msg = f"CRITICAL AGENT FAILURE: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            trace_handler.trace.append(f"⚠️ Agent Error: {str(e)}")
            # Fall through to fallback
    
    # --- FALLBACK LOGIC ---
    trace = trace_handler.get_trace()
    trace.append("⚠️ Quote Agent: Using deterministic fallback.")
    
    base_rate = 0.0005
    age_factor = 2.0 if age >= 55 else (1.5 if age < 25 else 1.0) 
    if health_status and health_status.lower() == "excellent": health_factor = 0.8
    else: health_factor = 1.0
    
    monthly_premium = round(coverage_amount * base_rate * age_factor * health_factor, 2)
    annual_premium = monthly_premium * 12
    
    trace.append(f"🤖 Quote Agent: Final Calculation: {monthly_premium}")
    
    return {
        "monthlyPremium": monthly_premium,
        "annualPremium": annual_premium,
        "coverageAmount": coverage_amount,
        "age": age,
        "age": age,
        "healthStatus": health_status,
        "isSmoker": is_smoker,
        "agentStatus": "Quote Agent (Fallback)",
        "agentTrace": trace
    }


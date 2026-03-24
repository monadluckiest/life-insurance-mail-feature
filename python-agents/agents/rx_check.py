
import time
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm_service import get_llm
from agent_tools import prescription_check_tool, medication_risk_analyzer_tool
from callbacks import AgentTraceCallbackHandler

def run_rx_agent(applicant_name: str, age: int, health_status: str, medications: str = None, external_trace_handler=None):
    """
    Dedicated Rx Check Agent.
    Responsibilities:
    1. Fetch Prescription History (PBM Check) OR Use Self-Reported Meds
    2. Analyze Medications for Risk
    3. Return structured Risk Assessment
    """
    
    # Use provided handler or create new one
    trace_handler = external_trace_handler if external_trace_handler else AgentTraceCallbackHandler()
    
    trace_handler.trace.append(f"🤖 Rx Agent: precise risk assessment for {applicant_name} (Age: {age})...")
    
    llm = get_llm()
    
    if not llm:
        return {"error": "LLM not available"}
        
    try:
        # Define Tools
        tools = [prescription_check_tool, medication_risk_analyzer_tool]
        
        # Logic Switch: If medications provided, we skip the fetch and directly analyze
        prompt_instruction = ""
        context_input = ""
        
        if medications and len(medications.strip()) > 0:
            med_list = [m.strip() for m in medications.split(',')]
            trace_handler.trace.append(f"💉 Rx Agent: Analyzing Self-Reported Medications: {med_list}")
            
            # --- DETERMINISTIC SAFETY CHECK ---
            # override LLM if High Risk Keywords are present
            meds_lower = medications.lower()
            critical_meds = ["insulin", "furosemide", "clopidogrel", "nitroglycerin"]
            for crit in critical_meds:
                if crit in meds_lower:
                    trace_handler.trace.append(f"⚠️ Rx Agent: CRITICAL MEDICATION DETECTED ({crit.upper()}) - FORCING DECLINE")
                    return {
                        "decision": "DECLINE",
                        "reason": f"Automatic Decline: Critical High-Risk Medication Detected ({crit})",
                        "agentTrace": trace_handler.get_trace()
                    }
            # ----------------------------------

            # Specialized Prompt for Analizying Known Meds
            prompt_instruction = (
                "You are an expert Medical Risk Underwriter. "
                "The applicant has self-reported the following medications: {med_list}. "
                "Protocol:\n"
                "1. You MUST call 'medication_risk_analyzer_tool' with this list to get the risk analysis.\n"
                "2. Based on the analysis, determine Risk Rating (LOW, MODERATE, HIGH).\n"
                "3. Return Decision (APPROVE/REFER/DECLINE).\n"
                "Output format: 'Risk Rating: [RATE]. Decision: [DECISION]. Reason: [SUMMARY]'"
            )
            context_input = f"Analyze these meds: {medications}"
            
        else:
            # Standard Flow: Fetch -> Analyze
            prompt_instruction = (
                "You are an expert Medical Risk Underwriter specializing in Pharmacology. "
                "Protocol:\n"
                "1. Call 'prescription_check_tool(applicant_name, health_status, age)' to get records.\n"
                "2. If records are found, call 'medication_risk_analyzer_tool(medication_list)' to extract risk details.\n"
                "3. Based on the analysis, provide a 'Risk Rating' (LOW, MODERATE, HIGH) and a 'Decision' (APPROVE, REFER, DECLINE).\n"
                "4. If no meds are found, Risk is LOW and Decision is APPROVE.\n"
                "Output format: 'Risk Rating: [RATE]. Decision: [DECISION]. Reason: [SUMMARY]'"
            )
            context_input = f"Assess Rx Risk for {applicant_name}, Age {age}, Reported Health: {health_status}"

        # Define Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_instruction),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        input_vars = {"input": context_input}
        if medications:
             input_vars["med_list"] = medications
        
        result = agent_executor.invoke(
            input_vars,
            config={"callbacks": [trace_handler]}
        )
        
        output = result['output']
        trace_handler.trace.append(f"🤖 Rx Agent: Assessment Complete -> {output}")
        
        # Parse simple output (heuristic)
        decision = "REFER"
        if "APPROVE" in output.upper(): decision = "APPROVE"
        elif "DECLINE" in output.upper() or "REJECT" in output.upper(): decision = "DECLINE"
        
        return {
            "decision": decision,
            "reason": output,
            "agentTrace": trace_handler.get_trace() # If we own the handler
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Rx Agent Failed: {str(e)}"
        print(f"{error_msg}\n{traceback.format_exc()}")
        trace_handler.trace.append(f"⚠️ Rx Agent Error: {str(e)}")
        return {"decision": "REFER", "reason": "Agent Error", "agentTrace": trace_handler.trace}

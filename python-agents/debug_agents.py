
import sys
import traceback

print("🔍 Debugging Python Environment...")

try:
    print("1️⃣ Testing Imports...")
    from llm_service import get_llm
    print("   ✅ llm_service imported")
    
    from callbacks import AgentTraceCallbackHandler
    print("   ✅ callbacks imported")
    
    from agent_tools import risk_analysis_tool, premium_calculator_tool
    print("   ✅ agent_tools imported")
    
    print("2️⃣ Testing Quote Agent Logic...")
    from agents.quote import run_quote_agent
    
    # Mock Request
    data = {
        "age": 30,
        "coverageAmount": 500000,
        "healthStatus": "Excellent"
    }
    
    print(f"   INVOKING run_quote_agent({data})...")
    result = run_quote_agent(data)
    print("   ✅ Result:", result)

except Exception as e:
    print("\n❌ CRITICAL FAILURE:")
    traceback.print_exc()

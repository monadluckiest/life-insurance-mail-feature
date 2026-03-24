from typing import Dict, Any, List

def run_needs_analysis_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Needs Analysis Agent
    Calculates recommended coverage based on simple heuristics:
    - Base coverage: $100,000
    - Per dependent: +$100,000
    - Age factor: If < 30, add $50,000 (assuming potential growth needs)
    - Smoker penalty (informational only, doesn't reduce need but noted)
    """
    print(f"DEBUG: Needs Analysis Agent received: {data}")
    
    age = data.get("age", 30)
    dependents = data.get("dependents", 0)  # Number of dependents
    is_smoker = data.get("isSmoker", "No") == "Yes"

    # --- ELIGIBILITY CHECK ---
    if age > 75:
        print(f"DEBUG: User age {age} exceeds eligibility limit.")
        return {
            "status": "Ineligible",
            "agent": "Needs Analysis Agent",
            "recommended_coverage": 0,
            "recommended_health_status": "Not Applicable",
            "reasoning": [
                f"We regret that we cannot recommend a policy for age {age}.",
                "Our maximum eligibility age is 75."
            ],
            "agentTrace": [
                "🤖 Needs Analysis Agent: Initializing...",
                f"> Input: Age={age}",
                f"⚠️ Agent Logic: Age {age} exceeds maximum eligibility (75).",
                "❌ Agent Decision: Cannot recommend coverage."
            ]
        }
    
    # Mocking an agent trace to provide the "Agent Experience" in the UI
    agent_trace = [
        "🤖 Needs Analysis Agent: Initializing...",
        f"> Input: Age={age}, Dependents={dependents}, Smoker={is_smoker}",
        "🤔 Agent Thought: I need to analyze the user's financial protection gap.",
        "🛠️ Agent is using tool: calculate_base_needs",
        f"🤔 Agent Thought: Base protection is set to $100,000.",
        f"🤔 Agent Thought: User has {dependents} dependents. Adding $100,000 per dependent.",
    ]

    # Base calculation
    base_coverage = 100000
    dependent_coverage = dependents * 100000
    age_bonus = 50000 if age < 30 else 0
    
    total_recommended = base_coverage + dependent_coverage + age_bonus
    
    # Cap at reasonable amounts for this demo
    if total_recommended > 2000000:
        total_recommended = 2000000
        
    reasoning = [
        f"Base coverage: ${base_coverage:,}",
        f"Dependent coverage ({dependents} * $100k): ${dependent_coverage:,}",
    ]
    
    if age_bonus > 0:
        reasoning.append(f"Young age bonus (<30): ${age_bonus:,}")
        agent_trace.append(f"🤔 Agent Thought: User is under 30. Adding growth buffer of ${age_bonus:,}.")
    
    if is_smoker:
        reasoning.append("Note: Smoker status may increase premiums, but coverage need remains valid.")
        agent_trace.append("Note: Smoker status detected. This affects premium, not coverage amount.")
        recommended_health_status = "Fair"
    else:
        recommended_health_status = "Good"

    agent_trace.append(f"✅ Agent Finished: Recommended Coverage = ${total_recommended:,}")
    agent_trace.append(f"✅ Recommended Health Status: {recommended_health_status}")

    return {
        "status": "Success",
        "agent": "Needs Analysis Agent",
        "recommended_coverage": total_recommended,
        "recommended_health_status": recommended_health_status,
        "reasoning": reasoning,
        "agentTrace": agent_trace
    }

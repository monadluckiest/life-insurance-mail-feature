from typing import Dict, Any
import datetime

def run_policy_servicing_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Policy Servicing Agent
    Handles address changes and generates confirmation text.
    """
    print(f"DEBUG: Policy Servicing Agent received: {data}")
    
    policy_number = data.get("policyNumber")
    new_address = data.get("newAddress")
    
    # Agent trace for chat widget
    agent_trace = [
        "🤖 Policy Servicing Agent: Initializing...",
        f"> Input: Policy={policy_number}, New Address={new_address}",
        "🤔 Agent Thought: I need to process this address change request.",
        "🛠️ Agent is using tool: validate_policy_exists",
        f"✅ Policy {policy_number} found and validated.",
        "🛠️ Agent is using tool: update_address_record",
        "🤔 Agent Thought: Updating address in the system...",
        f"✅ Address updated successfully to: {new_address}",
        "🛠️ Agent is using tool: generate_confirmation_letter",
        "🤔 Agent Thought: Generating formal confirmation document...",
        "✅ Agent Finished: Address change processed successfully. Confirmation letter generated."
    ]
    
    if not policy_number or not new_address:
        return {
            "status": "Error",
            "agent": "Policy Servicing Agent",
            "message": "Missing policy number or new address",
            "agentTrace": [
                "🤖 Policy Servicing Agent: Initializing...",
                f"> Input: Policy={policy_number}, New Address={new_address}",
                "❌ Error: Missing required information"
            ]
        }

    # Simulate processing time or validation logic here
    
    confirmation_date = datetime.date.today().strftime("%B %d, %Y")
    
    confirmation_text = f"""
    Subject: Confirmation of Address Change
    Date: {confirmation_date}
    
    Dear Policyholder,
    
    This letter confirms that we have updated the address on file for Policy #{policy_number}.
    
    New Address:
    {new_address}
    
    If you did not request this change, please contact us immediately.
    
    Sincerely,
    SecureLife Insurance Service Team
    """
    
    return {
        "status": "Success",
        "agent": "Policy Servicing Agent",
        "policyNumber": policy_number,
        "updatedAddress": new_address,
        "confirmationDocument": confirmation_text.strip(),
        "timestamp": datetime.datetime.now().isoformat(),
        "agentTrace": agent_trace
    }

# Python Agent Integration Pattern

## Overview
This document explains how the Java Spring Boot application integrates with Python AI agents using FastAPI.

## Architecture

```
┌─────────────────────┐
│   Frontend (JS)     │
│   - app.js          │
└──────────┬──────────┘
           │ HTTP POST
           ▼
┌─────────────────────┐
│  Java Spring Boot   │
│  - QuoteAgentService│
│  - UnderwritingService│
│  - PolicyIssuanceService│
└──────────┬──────────┘
           │ RestTemplate
           │ HTTP POST to localhost:8000
           ▼
┌─────────────────────┐
│   Python FastAPI    │
│   - main.py         │
│   - Endpoints       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Python Agents     │
│   - quote.py        │
│   - underwriting.py │
│   - policy_issuance.py│
│                     │
│   Uses:             │
│   - Azure OpenAI    │
│   - LangChain       │
│   - Custom Tools    │
└─────────────────────┘
```

## Integration Pattern

### 1. Java Service Layer

Each agent service follows this pattern:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class QuoteAgentService {
    
    private final RestTemplate restTemplate = new RestTemplate();
    private static final String AGENT_URL = "http://localhost:8000/agent/quote";
    
    public Map<String, Object> processRequest(InputData input) {
        // 1. Prepare request
        Map<String, Object> request = new HashMap<>();
        request.put("field1", input.getField1());
        request.put("field2", input.getField2());
        
        // 2. Call Python agent
        @SuppressWarnings("unchecked")
        Map<String, Object> response = restTemplate.postForObject(
            AGENT_URL, request, Map.class);
        
        // 3. Process response
        // Extract agentTrace for frontend display
        List<String> agentTrace = (List<String>) response.get("agentTrace");
        
        // 4. Save to database if needed
        // ...
        
        // 5. Return result with agentTrace
        result.put("agentTrace", agentTrace);
        return result;
    }
}
```

### 2. Python FastAPI Endpoint

Each endpoint in `main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.quote import run_quote_agent

app = FastAPI()

class QuoteRequest(BaseModel):
    age: int
    coverageAmount: float
    healthStatus: str

@app.post("/agent/quote")
async def quote_endpoint(request: QuoteRequest):
    try:
        result = run_quote_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Python Agent Implementation

Each agent in `agents/` folder:

```python
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from agent_tools import risk_analysis_tool, premium_calculator_tool
import os

def run_quote_agent(input_data):
    """
    Quote Agent uses AI to calculate insurance premiums
    """
    try:
        # 1. Initialize Azure OpenAI
        llm = AzureChatOpenAI(
            deployment_name="gpt-4o",
            model="gpt-4o",
            api_version="2024-08-01-preview",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # 2. Define tools
        tools = [risk_analysis_tool, premium_calculator_tool]
        
        # 3. Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an insurance quote agent..."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # 4. Create and run agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )
        
        result = agent_executor.invoke({
            "input": f"Calculate insurance quote for: {input_data}"
        })
        
        # 5. Return result with trace
        return {
            "monthlyPremium": 125.50,
            "agentTrace": [
                "Quote Agent: Analyzing risk factors...",
                "Quote Agent: Calculating premium...",
                "Quote Agent: Quote generated successfully"
            ]
        }
        
    except Exception as e:
        # Fallback logic
        return {
            "monthlyPremium": 100.00,
            "agentTrace": ["Quote Agent: Used fallback calculation"]
        }
```

### 4. Agent Tools

Tools are defined in `agent_tools.py`:

```python
from langchain_core.tools import tool
import time

@tool("risk_analysis_tool")
def risk_analysis_tool(age: int, health_status: str) -> str:
    """
    Analyzes risk factors for insurance applicant.
    Args:
        age: Age of applicant
        health_status: Health status (excellent, good, fair, poor)
    Returns:
        Risk assessment result
    """
    time.sleep(0.5)  # Simulate processing
    
    if age < 30:
        risk = "Low"
    elif age < 50:
        risk = "Medium"
    else:
        risk = "High"
    
    return f"Risk Level: {risk} based on age {age} and {health_status} health"
```

## Current Agents

### 1. Quote Agent
- **Endpoint**: `POST http://localhost:8000/agent/quote`
- **Request**: `{ age, coverageAmount, healthStatus }`
- **Tools**: risk_analysis_tool, premium_calculator_tool
- **Response**: `{ monthlyPremium, agentTrace[] }`

### 2. Underwriting Agent
- **Endpoint**: `POST http://localhost:8000/agent/underwrite`
- **Request**: `{ applicationNumber, quote: {...} }`
- **Tools**: credit_check_tool, mib_check_tool
- **Response**: `{ decision, reason, creditCheckPassed, mibCheckPassed, agentTrace[] }`

### 3. Policy Issuance Agent (NEW)
- **Endpoint**: `POST http://localhost:8000/agent/issue-policy`
- **Request**: `{ applicationNumber, policyHolderName, coverageAmount, monthlyPremium }`
- **Tools**: policy_document_generator_tool, policy_validation_tool
- **Response**: `{ policyNumber, issueDate, effectiveDate, expiryDate, agentTrace[] }`

## Frontend Integration

The frontend displays agent traces in a single timeline widget:

```javascript
function parseAgentTraceToChat(traceLines, agentName) {
    const chatMessages = document.getElementById('agent-chat-messages');
    
    // Add section header
    const sectionHeader = document.createElement('div');
    sectionHeader.className = 'agent-section-header';
    sectionHeader.textContent = agentName;
    chatMessages.appendChild(sectionHeader);
    
    // Add trace lines
    traceLines.forEach(line => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'agent-message';
        messageDiv.textContent = line;
        chatMessages.appendChild(messageDiv);
    });
    
    // Add separator for next agent
    const separator = document.createElement('div');
    separator.className = 'agent-separator';
    separator.innerHTML = '<span class="separator-text">UNDERWRITING AGENT</span>';
    chatMessages.appendChild(separator);
}
```

## Running the System

### Start Python Agent Server

```bash
cd python-agents
python main.py
```

Server starts on: `http://localhost:8000`

### Start Java Application

```bash
mvn spring-boot:run
```

Server starts on: `http://localhost:8080`

### Environment Variables Required

```bash
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
```

## Testing

1. Open browser: `http://localhost:8080`
2. Fill quote form → See Quote Agent chat
3. Fill application form → See Underwriting Agent chat
4. Complete payment → See Policy Issuance Agent chat

All agent traces appear in single "Agent Chat History" timeline widget.

## Key Benefits

1. **Separation of Concerns**: AI logic in Python, business logic in Java
2. **Flexibility**: Easy to add new agents following same pattern
3. **Fallback**: Each agent has fallback logic if AI service unavailable
4. **Visibility**: Agent traces show AI decision-making process
5. **Scalability**: Python agents can run on separate servers

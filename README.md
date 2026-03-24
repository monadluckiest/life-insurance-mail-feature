# Life Insurance Application (Agentic MVP)

This application demonstrates a **Multi-Agent System** for Life Insurance Instant Issuance. It uses a **Sidecar Architecture** where a Java Spring Boot application delegates intelligent decision-making to a Python FastAPI service hosting the agents.

## Architecture
*   **Java Backend (Port 8080)**: Core application, persistence (H2), and orchestrator.
*   **Python Agent Service (Port 8000)**: Hosts the AI Agents.
    *   **Quote Agent**: Independent service for premium calculation.
    *   **Underwriting Agent**: Performs risk assessment using mocked external data (Credit/MIB) and a decision rules engine.

## Setup Instructions

### Prerequisites
*   **Java**: JDK 17+
*   **Maven**: 3.6+
*   **Python**: 3.10+
*   **Pip**: Latest version

### 1. Start Python Agents (Required)
The Java application depends on this service.
```bash
cd python-agents
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Java Application
In a separate terminal:
```bash
# Clean Build (Removes old artifacts and rebuilds)
mvn clean install

# Run the Application
java -jar target/life-insurance-app-1.0.0.jar
```

### 3. Access Application
*   **Web UI**: [http://localhost:8080](http://localhost:8080)
*   **Agent API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Features
*   **Instant Issuance (Happy Path)**: Submit an application with Age 30 and Excellent Health for instant approval.
*   **Agentic Delegation**: The Java app delegates `calculateQuote` and `performInstantUnderwriting` tasks to the Python service.
*   **Non-Deterministic Ready**: The Python service architecture allows for easy integration of LLM-based agents (e.g., using LangChain) for complex flows (Manual Underwriting).

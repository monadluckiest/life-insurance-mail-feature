
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Union

class AgentTraceCallbackHandler(BaseCallbackHandler):
    """Callback Handler that captures agent actions and thoughts for the UI."""
    
    def __init__(self):
        self.trace = []
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        # self.trace.append(f"🏁 Starting Agent Execution...")
        pass

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get("name")
        self.trace.append(f"🛠️ Agent is using tool: {tool_name}")
        self.trace.append(f"   Input: {input_str}")

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        self.trace.append(f"   Output: {output}")

    def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        self.trace.append(f"🤔 Agent Thought: {action.log}")

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> Any:
        self.trace.append(f"✅ Agent Finished: {finish.return_values}")
        
    def get_trace(self) -> List[str]:
        return self.trace


import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load .env if exists
load_dotenv()

def get_llm():
    """Returns an AzureChatOpenAI instance."""
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not api_key:
        print("⚠️  WARNING: AZURE_OPENAI_API_KEY not found.")
        return None
    
    return AzureChatOpenAI(
        azure_deployment=deployment,
        api_version=api_version,
        temperature=0, # Lower temperature for tool calling precision
        api_key=api_key,
        azure_endpoint=endpoint
    )

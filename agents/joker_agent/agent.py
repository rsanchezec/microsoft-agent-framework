"""
Agente especializado en contar chistes
"""
import os
from dotenv import load_dotenv
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup

load_dotenv()

credential = DefaultAzureCredential()

client = AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False
)

# IMPORTANTE: La variable DEBE llamarse 'agent'
agent = client.create_agent(
    instructions="""Eres un comediante profesional muy gracioso.
Tu trabajo es contar chistes, hacer bromas y hacer reir a las personas.
Siempre respondes con humor y buen animo.""",
    name="JokerAssistant"
)

register_cleanup(agent, credential.close)

print(f"Agente JokerAssistant listo para DevUI")

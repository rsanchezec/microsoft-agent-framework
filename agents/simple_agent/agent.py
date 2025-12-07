"""
Agente de ejemplo para DevUI
Este archivo sera auto-descubierto por DevUI cuando ejecutes: devui ./agents
"""
import os
from dotenv import load_dotenv
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup

load_dotenv()

# Crear credential
credential = DefaultAzureCredential()

# Crear cliente
client = AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False  # Mantener agente en Azure
)

# Crear agente
# IMPORTANTE: La variable DEBE llamarse 'agent' para que DevUI la encuentre
agent = client.create_agent(
    instructions="""Eres un asistente util y amigable.
Puedes responder preguntas generales, ayudar con tareas,
y mantener conversaciones naturales.""",
    name="SimpleAssistant"
)

# Registrar cleanup para cerrar recursos cuando DevUI se detenga
register_cleanup(agent, credential.close)

print(f"Agente '{agent.chat_client.agent_id or 'SimpleAssistant'}' listo para DevUI")

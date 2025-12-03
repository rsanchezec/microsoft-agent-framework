import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


def create_agent(client: AzureAIAgentClient, instructions: str, name: str):
    """Crea y retorna un agente con las instrucciones y nombre especificados."""
    return client.create_agent(
        instructions=instructions,
        name=name
    )


async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=False  # El agente NO se eliminará al cerrar el cliente
        ) as client:
            # Crear el agente usando la función separada
            agent = create_agent(
                client=client,
                instructions="Eres bueno contando chistes.",
                name="Joker"
            )

            # Usar el agente (esto crea el agente en AI Foundry si no existe)
            result = await agent.run("Cuéntame un chiste sobre un pirata.")
            print(result.text)

            # Ahora el agente ya está creado, mostramos su ID
            print(f"\n{'='*50}")
            print(f"Agent ID (asistente): {agent.chat_client.agent_id}")
            print(f"Guarda este ID para reutilizar el agente en AI Foundry")
            print(f"{'='*50}\n")
            print("-" * 30)
            print("Usar el agente con streaming")
            # Usar el agente con streaming
            async for update in agent.run_stream("Cuéntame un chiste sobre un pirata."):
                if update.text:
                    print(update.text, end="", flush=True)
            print() 



asyncio.run(main())
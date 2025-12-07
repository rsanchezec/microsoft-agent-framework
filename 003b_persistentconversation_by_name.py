"""
Script que demuestra cómo usar el NOMBRE del agente en lugar del ID.
Usa el project_client subyacente para buscar el agente por nombre.
"""
import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

# En lugar de usar AGENT_ID, usa el nombre del agente
AGENT_NAME = "Joker"  # El nombre que le diste al agente en 001_createandrunanagent.py
THREAD_ID = None


async def main():
    async with DefaultAzureCredential() as credential:
        # Paso 1: Crear el cliente SIN agent_id
        async with AzureAIAgentClient(
            async_credential=credential,
            thread_id=THREAD_ID
        ) as client:

            print(f"Buscando agente con nombre: '{AGENT_NAME}'...\n")

            # Paso 2: Buscar el agente por nombre listando todos los agentes
            try:
                agents_paged = client.agents_client.list_agents(limit=100)
                agent_id = None

                async for agent in agents_paged:
                    if agent.name == AGENT_NAME:
                        agent_id = agent.id
                        print(f"Agente encontrado!")
                        print(f"   Nombre: {agent.name}")
                        print(f"   ID: {agent_id}")
                        print(f"   Modelo: {agent.model}\n")
                        break

                if not agent_id:
                    print(f"Error: No se encontro el agente '{AGENT_NAME}'")
                    print(f"\nAsegurate de que el agente existe en Azure AI Foundry.")
                    print(f"   Puedes crearlo con el script 001_createandrunanagent.py")
                    return

            except Exception as e:
                print(f"Error al buscar el agente '{AGENT_NAME}'")
                print(f"Detalles: {e}")
                return

            # Paso 3: Crear un nuevo cliente CON el agent_id encontrado
            async with AzureAIAgentClient(
                async_credential=credential,
                agent_id=agent_id,  # Usar el ID obtenido del lookup
                thread_id=THREAD_ID
            ) as agent_client:

                agent = agent_client.create_agent(
                    instructions="Eres un asistente útil que recuerda el contexto de la conversación.",
                    name=AGENT_NAME
                )

                print("=== Conversación Persistente con Thread ===\n")

                # Crear un thread explícito
                thread = agent.get_new_thread(service_thread_id=THREAD_ID)

                # Primera interacción - establece contexto
                print("Usuario: Mi color favorito es el azul.")
                result = await agent.run("Mi color favorito es el azul.", thread=thread)
                print(f"Agente: {result.text}\n")

                # Obtener el Thread ID
                thread_id = thread.service_thread_id
                print(f"{'='*60}")
                print(f"Thread ID (Conversation ID): {thread_id}")
                print(f"Guarda este ID para continuar esta conversación más tarde")
                print(f"{'='*60}\n")

                # Segunda interacción - da más contexto
                print("Usuario: Y mi animal favorito es el perro.")
                result = await agent.run("Y mi animal favorito es el perro.", thread=thread)
                print(f"Agente: {result.text}\n")

                # Tercera interacción - el agente debe recordar el contexto
                print("Usuario: ¿Cuál es mi color favorito?")
                result = await agent.run("¿Cuál es mi color favorito?", thread=thread)
                print(f"Agente: {result.text}\n")

                # Cuarta interacción - el agente debe recordar ambos datos
                print("Usuario: ¿Recuerdas cuál es mi animal favorito?")
                result = await agent.run("¿Recuerdas cuál es mi animal favorito?", thread=thread)
                print(f"Agente: {result.text}\n")

                # Quinta interacción - combinar contexto
                print("Usuario: Recomiéndame un regalo basado en mis preferencias.")
                result = await agent.run("Recomiéndame un regalo basado en mis preferencias.", thread=thread)
                print(f"Agente: {result.text}\n")

                print(f"\n{'='*60}")
                print(f"Thread ID (Conversation ID): {thread_id}")
                print(f"Para continuar esta conversación, copia este Thread ID")
                print(f"y úsalo en el script 004_continuethreadconversation.py")
                print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())

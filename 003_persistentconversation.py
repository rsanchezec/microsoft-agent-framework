import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

# Configura el Agent ID que obtuviste del script 001
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"

# Puedes especificar un Thread ID existente para continuar una conversación
# o dejarlo en None para crear un nuevo thread
THREAD_ID = None  # Cambiar a un thread_id específico para reutilizar una conversación


async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=AGENT_ID,
            thread_id=THREAD_ID  # Especifica el thread para persistencia
        ) as client:
            agent = client.create_agent(
                instructions="Eres un asistente útil que recuerda el contexto de la conversación.",
                name="Assistant"
            )

            print("=== Conversación Persistente con Thread ===\n")

            # Crear un thread explícito para poder acceder al conversation_id después
            thread = agent.get_new_thread(service_thread_id=THREAD_ID)

            # Primera interacción - establece contexto
            print("Usuario: Mi color favorito es el azul.")
            result = await agent.run("Mi color favorito es el azul.", thread=thread)
            print(f"Agente: {result.text}\n")

            # Obtener el Thread ID del thread después de la primera interacción
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

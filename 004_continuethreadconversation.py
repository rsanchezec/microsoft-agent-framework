import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

# Configura el Agent ID
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"

# REEMPLAZA este Thread ID con el que obtuviste del script 003
# Debe ser un UUID como: fc737957-d5a1-4de2-9011-0c2d559aeb3e
THREAD_ID = "thread_7dLiIQQlgsCOCUw3neCkjMbr"


async def main():
    if THREAD_ID == "tu-thread-id-aqui":
        print("ERROR: Debes configurar el THREAD_ID con el ID que obtuviste del script 003")
        print("Ejecuta primero: uv run .\\003_persistentconversation.py")
        print("Y copia el Thread ID que te muestra al final.")
        return

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=AGENT_ID
        ) as client:
            agent = client.create_agent(
                instructions="Eres un asistente útil que recuerda el contexto de la conversación.",
                name="Assistant"
            )

            print(f"=== Continuando conversación existente ===")
            print(f"Thread ID: {THREAD_ID}\n")

            # Crear thread con el ID existente
            thread = agent.get_new_thread(service_thread_id=THREAD_ID)

            # El agente debe recordar todo el contexto de la conversación anterior
            print("Usuario: ¿Qué sabes sobre mis preferencias?")
            result = await agent.run("¿Qué sabes sobre mis preferencias?", thread=thread)
            print(f"Agente: {result.text}\n")

            # Agregar nueva información al contexto
            print("Usuario: También me gusta la pizza.")
            result = await agent.run("También me gusta la pizza.", thread=thread)
            print(f"Agente: {result.text}\n")

            # Verificar que recuerda todo el contexto (viejo y nuevo)
            print("Usuario: Resume todo lo que sabes de mí.")
            result = await agent.run("Resume todo lo que sabes de mí.", thread=thread)
            print(f"Agente: {result.text}\n")

            print(f"\n{'='*60}")
            print(f"La conversación se ha actualizado en el Thread: {THREAD_ID}")
            print(f"Puedes continuar ejecutando este script para seguir conversando")
            print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())

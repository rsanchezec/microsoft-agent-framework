import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

# REEMPLAZA ESTE ID CON EL "Agent ID (asistente)" QUE OBTUVISTE DEL SCRIPT 001
# Debe empezar con "asst_" como: asst_GJTfYzVWKzBMCD22nnfwo39r
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"


async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=AGENT_ID  # Reutiliza el agente existente
        ) as client:
            # No necesitas crear un nuevo agente, usa el existente
            agent = client.create_agent(
                instructions="Eres bueno contando chistes.",
                name="Joker"
            )

            print(f"Reutilizando agente con ID: {agent.chat_client.agent_id}\n")

            # Ejemplo 1: Pregunta simple
            print("=== Ejemplo 1: Pregunta simple ===")
            result = await agent.run("Cuéntame un chiste sobre un gato.")
            print(result.text)
            print()

            # Ejemplo 2: Con streaming
            print("=== Ejemplo 2: Con streaming ===")
            async for update in agent.run_stream("Cuéntame un chiste sobre un perro."):
                if update.text:
                    print(update.text, end="", flush=True)
            print("\n")

            # Ejemplo 3: Múltiples interacciones
            print("=== Ejemplo 3: Múltiples preguntas ===")
            preguntas = [
                "¿Cuál es la diferencia entre un pirata y un marinero?",
                "Cuéntame un chiste corto",
                "Dame un consejo gracioso"
            ]

            for pregunta in preguntas:
                print(f"\nPregunta: {pregunta}")
                result = await agent.run(pregunta)
                print(f"Respuesta: {result.text}")
                print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())

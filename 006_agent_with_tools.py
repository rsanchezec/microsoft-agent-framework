import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Annotated
from pydantic import Field
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

def get_weather(
    location: Annotated[str, Field(description="La ubicación para obtener el clima.")],
) -> str:
    """Get the weather for a given location."""
    return f"El clima en {location} es nublado con una máxima de 15°C."

"También puedes usar el decorador ai_function para especificar explícitamente el nombre y la descripción de la función:"
@ai_function(name="weather_tool", description="Recupera información meteorológica de cualquier ubicación.")
def get_weather(
    location: Annotated[str, Field(description="La ubicación para obtener el clima.")],
) -> str:
    return f"El clima en {location} es nublado con una máxima de 15°C."

def multiplicar(num1: int, num2: int) -> int:
    """Multiplica dos números enteros y retorna el resultado. Útil para cálculos."""
    print(f"\n[🔧 TOOL EJECUTADA: Multiplicando {num1} * {num2}...]\n")
    return num1 * num2

load_dotenv()

def create_agent(client: AzureAIAgentClient, instructions: str, name: str, tools: list):
    """Crea y retorna un agente con las instrucciones y nombre especificados."""
    return client.create_agent(
        instructions=instructions,
        name=name,
        tools=tools
    )

async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True  
        ) as client:

            tools = [multiplicar, get_weather]
            agent = create_agent(
                client=client,
                instructions="Eres una asistente útil.",
                name="Tools",
                tools=tools
            )
            task="¿Cómo es el clima en Ámsterdam?"
            print(f"Pregunta enviada al Agente: {task}")
            result = await agent.run(task)
            print(f"Respuesta final del Agente:\n{result.text}")
            print("-" * 30)
            task="¿Cuál es el área de un terreno rectangular que mide 45 metros de ancho por 12 metros de largo?"
            print(f"Pregunta enviada al Agente: {task}")
            result = await agent.run(task)
            print(f"Respuesta final del Agente:\n{result.text}")

asyncio.run(main())
import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Optional

# --- HERRAMIENTA DISPONIBLE PARA EL AGENTE DESARROLLADOR ---
def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números. Utilizar para cualquier cálculo complejo."""
    return a * b

load_dotenv()

# 1. Cambiamos la firma para que tools sea opcional (None por defecto)
def create_agent(client: AzureAIAgentClient, instructions: str, name: str, tools: Optional[list] = None):
    """
    Crea y retorna un agente. Si se proporciona una lista de herramientas, se agregan.
    """
    
    # 2. Creamos un diccionario con los parámetros obligatorios
    params = {
        "instructions": instructions,
        "name": name
    }

    # 3. Solo si tools tiene valor (no es None y no es una lista vacía), lo agregamos al diccionario
    if tools:
        params["tools"] = tools

    # 4. Desempaquetamos el diccionario usando **params
    # Esto equivale a escribir instructions=..., name=..., y tools=... (si existe)
    return client.create_agent(**params)

async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=False  
        ) as client:
            
            developer_agent = create_agent(
                client=client,
                instructions="Eres un Desarrollador Senior de Python. Respondes con código Python cuando sea apropiado y utilizas tus herramientas para resolver problemas.",
                name="Developer",
                tools=[multiplicar]
            )

            manager_agent = create_agent(
                client=client,
                instructions="Eres un Product Manager estricto. Tu trabajo es asignar tareas de producto y evaluar si las respuestas son soluciones de código válidas.",
                name="ProductManager"
            )

            task = "Necesito una función Python llamada 'calcular_iva' que reciba un precio base y retorne el precio final. Usa un IVA del 16%."

            print(f"[{manager_agent.name}]: Enviando la tarea...")
            print(f"   -> Tarea: '{task}'")
            print("-" * 60)

            developer_response = await developer_agent.run(task)
    
            print(f"[{developer_agent.name}]: Respuesta/Propuesta:")
            print(developer_response.text)
            print("-" * 60)

            evaluacion = await manager_agent.run(
                f"El desarrollador propuso lo siguiente. ¿Es una solución aceptable para el producto?\n\nPropuesta: {developer_response.text}"
            )

            print(f"[{manager_agent.name}]: Evaluación final:")
            print(evaluacion.text)

asyncio.run(main())
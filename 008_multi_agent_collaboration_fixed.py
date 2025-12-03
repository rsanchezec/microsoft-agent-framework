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

def create_agent(client: AzureAIAgentClient, instructions: str, name: str, tools: Optional[list] = None):
    """
    Crea y retorna un agente. Si se proporciona una lista de herramientas, se agregan.
    """
    params = {
        "instructions": instructions,
        "name": name
    }

    if tools:
        params["tools"] = tools

    return client.create_agent(**params)

async def create_and_persist_agent(credential, instructions: str, name: str, tools: Optional[list] = None) -> str:
    """
    Crea un agente persistente en Azure AI Foundry y retorna su ID.

    Args:
        credential: Credencial de Azure
        instructions: Instrucciones del agente
        name: Nombre del agente
        tools: Lista opcional de herramientas/funciones

    Returns:
        str: ID del agente creado
    """
    async with AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    ) as client:
        agent = create_agent(
            client=client,
            instructions=instructions,
            name=name,
            tools=tools
        )

        # Ejecutar una vez para obtener el ID real del agente
        await agent.run("Hola, confirma que estas listo.")
        agent_id = agent.chat_client.agent_id

        print(f"[OK] Agente '{name}' creado (ID: {agent_id})")
        print(f"     Este agente PERSISTIRA en AI Foundry")

        return agent_id

async def main():
    async with DefaultAzureCredential() as credential:

        print("=" * 60)
        print("CREANDO AGENTES...")
        print("=" * 60)

        # PASO 1: Crear el Developer Agent
        developer_id = await create_and_persist_agent(
            credential=credential,
            instructions="Eres un Desarrollador Senior de Python. Respondes con código Python cuando sea apropiado y utilizas tus herramientas para resolver problemas.",
            name="Developer",
            tools=[multiplicar]
        )

        # PASO 2: Crear el Manager Agent
        manager_id = await create_and_persist_agent(
            credential=credential,
            instructions="Eres un Product Manager estricto. Tu trabajo es asignar tareas de producto y evaluar si las respuestas son soluciones de código válidas.",
            name="ProductManager"
        )

        print("=" * 60)
        print("AMBOS AGENTES AHORA ESTAN PERSISTIDOS EN AI FOUNDRY")
        print("=" * 60)
        print()
        
        # PASO 3: Reconectar con los agentes usando sus IDs
        print("Reconectando con los agentes persistidos...")
        
        # Crear un cliente conectado al Developer Agent
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=developer_id  # Conectar al agente existente
        ) as dev_client:

            # Obtener el agente desde el cliente
            developer_agent = create_agent(
                client=dev_client,
                instructions="Eres un Desarrollador Senior de Python. Respondes con código Python cuando sea apropiado y utilizas tus herramientas para resolver problemas.",
                name="Developer",
                tools=[multiplicar]
            )

            task = "Necesito una función Python llamada 'calcular_iva' que reciba un precio base y retorne el precio final. Usa un IVA del 16%."

            print(f"[Developer]: Procesando tarea...")
            print(f"   -> Tarea: '{task}'")
            print("-" * 60)

            # Ejecutar la tarea con el Developer Agent
            developer_response = await developer_agent.run(task)
            dev_response_text = developer_response.text

            print(f"[Developer]: Respuesta/Propuesta:")
            print(dev_response_text)
            print("-" * 60)
        
        # Crear un cliente conectado al Manager Agent
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=manager_id  # Conectar al agente existente
        ) as mgr_client:

            # Obtener el agente desde el cliente
            manager_agent = create_agent(
                client=mgr_client,
                instructions="Eres un Product Manager estricto. Tu trabajo es asignar tareas de producto y evaluar si las respuestas son soluciones de código válidas.",
                name="ProductManager"
            )

            # El Manager Agent evalúa la respuesta del Developer
            evaluacion = await manager_agent.run(
                f"El desarrollador propuso lo siguiente. ¿Es una solución aceptable para el producto?\n\nPropuesta: {dev_response_text}"
            )

            print(f"[ProductManager]: Evaluacion final:")
            print(evaluacion.text)
            print("=" * 60)
            print("PROCESO COMPLETADO")
            print(f"Revisa AI Foundry - deberias ver ambos agentes:")
            print(f"  1. Developer (ID: {developer_id})")
            print(f"  2. ProductManager (ID: {manager_id})")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
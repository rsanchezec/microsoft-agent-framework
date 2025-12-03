import os
from dotenv import load_dotenv
from datetime import date
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Optional

def herramienta_matematica(a: float, b: float) -> float:
    return a * b

def herramienta_financiera(eur: float) -> float:
    return eur * 1.08

def obtener_fecha() -> str:
    return date.today().strftime("%Y-%m-%d")



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

async def create_and_initialize_agent(credential, instructions: str, name: str, tools: Optional[list] = None):
    """
    Crea un agente con su propio cliente y lo inicializa.

    IMPORTANTE: Retorna tanto el cliente como el agente para mantener
    el cliente abierto durante toda la ejecución.

    Args:
        credential: Credencial de Azure
        instructions: Instrucciones del agente
        name: Nombre del agente
        tools: Lista opcional de herramientas/funciones

    Returns:
        tuple: (client, agent) - Ambos deben mantenerse en scope
    """
    # Cada agente necesita su PROPIO cliente
    client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )

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

    return client, agent
    
# Estas funciones ya no se necesitan aquí, se crearán dentro de main() como closures
# para que tengan acceso a los agentes especializados
    
async def main():
    async with DefaultAzureCredential() as credential:
        # Lista para mantener referencias a todos los clientes
        clients = []

        try:
            print("=" * 60)
            print("CREANDO AGENTES...")
            print("=" * 60)

            # Crear agentes especializados (cada uno con su propio cliente)
            math_client, math_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres una calculadora.",
                name="math_agent",
                tools=[herramienta_matematica]
            )
            clients.append(math_client)

            finance_client, finance_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un experto en divisas. Usas tu herramienta para convertir EUR a USD.",
                name="finance_agent",
                tools=[herramienta_financiera]
            )
            clients.append(finance_client)

            time_client, time_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un Cronista. Das la fecha actual.",
                name="time_agent",
                tools=[obtener_fecha]
            )
            clients.append(time_client)

            print("\n" + "=" * 60)
            print("CREANDO SUPERVISOR...")
            print("=" * 60)

            # Crear funciones wrapper que capturen los agentes (closures)
            async def consultar_matematicas(problema: str) -> str:
                """Úsalo para resolver problemas numéricos, cálculos o multiplicaciones."""
                print(f"\n[📞 SUPERVISOR -> MATH]: '{problema}'")
                respuesta = await math_agent.run(problema)
                return respuesta.text

            async def consultar_finanzas(pregunta: str) -> str:
                """Úsalo para conversiones de divisas EUR a USD o preguntas sobre dinero."""
                print(f"\n[📞 SUPERVISOR -> FINANCE]: '{pregunta}'")
                respuesta = await finance_agent.run(pregunta)
                return respuesta.text

            async def consultar_tiempo(pregunta: str) -> str:
                """Úsalo cuando el usuario pregunte por la FECHA, el DÍA, el AÑO o la HORA actual."""
                print(f"\n[📞 SUPERVISOR -> TIME]: '{pregunta}'")
                respuesta = await time_agent.run(pregunta)
                return respuesta.text

            # Crear el supervisor con su propio cliente
            supervisor_client, supervisor = await create_and_initialize_agent(
                credential=credential,
                instructions="""Eres un supervisor inteligente.
                Analiza la pregunta del usuario y delega al departamento correcto:
                - Usa consultar_matematicas para cálculos y problemas numéricos
                - Usa consultar_finanzas para conversiones de dinero
                - Usa consultar_tiempo para preguntas sobre fecha u hora actual
                """,
                name="supervisor_agent",
                tools=[consultar_matematicas, consultar_finanzas, consultar_tiempo]
            )
            clients.append(supervisor_client)

            print("\n" + "=" * 60)
            print("PROBANDO SUPERVISOR...")
            print("=" * 60)

            # Probar el supervisor con diferentes preguntas
            preguntas = [
                "¿Qué fecha es hoy?",
                "¿Cuánto es 5 por 7?",
                "Convierte 100 euros a dólares"
            ]

            for pregunta in preguntas:
                print(f"\n[USER]: {pregunta}")
                resultado = await supervisor.run(pregunta)
                print(f"[SUPERVISOR RESPONDE]: {resultado.text}")

        finally:
            # Cerrar todos los clientes al final
            print("\n" + "=" * 60)
            print("CERRANDO CLIENTES...")
            print("=" * 60)
            for client in clients:
                await client.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())
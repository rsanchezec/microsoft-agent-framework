"""
Ejemplo de agentes usando otros agentes como herramientas.
Versión con functools.partial para mayor reutilización.
"""

import os
from dotenv import load_dotenv
from datetime import date
import asyncio
from functools import partial
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Optional

# ============================================================
# HERRAMIENTAS BASE (funciones simples)
# ============================================================

def herramienta_matematica(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b

def herramienta_financiera(eur: float) -> float:
    """Convierte EUR a USD."""
    return eur * 1.08

def obtener_fecha() -> str:
    """Retorna la fecha actual."""
    return date.today().strftime("%Y-%m-%d")


# ============================================================
# FUNCIONES GENÉRICAS (fuera de main - reutilizables)
# ============================================================

async def consultar_agente_generico(
    agent,
    departamento: str,
    emoji: str,
    pregunta: str
) -> str:
    """
    Función genérica para consultar cualquier agente.

    Args:
        agent: El agente a consultar
        departamento: Nombre del departamento (para logging)
        emoji: Emoji para el log
        pregunta: La pregunta a hacer al agente

    Returns:
        str: La respuesta del agente
    """
    print(f"\n[{emoji} SUPERVISOR -> {departamento}]: '{pregunta}'")
    respuesta = await agent.run(pregunta)
    return respuesta.text


async def consultar_agente_simple(agent, pregunta: str) -> str:
    """
    Versión simple sin logging.
    Útil para testing o uso en otros contextos.
    """
    respuesta = await agent.run(pregunta)
    return respuesta.text


# ============================================================
# UTILIDADES
# ============================================================

load_dotenv()

def create_agent(client: AzureAIAgentClient, instructions: str, name: str, tools: Optional[list] = None):
    """Crea y retorna un agente."""
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
    Retorna tanto el cliente como el agente para mantener el cliente abierto.
    """
    client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=True
    )

    agent = create_agent(
        client=client,
        instructions=instructions,
        name=name,
        tools=tools
    )

    # Ejecutar una vez para obtener el ID
    await agent.run("Hola, confirma que estas listo.")
    agent_id = agent.chat_client.agent_id

    print(f"[OK] Agente '{name}' creado (ID: {agent_id})")
    print(f"     Este agente PERSISTIRA en AI Foundry")

    return client, agent


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

async def main():
    async with DefaultAzureCredential() as credential:
        clients = []

        try:
            print("=" * 60)
            print("CREANDO AGENTES ESPECIALIZADOS...")
            print("=" * 60)

            # Crear agentes especializados
            math_client, math_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres una calculadora. Usa tu herramienta para multiplicar números.",
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
            print("CREANDO HERRAMIENTAS CON PARTIAL...")
            print("=" * 60)

            # ✨ OPCIÓN 1: Usar partial con la función genérica completa
            consultar_matematicas = partial(
                consultar_agente_generico,
                math_agent,
                "MATH",
                "📐"
            )
            # Configurar metadata para que el LLM entienda la herramienta
            consultar_matematicas.__name__ = "consultar_matematicas"
            consultar_matematicas.__doc__ = "Úsalo para resolver problemas numéricos, cálculos o multiplicaciones."

            consultar_finanzas = partial(
                consultar_agente_generico,
                finance_agent,
                "FINANCE",
                "💰"
            )
            consultar_finanzas.__name__ = "consultar_finanzas"
            consultar_finanzas.__doc__ = "Úsalo para conversiones de divisas EUR a USD o preguntas sobre dinero."

            consultar_tiempo = partial(
                consultar_agente_generico,
                time_agent,
                "TIME",
                "📅"
            )
            consultar_tiempo.__name__ = "consultar_tiempo"
            consultar_tiempo.__doc__ = "Úsalo cuando el usuario pregunte por la FECHA, el DÍA, el AÑO o la HORA actual."

            print("[OK] Herramientas creadas con partial:")
            print(f"     - {consultar_matematicas.__name__}: {consultar_matematicas.__doc__}")
            print(f"     - {consultar_finanzas.__name__}: {consultar_finanzas.__doc__}")
            print(f"     - {consultar_tiempo.__name__}: {consultar_tiempo.__doc__}")

            print("\n" + "=" * 60)
            print("CREANDO SUPERVISOR...")
            print("=" * 60)

            # Crear el supervisor con las herramientas creadas con partial
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

            # Probar el supervisor
            preguntas = [
                "¿Qué fecha es hoy?",
                "¿Cuánto es 5 por 7?",
                "Convierte 100 euros a dólares"
            ]

            for pregunta in preguntas:
                print(f"\n[USER]: {pregunta}")
                resultado = await supervisor.run(pregunta)
                print(f"[SUPERVISOR RESPONDE]: {resultado.text}")

            print("\n" + "=" * 60)
            print("DEMOSTRANDO REUTILIZACIÓN...")
            print("=" * 60)

            # ✨ VENTAJA: Ahora podemos usar los agentes directamente
            # desde fuera del supervisor, con la función genérica
            print("\n[DEMO] Llamada directa al math_agent (sin supervisor):")
            respuesta_directa = await consultar_agente_simple(
                math_agent,
                "¿Cuánto es 12 multiplicado por 8?"
            )
            print(f"[RESPUESTA DIRECTA]: {respuesta_directa}")

            # También podemos crear nuevas herramientas sobre la marcha
            consultar_math_silencioso = partial(consultar_agente_simple, math_agent)
            print("\n[DEMO] Herramienta creada sobre la marcha (sin logging):")
            respuesta_silenciosa = await consultar_math_silencioso("¿Cuánto es 3 por 9?")
            print(f"[RESPUESTA SILENCIOSA]: {respuesta_silenciosa}")

        finally:
            # Cerrar todos los clientes
            print("\n" + "=" * 60)
            print("CERRANDO CLIENTES...")
            print("=" * 60)
            for client in clients:
                await client.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())

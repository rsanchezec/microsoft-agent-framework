"""
Travel Planner Workflow - Versión para PRODUCCIÓN

Este es el MISMO workflow que workflows/travel_planner/workflow.py,
pero como un script EJECUTABLE para producción.

Diferencias con workflow.py (DevUI):
- ✅ Tiene async main()
- ✅ Tiene asyncio.run()
- ✅ Ejecuta el workflow directamente
- ✅ Maneja input/output manualmente
- ✅ Gestión completa de recursos

Uso:
    python production_travel_planner.py
"""
import asyncio
import os
from dotenv import load_dotenv
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import WorkflowBuilder, WorkflowContext, executor, WorkflowOutputEvent

load_dotenv()


# ============================================================================
# PASO 1: Definir Executors (igual que workflow.py)
# ============================================================================

async def create_agents(credential):
    """Factory para crear todos los agentes"""

    # Agente 1: Location Selector
    location_client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )
    location_picker_agent = location_client.create_agent(
        instructions="""Eres un experto en seleccionar destinos de viaje.
Cuando el usuario te dice sus preferencias (clima, presupuesto, tipo de viaje),
seleccionas el destino más apropiado y retornas SOLO el nombre de la ciudad/país.""",
        name="LocationSelector"
    )

    # Agente 2: Destination Recommender
    destination_client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )
    destination_recommender_agent = destination_client.create_agent(
        instructions="""Eres un experto en recomendar lugares turísticos.
Dado un destino, recomiendas los mejores lugares para visitar,
actividades imperdibles y atracciones principales.""",
        name="DestinationRecommender"
    )

    # Agente 3: Weather Agent
    weather_client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )
    weather_agent = weather_client.create_agent(
        instructions="""Eres un experto en clima y mejor época para viajar.
Dado un destino, proporcionas información sobre el clima,
mejor temporada para visitar, qué empacar, etc.""",
        name="WeatherAgent"
    )

    # Agente 4: Cuisine Suggestion
    cuisine_client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )
    cuisine_agent = cuisine_client.create_agent(
        instructions="""Eres un experto en gastronomía local.
Dado un destino, recomiendas platos típicos,
restaurantes populares y experiencias culinarias.""",
        name="CuisineExpert"
    )

    # Agente 5: Itinerary Planner
    itinerary_client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    )
    itinerary_planner_agent = itinerary_client.create_agent(
        instructions="""Eres un planificador de viajes experto.
Recibes información sobre destinos, clima y comida, y creas
un itinerario detallado de viaje día por día.""",
        name="ItineraryPlanner"
    )

    return {
        'location_picker': location_picker_agent,
        'destination_recommender': destination_recommender_agent,
        'weather': weather_agent,
        'cuisine': cuisine_agent,
        'itinerary_planner': itinerary_planner_agent,
        'clients': [
            location_client,
            destination_client,
            weather_client,
            cuisine_client,
            itinerary_client
        ]
    }


def create_executors(agents):
    """Factory para crear executors con acceso a agentes"""

    @executor(id="LocationSelector")
    async def location_selector(user_query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[1/5] Location Selector procesando...")
        response = await agents['location_picker'].run(user_query)
        result = str(response)
        print(f"      Destino seleccionado: {result[:100]}...")
        await ctx.send_message(result)

    @executor(id="DestinationRecommender")
    async def destination_recommender(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[2a/5] Destination Recommender trabajando...")
        response = await agents['destination_recommender'].run(
            f"Recomienda los mejores lugares y actividades en: {location}"
        )
        result = str(response)
        print(f"       Recomendaciones listas!")
        await ctx.send_message(result)

    @executor(id="Weather")
    async def weather(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[2b/5] Weather Agent trabajando...")
        response = await agents['weather'].run(
            f"Proporciona información de clima y mejor época para viajar a: {location}"
        )
        result = str(response)
        print(f"       Información del clima lista!")
        await ctx.send_message(result)

    @executor(id="CuisineSuggestion")
    async def cuisine_suggestion(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[2c/5] Cuisine Expert trabajando...")
        response = await agents['cuisine'].run(
            f"Recomienda platos típicos y restaurantes en: {location}"
        )
        result = str(response)
        print(f"       Sugerencias culinarias listas!")
        await ctx.send_message(result)

    @executor(id="ItineraryPlanner")
    async def itinerary_planner(combined_info: list[str], ctx: WorkflowContext[str]) -> None:
        print(f"\n[3/5] Itinerary Planner creando plan...")

        destinations = combined_info[0]
        weather_info = combined_info[1]
        cuisine = combined_info[2]

        prompt = f"""
Crea un itinerario de viaje detallado basado en esta información:

DESTINOS Y ACTIVIDADES:
{destinations}

CLIMA Y MEJOR ÉPOCA:
{weather_info}

GASTRONOMÍA LOCAL:
{cuisine}

Proporciona un itinerario día por día estructurado y práctico.
"""

        response = await agents['itinerary_planner'].run(prompt)
        result = str(response)
        print(f"       ✓ Itinerario completo!")

        await ctx.yield_output(result)

    return {
        'location_selector': location_selector,
        'destination_recommender': destination_recommender,
        'weather': weather,
        'cuisine_suggestion': cuisine_suggestion,
        'itinerary_planner': itinerary_planner
    }


# ============================================================================
# PASO 2: MAIN - LO QUE FALTA EN workflow.py
# ============================================================================

async def main():
    """
    Función principal para ejecutar el workflow en PRODUCCIÓN.

    Esto es lo que DevUI hace automáticamente cuando usas workflow.py.
    """

    print("=" * 70)
    print("TRAVEL PLANNER WORKFLOW - VERSIÓN PRODUCCIÓN")
    print("=" * 70)

    # Crear credential
    async with DefaultAzureCredential() as credential:
        try:
            # Paso 1: Crear agentes
            print("\n[SETUP] Creando agentes...")
            agents_data = await create_agents(credential)
            agents = {k: v for k, v in agents_data.items() if k != 'clients'}
            clients = agents_data['clients']

            print("✓ 5 agentes creados")

            # Paso 2: Crear executors
            print("\n[SETUP] Creando executors...")
            executors = create_executors(agents)
            print("✓ 5 executors creados")

            # Paso 3: Construir workflow
            print("\n[SETUP] Construyendo workflow...")
            workflow = (
                WorkflowBuilder()
                .set_start_executor(executors['location_selector'])
                .add_fan_out_edges(
                    executors['location_selector'],
                    [
                        executors['destination_recommender'],
                        executors['weather'],
                        executors['cuisine_suggestion']
                    ]
                )
                .add_fan_in_edges(
                    [
                        executors['destination_recommender'],
                        executors['weather'],
                        executors['cuisine_suggestion']
                    ],
                    executors['itinerary_planner']
                )
                .build()
            )
            print("✓ Workflow construido")

            # Paso 4: EJECUTAR el workflow (esto DevUI lo hace por ti)
            print("\n" + "=" * 70)
            print("EJECUTANDO WORKFLOW")
            print("=" * 70)

            # Input del usuario (en DevUI viene del chat, aquí es hardcoded)
            user_input = "Quiero viajar a un lugar tropical con playas hermosas"
            print(f"\nInput del usuario: '{user_input}'")

            # Ejecutar workflow con streaming
            async for event in workflow.run_stream(user_input):
                if isinstance(event, WorkflowOutputEvent):
                    print("\n" + "=" * 70)
                    print("RESULTADO FINAL:")
                    print("=" * 70)
                    print(event.data)

            print("\n" + "=" * 70)
            print("✓ Workflow completado exitosamente")
            print("=" * 70)

        finally:
            # Paso 5: Cerrar clientes (cleanup manual)
            print("\n[CLEANUP] Cerrando clientes...")
            for client in clients:
                await client.__aexit__(None, None, None)
            print("✓ Recursos liberados")


# ============================================================================
# PASO 3: ENTRY POINT - LO QUE TAMBIÉN FALTA EN workflow.py
# ============================================================================

if __name__ == "__main__":
    """
    Entry point del script.

    workflow.py NO tiene esto porque DevUI lo importa como módulo.
    Scripts de producción SÍ necesitan esto.
    """
    asyncio.run(main())

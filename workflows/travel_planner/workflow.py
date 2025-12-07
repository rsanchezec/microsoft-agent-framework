"""
Travel Planner Workflow - Versión para DevUI

Este workflow implementa un planificador de viajes con arquitectura paralela:
- Location Selector → selecciona destino
- Fan-out a 3 agentes en paralelo:
  * Destination Recommender
  * Weather Agent
  * Cuisine Suggestion
- Fan-in → Itinerary Planner (combina todo)

Para usar con DevUI:
    devui ./workflows

IMPORTANTE: Este archivo define la variable 'workflow' que DevUI auto-descubre.
"""
import os
from dotenv import load_dotenv
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import WorkflowBuilder, WorkflowContext, executor
from agent_framework_devui import register_cleanup

load_dotenv()

# ============================================================================
# PASO 1: Crear Credential (compartido por todos los agentes)
# ============================================================================

credential = DefaultAzureCredential()

# ============================================================================
# PASO 2: Crear los 5 agentes del workflow
# ============================================================================

print("Creando agentes para Travel Planner Workflow...")

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

print("✓ 5 agentes creados para el workflow")

# ============================================================================
# PASO 3: Crear Executors (funciones del workflow)
# ============================================================================

@executor(id="LocationSelector")
async def location_selector(user_query: str, ctx: WorkflowContext[str]) -> None:
    """Selecciona el destino basado en las preferencias del usuario"""
    print(f"\n[1/5] Location Selector procesando...")
    response = await location_picker_agent.run(user_query)
    result = str(response)
    print(f"      Destino seleccionado: {result[:100]}...")
    await ctx.send_message(result)


@executor(id="DestinationRecommender")
async def destination_recommender(location: str, ctx: WorkflowContext[str]) -> None:
    """Recomienda lugares y actividades en el destino"""
    print(f"\n[2a/5] Destination Recommender trabajando...")
    response = await destination_recommender_agent.run(
        f"Recomienda los mejores lugares y actividades en: {location}"
    )
    result = str(response)
    print(f"       Recomendaciones listas!")
    await ctx.send_message(result)


@executor(id="Weather")
async def weather(location: str, ctx: WorkflowContext[str]) -> None:
    """Obtiene información del clima y mejor época para viajar"""
    print(f"\n[2b/5] Weather Agent trabajando...")
    response = await weather_agent.run(
        f"Proporciona información de clima y mejor época para viajar a: {location}"
    )
    result = str(response)
    print(f"       Información del clima lista!")
    await ctx.send_message(result)


@executor(id="CuisineSuggestion")
async def cuisine_suggestion(location: str, ctx: WorkflowContext[str]) -> None:
    """Sugiere experiencias gastronómicas locales"""
    print(f"\n[2c/5] Cuisine Expert trabajando...")
    response = await cuisine_agent.run(
        f"Recomienda platos típicos y restaurantes en: {location}"
    )
    result = str(response)
    print(f"       Sugerencias culinarias listas!")
    await ctx.send_message(result)


@executor(id="ItineraryPlanner")
async def itinerary_planner(combined_info: list[str], ctx: WorkflowContext[str]) -> None:
    """Crea el itinerario final combinando toda la información"""
    print(f"\n[3/5] Itinerary Planner creando plan...")

    # Combinar toda la información
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

    response = await itinerary_planner_agent.run(prompt)
    result = str(response)
    print(f"       ✓ Itinerario completo!")

    # Yield final output
    await ctx.yield_output(result)


# ============================================================================
# PASO 4: Construir el Workflow (Arquitectura Paralela)
# ============================================================================

print("\nConstruyendo workflow con arquitectura paralela...")

# IMPORTANTE: Esta variable DEBE llamarse 'workflow' para DevUI
workflow = (
    WorkflowBuilder()
    .set_start_executor(location_selector)
    .add_fan_out_edges(
        location_selector,
        [destination_recommender, weather, cuisine_suggestion]  # Ejecución PARALELA
    )
    .add_fan_in_edges(
        [destination_recommender, weather, cuisine_suggestion],  # Combina resultados
        itinerary_planner
    )
    .build()
)

print("✓ Workflow construido:")
print("  LocationSelector → [DestinationRecommender, Weather, CuisineSuggestion] → ItineraryPlanner")

# ============================================================================
# PASO 5: Registrar Cleanup
# ============================================================================

# Registrar cleanup para cerrar el credential cuando DevUI termine
register_cleanup(workflow, credential.close)

print("\n✓ Travel Planner Workflow listo para DevUI")
print("  Nombre: TravelPlanner")
print("  Agentes: 5")
print("  Patrón: Fan-out/Fan-in (Paralelo)")

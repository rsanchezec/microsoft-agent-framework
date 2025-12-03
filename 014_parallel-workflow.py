import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import WorkflowBuilder, WorkflowContext, WorkflowOutputEvent, executor, WorkflowViz
from typing import Optional

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("Project Endpoint: ", AZURE_ENDPOINT)
print("Model: ", AZURE_MODEL)


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
        should_cleanup_agent=True
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


def create_location_selector_executor(location_picker_agent):
    """Factory para crear el executor del location selector con acceso al agente"""
    @executor(id="LocationSelector")
    async def location_selector(user_query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[LOCATION SELECTOR] Procesando consulta: {user_query}")
        response = await location_picker_agent.run(user_query)
        result = str(response)
        print(f"[LOCATION SELECTOR] Ubicación seleccionada: {result[:100]}...")
        await ctx.send_message(result)
    return location_selector


def create_destination_recommender_executor(destination_recommender_agent):
    """Factory para crear el executor del destination recommender con acceso al agente"""
    @executor(id="DestinationRecommender")
    async def destination_recommender(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[DESTINATION RECOMMENDER] Recomendando destinos para: {location[:50]}...")
        response = await destination_recommender_agent.run(location)
        result = str(response)
        print(f"[DESTINATION RECOMMENDER] Destinos recomendados!")
        await ctx.send_message(result)
    return destination_recommender


def create_weather_executor(weather_agent):
    """Factory para crear el executor del weather con acceso al agente"""
    @executor(id="Weather")
    async def weather(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[WEATHER] Obteniendo información del clima para: {location[:50]}...")
        response = await weather_agent.run(location)
        result = str(response)
        print(f"[WEATHER] Información del clima obtenida!")
        await ctx.send_message(result)
    return weather


def create_cuisine_suggestion_executor(cuisine_suggestion_agent):
    """Factory para crear el executor del cuisine suggestion con acceso al agente"""
    @executor(id="CuisineSuggestion")
    async def cuisine_suggestion(location: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[CUISINE SUGGESTION] Sugiriendo cocina local para: {location[:50]}...")
        response = await cuisine_suggestion_agent.run(location)
        result = str(response)
        print(f"[CUISINE SUGGESTION] Sugerencias de cocina obtenidas!")
        await ctx.send_message(result)
    return cuisine_suggestion


def create_itinerary_planner_executor(itinerary_planner_agent):
    """Factory para crear el executor del itinerary planner con acceso al agente"""
    @executor(id="ItineraryPlanner")
    async def itinerary_planner(results: list[str], ctx: WorkflowContext[str]) -> None:
        print(f"\n[ITINERARY PLANNER] Creando itinerario con {len(results)} resultados...")
        combined_results = "\n\n".join(results)
        prompt = f"Basándote en esta información, crea un itinerario detallado de viaje:\n\n{combined_results}"
        response = await itinerary_planner_agent.run(prompt)
        result = str(response)
        print(f"[ITINERARY PLANNER] Itinerario completado!")
        await ctx.yield_output(result)
    return itinerary_planner


async def main():
    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            # ===================================================================
            # CREACIÓN DE AGENTES
            # ===================================================================
            print("=" * 60)
            print("CREANDO LOCATION PICKER AGENT...")
            location_picker_client, location_picker_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un asistente útil que ayuda a los usuarios a elegir una ubicación para sus vacaciones.",
                name="Location-Picker-Agent"
            )
            clients.append(location_picker_client)

            print("=" * 60)
            print("CREANDO DESTINATION RECOMMENDER AGENT...")
            destination_recommender_client, destination_recommender_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un experto en viajes que proporciona recomendaciones de vacaciones personalizadas basadas en las preferencias del usuario y las ubicaciones.",
                name="Destination-Recommender-Agent"
            )
            clients.append(destination_recommender_client)

            print("=" * 60)
            print("CREANDO WEATHER AGENT...")
            weather_client, weather_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un experto en meteorología que proporciona información precisa y actualizada sobre el clima para varias ubicaciones seleccionadas.",
                name="Weather-Agent"
            )
            clients.append(weather_client)

            print("=" * 60)
            print("CREANDO CUISINE SUGGESTION AGENT...")
            cuisine_suggestion_client, cuisine_suggestion_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un experto culinario que sugiere cocina local popular y opciones gastronómicas basadas en los destinos de vacaciones seleccionados.",
                name="Cuisine-Suggestion-Agent"
            )
            clients.append(cuisine_suggestion_client)

            print("=" * 60)
            print("CREANDO ITINERARY PLANNER AGENT...")
            itinerary_planner_client, itinerary_planner_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un experto en planificación de itinerarios que crea itinerarios de viaje detallados basados en las preferencias del usuario, destinos seleccionados, condiciones climáticas y opciones de cocina local.",
                name="Itinerary-Planner-Agent"
            )
            clients.append(itinerary_planner_client)

            # ===================================================================
            # CONSTRUCCIÓN DEL WORKFLOW PARALELO
            # ===================================================================
            print("\n" + "=" * 60)
            print("CONSTRUYENDO WORKFLOW PARALELO...")

            # Crear executors con acceso a los agentes
            location_selector_exec = create_location_selector_executor(location_picker_agent)
            destination_recommender_exec = create_destination_recommender_executor(destination_recommender_agent)
            weather_exec = create_weather_executor(weather_agent)
            cuisine_suggestion_exec = create_cuisine_suggestion_executor(cuisine_suggestion_agent)
            itinerary_planner_exec = create_itinerary_planner_executor(itinerary_planner_agent)

            # Construir el workflow con fan-out y fan-in
            workflow = (
                WorkflowBuilder()
                .set_start_executor(location_selector_exec)
                .add_fan_out_edges(
                    location_selector_exec,
                    [destination_recommender_exec, weather_exec, cuisine_suggestion_exec]
                )
                .add_fan_in_edges(
                    [destination_recommender_exec, weather_exec, cuisine_suggestion_exec],
                    itinerary_planner_exec
                )
                .build()
            )

            # Visualizar el workflow en consola
            viz = WorkflowViz(workflow)
            mermaid_content = viz.to_mermaid()
            print("\nDiagrama del Workflow Paralelo (Mermaid):")
            print("```mermaid")
            print(mermaid_content)
            print("```")

            # ===================================================================
            # EJECUCIÓN DEL WORKFLOW
            # ===================================================================
            print("\n" + "=" * 60)
            print("EJECUTANDO WORKFLOW PARALELO...")
            print("=" * 60)

            query = "Ayúdame a planear unas vacaciones a España con los siguientes detalles: Me encantan los sitios históricos, prefiero clima cálido y disfruto probar comida local."

            async for event in workflow.run_stream(query):
                if isinstance(event, WorkflowOutputEvent):
                    print("\n" + "=" * 60)
                    print("RESULTADO FINAL DEL WORKFLOW:")
                    print("=" * 60)
                    print(event.data)
                    print("=" * 60)

        finally:
            # Cerrar todos los clientes al final
            print("\n" + "=" * 60)
            print("CERRANDO CLIENTES...")
            for client in clients:
                await client.__aexit__(None, None, None)
            print("[OK] Todos los clientes cerrados correctamente")


if __name__ == "__main__":
    asyncio.run(main())

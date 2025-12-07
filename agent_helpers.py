"""
Módulo con funciones helper para trabajar con agentes en Azure AI Foundry.
Incluye funciones para buscar agentes por nombre, listar agentes, etc.
"""
from typing import Optional
from agent_framework_azure_ai import AzureAIAgentClient


async def get_agent_id_by_name(client: AzureAIAgentClient, agent_name: str) -> Optional[str]:
    """
    Busca un agente por nombre y retorna su ID.

    Args:
        client: Cliente de AzureAIAgentClient
        agent_name: Nombre del agente a buscar

    Returns:
        El agent_id (formato "asst_xxx...") si se encuentra, None si no existe

    Example:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agent_id = await get_agent_id_by_name(client, "MyAgent")
            if agent_id:
                print(f"Agent ID: {agent_id}")
    """
    try:
        # La API no soporta búsqueda directa por nombre, necesitamos listar y buscar
        agents_paged = client.agents_client.list_agents(limit=100)

        async for agent in agents_paged:
            if agent.name == agent_name:
                return agent.id

        return None
    except Exception as e:
        print(f"Error al buscar agente '{agent_name}': {e}")
        return None


async def list_all_agents(client: AzureAIAgentClient, limit: int = 100, order: str = "desc"):
    """
    Lista todos los agentes disponibles en Azure AI Foundry.

    Args:
        client: Cliente de AzureAIAgentClient
        limit: Número máximo de agentes por página (1-100, default: 100)
        order: Orden por fecha de creación - "asc" o "desc" (default: "desc")

    Returns:
        Lista de diccionarios con información de cada agente

    Example:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agents = await list_all_agents(client)
            for agent in agents:
                print(f"{agent['name']}: {agent['id']}")
    """
    agents_list = []

    agents_paged = client.agents_client.list_agents(limit=limit, order=order)

    async for agent in agents_paged:
        agents_list.append({
            "name": agent.name,
            "id": agent.id,
            "type": agent.object,
            "model": agent.model,
            "created_at": str(agent.created_at)
        })

    return agents_list


async def find_agents_by_pattern(client: AzureAIAgentClient, pattern: str, case_sensitive: bool = False):
    """
    Encuentra agentes cuyos nombres coincidan con un patrón.

    Args:
        client: Cliente de AzureAIAgentClient
        pattern: Patrón a buscar en los nombres de agentes
        case_sensitive: Si la búsqueda distingue mayúsculas/minúsculas (default: False)

    Returns:
        Lista de diccionarios con información de agentes que coinciden

    Example:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agents = await find_agents_by_pattern(client, "joke")
            # Encuentra "Joker", "JokeBot", etc.
    """
    all_agents = await list_all_agents(client)

    if not case_sensitive:
        pattern = pattern.lower()

    matching_agents = [
        agent for agent in all_agents
        if pattern in (agent["name"] if case_sensitive else agent["name"].lower())
    ]

    return matching_agents


async def agent_exists(client: AzureAIAgentClient, agent_name: str) -> bool:
    """
    Verifica si un agente con el nombre especificado existe.

    Args:
        client: Cliente de AzureAIAgentClient
        agent_name: Nombre del agente a verificar

    Returns:
        True si el agente existe, False si no

    Example:
        async with AzureAIAgentClient(async_credential=credential) as client:
            if await agent_exists(client, "MyAgent"):
                print("El agente existe")
    """
    agent_id = await get_agent_id_by_name(client, agent_name)
    return agent_id is not None


async def get_agent_info(client: AzureAIAgentClient, agent_name: str) -> Optional[dict]:
    """
    Obtiene información completa de un agente por nombre.

    Args:
        client: Cliente de AzureAIAgentClient
        agent_name: Nombre del agente

    Returns:
        Diccionario con información del agente, o None si no existe

    Example:
        async with AzureAIAgentClient(async_credential=credential) as client:
            info = await get_agent_info(client, "MyAgent")
            if info:
                print(f"ID: {info['id']}, Versión: {info['version']}")
    """
    try:
        # La API no soporta búsqueda directa por nombre, necesitamos listar y buscar
        agents_paged = client.agents_client.list_agents(limit=100)

        async for agent in agents_paged:
            if agent.name == agent_name:
                return {
                    "name": agent.name,
                    "id": agent.id,
                    "type": agent.object,
                    "model": agent.model,
                    "created_at": str(agent.created_at)
                }

        return None
    except Exception as e:
        print(f"Error al obtener información del agente '{agent_name}': {e}")
        return None

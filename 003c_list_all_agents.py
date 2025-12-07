"""
Script que demuestra cómo listar TODOS los agentes disponibles en Azure AI Foundry.
Útil para descubrir qué agentes tienes y sus IDs/nombres.
"""
import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:

            print("=" * 80)
            print("LISTADO DE TODOS LOS AGENTES EN AZURE AI FOUNDRY")
            print("=" * 80)
            print()

            # Listar todos los agentes usando el agents_client
            agents_paged = client.agents_client.list_agents(
                limit=100,  # Máximo por página
                order="desc"  # Más recientes primero
            )

            agent_count = 0

            async for agent in agents_paged:
                agent_count += 1
                print(f"Agente #{agent_count}:")
                print(f"  Nombre:     {agent.name}")
                print(f"  ID:         {agent.id}")
                print(f"  Tipo:       {agent.object}")
                print(f"  Modelo:     {agent.model}")
                print(f"  Creado:     {agent.created_at}")
                print()

            if agent_count == 0:
                print("No se encontraron agentes.")
                print("Crea uno usando el script 001_createandrunanagent.py")
            else:
                print("=" * 80)
                print(f"Total de agentes encontrados: {agent_count}")
                print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

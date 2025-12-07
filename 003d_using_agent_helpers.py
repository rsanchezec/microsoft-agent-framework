"""
Script de ejemplo que demuestra cómo usar el módulo agent_helpers.py
para trabajar con agentes usando nombres en lugar de IDs.
"""
import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_helpers import (
    get_agent_id_by_name,
    list_all_agents,
    find_agents_by_pattern,
    agent_exists,
    get_agent_info
)

load_dotenv()

AGENT_NAME = "Joker"


async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:

            print("=" * 80)
            print("DEMO: Uso de Agent Helpers")
            print("=" * 80)
            print()

            # 1. Verificar si el agente existe
            print(f"1. Verificando si existe el agente '{AGENT_NAME}'...")
            exists = await agent_exists(client, AGENT_NAME)
            print(f"   Resultado: {exists}")
            print()

            if not exists:
                print(f"El agente '{AGENT_NAME}' no existe.")
                print("Creando uno con el script 001_createandrunanagent.py...")
                return

            # 2. Obtener información completa del agente
            print(f"2. Obteniendo informacion del agente '{AGENT_NAME}'...")
            info = await get_agent_info(client, AGENT_NAME)
            if info:
                print(f"   Nombre:   {info['name']}")
                print(f"   ID:       {info['id']}")
                print(f"   Tipo:     {info['type']}")
                print(f"   Modelo:   {info['model']}")
                print(f"   Creado:   {info['created_at']}")
            print()

            # 3. Obtener solo el ID del agente
            print(f"3. Obteniendo ID del agente '{AGENT_NAME}'...")
            agent_id = await get_agent_id_by_name(client, AGENT_NAME)
            print(f"   Agent ID: {agent_id}")
            print()

            # 4. Listar todos los agentes
            print("4. Listando todos los agentes disponibles...")
            all_agents = await list_all_agents(client)
            print(f"   Total de agentes: {len(all_agents)}")
            for idx, agent in enumerate(all_agents, 1):
                print(f"   {idx}. {agent['name']} ({agent['id']})")
            print()

            # 5. Buscar agentes por patron
            print("5. Buscando agentes con patron 'joke'...")
            matching_agents = await find_agents_by_pattern(client, "joke")
            if matching_agents:
                print(f"   Encontrados {len(matching_agents)} agentes:")
                for agent in matching_agents:
                    print(f"   - {agent['name']} ({agent['id']})")
            else:
                print("   No se encontraron agentes con ese patron.")
            print()

            # 6. Usar el agente (ejemplo de conversacion)
            print("6. Usando el agente para una conversacion...")
            async with AzureAIAgentClient(
                async_credential=credential,
                agent_id=agent_id
            ) as agent_client:

                agent = agent_client.create_agent(
                    instructions="Eres un asistente util.",
                    name=AGENT_NAME
                )

                result = await agent.run("Cuentame un chiste corto.")
                print(f"   Usuario: Cuentame un chiste corto.")
                print(f"   Agente: {result.text}")
            print()

            print("=" * 80)
            print("Demo completada exitosamente")
            print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

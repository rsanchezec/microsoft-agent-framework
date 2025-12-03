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

def create_researcher_executor(researcher_agent):
    """Factory para crear el executor del researcher con acceso al agente"""
    @executor(id="run_researcher_agent")
    async def run_researcher_agent(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[RESEARCHER] Investigando: {query}")
        response = await researcher_agent.run(query)
        result = str(response)
        print(f"[RESEARCHER] Resultado: {result[:100]}...")
        await ctx.send_message(result)
    return run_researcher_agent

def create_writer_executor(writer_agent):
    """Factory para crear el executor del writer con acceso al agente"""
    @executor(id="run_writer_agent")
    async def run_writer_agent(research_data: str, ctx: WorkflowContext[str]) -> None:
        prompt = f"Basándote en esta investigación, escribe un ensayo:\n\n{research_data}"
        print(f"\n[WRITER] Escribiendo ensayo basado en investigación...")
        response = await writer_agent.run(prompt)
        result = str(response)
        print(f"[WRITER] Ensayo completado!")
        await ctx.yield_output(result)
    return run_writer_agent


async def main():
    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            print("=" * 60)
            print("CREANDO RESEARCHER AGENT...")
            researcher_client, researcher_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un investigador experto. Tu tarea es recopilar información y aportar ideas sobre un tema determinado. "
                              "Debes utilizar fuentes confiables y presentar la información de manera clara y concisa.",
                name="Researcher Agent"
            )
            clients.append(researcher_client)

            print("=" * 60)
            print("CREANDO WRITER AGENT...")
            writer_client, writer_agent = await create_and_initialize_agent(
                credential=credential,
                instructions="Eres un escritor creativo. Tu tarea es escribir un ensayo sobre un tema determinado. "
                              "Debes centrarte en la claridad, la coherencia y una narración atractiva.",
                name="Writer Agent"
            )
            clients.append(writer_client)

            # Crear executors con acceso a los agentes
            print("\n" + "=" * 60)
            print("CONSTRUYENDO WORKFLOW...")
            researcher_executor = create_researcher_executor(researcher_agent)
            writer_executor = create_writer_executor(writer_agent)

            # Construir el workflow
            workflow = (
                WorkflowBuilder()
                .add_edge(researcher_executor, writer_executor)
                .set_start_executor(researcher_executor)
                .build()
            )

            # Visualizar el workflow en consola
            viz = WorkflowViz(workflow)
            mermaid_content = viz.to_mermaid()
            print("\nDiagrama del Workflow (Mermaid):")
            print("```mermaid")
            print(mermaid_content)
            print("```")

            # Ejecutar el workflow
            print("\n" + "=" * 60)
            print("EJECUTANDO WORKFLOW...")
            print("=" * 60)

            query = "Investiga el impacto de la IA en la sociedad moderna"
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

if __name__ == "__main__":
    asyncio.run(main())
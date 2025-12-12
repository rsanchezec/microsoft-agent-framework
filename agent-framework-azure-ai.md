# agent-framework-azure-ai

Librería oficial de Microsoft para integrar Azure AI con el Agent Framework, permitiendo construir agentes inteligentes y workflows multi-agente con Azure AI Foundry.

## 🔗 Enlaces Rápidos

### 📚 Documentación Principal
- **[🎯 agent-framework-azure-ai - Ejemplos Python](https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start)** - Tutorial con ejemplos completos
- **[Create and Run Azure AI Agent](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/run-agent)** - Crear y ejecutar agentes
- **[Azure AI Foundry Agents Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent)** - Guía específica Azure AI
- **[API Reference - AzureAIAgentClient](https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework.azure.azureaiagentclient?view=agent-framework-python-latest)** - Referencia API completa

### 📦 Repositorios y Paquetes
- **[PyPI - agent-framework-azure-ai](https://pypi.org/project/agent-framework-azure-ai/)** - Este paquete (Azure AI)
- **[GitHub - microsoft/agent-framework](https://github.com/microsoft/agent-framework)** - Repositorio oficial
- **[PyPI - agent-framework-core](https://pypi.org/project/agent-framework-core/)** - Paquete base
- **[PyPI - agent-framework](https://pypi.org/project/agent-framework/)** - Paquete completo

### 🎓 Tutoriales y Guías
- **[Workflows Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/core-concepts/workflows)** - Guía de workflows
- **[Using Agents in Workflows](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/using-agents)** - Agentes en workflows
- **[Agent Observability](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-observability)** - Observabilidad

### 🔄 Migraciones
- **[From Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel)** - Migrar desde Semantic Kernel
- **[From AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)** - Migrar desde AutoGen

### ☁️ Azure AI Foundry
- **[Azure AI Foundry Portal](https://ai.azure.com/)** - Portal web
- **[Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)** - SDK Python
- **[Azure AI Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?view=foundry-classic)** - Inicio rápido

---

## Información General

- **Paquete PyPI**: `agent-framework-azure-ai`
- **Versión actual**: `1.0.0b251120` (Beta - 21 de noviembre de 2025)
- **Licencia**: MIT
- **Mantenedor**: Microsoft
- **Estado**: Beta (Development Status: 4)
- **Soporte Python**: 3.10, 3.11, 3.12, 3.13, 3.14

## Instalación

```bash
pip install agent-framework-azure-ai --pre
```

### Instalación con dependencias completas

```bash
pip install agent-framework-azure-ai azure-identity aiofiles --pre
```

## ¿Para qué sirve?

`agent-framework-azure-ai` es el cliente especializado de Azure AI para el Microsoft Agent Framework. Permite:

### 1. **Crear y Gestionar Agentes Inteligentes**
- Construir agentes conversacionales con Azure OpenAI
- Integrar modelos de Azure AI Foundry
- Gestionar conversaciones multi-turno

### 2. **Workflows Multi-Agente**
- Orquestar múltiples agentes en flujos de trabajo complejos
- Patrones secuenciales, paralelos y condicionales
- Streaming de respuestas en tiempo real

### 3. **Integración con Azure AI Foundry**
- Conexión nativa con proyectos de Azure AI Foundry
- Acceso a modelos desplegados en Azure
- Observabilidad con Application Insights

### 4. **Autenticación y Seguridad**
- Autenticación con Azure CLI
- Managed Identity
- Tokens de Azure Active Directory

## Características Principales

✅ **Cliente Azure AI nativo** para Agent Framework
✅ **Workflows complejos** con WorkflowBuilder
✅ **Streaming en tiempo real** de respuestas
✅ **Observabilidad automática** con Azure Monitor
✅ **Checkpointing** para guardar y resumir estados
✅ **Human-in-the-loop** para aprobaciones
✅ **Ejecutores personalizados** (clases y funciones)
✅ **Integración Azure OpenAI** y modelos Foundry

## Ejemplos de Uso

### 1. Cliente Básico

```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def main():
    client = AzureAIAgentClient(
        async_credential=AzureCliCredential(),
        project_endpoint="https://your-project.foundry.azure.com",
        model_deployment_name="gpt-4o"
    )
```

### 2. Crear Agente Simple

```python
import asyncio
from agent_framework import ChatAgent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def main():
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful assistant."
        ) as agent,
    ):
        result = await agent.run("Tell me about Azure AI")
        print(result.text)

asyncio.run(main())
```

### 3. Workflow Multi-Agente

```python
from agent_framework import WorkflowBuilder, AgentRunUpdateEvent, WorkflowOutputEvent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def main():
    client = AzureAIAgentClient(async_credential=AzureCliCredential())

    writer = await client.create_agent(
        instructions="You are a content writer.",
        name="writer"
    )

    reviewer = await client.create_agent(
        instructions="You are a content reviewer.",
        name="reviewer"
    )

    # Workflow: writer -> reviewer
    workflow = (WorkflowBuilder()
        .set_start_executor(writer)
        .add_edge(writer, reviewer)
        .build())

    # Ejecutar con streaming
    async for event in workflow.run_stream("Create a slogan for AI"):
        if isinstance(event, AgentRunUpdateEvent):
            print(f"{event.executor_id}: {event.data}")
        elif isinstance(event, WorkflowOutputEvent):
            print(f"Final: {event.data}")
```

### 4. Configurar Observabilidad

```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity import AzureCliCredential

client = AzureAIAgentClient(
    credential=AzureCliCredential(),
    project_endpoint="https://your-project.foundry.azure.com"
)

# Configurar Application Insights automáticamente
await client.setup_azure_ai_observability()
```

## Variables de Entorno

```bash
# Endpoint del proyecto Azure AI Foundry
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.foundry.azure.com/"

# Nombre del deployment del modelo
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

# Alternativamente, para Azure OpenAI directo
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"
```

## 📖 Documentación Oficial Completa

### 🎯 Microsoft Learn - Agent Framework

#### Tutoriales y Guías
- **[Microsoft Agent Framework - Página Principal](https://learn.microsoft.com/en-us/agent-framework/)** - Documentación principal
- **[Quick Start Tutorial](https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start)** - Tutorial de inicio rápido
- **[Create and Run an Agent](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/run-agent)** - Crear y ejecutar agentes
- **[Simple Sequential Workflow](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/simple-sequential-workflow)** - Workflow secuencial
- **[Agents in Workflows](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/agents-in-workflows)** - Tutorial completo
- **[Workflow with Branching Logic](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/workflow-with-branching-logic)** - Lógica condicional
- **[Checkpointing and Resuming](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming)** - Guardar estado

#### Guías de Usuario
- **[Workflows Core Concepts](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/core-concepts/workflows)** - Conceptos básicos
- **[Using Agents in Workflows](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/using-agents)** - Usar agentes
- **[Concurrent Orchestration](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/concurrent)** - Ejecución paralela
- **[Sequential Orchestration](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/sequential)** - Ejecución secuencial
- **[Agent Observability](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-observability)** - Observabilidad y tracing
- **[Workflows as Agents](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/as-agents)** - Workflows como agentes

#### Migraciones
- **[Migration from Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel)** - Guía de migración
- **[Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)** - Desde AutoGen

#### API Reference
- **[AzureAIAgentClient API Reference](https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework.azure.azureaiagentclient?view=agent-framework-python-latest)** - API completa
- **[agent_framework package](https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework?view=agent-framework-python-latest)** - Paquete principal

### ☁️ Azure AI Foundry

#### Documentación
- **[Azure AI Foundry - Inicio](https://learn.microsoft.com/en-us/azure/ai-foundry/)** - Página principal
- **[Azure AI Foundry Portal](https://ai.azure.com/)** - Portal web oficial
- **[Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?view=foundry-classic)** - Inicio rápido
- **[Agent Framework Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-framework)** - Conceptos

#### Python SDKs
- **[Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)** - SDK para proyectos
- **[Azure AI Agents SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python)** - SDK para agentes
- **[azure-ai-projects PyPI](https://pypi.org/project/azure-ai-projects/)** - Paquete PyPI

#### Herramientas y Recursos
- **[Function Calling](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/function-calling)** - Uso de funciones
- **[Azure Functions Samples](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/azure-functions-samples)** - Ejemplos
- **[Agent Evaluation SDK](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)** - Evaluación

### 📦 PyPI y Repositorios

#### Paquetes Python
- **[agent-framework-azure-ai](https://pypi.org/project/agent-framework-azure-ai/)** - **Este paquete principal** (Azure AI Integration)
- **[agent-framework-core](https://pypi.org/project/agent-framework-core/)** - Paquete core (dependencia)
- **[agent-framework](https://pypi.org/project/agent-framework/)** - Paquete completo
- **[azure-ai-agents](https://pypi.org/project/azure-ai-agents/)** - Azure AI Agents Service
- **[azure-ai-projects](https://pypi.org/project/azure-ai-projects/)** - Azure AI Foundry Projects
- **[azure-identity](https://pypi.org/project/azure-identity/)** - Autenticación Azure

#### GitHub
- **[microsoft/agent-framework](https://github.com/microsoft/agent-framework)** - Repositorio principal
- **[Agent Framework Issues](https://github.com/microsoft/agent-framework/issues)** - Reportar bugs
- **[Agent Framework Discussions](https://github.com/microsoft/agent-framework/discussions)** - Discusiones

### 🎥 Recursos Adicionales

- **[Azure AI Samples](https://github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo)** - Ejemplos empresariales
- **[Azure AI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)** - Docs generales
- **[Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)** - Azure OpenAI

## Paquetes Relacionados

| Paquete | Descripción |
|---------|-------------|
| `agent-framework-core` | Core del framework con abstracciones base |
| `agent-framework` | Framework completo para agentes |
| `agent-framework-azure-ai` | **Integración específica Azure AI (este paquete)** |
| `azure-ai-agents` | Cliente Azure AI Agents Service |
| `azure-ai-projects` | Cliente Azure AI Foundry Projects |
| `azure-identity` | Autenticación Azure |

## Arquitectura del Framework

```
agent-framework-core (base)
    ├── agent-framework (framework completo)
    ├── agent-framework-azure-ai (Azure AI - este paquete)
    ├── agent-framework-openai (OpenAI)
    └── agent-framework-ag-ui (UI components)
```

## Diferencias con otros clientes

| Cliente | Import | Uso |
|---------|--------|-----|
| `AzureAIAgentClient` | `from agent_framework_azure_ai import` | **Azure AI Foundry (recomendado)** |
| `AzureOpenAIChatClient` | `from agent_framework.azure import` | Azure OpenAI directo |
| `OpenAIChatClient` | `from agent_framework.openai import` | OpenAI API |

## Casos de Uso

### ✅ Usa `agent-framework-azure-ai` cuando:
- Trabajas con proyectos Azure AI Foundry
- Necesitas workflows multi-agente complejos
- Requieres observabilidad con Application Insights
- Usas autenticación Azure (CLI, Managed Identity)
- Necesitas checkpointing y estados persistentes

### ⚠️ Considera alternativas si:
- Solo necesitas llamadas simples a Azure OpenAI → `azure-openai`
- Trabajas únicamente con OpenAI API → `openai`
- Necesitas funcionalidad más básica → `azure-ai-projects`

## Requisitos del Sistema

- **Python**: >= 3.10
- **Sistema Operativo**: Windows, Linux, macOS
- **Azure**: Suscripción activa con Azure AI Foundry
- **Autenticación**: Azure CLI instalado o credenciales configuradas

## Instalación de Desarrollo

```bash
# Instalar todas las dependencias de desarrollo
pip install agent-framework-azure-ai azure-identity azure-ai-evaluation aiofiles --pre

# Para observabilidad
pip install azure-monitor-opentelemetry
```

## Soporte y Comunidad

- **Issues**: [GitHub Issues](https://github.com/microsoft/agent-framework/issues)
- **Licencia**: MIT
- **Changelog**: Disponible en PyPI releases

## Ejemplo Completo de Producción

```python
import asyncio
import os
from contextlib import AsyncExitStack
from agent_framework import ChatAgent, WorkflowBuilder, AgentRunUpdateEvent, WorkflowOutputEvent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def main():
    async with AsyncExitStack() as stack:
        # Credenciales
        credential = await stack.enter_async_context(AzureCliCredential())

        # Cliente Azure AI
        client = AzureAIAgentClient(
            async_credential=credential,
            project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
        )

        # Configurar observabilidad
        await client.setup_azure_ai_observability()

        # Crear agentes
        writer = await stack.enter_async_context(
            client.create_agent(
                instructions="You are an expert content writer.",
                name="content_writer"
            )
        )

        reviewer = await stack.enter_async_context(
            client.create_agent(
                instructions="You are a critical content reviewer.",
                name="content_reviewer"
            )
        )

        # Workflow
        workflow = (WorkflowBuilder()
            .set_start_executor(writer)
            .add_edge(writer, reviewer)
            .build())

        # Ejecutar
        print("Starting workflow...")
        async for event in workflow.run_stream("Write a short article about AI agents"):
            if isinstance(event, AgentRunUpdateEvent):
                print(f"[{event.executor_id}] {event.data}", end="", flush=True)
            elif isinstance(event, WorkflowOutputEvent):
                print(f"\n\n=== Final Output ===\n{event.data}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

**Última actualización**: Diciembre 2025
**Versión del documento**: 1.0
**Mantenido por**: Microsoft Agent Framework Team

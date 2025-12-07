# 🚀 Curso de Microsoft Agent Framework con Azure AI Foundry

Repositorio de aprendizaje del **Microsoft Agent Framework** usando **Azure AI Foundry** para crear agentes de IA persistentes, colaborativos y con capacidades avanzadas.

---

## 📚 Índice

- [Requisitos Previos](#-requisitos-previos)
- [Configuración Inicial](#-configuración-inicial)
- [Estructura del Curso](#-estructura-del-curso)
- [Scripts del Curso](#-scripts-del-curso)
  - [001: Crear y Ejecutar un Agente](#001_createandrunanagentpy)
  - [002: Reutilizar Agente Existente](#002_reuseexistingagentpy)
  - [003: Conversación Persistente](#003_persistentconversationpy)
  - [003b: Conversación por Nombre de Agente](#003b_persistentconversation_by_namepy)
  - [003c: Listar Todos los Agentes](#003c_list_all_agentspy)
  - [003d: Uso de Agent Helpers](#003d_using_agent_helperspy)
  - [004: Continuar Conversación](#004_continuethreadconversationpy)
  - [005: Uso de Imágenes con Agentes](#005_usingimageswithanagentpy)
  - [008: Colaboración Multi-Agente](#008_multi_agent_collaboration_fixedpy)
  - [009: Agentes como Herramientas (Closures)](#009_agents_using_other_agents_as_toolspy)
  - [010: Agentes como Herramientas (Partial)](#010_agents_using_other_agents_as_tools_with_partialpy)
  - [011: API WebSocket con Agent Framework](#011_assistant_websocket_agent_frameworkpy)
  - [012: Workflow Secuencial (Cierre Automático)](#012_sequential_workflowpy)
  - [013: Workflow Secuencial (Cierre Manual)](#013_sequential_workflowpy)
  - [014: Workflow Paralelo (Fan-out/Fan-in)](#014_parallel-workflowpy)
  - [015: Agentes con MCP Tools](#015_agent_with_mcp_toolspy)
  - [016: Context Providers](#016_context_providerspy)
  - [017: Middleware](#017_middlewarepy)
  - [018: Observabilidad y Telemetría](#018_observability_telemetrypy)
  - [019: Workflows Condicionales](#019_conditional_workflowspy)
  - [020: Group Chat Workflows](#020_group_chat_workflowpy)
  - [021: Supervisor Pattern](#021_supervisor_patternpy)
  - [022: Visualización y Debugging de Workflows](#022_workflow_visualization_debuggingpy)
  - [agent_helpers: Utilidades para Gestión de Agentes](#agent_helperspy)
- [DevUI para Debugging Interactivo](#-devui-para-debugging-interactivo)
  - [Agentes para DevUI](#agentes-para-devui)
  - [Workflows para DevUI](#workflows-para-devui)
- [Conceptos Clave](#-conceptos-clave)
- [Problemas Comunes](#-problemas-comunes-y-soluciones)
- [Recursos Adicionales](#-recursos-adicionales)

---

## 🔧 Requisitos Previos

- **Python 3.10+**
- **Azure Subscription** con acceso a Azure AI Foundry
- **Paquetes necesarios:**
  ```bash
  pip install agent-framework-azure-ai
  pip install azure-identity
  pip install python-dotenv
  pip install httpx

  # Para el script 011 (WebSocket API)
  pip install fastapi
  pip install uvicorn
  pip install websockets
  ```

---

## ⚙️ Configuración Inicial

### 1. Archivo `.env`

Crea un archivo `.env` en la raíz del proyecto:

```env
AZURE_AI_PROJECT_ENDPOINT=https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

**⚠️ Importante:**
- Usa `AZURE_AI_PROJECT_ENDPOINT` (no `AZURE_OPENAI_ENDPOINT`)
- Usa `AZURE_AI_MODEL_DEPLOYMENT_NAME` (no `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`)
- El endpoint es de Azure AI Foundry, no Azure OpenAI directo

### 2. Autenticación Azure

El proyecto usa `DefaultAzureCredential`, que intenta múltiples métodos:
1. Variables de entorno
2. Managed Identity
3. Visual Studio Code
4. Azure CLI (`az login`)
5. Azure PowerShell

**Recomendación:** Ejecuta `az login` antes de correr los scripts.

---

## 🏗️ Arquitectura: AIProjectClient vs Agent Framework

Este proyecto demuestra **dos enfoques diferentes** para trabajar con agentes de Azure AI. Es importante entender la diferencia de niveles de abstracción:

### 📊 Capas de Abstracción

```
┌─────────────────────────────────────────────────────────┐
│          Tu Aplicación (Frontend/Backend)               │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐     ┌──────────────────────┐
│ Agent Framework   │     │  AIProjectClient     │
│ (Capa Alta)       │     │  (Capa Media-Baja)   │
│                   │     │                      │
│ ✨ Abstracción    │     │ 🔧 Control Granular  │
│ ✨ Simplicidad    │     │ 🔧 Más Código        │
│ ✨ Polling Auto   │     │ 🔧 Polling Manual    │
└─────────┬─────────┘     └──────────┬───────────┘
          │                          │
          └──────────┬───────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │   Azure AI Foundry      │
        │   (REST API)            │
        │                         │
        │ - Agents API            │
        │ - Threads API           │
        │ - Messages API          │
        │ - Runs API              │
        └─────────────────────────┘
```

---

### 🔍 Diferencias Principales

| Aspecto | Agent Framework | AIProjectClient |
|---------|-----------------|-----------------|
| **Nivel de Abstracción** | 🔝 **Alto** - Oculta complejidad | 🔧 **Medio-Bajo** - Exposición directa a la API |
| **Facilidad de Uso** | ✨ Muy fácil - Una sola llamada | 🔧 Moderado - Múltiples pasos |
| **Código Requerido** | 📝 Mínimo (3-5 líneas) | 📜 Más verboso (10-15 líneas) |
| **Control** | ⚡ Automático (polling, estados) | 🎛️ Manual (control total) |
| **Propósito** | 🚀 Desarrollo rápido, prototipos | 🏗️ Control fino, casos complejos |

---

### 💡 Explicación Detallada

#### **Agent Framework** (Capa de Abstracción Alta)

El **Agent Framework** es una **capa de alto nivel** construida **encima** de AIProjectClient. Piensa en ella como un **wrapper inteligente** que simplifica las operaciones comunes.

**Analogía:** Es como usar un **coche automático** 🚗
- No necesitas cambiar marchas manualmente
- El sistema hace el trabajo pesado por ti
- Más fácil de aprender y usar
- Perfecto para el 90% de los casos de uso

**Características:**
```python
# ✨ UNA SOLA LLAMADA hace todo el trabajo:
result = await agent.run("Tu pregunta", thread=thread)

# Internamente hace:
# 1. Crea el mensaje
# 2. Inicia el run
# 3. Hace polling automático del estado
# 4. Espera hasta que termine
# 5. Obtiene la respuesta
# 6. Retorna el resultado
```

**Cuándo usar Agent Framework:**
- ✅ Desarrollo rápido de aplicaciones
- ✅ Prototipos y MVPs
- ✅ Casos de uso estándar
- ✅ Quieres menos código y más productividad
- ✅ No necesitas control granular de cada paso

---

#### **AIProjectClient** (Capa de Abstracción Media-Baja)

**AIProjectClient** es una **interfaz directa** a la API REST de Azure AI Foundry. Te da **control total** sobre cada paso del proceso.

**Analogía:** Es como usar un **coche manual** 🏎️
- Tienes que cambiar marchas tú mismo
- Control total sobre cada aspecto
- Más complejo pero más flexible
- Para casos avanzados o específicos

**Características:**
```python
# 🔧 CONTROL MANUAL de cada paso:

# 1. Crear mensaje manualmente
client.agents.create_message(
    thread_id=thread_id,
    role="user",
    content="Tu pregunta"
)

# 2. Iniciar run manualmente
run = client.agents.create_run(
    thread_id=thread_id,
    agent_id=agent_id
)

# 3. Hacer polling manual del estado
while run.status in ["queued", "in_progress"]:
    time.sleep(1)
    run = client.agents.get_run(thread_id=thread_id, run_id=run.id)

# 4. Obtener mensajes manualmente
messages = client.agents.list_messages(thread_id=thread_id)
response = messages.data[0].content[0].text.value
```

**Cuándo usar AIProjectClient:**
- ✅ Necesitas control fino sobre cada paso
- ✅ Casos de uso complejos o poco comunes
- ✅ Debugging avanzado
- ✅ Integración con sistemas existentes
- ✅ Optimización de rendimiento específica
- ✅ Manejo personalizado de estados y errores

---

### 🎯 Comparación Práctica: Mismo Resultado, Diferente Enfoque

#### **Agent Framework** (Alto Nivel)
```python
# 3 líneas para obtener una respuesta
thread = agent.get_new_thread()
result = await agent.run("¿Cuál es la capital de Francia?", thread=thread)
print(result.text)  # "París"
```

#### **AIProjectClient** (Bajo Nivel)
```python
# 12+ líneas para el mismo resultado
thread = client.agents.create_thread()

client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="¿Cuál es la capital de Francia?"
)

run = client.agents.create_run(
    thread_id=thread.id,
    agent_id=agent_id
)

while run.status in ["queued", "in_progress"]:
    time.sleep(1)
    run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

messages = client.agents.list_messages(thread_id=thread.id)
print(messages.data[0].content[0].text.value)  # "París"
```

---

### 🏆 Recomendaciones

#### **Usa Agent Framework si:**
- 🎯 Estás empezando con Azure AI Agents
- 🎯 Quieres código limpio y mantenible
- 🎯 Necesitas desarrollo rápido
- 🎯 Tu caso de uso es estándar (chat, Q&A, asistentes)
- 🎯 Prefieres simplicidad sobre control

#### **Usa AIProjectClient si:**
- 🎯 Necesitas control total del flujo
- 🎯 Implementas lógica personalizada de estados
- 🎯 Trabajas con hubs y múltiples proyectos
- 🎯 Requieres optimizaciones específicas
- 🎯 Integras con arquitecturas complejas existentes

---

### 📚 En Este Proyecto

Este repositorio incluye **ejemplos de ambos enfoques**:

**Scripts con Agent Framework (001-011):**
- Scripts `001` a `010`: Operaciones básicas y avanzadas
- Script `011`: API WebSocket con Agent Framework
- ✨ **Recomendado para aprender y proyectos nuevos**

**Script con AIProjectClient:**
- `assistant_websocket.py`: API WebSocket con AIProjectClient
- 🔧 **Para comparación y casos de control fino**

**Documentación comparativa:**
- `WEBSOCKET_COMPARISON.md`: Comparación detallada entre ambos enfoques

---

### 💡 Conclusión Clave

```
Agent Framework = AIProjectClient + Automatización + Simplicidad

El Agent Framework NO reemplaza a AIProjectClient,
sino que lo COMPLEMENTA ofreciendo una capa de abstracción
que hace el desarrollo más rápido y el código más limpio
para la mayoría de los casos de uso.
```

**Analogía Final:**
- **Agent Framework** = jQuery para JavaScript (simplifica operaciones comunes)
- **AIProjectClient** = JavaScript Vanilla (control total, más complejo)

Ambos son válidos, elige según tus necesidades específicas. Para aprender y desarrollar rápidamente, empieza con **Agent Framework**. 🚀

---

## 📖 Estructura del Curso

Este curso está organizado en módulos progresivos:

```
Nivel 1: Fundamentos
├── 001: Crear agente básico
├── 002: Reutilizar agentes
└── 003: Conversaciones con contexto

Nivel 2: Persistencia
├── 004: Continuar conversaciones
└── 005: Agentes con imágenes

Nivel 3: Avanzado - Colaboración y Workflows
├── 008: Colaboración multi-agente
├── 009: Agentes como herramientas (closures)
├── 010: Agentes como herramientas (partial)
├── 011: API WebSocket con Agent Framework
├── 012: Workflow secuencial (cierre automático)
├── 013: Workflow secuencial (cierre manual)
└── 014: Workflow paralelo (fan-out/fan-in)

Nivel 4: Herramientas y Extensibilidad
├── 015: MCP Tools (Model Context Protocol)
├── 016: Context Providers (contexto dinámico)
└── 017: Middleware (interceptores)

Nivel 5: Producción
├── 018: Observabilidad y Telemetría (métricas, logging)
├── 019: Workflows Condicionales (if/else routing)
├── 020: Group Chat Workflows (panel de expertos)
└── 021: Supervisor Pattern (orquestación avanzada)
```

---

## 🎓 Scripts del Curso

### `001_createandrunanagent.py`

**Objetivo:** Crear tu primer agente y obtener su ID

**Conceptos:**
- Creación de agente con `AzureAIAgentClient`
- Persistencia con `should_cleanup_agent=False`
- Obtención del Agent ID para reutilización
- Streaming vs respuesta directa

**Código clave:**
```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False  # Agente persiste en Azure
    ) as client:
        agent = client.create_agent(
            instructions="Eres bueno contando chistes.",
            name="Joker"
        )

        # Primera ejecución (crea el agente en Azure)
        result = await agent.run("Tell me a joke")

        # Obtener Agent ID después de ejecutar
        agent_id = agent.chat_client.agent_id
        print(f"Agent ID: {agent_id}")
```

**Salida esperada:**
```
Agent ID: asst_xxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Puntos importantes:**
- El agente NO se crea en Azure hasta la primera llamada a `run()`
- Guarda el `Agent ID` para usarlo en otros scripts
- `should_cleanup_agent=False` hace que el agente persista en Azure AI Foundry

---

### `002_reuseexistingagent.py`

**Objetivo:** Reutilizar un agente existente por su ID

**Conceptos:**
- Conexión a agentes existentes
- Mismo agente, diferentes sesiones
- No se crea un nuevo agente

**Código clave:**
```python
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"  # Del script 001

async with AzureAIAgentClient(
    async_credential=credential,
    agent_id=AGENT_ID  # Conectar a agente existente
) as client:
    agent = client.create_agent(
        instructions="Eres bueno contando chistes.",
        name="Joker"
    )

    # El agente recuerda su configuración
    result = await agent.run("Tell me another joke")
```

**⚠️ Puntos importantes:**
- Las instrucciones y nombre deben coincidir con el agente original
- Puedes usar el mismo agente desde múltiples scripts
- Cada ejecución es una conversación nueva (sin contexto previo)

---

### `003_persistentconversation.py`

**Objetivo:** Crear una conversación con memoria/contexto

**Conceptos:**
- Threads explícitos para gestionar contexto
- El agente recuerda información de mensajes anteriores
- Obtención del Thread ID para continuar después

**Código clave:**
```python
# Crear thread explícito
thread = agent.get_new_thread(service_thread_id=None)

# Primera interacción
result1 = await agent.run("Mi color favorito es azul", thread=thread)

# Segunda interacción (el agente recuerda el contexto)
result2 = await agent.run("¿Cuál es mi color favorito?", thread=thread)
# Respuesta: "Tu color favorito es azul"

# Obtener Thread ID para continuar después
thread_id = thread.service_thread_id
print(f"Thread ID: {thread_id}")
```

**Diferencia clave:**
```python
# ❌ SIN thread (no hay contexto entre llamadas)
await agent.run("Me llamo Juan")
await agent.run("¿Cómo me llamo?")  # No sabe

# ✅ CON thread (mantiene contexto)
await agent.run("Me llamo Juan", thread=thread)
await agent.run("¿Cómo me llamo?", thread=thread)  # "Juan"
```

**⚠️ Puntos importantes:**
- Siempre usar el mismo `thread` para mantener contexto
- Guardar `thread.service_thread_id` para continuar después

---

### `003b_persistentconversation_by_name.py`

**Objetivo:** Buscar y usar un agente por su nombre (en lugar de ID)

**Conceptos:**
- Buscar agente existente por nombre usando `agents_client.list_agents()`
- Búsqueda manual iterando sobre todos los agentes
- Mismo flujo de conversación que 003

**Código clave:**
```python
AGENT_NAME = "Joker"

async with AzureAIAgentClient(async_credential=credential) as client:
    # Buscar agente por nombre
    agents_paged = client.agents_client.list_agents(limit=100)
    agent_id = None
    async for agent in agents_paged:
        if agent.name == AGENT_NAME:
            agent_id = agent.id
            break

    if agent_id:
        # Usar el agent_id encontrado
        async with AzureAIAgentClient(
            async_credential=credential,
            agent_id=agent_id
        ) as agent_client:
            agent = agent_client.create_agent(...)
            result = await agent.run("Tu pregunta", thread=thread)
```

**⚠️ Puntos importantes:**
- Más legible que usar IDs hardcodeados
- Requiere búsqueda manual (no hay API directa por nombre)
- Útil cuando tienes muchos agentes y prefieres referirlos por nombre

---

### `003c_list_all_agents.py`

**Objetivo:** Listar todos los agentes disponibles en Azure AI Foundry

**Conceptos:**
- Descubrir qué agentes existen en tu proyecto
- API de listado: `agents_client.list_agents()`
- Información de cada agente: nombre, ID, modelo, fecha de creación

**Código clave:**
```python
async with AzureAIAgentClient(async_credential=credential) as client:
    # Listar todos los agentes
    agents_paged = client.agents_client.list_agents(
        limit=100,
        order="desc"
    )

    async for agent in agents_paged:
        print(f"Nombre:  {agent.name}")
        print(f"ID:      {agent.id}")
        print(f"Modelo:  {agent.model}")
        print(f"Creado:  {agent.created_at}")
```

**⚠️ Puntos importantes:**
- Útil para explorar recursos existentes
- Soporta paginación con `limit` y `order`
- Muestra información básica de cada agente

---

### `003d_using_agent_helpers.py`

**Objetivo:** Demostrar el uso del módulo `agent_helpers.py`

**Conceptos:**
- Funciones helper reutilizables para gestión de agentes
- Búsqueda por nombre, patrón, verificación de existencia
- Código más limpio y mantenible

**Código clave:**
```python
from agent_helpers import get_agent_id_by_name, agent_exists

async with AzureAIAgentClient(async_credential=credential) as client:
    # Verificar si existe
    if await agent_exists(client, "MyAgent"):
        # Obtener ID por nombre
        agent_id = await get_agent_id_by_name(client, "MyAgent")
        # Usar el agente...
```

**⚠️ Puntos importantes:**
- Simplifica operaciones comunes con agentes
- Ver `agent_helpers.py` para todas las funciones disponibles
- Reutilizable en todos tus scripts

---

### `004_continuethreadconversation.py`

**Objetivo:** Continuar una conversación existente

**Conceptos:**
- Reutilización de Agent ID + Thread ID
- El agente recuerda toda la conversación anterior
- Conversaciones persistentes entre ejecuciones

**Código clave:**
```python
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"
THREAD_ID = "thread_7dLiIQQlgsCOCUw3neCkjMbr"

async with AzureAIAgentClient(
    async_credential=credential,
    agent_id=AGENT_ID
) as client:
    agent = client.create_agent(...)

    # Conectar al thread existente
    thread = agent.get_new_thread(service_thread_id=THREAD_ID)

    # El agente recuerda todo el contexto anterior
    result = await agent.run("¿Qué sabes de mí?", thread=thread)
```

**Flujo completo:**
```
Script 003 (Primera sesión):
└── "Mi color favorito es azul"
└── Thread ID: thread_xxx

Script 004 (Días después):
└── Usar mismo Thread ID
└── "¿Cuál era mi color favorito?" → "Azul"
```

---

### `005_usingimageswithanagent.py`

**Objetivo:** Trabajar con imágenes (vision)

**Conceptos:**
- Modelos con capacidades de vision (GPT-4o)
- `DataContent` para imágenes (bytes)
- `UriContent` NO soportado en Azure AI Foundry
- Descarga de imágenes desde URLs

**Código clave:**
```python
from agent_framework import ChatMessage, TextContent, DataContent, Role
import httpx

# Opción 1: Imagen local
with open("./images/nature.jpg", "rb") as f:
    image_bytes = f.read()

message = ChatMessage(
    role=Role.USER,
    contents=[
        TextContent(text="¿Qué ves en esta imagen?"),
        DataContent(data=image_bytes, media_type="image/jpeg")
    ]
)

# Opción 2: Imagen desde URL (descargar primero)
async def download_image(url: str) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        return response.content

image_data = await download_image("https://example.com/image.jpg")
message = ChatMessage(
    role=Role.USER,
    contents=[
        TextContent(text="Describe esta imagen"),
        DataContent(data=image_data, media_type="image/jpeg")
    ]
)

result = await agent.run(message)
```

**⚠️ Importante:**
```python
# ❌ NO FUNCIONA en Azure AI Foundry
UriContent(uri="https://...", media_type="image/jpeg")

# ✅ FUNCIONA (descargar primero)
image_data = await download_image("https://...")
DataContent(data=image_data, media_type="image/jpeg")
```

---

### `008_multi_agent_collaboration_fixed.py`

**Objetivo:** Colaboración entre múltiples agentes

**Conceptos:**
- Múltiples agentes con roles específicos
- Comunicación entre agentes
- Herramientas/funciones personalizadas
- Arquitectura de agentes especializados

**Arquitectura:**
```
┌─────────────────────┐
│  Developer Agent    │  ← Crea código
│  + Tool: multiplicar│
└──────────┬──────────┘
           │ Propuesta
           ▼
┌─────────────────────┐
│ Product Manager     │  ← Evalúa código
│      Agent          │
└─────────────────────┘
```

**Código clave:**
```python
# Definir herramienta
def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b

# Función auxiliar optimizada
async def create_and_persist_agent(credential, instructions, name, tools=None):
    """Crea un agente persistente y retorna su ID."""
    async with AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    ) as client:
        agent = client.create_agent(
            instructions=instructions,
            name=name,
            tools=tools
        )
        await agent.run("Confirma que estás listo")
        return agent.chat_client.agent_id

# Crear agentes
developer_id = await create_and_persist_agent(
    credential=credential,
    instructions="Eres un Desarrollador Senior de Python.",
    name="Developer",
    tools=[multiplicar]
)

manager_id = await create_and_persist_agent(
    credential=credential,
    instructions="Eres un Product Manager estricto.",
    name="ProductManager"
)

# Colaboración
async with AzureAIAgentClient(agent_id=developer_id) as dev_client:
    developer_agent = dev_client.create_agent(...)
    dev_response = await developer_agent.run("Crea función calcular_iva")

async with AzureAIAgentClient(agent_id=manager_id) as mgr_client:
    manager_agent = mgr_client.create_agent(...)
    evaluation = await manager_agent.run(f"Evalúa: {dev_response.text}")
```

**Flujo:**
1. Crear Developer Agent (con herramienta `multiplicar`)
2. Crear Manager Agent (sin herramientas)
3. Developer procesa tarea → genera código
4. Manager evalúa la propuesta → aprueba/rechaza

---

### `009_agents_using_other_agents_as_tools.py`

**Objetivo:** Usar agentes como herramientas de otros agentes (patrón supervisor)

**Conceptos:**
- Patrón supervisor-delegado
- Agentes especializados con responsabilidades únicas
- Closures para capturar contexto de agentes
- Delegación inteligente de tareas

**Arquitectura:**
```
┌─────────────────────────────┐
│   Supervisor Agent          │
│   (Delega tareas)           │
└──────────┬──────────────────┘
           │
    ┌──────┴───────┬───────────┐
    │              │           │
    ▼              ▼           ▼
┌───────┐    ┌──────────┐  ┌────────┐
│ Math  │    │ Finance  │  │  Time  │
│ Agent │    │  Agent   │  │ Agent  │
└───────┘    └──────────┘  └────────┘
```

**Código clave:**
```python
# Paso 1: Crear agentes especializados
math_client, math_agent = await create_and_initialize_agent(
    credential=credential,
    instructions="Eres una calculadora.",
    name="math_agent",
    tools=[herramienta_matematica]
)

finance_client, finance_agent = await create_and_initialize_agent(
    credential=credential,
    instructions="Eres un experto en divisas.",
    name="finance_agent",
    tools=[herramienta_financiera]
)

time_client, time_agent = await create_and_initialize_agent(
    credential=credential,
    instructions="Eres un Cronista.",
    name="time_agent",
    tools=[obtener_fecha]
)

# Paso 2: Crear funciones wrapper (closures) que capturan los agentes
async def consultar_matematicas(problema: str) -> str:
    """Úsalo para resolver problemas numéricos, cálculos o multiplicaciones."""
    print(f"\n[📞 SUPERVISOR -> MATH]: '{problema}'")
    respuesta = await math_agent.run(problema)
    return respuesta.text

async def consultar_finanzas(pregunta: str) -> str:
    """Úsalo para conversiones de divisas EUR a USD."""
    print(f"\n[📞 SUPERVISOR -> FINANCE]: '{pregunta}'")
    respuesta = await finance_agent.run(pregunta)
    return respuesta.text

async def consultar_tiempo(pregunta: str) -> str:
    """Úsalo cuando el usuario pregunte por la FECHA."""
    print(f"\n[📞 SUPERVISOR -> TIME]: '{pregunta}'")
    respuesta = await time_agent.run(pregunta)
    return respuesta.text

# Paso 3: Crear supervisor con las funciones wrapper como herramientas
supervisor_client, supervisor = await create_and_initialize_agent(
    credential=credential,
    instructions="""Eres un supervisor inteligente.
    Analiza la pregunta del usuario y delega al departamento correcto:
    - Usa consultar_matematicas para cálculos
    - Usa consultar_finanzas para conversiones de dinero
    - Usa consultar_tiempo para preguntas sobre fecha/hora
    """,
    name="supervisor_agent",
    tools=[consultar_matematicas, consultar_finanzas, consultar_tiempo]
)

# Paso 4: Usar el supervisor
resultado = await supervisor.run("¿Cuánto es 5 por 7?")
# Supervisor → Delega a math_agent → Retorna resultado
```

**Flujo de ejecución:**
```
Usuario: "¿Cuánto es 5 por 7?"
    ↓
Supervisor Agent (analiza)
    ↓
Llama a consultar_matematicas("¿Cuánto es 5 por 7?")
    ↓
Math Agent (ejecuta herramienta_matematica)
    ↓
Retorna: 35
    ↓
Supervisor: "El resultado es 35"
```

**⚠️ Puntos importantes:**
- Las funciones wrapper se definen dentro de `main()` como closures
- Cada agente necesita su propio `AzureAIAgentClient`
- Los clientes deben mantenerse abiertos mientras los agentes estén en uso
- Los closures capturan referencias a los agentes especializados

---

### `010_agents_using_other_agents_as_tools_with_partial.py`

**Objetivo:** Mismo patrón que 009, pero usando `functools.partial` para mayor reutilización

**Conceptos:**
- `functools.partial` para aplicación parcial de funciones
- Código más reutilizable y mantenible
- Funciones genéricas fuera de `main()`
- Mejor separación de responsabilidades

**Ventajas sobre 009:**
1. **Reutilización:** Las funciones genéricas pueden usarse en múltiples contextos
2. **Mantenibilidad:** Menos código duplicado
3. **Flexibilidad:** Fácil crear nuevas herramientas sobre la marcha
4. **Testabilidad:** Funciones genéricas más fáciles de testear

**Código clave:**
```python
# Paso 1: Definir función genérica FUERA de main() (reutilizable)
async def consultar_agente_generico(
    agent,
    departamento: str,
    emoji: str,
    pregunta: str
) -> str:
    """Función genérica para consultar cualquier agente."""
    print(f"\n[{emoji} SUPERVISOR -> {departamento}]: '{pregunta}'")
    respuesta = await agent.run(pregunta)
    return respuesta.text

# Paso 2: Crear agentes especializados (igual que 009)
math_client, math_agent = await create_and_initialize_agent(...)
finance_client, finance_agent = await create_and_initialize_agent(...)
time_client, time_agent = await create_and_initialize_agent(...)

# Paso 3: Usar partial para crear herramientas específicas
from functools import partial

consultar_matematicas = partial(
    consultar_agente_generico,
    math_agent,      # Agente fijo
    "MATH",          # Departamento fijo
    "📐"             # Emoji fijo
)
# pregunta será el único parámetro que cambia

# Configurar metadata para que el LLM entienda la herramienta
consultar_matematicas.__name__ = "consultar_matematicas"
consultar_matematicas.__doc__ = "Úsalo para resolver problemas numéricos."

# Similar para finanzas y tiempo
consultar_finanzas = partial(
    consultar_agente_generico,
    finance_agent,
    "FINANCE",
    "💰"
)
consultar_finanzas.__name__ = "consultar_finanzas"
consultar_finanzas.__doc__ = "Úsalo para conversiones de divisas."

consultar_tiempo = partial(
    consultar_agente_generico,
    time_agent,
    "TIME",
    "📅"
)
consultar_tiempo.__name__ = "consultar_tiempo"
consultar_tiempo.__doc__ = "Úsalo cuando el usuario pregunte por la FECHA."

# Paso 4: Crear supervisor (igual que 009)
supervisor_client, supervisor = await create_and_initialize_agent(
    credential=credential,
    instructions="Eres un supervisor inteligente...",
    name="supervisor_agent",
    tools=[consultar_matematicas, consultar_finanzas, consultar_tiempo]
)

# ✨ VENTAJA EXTRA: Reutilizar agentes fuera del supervisor
async def consultar_agente_simple(agent, pregunta: str) -> str:
    """Versión simple sin logging."""
    respuesta = await agent.run(pregunta)
    return respuesta.text

# Crear herramienta sobre la marcha
consultar_math_directo = partial(consultar_agente_simple, math_agent)
respuesta = await consultar_math_directo("¿Cuánto es 3 por 9?")
```

**Comparación 009 vs 010:**

| Aspecto | 009 (Closures) | 010 (Partial) |
|---------|----------------|---------------|
| **Definición** | Dentro de `main()` | Fuera de `main()` |
| **Reutilización** | Limitada | Alta |
| **Duplicación** | Código repetido | Función genérica única |
| **Flexibilidad** | Media | Alta |
| **Complejidad** | Baja | Media |
| **Testing** | Difícil | Fácil |

**Cuándo usar cada uno:**
- **Closures (009):** Casos simples, código específico, prototipado rápido
- **Partial (010):** Proyectos grandes, reutilización, múltiples supervisores

**⚠️ Puntos importantes:**
- `partial` fija los primeros N parámetros de una función
- Siempre configurar `__name__` y `__doc__` para que el LLM entienda la herramienta
- La función genérica puede vivir fuera de `main()` para reutilización
- Puedes crear múltiples versiones (con logging, sin logging, etc.)

---

### `011_assistant_websocket_agent_framework.py`

**Objetivo:** API WebSocket con FastAPI usando Agent Framework para conversaciones persistentes

**Conceptos:**
- FastAPI con WebSocket endpoints
- Agent Framework Azure AI (proyectos directos, sin hub)
- Threads persistentes por usuario
- Gestión de sesiones de chat
- API REST + WebSocket combinados

**Arquitectura:**
```
┌─────────────────────────────────────┐
│   Frontend (React/Vue/etc)          │
│   WebSocket Client                  │
└──────────────┬──────────────────────┘
               │ WebSocket
               │ (ws://localhost:8000/ws/chat)
               ▼
┌─────────────────────────────────────┐
│   FastAPI Server                    │
│   011_assistant_websocket...py      │
├─────────────────────────────────────┤
│   AgentFrameworkChatManager         │
│   - Gestiona conexiones WS          │
│   - Mantiene threads por usuario    │
│   - Reutiliza agente existente      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Azure AI Foundry                  │
│   - Agent (asst_xxx)                │
│   - Threads persistentes            │
└─────────────────────────────────────┘
```

**Variables de entorno requeridas:**
```env
# Endpoint del proyecto (agent_framework_azure_ai)
AZURE_AI_PROJECT_ENDPOINT=https://xxx.services.ai.azure.com/api/projects/xxx

# Modelo deployment
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Agent ID a reutilizar
AZURE_AGENT_ID=asst_EkJeB3eaxhhwTsRxRp9JZBU4

# Configuración del servidor (opcionales)
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Código clave:**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

class AgentFrameworkChatManager:
    """Gestor de sesiones de chat con threads persistentes"""

    def __init__(self):
        self.agent_id = os.getenv("AZURE_AGENT_ID")
        self.user_threads: Dict[str, str] = {}  # {user_id: thread_id}
        self.active_connections: Dict[str, WebSocket] = {}

    async def send_to_assistant(self, user_id: str, message: str):
        """Envía mensaje usando thread persistente"""
        thread_id = self.user_threads.get(user_id, None)

        async with AzureAIAgentClient(
            async_credential=DefaultAzureCredential(),
            agent_id=self.agent_id
        ) as client:
            agent = client.create_agent(
                instructions="Eres un asistente útil...",
                name="Assistant"
            )

            # Reutilizar o crear thread
            thread = agent.get_new_thread(service_thread_id=thread_id)
            result = await agent.run(message, thread=thread)

            # Guardar thread_id si es nuevo
            if user_id not in self.user_threads:
                self.user_threads[user_id] = thread.service_thread_id

            return result.text

# WebSocket endpoint
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 1. Inicializar sesión
    init_data = await websocket.receive_json()
    user_id = init_data["user_id"]

    # 2. Loop de mensajes
    while True:
        message_data = await websocket.receive_json()

        if message_data["type"] == "message":
            # Obtener respuesta del agente
            response = await chat_manager.send_to_assistant(
                user_id,
                message_data["message"]
            )

            # Enviar respuesta al cliente
            await websocket.send_json({
                "type": "bot_message",
                "message": response
            })
```

**Protocolo WebSocket:**

1. **Inicializar sesión:**
```json
// Cliente → Servidor
{
    "type": "init",
    "user_id": "usuario_123"
}

// Servidor → Cliente
{
    "type": "session_ready",
    "thread_id": "thread_xxx",
    "is_new_session": false
}
```

2. **Enviar mensaje:**
```json
// Cliente → Servidor
{
    "type": "message",
    "message": "¿Cuál es mi color favorito?"
}

// Servidor → Cliente
{
    "type": "bot_message",
    "message": "Tu color favorito es azul",
    "status": "success"
}
```

3. **Limpiar sesión:**
```json
// Cliente → Servidor
{
    "type": "clear_session"
}

// Servidor → Cliente
{
    "type": "session_cleared",
    "message": "Tu historial ha sido eliminado"
}
```

**Endpoints REST:**
- `GET /` - Información de la API
- `GET /health` - Health check (para Azure Container Apps)
- `GET /api/stats` - Estadísticas del servidor
- `GET /docs` - Documentación Swagger automática

**Endpoints WebSocket:**
- `WS /ws/chat` - Conexión para chat persistente

**Ejecutar el servidor:**
```bash
# Desarrollo (con auto-reload)
python 011_assistant_websocket_agent_framework.py

# Producción
ENVIRONMENT=production python 011_assistant_websocket_agent_framework.py
```

**Diferencias con `assistant_websocket.py`:**

| Aspecto | `assistant_websocket.py` | `011_assistant_websocket_agent_framework.py` |
|---------|--------------------------|---------------------------------------------|
| **Cliente** | `AIProjectClient` | `AzureAIAgentClient` |
| **Conexión** | Connection String (Hub + Proyecto) | Endpoint de Proyecto (solo proyecto) |
| **Variable Env** | `PROJECT_CONNECTION_STRING` | `AZURE_AI_PROJECT_ENDPOINT` |
| **Patrón** | Sync con polling manual | Async con polling automático |
| **Thread Creation** | `client.agents.create_thread()` | `agent.get_new_thread(service_thread_id=xxx)` |
| **Mensaje + Run** | 2 pasos separados | 1 paso con `agent.run()` |
| **Código** | Más verboso | Más conciso |

**Ventajas de usar Agent Framework:**
1. ✅ Código más simple y legible
2. ✅ Polling automático (no necesitas hacer loop)
3. ✅ Integración directa con proyecto (sin hub)
4. ✅ Patrón async nativo
5. ✅ Menos líneas de código para misma funcionalidad

**Casos de uso:**
- Chatbots con memoria de conversación
- Asistentes virtuales para sitios web
- Sistemas de soporte al cliente
- Aplicaciones de chat empresariales
- Integración con React/Vue/Angular frontends

**⚠️ Puntos importantes:**
- Cada usuario tiene su propio thread_id (persistencia por usuario)
- Los threads se mantienen entre desconexiones
- Usar `clear_session` para eliminar el historial de un usuario
- El servidor mantiene conexiones activas y threads persistentes
- Compatible con Azure Container Apps para producción

**Flujo completo:**
```
1. Cliente conecta → WebSocket acepta conexión
2. Cliente envía "init" → Servidor crea/recupera thread
3. Cliente envía "message" → Servidor ejecuta agent.run()
4. Agente procesa en Azure → Respuesta automática
5. Servidor envía respuesta → Cliente la muestra
6. (Repetir 3-5 para cada mensaje)
7. Cliente desconecta → Thread persiste en Azure
8. Cliente reconecta → Recupera mismo thread y contexto
```

**Testing con herramientas:**

WebSocket client (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

// Inicializar
ws.send(JSON.stringify({
    type: "init",
    user_id: "test_user_123"
}));

// Enviar mensaje
ws.send(JSON.stringify({
    type: "message",
    message: "Hola, ¿cómo estás?"
}));

// Recibir respuestas
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

**Ver también:**
- `WEBSOCKET_COMPARISON.md` - Comparación detallada entre ambas implementaciones
- `assistant_websocket.py` - Versión con AIProjectClient (hub + proyecto)

---

### `012_sequential_workflow.py`

**Objetivo:** Demostrar workflows secuenciales con múltiples agentes (versión con cierre automático)

> **Nota:** Este script y `013_sequential_workflow.py` son **funcionalmente idénticos**. La única diferencia es el enfoque de gestión de recursos. Ninguno es superior; usa el que prefieras.

**Conceptos:**
- Orquestación de múltiples agentes en un flujo secuencial
- `WorkflowBuilder` para conectar executors
- Patrón pipeline: Researcher Agent → Writer Agent
- Cierre automático de recursos con `async with`
- Factory pattern para dar acceso a agentes a los executors
- Visualización del workflow en formato Mermaid

**Arquitectura:**
```
Input → Researcher (investiga) → Writer (escribe ensayo) → Output
```

**Conceptos Clave:**
- **Executor:** Función decorada con `@executor` que representa una tarea
- **Factory Pattern:** Usar funciones factory para dar a los executors acceso a los agentes mediante closures
- **WorkflowBuilder:** Conecta executors con `.add_edge()` y define el punto de inicio
- **Context:** `ctx.send_message()` envía datos al siguiente, `ctx.yield_output()` produce el resultado final
- **Cierre Automático:** Los clientes se cierran automáticamente con `async with`

**Código clave:**
```python
from agent_framework import WorkflowBuilder, WorkflowContext, executor

# 1. Crear executors con factory pattern
def create_researcher_executor(researcher_agent):
    @executor(id="run_researcher_agent")
    async def run_researcher_agent(query: str, ctx: WorkflowContext[str]) -> None:
        response = await researcher_agent.run(query)
        await ctx.send_message(str(response))  # Envía al siguiente
    return run_researcher_agent

def create_writer_executor(writer_agent):
    @executor(id="run_writer_agent")
    async def run_writer_agent(research_data: str, ctx: WorkflowContext[str]) -> None:
        prompt = f"Basándote en esta investigación: {research_data}"
        response = await writer_agent.run(prompt)
        await ctx.yield_output(str(response))  # Output final
    return run_writer_agent

# 2. Crear clientes y agentes con async with
async with AzureAIAgentClient(...) as researcher_client:
    researcher_agent = researcher_client.create_agent(...)

    async with AzureAIAgentClient(...) as writer_client:
        writer_agent = writer_client.create_agent(...)

        # 3. Construir workflow
        researcher_exec = create_researcher_executor(researcher_agent)
        writer_exec = create_writer_executor(writer_agent)

        workflow = (
            WorkflowBuilder()
            .add_edge(researcher_exec, writer_exec)
            .set_start_executor(researcher_exec)
            .build()
        )

        # 4. Ejecutar workflow
        async for event in workflow.run_stream("query"):
            if isinstance(event, WorkflowOutputEvent):
                print(event.data)

        # Los clientes se cierran automáticamente
```

**Flujo de Ejecución:**
```
1. Usuario provee query inicial
2. Workflow envía query al Researcher Executor
3. Researcher Agent investiga y genera datos de investigación
4. Researcher Executor usa ctx.send_message() para pasar datos al Writer
5. Writer Executor recibe datos de investigación
6. Writer Agent genera ensayo basado en la investigación
7. Writer Executor usa ctx.yield_output() para emitir resultado final
8. Workflow termina, clientes se cierran automáticamente
```

**⚠️ Puntos importantes:**
- Usar **factory pattern** para dar a los executors acceso a los agentes mediante closures
- Los executors deben usar `@executor` decorator con un ID único
- `ctx.send_message()` pasa datos al siguiente executor en el pipeline
- `ctx.yield_output()` emite el resultado final del workflow
- `async with` garantiza que los recursos se cierren automáticamente
- El script genera visualización Mermaid del workflow

**Cuándo usar este enfoque:**
- Workflows **secuenciales** o **pipeline** (A → B → C)
- Cuando prefieres código más conciso
- Cuando quieres cierre automático garantizado de recursos
- Para workflows simples y medianos

**Ver también:**
- `013_sequential_workflow.py` - Mismo workflow con cierre manual
- Sección "Gestión de Recursos: Cierre Manual vs Automático" en CLAUDE.md

---

### `013_sequential_workflow.py`

**Objetivo:** El mismo workflow secuencial que 012, pero usando cierre manual de recursos (versión con cierre manual)

> **Nota:** Este script y `012_sequential_workflow.py` son **funcionalmente idénticos**. La única diferencia es el enfoque de gestión de recursos. Ninguno es superior; usa el que prefieras.

**Conceptos:**
- **Misma funcionalidad** que 012_sequential_workflow.py
- **Diferente enfoque:** Cierre manual con `__aexit__()` en lugar de `async with`
- Útil para comparar ambos enfoques de gestión de recursos
- Demuestra el patrón con `create_and_initialize_agent()` que retorna cliente y agente
- Más apropiado para patrones supervisor (aunque funciona igual para secuencial)

**Diferencias Clave con 012:**

| Aspecto | 012 (Cierre Automático) | 013 (Cierre Manual) |
|---------|--------------------------|---------------------|
| **Creación de clientes** | `async with AzureAIAgentClient(...) as client:` | `client = AzureAIAgentClient(...)` |
| **Función helper** | `initialize_agent()` (solo inicializa) | `create_and_initialize_agent()` (crea y retorna todo) |
| **Retorno** | Solo agente | Tuple (client, agent) |
| **Cierre** | Automático al salir del bloque | Manual con `await client.__aexit__()` |
| **Lista de clients** | No necesaria | `clients = []` para rastrear |
| **Try/Finally** | No necesario | Requerido para garantizar cierre |

**Código clave (diferencias):**
```python
# 1. Función que retorna cliente Y agente
async def create_and_initialize_agent(credential, instructions, name):
    client = AzureAIAgentClient(async_credential=credential, should_cleanup_agent=True)
    agent = create_agent(client, instructions, name)
    await agent.run("Hola, confirma que estas listo.")
    return client, agent  # ← Retorna AMBOS

# 2. Crear agentes y rastrear clientes
async with DefaultAzureCredential() as credential:
    clients = []  # ← Lista para rastrear clientes

    try:
        # Crear agentes sin async with
        researcher_client, researcher_agent = await create_and_initialize_agent(...)
        clients.append(researcher_client)

        writer_client, writer_agent = await create_and_initialize_agent(...)
        clients.append(writer_client)

        # Construir y ejecutar workflow (igual que 012)
        # ...

    finally:
        # 3. Cierre manual de todos los clientes
        for client in clients:
            await client.__aexit__(None, None, None)
```

**Comparación Visual:**
```
012 (Automático):              013 (Manual):
┌─────────────────┐           ┌─────────────────┐
│ async with A:   │           │ crear A, B, C   │
│   async with B: │           │ todos activos   │
│     workflow    │           │ try:            │
│   B cierra ←    │           │   workflow      │
│ A cierra ←      │           │ finally:        │
└─────────────────┘           │   cerrar todos  │
                              └─────────────────┘
```

**¿Cuándo este enfoque es más natural?**
- Patrones **supervisor** donde necesitas todos los agentes activos simultáneamente
- Cuando prefieres control explícito sobre el ciclo de vida de recursos
- Cuando el anidamiento profundo de `async with` se vuelve difícil de leer
- **Nota:** Para workflows secuenciales simples (como este), ambos enfoques funcionan igual de bien

**Para workflows secuenciales simples (como este):**
- Ambos enfoques son **igualmente válidos**
- `async with` (012) requiere menos código
- Cierre manual (013) ofrece más control explícito
- **Elige el que te parezca más claro**

**⚠️ Puntos importantes:**
- Siempre mantener lista de `clients` para rastrear qué cerrar
- Usar `try/finally` para garantizar cierre incluso con errores
- Cerrar con `await client.__aexit__(None, None, None)`
- No mezclar enfoques (todo manual o todo automático)

**Errores Comunes:**

❌ **No cerrar clientes:**
```python
# Incorrecto - memory leak
clients = []
client1 = AzureAIAgentClient(...)
clients.append(client1)
# ... usar agentes ...
# Sin cerrar!
```

✅ **Siempre usar try/finally:**
```python
# Correcto
try:
    # ... crear y usar agentes ...
finally:
    for client in clients:
        await client.__aexit__(None, None, None)
```

**Ver también:**
- `012_sequential_workflow.py` - Mismo workflow con cierre automático
- Sección "Gestión de Recursos: Cierre Manual vs Automático" en CLAUDE.md

---

### `014_parallel-workflow.py`

**Objetivo:** Workflows paralelos con fan-out y fan-in (ejecución paralela de múltiples agentes)

**Conceptos:**
- Orquesta 5 agentes en un flujo paralelo (fan-out y fan-in)
- `WorkflowBuilder` con `.add_fan_out_edges()` y `.add_fan_in_edges()`
- Patrón: Selector → (Recommender + Weather + Cuisine en paralelo) → Planner
- Cierre manual de recursos (mismo estilo que 013)
- Factory pattern para todos los executors

**Arquitectura:**
```
Input → Location Selector
        ↓ (fan-out - ejecución paralela)
        ├→ Destination Recommender ┐
        ├→ Weather Agent            ├→ (fan-in - combina resultados)
        └→ Cuisine Suggestion       ┘
                ↓
        Itinerary Planner → Output
```

**Conceptos Clave:**
- **Fan-out:** Un executor envía datos a múltiples executors que se ejecutan en **paralelo**
- **Fan-in:** Múltiples executors envían resultados a un solo executor que los **combina**
- **Ejecución Paralela:** Los 3 agentes (Destination, Weather, Cuisine) procesan simultáneamente
- **Lista de Resultados:** El executor de fan-in recibe `list[str]` con todos los resultados

**Código clave:**
```python
from agent_framework import WorkflowBuilder, WorkflowContext, executor

# El executor de fan-in recibe una LISTA de resultados
def create_itinerary_planner_executor(itinerary_planner_agent):
    @executor(id="ItineraryPlanner")
    async def itinerary_planner(
        results: list[str],  # ← ¡LISTA! No str
        ctx: WorkflowContext[str]
    ) -> None:
        # Combinar los 3 resultados
        combined_results = "\n\n".join(results)
        prompt = f"Basándote en esta información, crea un itinerario: {combined_results}"
        response = await itinerary_planner_agent.run(prompt)
        await ctx.yield_output(str(response))
    return itinerary_planner

# Construir workflow paralelo
workflow = (
    WorkflowBuilder()
    .set_start_executor(location_exec)
    .add_fan_out_edges(
        location_exec,
        [destination_exec, weather_exec, cuisine_exec]  # Ejecución paralela
    )
    .add_fan_in_edges(
        [destination_exec, weather_exec, cuisine_exec],  # Combina resultados
        itinerary_exec
    )
    .build()
)
```

**Diferencias con Workflow Secuencial (012/013):**

| Aspecto | Secuencial (012/013) | Paralelo (014) |
|---------|----------------------|----------------|
| **Número de agentes** | 2 | 5 |
| **Conexiones** | `.add_edge(A, B)` | `.add_fan_out_edges()` + `.add_fan_in_edges()` |
| **Ejecución** | Secuencial (uno tras otro) | Paralela (3 simultáneos) |
| **Flujo** | Lineal (A → B) | Red (A → [B,C,D] → E) |
| **Input del último executor** | `str` (un resultado) | `list[str]` (múltiples resultados) |
| **Uso típico** | Pipeline, transformaciones | Gather-scatter, aggregación |

**Caso de Uso:**
Planificador de vacaciones que recopila información de múltiples fuentes (destinos, clima, comida) de forma paralela y luego las combina en un itinerario completo.

**Ver también:**
- `012_sequential_workflow.py` y `013_sequential_workflow.py` - Workflows secuenciales
- `014_parallel-workflow_docs.html` - Documentación completa con diagramas

---

### `015_agent_with_mcp_tools.py`

**Objetivo:** Usar HostedMCPTool (Model Context Protocol Tools) con agentes

**Conceptos:**
- 7 ejemplos completos de configuración de MCP Tools
- Diferentes modos de aprobación (always_require, never_require, específico)
- Filtrado de herramientas permitidas (allowed_tools)
- Autenticación con headers (Bearer tokens, API keys)
- MCP (Model Context Protocol): Protocolo para extender capacidades de agentes

**Código clave:**
```python
from agent_framework import HostedMCPTool

# Ejemplo básico
mcp_tool = HostedMCPTool(
    name="my_tool",
    url="https://api.example.com/mcp"
)

# Con autenticación y aprobación
mcp_tool_secure = HostedMCPTool(
    name="secure_api",
    description="API que requiere autenticación",
    url="https://api.example.com/mcp",
    approval_mode="always_require",
    headers={
        "Authorization": "Bearer your-token-here"
    }
)

# Con herramientas filtradas
mcp_tool_filtered = HostedMCPTool(
    name="filtered_api",
    url="https://api.example.com/mcp",
    allowed_tools=["search", "calculate"],  # Solo estas 2
    approval_mode="never_require"
)

# Crear agente con MCP Tools
agent = client.create_agent(
    name="MCP Agent",
    instructions="Eres un asistente con acceso a herramientas externas",
    tools=[mcp_tool, mcp_tool_secure, mcp_tool_filtered]
)
```

**Modos de Aprobación:**

| Modo | Descripción | Uso |
|------|-------------|-----|
| `"always_require"` | Siempre requiere aprobación del usuario | APIs peligrosas/destructivas |
| `"never_require"` | Nunca requiere aprobación (auto) | APIs seguras/solo lectura |
| Específico (dict) | Aprobación por herramienta | Mix de operaciones seguras/peligrosas |

**⚠️ Nota:** El script usa URLs de ejemplo. Para uso en producción, reemplaza con URLs de servidores MCP reales y configura autenticación válida.

---

### `016_context_providers.py`

**Objetivo:** Usar Context Providers para inyectar contexto dinámico a los agentes

**Conceptos:**
- 7 ejemplos completos de Context Providers
- Inyección automática de contexto antes de cada invocación
- Múltiples providers combinables (AggregateContextProvider)
- Providers con estado dinámico
- Separación de contexto vs lógica del agente

**Context Providers Implementados:**
1. **DateTimeContextProvider** - Contexto temporal (fecha/hora actual)
2. **UserContextProvider** - Información del usuario
3. **BusinessRulesContextProvider** - Reglas de negocio dinámicas
4. **ConversationMemoryProvider** - Memoria de conversación
5. **DynamicPricingContextProvider** - Estado dinámico (pricing)

**Código clave:**
```python
from agent_framework import ContextProvider, Context

class DateTimeContextProvider(ContextProvider):
    async def invoking(self, messages, **kwargs) -> Context:
        """Llamado ANTES de cada invocación del agente"""
        now = datetime.now()
        temporal_context = f"Fecha actual: {now.strftime('%Y-%m-%d')}"

        return Context(
            instructions=temporal_context,
            messages=[],
            tools=[]
        )

    async def invoked(self, messages, **kwargs) -> None:
        """Llamado DESPUÉS de cada invocación (opcional)"""
        print("Contexto temporal inyectado")

# Usar con agente
agent = client.create_agent(
    name="Time-Aware Assistant",
    instructions="Eres un asistente consciente del tiempo",
    context_providers=[datetime_provider]  # ← Inyección automática
)

# Múltiples providers
agent = client.create_agent(
    name="Contextual Assistant",
    context_providers=[
        datetime_provider,
        user_provider,
        business_provider,
        memory_provider
    ]  # ← Se combinan automáticamente
)
```

**Ventajas de Context Providers:**
- ✅ Contexto dinámico que cambia por invocación
- ✅ No modifica instrucciones base del agente
- ✅ Reutilizable entre múltiples agentes
- ✅ Combinable (múltiples providers)
- ✅ Testeable independientemente

**Casos de Uso:**
- Información de usuario (perfil, rol, preferencias)
- Contexto temporal (fecha, hora, zona horaria)
- Reglas de negocio (horarios, políticas, límites)
- Datos de sistemas externos (CRM, bases de datos)
- Estado de sesión (carrito, progreso, historial)

---

### `017_middleware.py`

**Objetivo:** Usar Middleware para interceptar y modificar comportamiento de agentes

**Conceptos:**
- 3 tipos de middleware: Agent, Function, Chat
- 8 ejemplos completos de middleware
- Cadenas de middleware (múltiples en secuencia)
- Cross-cutting concerns sin modificar código principal
- Casos de uso: logging, validación, caching, seguridad

**Tipos de Middleware:**

| Tipo | Decorador | Intercepta | Uso |
|------|-----------|------------|-----|
| **Agent** | `@agent_middleware` | Runs completos del agente | Logging, timing, auth |
| **Function** | `@function_middleware` | Llamadas a tools/funciones | Validación, cache |
| **Chat** | `@chat_middleware` | Mensajes de chat | Filtrado de contenido |

**Código clave:**
```python
from agent_framework import (
    agent_middleware,
    function_middleware,
    chat_middleware,
    AgentRunContext,
    FunctionInvocationContext,
    ChatContext
)

# Agent Middleware - Logging
@agent_middleware
async def logging_middleware(context: AgentRunContext, next):
    print(f"[LOG] Iniciando run del agente '{context.agent.name}'")
    await next(context)  # ← Ejecutar agente
    print(f"[LOG] Run completado: {context.result}")

# Function Middleware - Caching
_cache = {}

@function_middleware
async def caching_middleware(context: FunctionInvocationContext, next):
    cache_key = f"{context.function.name}:{str(context.arguments)}"

    if cache_key in _cache:
        print("[CACHE] Hit!")
        context.result = _cache[cache_key]
        return  # No ejecutar función

    await next(context)  # Ejecutar función
    _cache[cache_key] = context.result

# Usar con agente
agent = client.create_agent(
    name="Agent with Middleware",
    instructions="...",
    middleware=[
        logging_middleware,
        timing_middleware,
        caching_middleware
    ]  # ← Ejecutan en ORDEN
)
```

**Middlewares Implementados:**
1. **logging_agent_middleware** - Logging de runs
2. **timing_agent_middleware** - Medición de performance
3. **content_filter_middleware** - Filtrado de contenido sensible
4. **logging_function_middleware** - Logging de tools
5. **validation_function_middleware** - Validación de argumentos
6. **caching_function_middleware** - Cache de resultados
7. **logging_chat_middleware** - Logging de mensajes
8. **auth_middleware** - Autenticación

**Casos de Uso Comunes:**
- 📝 Logging y auditoría
- ✅ Validación de inputs/outputs
- 🔒 Filtrado de contenido sensible
- 🚦 Rate limiting y cuotas
- 🔐 Autenticación y autorización
- 📊 Métricas y analytics
- 💾 Caching de resultados
- 🔄 Retry logic

---

### `018_observability_telemetry.py`

**Objetivo:** Implementar observabilidad y telemetría para monitorear agentes en producción

**Conceptos:**
- Logging estructurado (JSON)
- Métricas de rendimiento
- Tracking de tokens y costos
- Rastreo de errores
- Analytics de conversaciones
- Exportación de métricas
- Wrapper observable para agentes

**Componentes Principales:**

**1. AgentMetrics - Clase de Métricas**
```python
@dataclass
class AgentMetrics:
    agent_name: str
    total_runs: int = 0
    total_errors: int = 0
    total_execution_time: float = 0.0
    total_tokens_prompt: int = 0
    total_tokens_completion: int = 0
    total_cost_usd: float = 0.0
    run_history: List[Dict] = None

    @property
    def avg_execution_time(self) -> float:
        return self.total_execution_time / self.total_runs

    @property
    def success_rate(self) -> float:
        return (self.total_runs - self.total_errors) / self.total_runs * 100
```

**2. MetricsCollector - Recolector Centralizado**
```python
class MetricsCollector:
    """Collector centralizado de métricas para múltiples agentes"""

    def record_run(
        self,
        agent_name: str,
        execution_time: float,
        tokens_prompt: int,
        tokens_completion: int,
        cost_usd: float,
        error: bool = False
    ):
        # Registra métricas automáticamente
        pass

    def export_metrics(self, filename: str):
        # Exporta a JSON
        pass
```

**3. ObservableAgent - Wrapper con Observabilidad Automática**
```python
class ObservableAgent:
    """Wrapper que agrega observabilidad automática"""

    async def run(self, query: str) -> Any:
        start_time = time.time()
        try:
            response = await self.agent.run(query)
            # Registrar métricas exitosas
        except Exception as e:
            # Registrar error
            raise
        finally:
            # Calcular y guardar métricas
            metrics_collector.record_run(...)

        return response
```

**Métricas Rastreadas:**
- ⏱️ Tiempo de ejecución (total y promedio)
- 🔢 Uso de tokens (prompt + completion)
- 💰 Costos estimados (USD)
- ✅ Tasa de éxito / errores
- 📊 Historial completo de runs
- 📈 Métricas agregadas globales

**Integración en Producción:**
En producción, integrar con:
- OpenTelemetry (tracing distribuido)
- Azure Application Insights
- Prometheus + Grafana (métricas y dashboards)
- ELK Stack (logs centralizados)

---

### `019_conditional_workflows.py`

**Objetivo:** Workflows condicionales con decisiones dinámicas (if/else routing)

**Conceptos:**
- 3 patrones de conditional workflows
- Routing dinámico basado en contenido
- Retry logic con loops
- Escalado por complejidad
- `send_message_to()` para routing dirigido

**Patrones Implementados:**

**1. Classifier Pattern (If/Else Routing)**
```python
def create_classifier_executor(classifier_agent):
    @executor(id="Classifier")
    async def classifier(query: str, ctx: WorkflowContext[str]) -> None:
        # Clasificar la consulta
        response = await classifier_agent.run(classification_prompt)
        category = str(response).strip().lower()

        # ROUTING CONDICIONAL
        if "technical" in category:
            await ctx.send_message_to("TechnicalHandler", query)
        elif "creative" in category:
            await ctx.send_message_to("CreativeHandler", query)
        else:
            await ctx.send_message_to("GeneralHandler", query)

    return classifier
```

**2. Validator Pattern (Retry Logic)**
```python
def create_validator_executor(validator_agent):
    @executor(id="Validator")
    async def validator(data: dict, ctx: WorkflowContext[dict]) -> None:
        content = data["content"]
        attempt = data.get("attempt", 1)
        is_valid = len(content) > 50

        if is_valid:
            # ✅ VÁLIDO: Terminar con éxito
            await ctx.send_message_to("Finalizer", content)
        else:
            # ❌ INVÁLIDO: Decidir retry o fallar
            if attempt < 3:
                # 🔄 RETRY
                await ctx.send_message_to("Improver", {
                    "content": content,
                    "query": query,
                    "attempt": attempt + 1
                })
            else:
                # ⚠️ MAX INTENTOS
                await ctx.send_message_to("Finalizer", f"[FAILED] {content}")

    return validator
```

**3. Complexity Router Pattern**
```python
def create_complexity_router_executor(router_agent):
    @executor(id="ComplexityRouter")
    async def complexity_router(query: str, ctx: WorkflowContext[str]) -> None:
        # Evaluar complejidad (1-10)
        response = await router_agent.run(complexity_prompt)
        complexity = int(response)

        # ROUTING BASADO EN SCORE
        if complexity <= 3:
            await ctx.send_message_to("SimpleAgent", query)
        elif complexity <= 7:
            await ctx.send_message_to("StandardAgent", query)
        else:
            await ctx.send_message_to("ExpertAgent", query)

    return complexity_router
```

**Casos de Uso:**
- Sistema de triage (clasificar consultas por tipo/urgencia)
- Quality assurance con retry automático
- Escalado dinámico (modelo simple/estándar/experto según complejidad)
- Routing basado en contenido (técnico, creativo, general)

**Ver también:**
- `019_conditional_workflows_docs.html` - Documentación completa con diagramas

---

### `020_group_chat_workflow.py`

**Objetivo:** Group Chat workflows - Panel de expertos con múltiples agentes

**Conceptos:**
- Round-robin selection (turnos secuenciales)
- Task-based selection (selección por especialidad)
- Debate pattern (múltiples perspectivas)
- Agregación de respuestas de múltiples expertos

**Código clave:**
```python
# Round-Robin Selection
class RoundRobinSelector:
    def __init__(self, agents: List[str]):
        self.agents = agents
        self.current_index = 0

    def select_next(self) -> str:
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent

# Task-Based Selection
async def select_agent_by_task(task: str, available_agents: Dict[str, str]) -> str:
    if "code" in task.lower():
        return "EngineerAgent"
    elif "design" in task.lower():
        return "DesignerAgent"
    else:
        return "GeneralistAgent"
```

**Casos de Uso:**
- Panel de expertos (múltiples especialistas opinan)
- Code review (varios revisores evalúan código)
- Debate y consenso (perspectivas múltiples antes de decidir)
- Brainstorming distribuido

---

### `021_supervisor_pattern.py`

**Objetivo:** Patrón supervisor avanzado con orquestación compleja

**Conceptos:**
- Supervisor jerárquico (supervisor de supervisores)
- Delegación paralela (múltiples tareas simultáneas)
- Supervisión multi-nivel
- Agregación de resultados complejos

**Arquitectura:**
```
        Supervisor Principal
                ↓
        ┌───────┼───────┐
        ↓       ↓       ↓
    SubSuper1 SubSuper2 SubSuper3
        ↓       ↓       ↓
    [Tools] [Tools] [Tools]
```

**Casos de Uso:**
- Sistemas empresariales complejos
- Workflows multi-departamento
- Orquestación de microservicios
- Proyectos con múltiples fases

---

### `022_workflow_visualization_debugging.py`

**Objetivo:** Visualización y debugging de workflows

**Conceptos:**
- WorkflowViz para generar diagramas de workflows
- Múltiples formatos de salida: Mermaid, DOT, SVG, PNG, PDF
- Event-based debugging con ExecutorInvokedEvent, ExecutorCompletedEvent
- Inspección en tiempo real del flujo de ejecución

**Código clave:**
```python
from agent_framework import WorkflowViz

# Visualización de workflows
viz = WorkflowViz(workflow)

# Generar diagrama Mermaid
mermaid_diagram = viz.to_mermaid()
print(mermaid_diagram)

# Generar diagrama DOT (Graphviz)
dot_diagram = viz.to_digraph()

# Exportar a formatos de imagen
viz.export(format='svg', filename='workflow.svg')
viz.save_png('workflow.png')
viz.save_pdf('workflow.pdf')

# Event-based debugging
async for event in workflow.run_stream("input"):
    if isinstance(event, ExecutorInvokedEvent):
        print(f"[INVOKE] {event.executor_id}")
    elif isinstance(event, ExecutorCompletedEvent):
        print(f"[COMPLETE] {event.executor_id}")
    elif isinstance(event, WorkflowOutputEvent):
        print(f"[OUTPUT] {event.data}")
```

**Formatos de Salida:**
- **Mermaid**: Diagramas de flujo para documentación
- **DOT**: Formato Graphviz para visualización avanzada
- **SVG**: Vector gráfico escalable
- **PNG**: Imagen rasterizada
- **PDF**: Documento imprimible

**Eventos de Debugging:**
- `ExecutorInvokedEvent`: Cuando un executor inicia
- `ExecutorCompletedEvent`: Cuando un executor termina
- `WorkflowOutputEvent`: Cuando se produce output final
- `ExecutorErrorEvent`: Cuando hay un error

**⚠️ Puntos importantes:**
- Útil para debugging de workflows complejos
- Visualización ayuda a entender flujos paralelos y condicionales
- Events permiten tracking en tiempo real
- Ver `WORKFLOW_VISUALIZATION_GUIDE.md` para más detalles

---

### `agent_helpers.py`

**Objetivo:** Módulo de utilidades para gestión de agentes

**Funciones Disponibles:**

1. **`get_agent_id_by_name(client, agent_name)`**
   - Obtiene el ID de un agente por su nombre
   - Búsqueda manual iterando sobre todos los agentes
   - Retorna `None` si no encuentra el agente

2. **`list_all_agents(client, limit=100, order="desc")`**
   - Lista todos los agentes del proyecto
   - Retorna lista de objetos Agent
   - Soporta paginación y ordenamiento

3. **`find_agents_by_pattern(client, pattern, case_sensitive=False)`**
   - Busca agentes cuyo nombre coincida con un patrón
   - Soporta búsqueda case-insensitive
   - Retorna lista de agentes que coinciden

4. **`agent_exists(client, agent_name)`**
   - Verifica si un agente existe por nombre
   - Retorna `True` o `False`
   - Útil antes de intentar usar un agente

5. **`get_agent_info(client, agent_name)`**
   - Obtiene información completa de un agente
   - Retorna objeto Agent o `None`
   - Incluye nombre, ID, modelo, fecha de creación

**Código de ejemplo:**
```python
from agent_helpers import (
    get_agent_id_by_name,
    agent_exists,
    find_agents_by_pattern,
    get_agent_info
)

async with AzureAIAgentClient(async_credential=credential) as client:
    # Verificar existencia
    if await agent_exists(client, "MyAgent"):
        # Obtener ID
        agent_id = await get_agent_id_by_name(client, "MyAgent")

        # Obtener info completa
        agent_info = await get_agent_info(client, "MyAgent")
        print(f"Modelo: {agent_info.model}")

    # Buscar por patrón
    agents = await find_agents_by_pattern(client, "Joker")
    for agent in agents:
        print(f"{agent.name}: {agent.id}")
```

**⚠️ Puntos importantes:**
- Módulo reutilizable en todos tus proyectos
- Simplifica operaciones comunes con agentes
- Búsqueda manual necesaria (no hay API directa por nombre)
- Ver script `003d_using_agent_helpers.py` para ejemplos completos

---

## 🎨 DevUI para Debugging Interactivo

**DevUI** es una interfaz web de desarrollo que permite interactuar con agentes y workflows de forma visual e interactiva, facilitando el debugging y pruebas.

### ¿Qué es DevUI?

DevUI es un servidor web integrado en el Agent Framework que:
- Proporciona una interfaz tipo chat para probar agentes
- Permite ejecutar workflows visualmente
- Soporta auto-descubrimiento de agentes y workflows
- Incluye visualización de eventos en tiempo real
- Compatible con OpenAI API (ChatGPT-compatible)

### Instalación

```bash
pip install agent-framework-devui
```

### Conceptos Clave

**Auto-Discovery:** DevUI escanea directorios buscando archivos que definen variables específicas:
- `agent` en archivos `agent.py` → Carga agentes
- `workflow` en archivos `workflow.py` → Carga workflows

**Estructura de Directorios:**
```
proyecto/
├── agents/              # Agentes individuales
│   ├── agente1/
│   │   └── agent.py    # Debe exportar variable 'agent'
│   └── agente2/
│       └── agent.py
└── workflows/           # Workflows complejos
    ├── workflow1/
    │   └── workflow.py  # Debe exportar variable 'workflow'
    └── workflow2/
        └── workflow.py
```

---

### Agentes para DevUI

**Directorio:** `agents/`

**Estructura:**
```
agents/
├── simple_agent/
│   └── agent.py          # Asistente general
└── joker_agent/
    └── agent.py          # Asistente de chistes
```

**Cómo Crear un Agente para DevUI:**

```python
# agents/mi_agente/agent.py
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()
client = AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False
)

# IMPORTANTE: La variable DEBE llamarse 'agent'
agent = client.create_agent(
    instructions="Tu prompt aquí",
    name="MiAgente"
)

# Registrar cleanup para evitar memory leaks
register_cleanup(agent, credential.close)
```

**Uso:**
```bash
# Iniciar DevUI desde el directorio raíz
devui ./agents

# O desde la carpeta agents/
cd agents
devui

# DevUI:
# 1. Escanea subdirectorios buscando agent.py
# 2. Carga todos los agentes
# 3. Muestra dropdown para seleccionar agente
# 4. Inicia servidor en http://localhost:8080
# 5. Abre el navegador automáticamente
```

**Características:**
- Interfaz tipo chat para conversación natural
- Dropdown para cambiar entre agentes
- Historial de conversación
- Streaming de respuestas en tiempo real
- Reinicio de conversación

**Ver:** `agents/README.md` para más detalles

---

### Workflows para DevUI

**Directorio:** `workflows/`

**Estructura:**
```
workflows/
└── travel_planner/
    └── workflow.py       # Planificador de viajes
```

**Cómo Crear un Workflow para DevUI:**

```python
# workflows/mi_workflow/workflow.py
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import WorkflowBuilder, WorkflowContext, executor
from agent_framework_devui import register_cleanup
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()

# Crear agentes
client = AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False
)

agent1 = client.create_agent(instructions="...", name="Agent1")
agent2 = client.create_agent(instructions="...", name="Agent2")

# Crear executors
@executor(id="executor1")
async def executor1_func(input: str, ctx: WorkflowContext[str]) -> None:
    response = await agent1.run(input)
    await ctx.send_message(str(response))

@executor(id="executor2")
async def executor2_func(input: str, ctx: WorkflowContext[str]) -> None:
    response = await agent2.run(input)
    await ctx.yield_output(str(response))

# IMPORTANTE: La variable DEBE llamarse 'workflow'
workflow = (
    WorkflowBuilder()
    .set_start_executor(executor1_func)
    .add_edge(executor1_func, executor2_func)
    .build()
)

register_cleanup(workflow, credential.close)
```

**Uso:**
```bash
# Iniciar DevUI desde el directorio raíz
devui ./workflows

# O desde la carpeta workflows/
cd workflows
devui
```

**Ejemplo Disponible: Travel Planner**

Workflow paralelo con 5 agentes:
```
Input → LocationSelector
        ↓ (fan-out - paralelo)
        ├→ DestinationRecommender ┐
        ├→ WeatherAgent            ├→ (fan-in - combina)
        └→ CuisineExpert           ┘
                ↓
        ItineraryPlanner → Output
```

**Ver:** `workflows/README.md` para más detalles

---

### Diferencias: Agentes vs Workflows en DevUI

| Aspecto | Agentes | Workflows |
|---------|---------|-----------|
| **Variable** | `agent` | `workflow` |
| **Tipo** | ChatAgent | Workflow |
| **Ejecución** | Respuesta única | Flujo multi-paso |
| **Visualización** | Chat directo | Ejecución de executors |
| **Uso** | Conversación simple | Orquestación compleja |
| **Directorio** | `agents/` | `workflows/` |

---

### Tips para DevUI

1. **Naming:** Usa nombres descriptivos para agentes y workflows
2. **register_cleanup():** SIEMPRE registrar cleanup para evitar memory leaks
3. **should_cleanup_agent=False:** Mantener agentes en Azure AI Foundry
4. **Múltiples agentes:** DevUI carga TODOS los agentes y muestra dropdown
5. **Múltiples workflows:** Similar a agentes, todos se cargan
6. **Debugging:** DevUI es ideal para probar agentes antes de integrarlos

---

### Recursos DevUI

- **Guía Completa:** `DEVUI_GUIDE.md`
- **Ejemplos de Agentes:** `agents/` directory
- **Ejemplos de Workflows:** `workflows/` directory
- **Script Demo:** `023_devui_demo.py` (versión programática)

---

## 🧠 Conceptos Clave

### 1. Cliente vs Agente

```python
# AzureAIAgentClient - Gestiona conexión a Azure
client = AzureAIAgentClient(async_credential=credential)

# ChatAgent - Agente ejecutable (retornado por create_agent)
agent = client.create_agent(...)

# Relación
agent.chat_client  # → Referencia al AzureAIAgentClient
```

**⚠️ Error común:**
```python
# ❌ INCORRECTO
client = AzureAIAgentClient(agent_id=xxx)
result = await client.run("mensaje")  # client NO tiene .run()

# ✅ CORRECTO
client = AzureAIAgentClient(agent_id=xxx)
agent = client.create_agent(...)
result = await agent.run("mensaje")  # agent SÍ tiene .run()
```

### 2. IDs y sus Ubicaciones

```python
# Agent ID
agent.chat_client.agent_id  # ✅ Correcto (después de run)
agent.agent_id              # ❌ No existe

# Thread ID
thread.service_thread_id    # ✅ Correcto (thread explícito)
agent.chat_client.thread_id # ❌ Puede ser None
```

### 3. Creación Lazy (Perezosa)

```python
agent = client.create_agent(...)
print(agent.chat_client.agent_id)  # None (aún no creado)

await agent.run("Hola")
print(agent.chat_client.agent_id)  # asst_xxx (ahora sí existe)
```

### 4. Threads: Explícitos vs Implícitos

```python
# Thread implícito (no accesible)
result = await agent.run("Hola")
# No puedes obtener el Thread ID fácilmente

# Thread explícito (accesible)
thread = agent.get_new_thread()
result = await agent.run("Hola", thread=thread)
thread_id = thread.service_thread_id  # ✅ Disponible
```

### 5. Persistencia

```python
# Agente se elimina al cerrar (DEFAULT)
AzureAIAgentClient(async_credential=credential)

# Agente persiste en Azure AI Foundry
AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False  # ✅ Persistente
)
```

### 6. Context Manager Pattern

```python
# ✅ CORRECTO - Recursos se cierran automáticamente
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        # Tu código aquí

# ❌ INCORRECTO - Puede dejar sesiones abiertas
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)
# Puede causar: "Unclosed client session"
```

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: "Please provide an endpoint or a base_url"

**Causa:** Variables de entorno incorrectas

**Solución:**
```env
# ❌ INCORRECTO (Azure OpenAI directo)
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=...

# ✅ CORRECTO (Azure AI Foundry)
AZURE_AI_PROJECT_ENDPOINT=https://xxx.services.ai.azure.com/api/projects/xxx
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

### Problema 2: "Unclosed client session"

**Causa:** No usar context managers

**Solución:**
```python
# ✅ Usar async with para TODO
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        # código
```

### Problema 3: Agent ID o Thread ID es None

**Causa:** Creación lazy del agente

**Solución:**
```python
# ✅ Ejecutar primero, luego obtener ID
agent = client.create_agent(...)
await agent.run("Hola")  # Crea el agente en Azure
agent_id = agent.chat_client.agent_id  # Ahora tiene valor
```

### Problema 4: AttributeError 'ChatAgent' object has no attribute

**Causa:** Acceso incorrecto a propiedades

**Solución:**
```python
# ✅ CORRECTO
agent.chat_client.agent_id      # Agent ID
thread.service_thread_id        # Thread ID

# ❌ INCORRECTO
agent.agent_id                  # No existe
agent.thread_id                 # No existe
```

### Problema 5: UriContent no funciona con imágenes

**Causa:** Azure AI Foundry no soporta URLs externas

**Solución:**
```python
# ✅ Descargar primero
image_data = await download_image(url)
DataContent(data=image_data, media_type="image/jpeg")
```

### Problema 6: UnicodeEncodeError en Windows

**Causa:** Caracteres unicode (✓, ñ) en consola Windows

**Solución:**
```python
# ❌ Puede fallar en Windows
print("✓ Agente creado")

# ✅ Usar caracteres ASCII
print("[OK] Agente creado")
```

---

## 📊 Comparativa: Azure OpenAI vs Azure AI Foundry

| Aspecto | Azure OpenAI | Azure AI Foundry |
|---------|--------------|------------------|
| **Cliente** | `AzureOpenAIChatClient` | `AzureAIAgentClient` |
| **Paquete** | `agent_framework.azure` | `agent_framework_azure_ai` |
| **Endpoint Env** | `AZURE_OPENAI_ENDPOINT` | `AZURE_AI_PROJECT_ENDPOINT` |
| **Model Env** | `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | `AZURE_AI_MODEL_DEPLOYMENT_NAME` |
| **Credential Param** | `credential` | `async_credential` |
| **Credential Type** | Sync o Async | Solo Async |
| **Formato Endpoint** | `https://xxx.openai.azure.com/` | `https://xxx.services.ai.azure.com/api/projects/xxx` |
| **Persistencia** | No nativa | ✅ Agentes persistentes |

---

## 💡 Mejores Prácticas

1. **Siempre usar `async with`**
   - Garantiza cierre correcto de recursos
   - Evita "unclosed session" warnings

2. **Threads explícitos para persistencia**
   - Si necesitas el Thread ID, créalo explícitamente
   - Usar `thread = agent.get_new_thread()`

3. **Guardar IDs importantes**
   - Agent ID: Para reutilizar agentes
   - Thread ID: Para continuar conversaciones

4. **Verificar creación lazy**
   - Ejecutar `agent.run()` antes de obtener IDs
   - Los agentes no existen en Azure hasta la primera ejecución

5. **Un thread por conversación**
   - No mezclar contextos diferentes en el mismo thread
   - Crear nuevo thread para cada conversación independiente

6. **Nombres descriptivos**
   - Facilita identificar agentes en Azure AI Foundry Portal
   - Usar nombres que reflejen el propósito del agente

7. **`should_cleanup_agent=False` cuando sea necesario**
   - Usar cuando quieres que el agente persista
   - Por defecto, los agentes se eliminan al cerrar

8. **Manejo de imágenes**
   - Siempre usar `DataContent` (bytes)
   - Descargar imágenes de URLs primero
   - No usar `UriContent` directamente

---

## 🎯 Patrones de Código Útiles

### Patrón 1: Crear Agente Persistente

```python
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    ) as client:
        agent = client.create_agent(
            instructions="Tu prompt aquí",
            name="NombreAgente"
        )
        result = await agent.run("Primera pregunta")
        agent_id = agent.chat_client.agent_id
        print(f"Guarda este ID: {agent_id}")
```

### Patrón 2: Reutilizar Agente Existente

```python
AGENT_ID = "asst_xxx..."

async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        agent_id=AGENT_ID
    ) as client:
        agent = client.create_agent(
            instructions="Mismo prompt",
            name="MismoNombre"
        )
        result = await agent.run("Nueva pregunta")
```

### Patrón 3: Conversación Nueva con Contexto

```python
async with AzureAIAgentClient(agent_id=AGENT_ID, ...) as client:
    agent = client.create_agent(...)
    thread = agent.get_new_thread()

    await agent.run("Me llamo Juan", thread=thread)
    await agent.run("¿Cómo me llamo?", thread=thread)  # "Juan"

    thread_id = thread.service_thread_id
    print(f"Thread ID: {thread_id}")
```

### Patrón 4: Continuar Conversación Existente

```python
AGENT_ID = "asst_xxx..."
THREAD_ID = "thread_xxx..."

async with AzureAIAgentClient(agent_id=AGENT_ID, ...) as client:
    agent = client.create_agent(...)
    thread = agent.get_new_thread(service_thread_id=THREAD_ID)

    result = await agent.run("¿Qué recuerdas?", thread=thread)
```

### Patrón 5: Streaming de Respuestas

```python
async for update in agent.run_stream("Tu pregunta", thread=thread):
    if update.text:
        print(update.text, end="", flush=True)
print()  # Nueva línea
```

### Patrón 6: Agente con Herramientas

```python
def mi_funcion(param: str) -> str:
    """Descripción de la función."""
    return f"Resultado: {param}"

agent = client.create_agent(
    instructions="Usa las herramientas disponibles",
    name="AgentWithTools",
    tools=[mi_funcion]
)
```

### Patrón 7: Multi-Agente Optimizado

```python
async def create_and_persist_agent(credential, instructions, name, tools=None):
    async with AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=False
    ) as client:
        agent = client.create_agent(
            instructions=instructions,
            name=name,
            tools=tools
        )
        await agent.run("Confirma que estás listo")
        return agent.chat_client.agent_id

# Uso
agent1_id = await create_and_persist_agent(cred, "prompt1", "Agent1")
agent2_id = await create_and_persist_agent(cred, "prompt2", "Agent2")
```

### Patrón 8: Supervisor-Delegado con Closures

```python
# Crear agentes especializados
math_client, math_agent = await create_and_initialize_agent(
    credential, "Eres calculadora", "math_agent", [herramienta_math]
)

# Crear wrapper como herramienta
async def consultar_matematicas(problema: str) -> str:
    """Resuelve problemas matemáticos."""
    respuesta = await math_agent.run(problema)
    return respuesta.text

# Supervisor que usa el agente como herramienta
supervisor_client, supervisor = await create_and_initialize_agent(
    credential,
    "Eres supervisor. Delega a consultar_matematicas para cálculos.",
    "supervisor",
    tools=[consultar_matematicas]
)
```

### Patrón 9: Supervisor-Delegado con Partial

```python
from functools import partial

# Función genérica reutilizable
async def consultar_agente_generico(agent, dept: str, pregunta: str) -> str:
    respuesta = await agent.run(pregunta)
    return respuesta.text

# Crear herramienta con partial
consultar_matematicas = partial(consultar_agente_generico, math_agent, "MATH")
consultar_matematicas.__name__ = "consultar_matematicas"
consultar_matematicas.__doc__ = "Resuelve problemas matemáticos."

# Usar en supervisor
supervisor = await create_and_initialize_agent(
    credential,
    "Delega a consultar_matematicas para cálculos.",
    "supervisor",
    tools=[consultar_matematicas]
)
```

### Patrón 10: Workflow Secuencial (Cierre Automático)

```python
from agent_framework import WorkflowBuilder, WorkflowContext, executor

# 1. Crear factory functions para executors
def create_researcher_executor(agent):
    @executor(id="run_researcher")
    async def run_researcher(query: str, ctx: WorkflowContext[str]) -> None:
        response = await agent.run(query)
        await ctx.send_message(str(response))
    return run_researcher

def create_writer_executor(agent):
    @executor(id="run_writer")
    async def run_writer(data: str, ctx: WorkflowContext[str]) -> None:
        response = await agent.run(f"Escribe ensayo sobre: {data}")
        await ctx.yield_output(str(response))
    return run_writer

# 2. Usar async with para cierre automático
async with AzureAIAgentClient(...) as researcher_client:
    researcher = researcher_client.create_agent(...)

    async with AzureAIAgentClient(...) as writer_client:
        writer = writer_client.create_agent(...)

        # 3. Construir workflow
        workflow = (
            WorkflowBuilder()
            .add_edge(create_researcher_executor(researcher),
                      create_writer_executor(writer))
            .set_start_executor(create_researcher_executor(researcher))
            .build()
        )

        # 4. Ejecutar
        async for event in workflow.run_stream("query"):
            if isinstance(event, WorkflowOutputEvent):
                print(event.data)
```

### Patrón 11: Workflow Secuencial (Cierre Manual)

```python
from agent_framework import WorkflowBuilder, WorkflowContext, executor

async def create_and_initialize_agent(credential, instructions, name):
    client = AzureAIAgentClient(async_credential=credential)
    agent = client.create_agent(instructions=instructions, name=name)
    await agent.run("Confirma que estás listo")
    return client, agent

# 1. Crear agentes y rastrear clientes
async with DefaultAzureCredential() as credential:
    clients = []

    try:
        # Crear agentes
        r_client, researcher = await create_and_initialize_agent(...)
        clients.append(r_client)

        w_client, writer = await create_and_initialize_agent(...)
        clients.append(w_client)

        # 2. Construir y ejecutar workflow (igual que patrón 10)
        workflow = (...)

        async for event in workflow.run_stream("query"):
            if isinstance(event, WorkflowOutputEvent):
                print(event.data)

    finally:
        # 3. Cerrar manualmente todos los clientes
        for client in clients:
            await client.__aexit__(None, None, None)
```

---

## 🔄 Flujo de Trabajo Típico

### Sesión 1: Crear y Configurar
```bash
1. python 001_createandrunanagent.py
   → Copiar Agent ID: asst_xxx

2. python 003_persistentconversation.py
   → Usar Agent ID anterior
   → Copiar Thread ID: thread_xxx
```

### Sesión 2: Continuar Trabajo
```bash
1. python 002_reuseexistingagent.py
   → Usar Agent ID guardado
   → Nueva conversación (sin contexto anterior)

2. python 004_continuethreadconversation.py
   → Usar Agent ID + Thread ID guardados
   → Continuar conversación (con contexto)
```

### Sesión 3: Trabajo Avanzado
```bash
1. python 005_usingimageswithanagent.py
   → Agente con capacidades de vision

2. python 008_multi_agent_collaboration_fixed.py
   → Múltiples agentes colaborando

3. python 009_agents_using_other_agents_as_tools.py
   → Patrón supervisor-delegado con closures

4. python 010_agents_using_other_agents_as_tools_with_partial.py
   → Patrón supervisor-delegado con functools.partial

5. python 011_assistant_websocket_agent_framework.py
   → API WebSocket para integración con frontends
   → Endpoints: ws://localhost:8000/ws/chat

6. python 012_sequential_workflow.py
   → Workflow secuencial con cierre automático
   → Researcher → Writer pipeline

7. python 013_sequential_workflow.py
   → Mismo workflow que 012 pero con cierre manual
   → Comparar enfoques de gestión de recursos
```

---

## 📁 Estructura del Proyecto

```
MicrosoftAgentFramework/
├── .env                                          # Configuración (NO versionar)
├── README.md                                     # Este archivo
├── CLAUDE.md                                     # Documentación técnica detallada
├── WEBSOCKET_COMPARISON.md                       # Comparación WebSocket APIs
├── DEVUI_GUIDE.md                                # Guía completa de DevUI
├── WORKFLOW_VISUALIZATION_GUIDE.md               # Guía de visualización de workflows
│
├── 001_createandrunanagent.py                    # Nivel 1: Crear agente
├── 002_reuseexistingagent.py                    # Nivel 1: Reutilizar agente
├── 003_persistentconversation.py                # Nivel 1: Conversación con contexto
├── 003b_persistentconversation_by_name.py        # Nivel 1: Conversación por nombre
├── 003c_list_all_agents.py                       # Nivel 1: Listar agentes
├── 003d_using_agent_helpers.py                   # Nivel 1: Demo de agent_helpers
├── 004_continuethreadconversation.py            # Nivel 2: Continuar conversación
├── 005_usingimageswithanagent.py                # Nivel 2: Agentes con vision
├── 008_multi_agent_collaboration_fixed.py       # Nivel 3: Multi-agente
├── 009_agents_using_other_agents_as_tools.py    # Nivel 3: Agentes como herramientas (closures)
├── 010_agents_using_other_agents_as_tools_with_partial.py  # Nivel 3: Agentes como herramientas (partial)
├── 011_assistant_websocket_agent_framework.py   # Nivel 3: API WebSocket con Agent Framework
├── 012_sequential_workflow.py                    # Nivel 3: Workflow secuencial (cierre automático)
├── 013_sequential_workflow.py                    # Nivel 3: Workflow secuencial (cierre manual)
├── 014_parallel-workflow.py                      # Nivel 3: Workflow paralelo (fan-out/fan-in)
├── 015_agent_with_mcp_tools.py                   # Nivel 4: MCP Tools (Model Context Protocol)
├── 016_context_providers.py                      # Nivel 4: Context Providers
├── 017_middleware.py                             # Nivel 4: Middleware
├── 018_observability_telemetry.py                # Nivel 4: Observabilidad y telemetría
├── 019_conditional_workflows.py                  # Nivel 4: Workflows condicionales
├── 020_group_chat_workflow.py                    # Nivel 4: Group Chat
├── 021_supervisor_pattern.py                     # Nivel 4: Supervisor Pattern
├── 022_workflow_visualization_debugging.py       # Nivel 4: Visualización de workflows
├── 023_devui_demo.py                             # DevUI demo (versión programática)
│
├── agent_helpers.py                              # Módulo de utilidades para agentes
├── assistant_websocket.py                        # API WebSocket con AIProjectClient
│
├── agents/                                        # Agentes para DevUI (auto-discovery)
│   ├── README.md                                 # Documentación de agentes
│   ├── simple_agent/
│   │   └── agent.py                              # Asistente general
│   └── joker_agent/
│       └── agent.py                              # Asistente de chistes
│
├── workflows/                                     # Workflows para DevUI (auto-discovery)
│   ├── README.md                                 # Documentación de workflows
│   └── travel_planner/
│       └── workflow.py                           # Planificador de viajes (paralelo)
│
└── images/
    └── nature.jpg                                # Imagen de ejemplo
```

---

## 🌐 Recursos Adicionales

### Documentación Oficial

- **Microsoft Agent Framework - Tutoriales:**
  [https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/function-tools-approvals?pivots=programming-language-python](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/function-tools-approvals?pivots=programming-language-python)

- **Azure AI Foundry:**
  [https://learn.microsoft.com/en-us/azure/ai-foundry/](https://learn.microsoft.com/en-us/azure/ai-foundry/)

- **Agent Framework Python SDK:**
  [https://pypi.org/project/agent-framework-azure-ai/](https://pypi.org/project/agent-framework-azure-ai/)

### Conceptos Relacionados

- **Agents:** Entidades de IA con instrucciones y capacidades específicas
- **Threads:** Conversaciones con contexto persistente
- **Tools/Functions:** Capacidades personalizadas para agentes
- **Vision Models:** Modelos con capacidad de procesar imágenes (GPT-4o)
- **Context Providers:** Proveedores de contexto dinámico
- **Middleware:** Interceptores de mensajes
- **Workflows:** Orquestación de múltiples agentes (secuencial, paralelo, condicional)
- **WorkflowViz:** Visualización de workflows en múltiples formatos
- **DevUI:** Interfaz web para debugging interactivo de agentes y workflows
- **MCP Tools:** Model Context Protocol para herramientas externas
- **Observability:** Logging, métricas y telemetría para producción

### Próximos Temas Sugeridos

1. **RAG (Retrieval Augmented Generation):** Búsqueda de documentos
2. **Custom Tools:** Herramientas personalizadas avanzadas
3. **Approvals:** Flujos de aprobación humana
4. ✅ **Observability:** Logging y telemetría (implementado en 018)
5. ✅ **Workflows Secuenciales:** Orquestación de agentes (implementado en 012 y 013)
6. ✅ **Workflows Paralelos:** Fan-out/Fan-in (implementado en 014)
7. ✅ **Workflows Condicionales:** If/else routing (implementado en 019)
8. ✅ **MCP Tools:** Model Context Protocol (implementado en 015)
9. ✅ **Context Providers:** Contexto dinámico (implementado en 016)
10. ✅ **Middleware:** Interceptores (implementado en 017)
11. ✅ **Group Chat:** Panel de expertos (implementado en 020)
12. ✅ **Supervisor Pattern:** Orquestación avanzada (implementado en 021)
13. ✅ **Workflow Visualization:** Diagramas y debugging (implementado en 022)
14. ✅ **DevUI:** Debugging interactivo (implementado en agents/ y workflows/)
15. ✅ **Agent Helpers:** Utilidades para gestión (implementado en agent_helpers.py)
16. **Error Handling:** Manejo robusto de errores
17. **Advanced RAG:** Vector stores y semantic search

---

## 🎓 Conclusión

Este curso cubre los fundamentos y conceptos avanzados del Microsoft Agent Framework:

**Fundamentos:**
- ✅ Crear agentes persistentes
- ✅ Gestionar conversaciones con contexto
- ✅ Reutilizar agentes y conversaciones (por ID y por nombre)
- ✅ Utilidades para gestión de agentes (agent_helpers.py)
- ✅ Trabajar con imágenes (vision)

**Colaboración Multi-Agente:**
- ✅ Colaboración multi-agente
- ✅ Patrón supervisor-delegado
- ✅ Agentes como herramientas de otros agentes
- ✅ Closures y `functools.partial` para reutilización

**Workflows:**
- ✅ Workflows secuenciales (cierre automático y manual)
- ✅ Workflows paralelos (fan-out/fan-in)
- ✅ Workflows condicionales (routing dinámico)
- ✅ Group chat workflows (panel de expertos)
- ✅ Supervisor pattern avanzado
- ✅ Visualización de workflows (Mermaid, DOT, SVG, PNG, PDF)
- ✅ Event-based debugging

**Herramientas y Extensibilidad:**
- ✅ MCP Tools (Model Context Protocol)
- ✅ Context Providers (contexto dinámico)
- ✅ Middleware (interceptores)
- ✅ Herramientas personalizadas

**Producción:**
- ✅ Observabilidad y telemetría
- ✅ Gestión de recursos (cierre automático vs manual)
- ✅ Factory pattern para executors
- ✅ APIs WebSocket para integración con aplicaciones web

**Debugging:**
- ✅ DevUI (interfaz web interactiva)
- ✅ Workflow visualization
- ✅ Event-based debugging
- ✅ Auto-discovery de agentes y workflows

**Próximo paso:** Explorar temas avanzados como RAG, error handling avanzado y vector stores.

---

## 📝 IDs de Referencia (Actuales)

```python
# Agent ID actual del proyecto
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"

# Thread ID actual del proyecto
THREAD_ID = "thread_7dLiIQQlgsCOCUw3neCkjMbr"
```

**Nota:** Estos IDs son específicos de este proyecto. Genera tus propios IDs al ejecutar los scripts.

---

## 🤝 Contribuciones

Este es un repositorio de aprendizaje. Siéntete libre de:
- Agregar nuevos ejemplos
- Mejorar la documentación
- Reportar problemas o errores
- Compartir casos de uso

---

## 📜 Licencia

Este proyecto es de código abierto con fines educativos.

---

**Última actualización:** 2025-12-07
**Versión:** 1.3.0
**Autor:** Curso de Microsoft Agent Framework

**Novedades en v1.3.0:**
- DevUI para debugging interactivo
- Workflow visualization (múltiples formatos)
- Agent helpers (utilidades de gestión)
- Directorios agents/ y workflows/ para auto-discovery
- Guías completas: DEVUI_GUIDE.md y WORKFLOW_VISUALIZATION_GUIDE.md

# Microsoft Agent Framework - Documentación del Proyecto

## 📋 Información General

Este proyecto utiliza el **Microsoft Agent Framework** con **Azure AI Foundry** para crear y gestionar agentes de IA con conversaciones persistentes.

---

## 🔑 Configuración (.env)

```env
AZURE_AI_PROJECT_ENDPOINT=https://agentframeworkproject.services.ai.azure.com/api/projects/proj-agentframework
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

### Variables Importantes
- `AZURE_AI_PROJECT_ENDPOINT`: Endpoint de Azure AI Foundry (no Azure OpenAI directo)
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: Nombre del modelo desplegado en Azure

---

## 🆔 IDs del Proyecto

### Agent ID (Asistente)
```
asst_EkJeB3eaxhhwTsRxRp9JZBU4
```
- **Propósito**: Identificador del agente en Azure AI Foundry
- **Formato**: Comienza con `asst_`
- **Uso**: Reutilizar el mismo agente en múltiples sesiones
- **Persistencia**: Se mantiene en Azure AI Foundry si `should_cleanup_agent=False`

### Thread ID (Conversación)
```
thread_7dLiIQQlgsCOCUw3neCkjMbr
```
- **Propósito**: Identificador de la conversación/hilo
- **Formato**: Comienza con `thread_`
- **Uso**: Mantener el contexto de conversaciones entre ejecuciones
- **Persistencia**: Se almacena en Azure AI Foundry

---

## 📁 Estructura de Scripts

### 001_createandrunanagent.py
**Propósito**: Crear un agente nuevo y obtener su ID

**Características**:
- Crea un agente en Azure AI Foundry
- Muestra el Agent ID después de la primera ejecución
- Demuestra uso básico y streaming
- Configurado con `should_cleanup_agent=False` para persistencia

**Código clave**:
```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

async with AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False  # El agente NO se eliminará
) as client:
    agent = client.create_agent(
        instructions="Eres bueno contando chistes.",
        name="Joker"
    )
    result = await agent.run("Tell me a joke")
    print(f"Agent ID: {agent.chat_client.agent_id}")
```

### 002_reuseexistingagent.py
**Propósito**: Reutilizar un agente existente por su ID

**Características**:
- Conecta a un agente existente usando `agent_id`
- Múltiples ejemplos de uso (simple, streaming, múltiples preguntas)
- No crea un nuevo agente, usa uno ya creado

**Código clave**:
```python
AGENT_ID = "asst_EkJeB3eaxhhwTsRxRp9JZBU4"

async with AzureAIAgentClient(
    async_credential=credential,
    agent_id=AGENT_ID  # Reutiliza el agente existente
) as client:
    agent = client.create_agent(...)
```

### 003_persistentconversation.py
**Propósito**: Crear una conversación con contexto persistente

**Características**:
- Crea un thread explícito para gestionar el contexto
- Demuestra memoria de conversación (recuerda información previa)
- Muestra el Thread ID para reutilizarlo después
- Todas las interacciones usan el mismo thread

**Código clave**:
```python
# Crear thread explícito
thread = agent.get_new_thread(service_thread_id=None)

# Usar el mismo thread en todas las interacciones
result = await agent.run("Mi color favorito es azul", thread=thread)
result = await agent.run("¿Cuál es mi color favorito?", thread=thread)

# Obtener Thread ID
thread_id = thread.service_thread_id
```

### 004_continuethreadconversation.py
**Propósito**: Continuar una conversación existente usando Thread ID

**Características**:
- Reutiliza un thread existente por su ID
- El agente recuerda toda la conversación anterior
- Permite agregar nueva información al contexto
- Demuestra persistencia de conversaciones entre ejecuciones

**Código clave**:
```python
THREAD_ID = "thread_7dLiIQQlgsCOCUw3neCkjMbr"

# Crear thread con ID existente
thread = agent.get_new_thread(service_thread_id=THREAD_ID)

# El agente recuerda el contexto anterior
result = await agent.run("¿Qué sabes de mí?", thread=thread)
```

### 015_agent_with_mcp_tools.py
**Propósito**: Demostrar cómo usar HostedMCPTool (Model Context Protocol Tools) con agentes

**Características**:
- 7 ejemplos completos de configuración de MCP Tools
- Diferentes modos de aprobación (always_require, never_require, específico)
- Filtrado de herramientas permitidas (allowed_tools)
- Autenticación con headers (Bearer tokens, API keys)
- Ejemplo de agente usando múltiples herramientas MCP
- Tabla comparativa de configuraciones

**Conceptos Clave**:
- **HostedMCPTool**: Clase para conectar agentes a servidores MCP externos
- **Approval Mode**: Control de cuándo se requiere aprobación del usuario
- **Allowed Tools**: Filtrar qué herramientas del servidor MCP puede usar el agente
- **Headers**: Autenticación y configuración de peticiones HTTP
- **MCP (Model Context Protocol)**: Protocolo para extender capacidades de agentes

**Código clave**:
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

**7 Ejemplos Incluidos**:
1. HostedMCPTool básico (mínima configuración)
2. MCP Tool con modos de aprobación
3. MCP Tool con herramientas permitidas (allowed_tools)
4. MCP Tool con autenticación (headers)
5. MCP Tool con aprobación específica por herramienta
6. Agente usando múltiples MCP Tools
7. Tabla comparativa de configuraciones

**Modos de Aprobación**:

| Modo | Descripción | Uso |
|------|-------------|-----|
| `"always_require"` | Siempre requiere aprobación del usuario | APIs peligrosas/destructivas |
| `"never_require"` | Nunca requiere aprobación (auto) | APIs seguras/solo lectura |
| Específico (dict) | Aprobación por herramienta | Mix de operaciones seguras/peligrosas |

**Nota Importante**: El script usa URLs de ejemplo. Para uso en producción:
- Reemplaza con URLs de servidores MCP reales
- Configura autenticación con tokens/API keys válidos
- Asegúrate de que los servidores MCP estén activos

### 016_context_providers.py
**Propósito**: Demostrar cómo usar Context Providers para inyectar contexto dinámico a los agentes

**Características**:
- 7 ejemplos completos de Context Providers
- Inyección automática de contexto antes de cada invocación
- Múltiples providers combinables (AggregateContextProvider)
- Providers con estado dinámico
- Separación de contexto vs lógica del agente

**Context Providers Implementados**:
1. **DateTimeContextProvider** - Contexto temporal (fecha/hora actual)
2. **UserContextProvider** - Información del usuario
3. **BusinessRulesContextProvider** - Reglas de negocio dinámicas
4. **ConversationMemoryProvider** - Memoria de conversación
5. **DynamicPricingContextProvider** - Estado dinámico (pricing)

**Código clave**:
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

**Ventajas de Context Providers**:
- ✅ Contexto dinámico que cambia por invocación
- ✅ No modifica instrucciones base del agente
- ✅ Reutilizable entre múltiples agentes
- ✅ Combinable (múltiples providers)
- ✅ Testeable independientemente
- ✅ Separación de concerns

**Casos de Uso**:
- Información de usuario (perfil, rol, preferencias)
- Contexto temporal (fecha, hora, zona horaria)
- Reglas de negocio (horarios, políticas, límites)
- Datos de sistemas externos (CRM, bases de datos)
- Estado de sesión (carrito, progreso, historial)

### 017_middleware.py
**Propósito**: Demostrar cómo usar Middleware para interceptar y modificar comportamiento de agentes

**Características**:
- 3 tipos de middleware: Agent, Function, Chat
- 8 ejemplos completos de middleware
- Cadenas de middleware (múltiples en secuencia)
- Cross-cutting concerns sin modificar código principal
- Casos de uso: logging, validación, caching, seguridad

**Tipos de Middleware**:

| Tipo | Decorador | Intercepta | Uso |
|------|-----------|------------|-----|
| **Agent** | `@agent_middleware` | Runs completos del agente | Logging, timing, auth |
| **Function** | `@function_middleware` | Llamadas a tools/funciones | Validación, cache |
| **Chat** | `@chat_middleware` | Mensajes de chat | Filtrado de contenido |

**Código clave**:
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

# Agent Middleware - Timing
@agent_middleware
async def timing_middleware(context: AgentRunContext, next):
    start = time.time()
    await next(context)
    elapsed = time.time() - start
    print(f"[TIMING] Tiempo: {elapsed:.2f}s")

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

**Middlewares Implementados**:
1. **logging_agent_middleware** - Logging de runs
2. **timing_agent_middleware** - Medición de performance
3. **content_filter_middleware** - Filtrado de contenido sensible
4. **logging_function_middleware** - Logging de tools
5. **validation_function_middleware** - Validación de argumentos
6. **caching_function_middleware** - Cache de resultados
7. **logging_chat_middleware** - Logging de mensajes
8. **auth_middleware** - Autenticación

**Casos de Uso Comunes**:
- 📝 Logging y auditoría
- ✅ Validación de inputs/outputs
- 🔒 Filtrado de contenido sensible
- 🚦 Rate limiting y cuotas
- 🔐 Autenticación y autorización
- 📊 Métricas y analytics
- 💾 Caching de resultados
- 🔄 Retry logic

**Importante**:
- Los middlewares se ejecutan en el ORDEN especificado
- Siempre llamar `await next(context)` para continuar la cadena
- Puedes modificar `context` antes o después de `next()`
- Si no llamas `next()`, interrumpes la ejecución

### 018_observability_telemetry.py
**Propósito**: Implementar observabilidad y telemetría para monitorear agentes en producción

**Características**:
- Logging estructurado (JSON)
- Métricas de rendimiento
- Tracking de tokens y costos
- Rastreo de errores
- Analytics de conversaciones
- Exportación de métricas
- Wrapper observable para agentes

**Componentes Principales**:

**1. Logging Estructurado**
```python
# Logger con formato JSON
logger = setup_structured_logging()

logger.info(
    "Agent run completed",
    extra={'extra_data': {
        'agent_name': 'MyAgent',
        'execution_time': 1.23,
        'tokens': 500,
        'cost': 0.001
    }}
)
```

**2. Clase de Métricas**
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

**3. Metrics Collector**
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

**4. Observable Agent Wrapper**
```python
class ObservableAgent:
    """Wrapper que agrega observabilidad automática"""

    def __init__(self, agent, agent_name: str):
        self.agent = agent
        self.agent_name = agent_name

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
            execution_time = time.time() - start_time
            metrics_collector.record_run(...)

        return response

# Uso
observable_agent = ObservableAgent(
    agent=base_agent,
    agent_name="MyAgent"
)

response = await observable_agent.run("query")
# ← Métricas registradas automáticamente
```

**Métricas Rastreadas**:
- ⏱️ Tiempo de ejecución (total y promedio)
- 🔢 Uso de tokens (prompt + completion)
- 💰 Costos estimados (USD)
- ✅ Tasa de éxito / errores
- 📊 Historial completo de runs
- 📈 Métricas agregadas globales

**Funcionalidades**:
- Logging estructurado con formato JSON
- Métricas por agente individual
- Métricas globales agregadas
- Exportación a JSON
- Tracking de errores
- Analytics de patrones de uso

**Integración en Producción**:
```
En producción, integrar con:
• OpenTelemetry (tracing distribuido)
• Azure Application Insights
• Prometheus + Grafana (métricas y dashboards)
• ELK Stack (logs centralizados)
• DataDog, New Relic, Splunk, etc.
```

**Datos que se deben rastrear**:
- Latencia y tiempo de respuesta
- Uso de tokens y costos
- Tasas de error y tipos de errores
- Patrones de consultas
- Uso de herramientas/tools
- Satisfacción del usuario (si aplicable)

### 012_sequential_workflow.py
**Propósito**: Demostrar workflows secuenciales con múltiples agentes (versión con cierre automático)

> **Nota**: Este script y `013_sequential_workflow.py` son **funcionalmente idénticos**. La única diferencia es el enfoque de gestión de recursos. Ninguno es superior; usa el que prefieras.

**Características**:
- Orquesta múltiples agentes en un flujo secuencial
- Usa `WorkflowBuilder` para conectar executors
- Patrón: Researcher Agent → Writer Agent (pipeline)
- Cierre automático de recursos con `async with`
- Visualización del workflow en formato Mermaid

**Arquitectura**:
```
Input → Researcher (investiga) → Writer (escribe ensayo) → Output
```

**Código clave**:
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

**Conceptos Clave**:
- **Executor**: Función decorada con `@executor` que representa una tarea
- **Factory Pattern**: Usar funciones factory para dar a los executors acceso a los agentes mediante closures
- **WorkflowBuilder**: Conecta executors con `.add_edge()` y define el punto de inicio
- **Context**: `ctx.send_message()` envía datos al siguiente, `ctx.yield_output()` produce el resultado final
- **Cierre Automático**: Los clientes se cierran automáticamente con `async with`

**Visualización**:
El script genera un diagrama Mermaid del workflow en la consola.

### 013_sequential_workflow.py
**Propósito**: El mismo workflow secuencial que 012, pero usando cierre manual de recursos (versión con cierre manual)

> **Nota**: Este script y `012_sequential_workflow.py` son **funcionalmente idénticos**. La única diferencia es el enfoque de gestión de recursos. Ninguno es superior; usa el que prefieras.

**Características**:
- **Misma funcionalidad** que 012_sequential_workflow.py
- **Diferente enfoque**: Cierre manual con `__aexit__()` en lugar de `async with`
- Útil para comparar ambos enfoques de gestión de recursos
- Demuestra el patrón con `create_and_initialize_agent()` que retorna cliente y agente
- Más apropiado para patrones supervisor (aunque funciona igual para secuencial)

**Diferencias Clave con 012**:

| Aspecto | 012 (Cierre Automático) | 013 (Cierre Manual) |
|---------|--------------------------|---------------------|
| **Creación de clientes** | `async with AzureAIAgentClient(...) as client:` | `client = AzureAIAgentClient(...)` |
| **Función helper** | `initialize_agent()` (solo inicializa) | `create_and_initialize_agent()` (crea y retorna todo) |
| **Retorno** | Solo agente | Tuple (client, agent) |
| **Cierre** | Automático al salir del bloque | Manual con `await client.__aexit__()` |
| **Lista de clients** | No necesaria | `clients = []` para rastrear |
| **Try/Finally** | No necesario | Requerido para garantizar cierre |

**Código clave (diferencias)**:
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

        # Construir y ejecutar workflow
        # ... (igual que 012) ...

    finally:
        # 3. Cierre manual de todos los clientes
        for client in clients:
            await client.__aexit__(None, None, None)
```

**¿Cuándo este enfoque es más natural?**
- Patrones supervisor donde necesitas todos los agentes activos simultáneamente
- Cuando prefieres control explícito sobre el ciclo de vida de recursos
- Cuando el anidamiento profundo de `async with` se vuelve difícil de leer
- **Nota**: Para workflows secuenciales simples (como este), ambos enfoques funcionan igual de bien

**Comparación Visual**:
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

**Ver también**: Sección "7. Gestión de Recursos: Cierre Manual vs Automático" para entender cuándo usar cada enfoque.

### 014_parallel-workflow.py
**Propósito**: Demostrar workflows paralelos con fan-out y fan-in (ejecución paralela de múltiples agentes)

**Características**:
- Orquesta 5 agentes en un flujo paralelo (fan-out y fan-in)
- Usa `WorkflowBuilder` con `.add_fan_out_edges()` y `.add_fan_in_edges()`
- Patrón: Selector → (Recommender + Weather + Cuisine en paralelo) → Planner
- Cierre manual de recursos con `__aexit__()` (mismo estilo que 013)
- Visualización del workflow en formato Mermaid
- Factory pattern para todos los executors

**Arquitectura**:
```
Input → Location Selector
        ↓ (fan-out - ejecución paralela)
        ├→ Destination Recommender ┐
        ├→ Weather Agent            ├→ (fan-in - combina resultados)
        └→ Cuisine Suggestion       ┘
                ↓
        Itinerary Planner → Output
```

**Código clave**:
```python
from agent_framework import WorkflowBuilder, WorkflowContext, executor

# 1. Crear executors con factory pattern
def create_location_selector_executor(location_picker_agent):
    @executor(id="LocationSelector")
    async def location_selector(user_query: str, ctx: WorkflowContext[str]) -> None:
        response = await location_picker_agent.run(user_query)
        await ctx.send_message(str(response))  # Fan-out desde aquí
    return location_selector

def create_destination_recommender_executor(destination_recommender_agent):
    @executor(id="DestinationRecommender")
    async def destination_recommender(location: str, ctx: WorkflowContext[str]) -> None:
        response = await destination_recommender_agent.run(location)
        await ctx.send_message(str(response))  # Hacia fan-in
    return destination_recommender

# (Similarmente para weather_executor, cuisine_suggestion_executor)

def create_itinerary_planner_executor(itinerary_planner_agent):
    @executor(id="ItineraryPlanner")
    async def itinerary_planner(results: list[str], ctx: WorkflowContext[str]) -> None:
        # Recibe lista de resultados del fan-in
        combined_results = "\n\n".join(results)
        response = await itinerary_planner_agent.run(combined_results)
        await ctx.yield_output(str(response))  # Output final
    return itinerary_planner

# 2. Crear agentes con cierre manual (igual que 013)
async with DefaultAzureCredential() as credential:
    clients = []
    try:
        # Crear 5 agentes
        location_client, location_agent = await create_and_initialize_agent(...)
        clients.append(location_client)

        destination_client, destination_agent = await create_and_initialize_agent(...)
        clients.append(destination_client)

        # ... (weather, cuisine, itinerary)

        # 3. Construir workflow paralelo
        location_exec = create_location_selector_executor(location_agent)
        destination_exec = create_destination_recommender_executor(destination_agent)
        weather_exec = create_weather_executor(weather_agent)
        cuisine_exec = create_cuisine_suggestion_executor(cuisine_agent)
        itinerary_exec = create_itinerary_planner_executor(itinerary_agent)

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

        # 4. Ejecutar workflow
        async for event in workflow.run_stream("query"):
            if isinstance(event, WorkflowOutputEvent):
                print(event.data)

    finally:
        # Cierre manual de todos los clientes
        for client in clients:
            await client.__aexit__(None, None, None)
```

**Conceptos Clave**:
- **Fan-out**: Un executor envía datos a múltiples executors que se ejecutan en **paralelo**
- **Fan-in**: Múltiples executors envían resultados a un solo executor que los **combina**
- **Ejecución Paralela**: Los 3 agentes (Destination, Weather, Cuisine) procesan simultáneamente
- **Lista de Resultados**: El executor de fan-in recibe `list[str]` con todos los resultados
- **Mismo patrón de cierre que 013**: Cierre manual con `clients = []` y `__aexit__()`

**Diferencias con Workflow Secuencial (012/013)**:

| Aspecto | Secuencial (012/013) | Paralelo (014) |
|---------|----------------------|----------------|
| **Número de agentes** | 2 | 5 |
| **Conexiones** | `.add_edge(A, B)` | `.add_fan_out_edges()` + `.add_fan_in_edges()` |
| **Ejecución** | Secuencial (uno tras otro) | Paralela (3 simultáneos) |
| **Flujo** | Lineal (A → B) | Red (A → [B,C,D] → E) |
| **Input del último executor** | `str` (un resultado) | `list[str]` (múltiples resultados) |
| **Uso típico** | Pipeline, transformaciones | Gather-scatter, aggregación |

**Visualización**:
El script genera un diagrama Mermaid del workflow paralelo en la consola.

**Caso de Uso**:
Planificador de vacaciones que recopila información de múltiples fuentes (destinos, clima, comida) de forma paralela y luego las combina en un itinerario completo.

---

## 🔧 Conceptos Técnicos Importantes

### 1. Cliente vs Agente
```python
# AzureAIAgentClient - Cliente que gestiona la conexión
client = AzureAIAgentClient(async_credential=credential)

# ChatAgent - Wrapper que retorna create_agent()
agent = client.create_agent(...)  # Retorna ChatAgent

# Acceso al cliente desde el agente
agent.chat_client  # Referencia al AzureAIAgentClient
```

### 2. IDs y sus ubicaciones
```python
# Agent ID - Acceso correcto
agent.chat_client.agent_id  # ✅ Correcto
agent.agent_id              # ❌ No existe

# Thread ID - Acceso correcto
thread.service_thread_id    # ✅ Correcto (después de crear thread explícito)
agent.chat_client.thread_id # ❌ Puede ser None
result.conversation_id      # ❌ AgentRunResponse no tiene este atributo
```

### 3. Creación Lazy (Perezosa)
- El agente NO se crea en Azure hasta la primera llamada a `agent.run()`
- Por eso `agent.chat_client.agent_id` es `None` antes de ejecutar
- Siempre ejecutar al menos una vez antes de obtener el ID

### 4. Threads Explícitos vs Implícitos
```python
# Thread implícito (no se puede acceder al ID fácilmente)
result = await agent.run("Hola")

# Thread explícito (permite acceder al ID)
thread = agent.get_new_thread()
result = await agent.run("Hola", thread=thread)
thread_id = thread.service_thread_id  # ✅ Accesible
```

### 5. Persistencia del Agente
```python
# El agente se elimina al cerrar (DEFAULT)
AzureAIAgentClient(async_credential=credential)

# El agente se mantiene en Azure
AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False  # ✅ Persistente
)
```

### 6. Context Manager Pattern
```python
# ✅ CORRECTO - Cierra recursos automáticamente
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        # Tu código aquí

# ❌ INCORRECTO - Puede dejar sesiones abiertas
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)
# ... uso sin cerrar
```

### 7. Gestión de Recursos: Cierre Manual vs Automático

Existen dos enfoques **igualmente válidos** para gestionar el ciclo de vida de los clientes. Ninguno es superior al otro; la elección depende del patrón de arquitectura que estés implementando.

#### 🔄 Cierre Automático con `async with` (Apropiado para Workflows Secuenciales)

**Cuándo usar:**
- Workflows **secuenciales** o **pipeline** (A → B → C)
- Los agentes se activan uno después del otro
- Cada agente termina antes de que el siguiente empiece

**Características:**
- Código más conciso (menos líneas)
- Cierre automático garantizado, incluso con errores
- Libera recursos inmediatamente al salir del bloque
- Python se encarga del cleanup (menos código manual)

**Ejemplo:**
```python
async with DefaultAzureCredential() as credential:
    # Primer agente
    async with AzureAIAgentClient(async_credential=credential) as client1:
        agent1 = client1.create_agent(...)
        result1 = await agent1.run("task 1")
    # ← client1 se cierra automáticamente aquí

    # Segundo agente (usa resultado del primero)
    async with AzureAIAgentClient(async_credential=credential) as client2:
        agent2 = client2.create_agent(...)
        result2 = await agent2.run(f"process: {result1}")
    # ← client2 se cierra automáticamente aquí
```

**Patrón Visual:**
```
async with client1:
    usar agent1
    ← cierre automático

    async with client2:
        usar agent2
        ← cierre automático
```

#### 🔧 Cierre Manual con `__aexit__()` (Apropiado para Patrón Supervisor)

**Cuándo usar:**
- Patrón **Supervisor + Herramientas**
- Un agente coordinador controla múltiples agentes
- Todos los agentes deben estar **activos simultáneamente**
- El supervisor puede llamar cualquier agente en cualquier momento

**Características:**
- Todos los agentes disponibles simultáneamente
- Mayor flexibilidad para decisiones dinámicas
- Control explícito sobre el ciclo de vida de recursos
- Supervisor puede acceder a cualquier agente en cualquier momento

**Ejemplo:**
```python
async with DefaultAzureCredential() as credential:
    clients = []  # Rastrear todos los clientes

    try:
        # Crear múltiples agentes (todos permanecen activos)
        client1 = AzureAIAgentClient(async_credential=credential)
        agent1 = client1.create_agent(...)
        clients.append(client1)

        client2 = AzureAIAgentClient(async_credential=credential)
        agent2 = client2.create_agent(...)
        clients.append(client2)

        client3 = AzureAIAgentClient(async_credential=credential)
        agent3 = client3.create_agent(...)
        clients.append(client3)

        # Supervisor decide dinámicamente qué agente usar
        supervisor = client_supervisor.create_agent(...)

        # Todos los agentes están disponibles simultáneamente
        result = await agent1.run("task 1")
        result = await agent3.run("task 2")  # Puede saltar agentes
        result = await agent1.run("task 3")  # Puede reusar agentes

    finally:
        # Cerrar todos los clientes manualmente
        for client in clients:
            await client.__aexit__(None, None, None)
```

**Patrón Visual:**
```
crear client1, client2, client3
↓
todos están activos simultáneamente
↓
supervisor usa cualquiera en cualquier orden
↓
cerrar todos manualmente al final
```

#### 📊 Comparación de Enfoques

> **Nota Importante**: Ambos enfoques son **igualmente correctos y válidos**. Esta tabla muestra diferencias, no superioridad.

| Aspecto | **Cierre Automático** (`async with`) | **Cierre Manual** (`__aexit__()`) |
|---------|--------------------------------------|-------------------------------------|
| **Patrón ideal** | Secuencial/Pipeline | Supervisor/Herramientas |
| **Flujo típico** | A → B → C (lineal) | Supervisor controla A, B, C |
| **Agentes activos** | Secuencialmente | Todos simultáneamente |
| **Decisiones** | Predefinidas en código | Dinámicas en runtime |
| **Gestión de memoria** | Libera recursos escalonadamente | Mantiene todos hasta el final |
| **Líneas de código** | Menos líneas | Más líneas |
| **Cierre de recursos** | Automático con `async with` | Manual con `try/finally` |
| **Complejidad** | Anidamiento de bloques | Lista + loop de cierre |
| **Mejor para** | Workflows simples/medianos | Workflows complejos/supervisores |

#### 🎯 Guía para Elegir el Enfoque

> **Importante**: Esta es una guía, no una regla estricta. Ambos enfoques funcionan en ambos casos.

**¿Puedes dibujar el flujo como una LÍNEA?** → `async with` es más simple para este caso
```
A → B → C → D
(Pero cierre manual también funciona)
```

**¿El flujo es una RED con decisiones?** → Cierre manual es más natural para este caso
```
    Supervisor
        ↓
    ┌───┼───┐
    ↓   ↓   ↓
    A   B   C
(Pero async with también funciona)
```

**Para workflows secuenciales simples (como 012/013):**
- Ambos enfoques son **igualmente válidos**
- `async with` requiere menos código
- Cierre manual ofrece más control explícito
- **Elige el que te parezca más claro**

#### 💡 Ejemplos de Casos de Uso

**Cierre Automático:**
- Blog post generator: Research → Outline → Draft → Edit
- Data pipeline: Extract → Transform → Load
- Report generator: Gather data → Analyze → Format
- Sequential workflow: 012_sequential_workflow.py

**Cierre Manual:**
- AI Assistant con múltiples capacidades
- Supervisor que delega a especialistas
- Agente que puede consultar múltiples expertos
- RAG system con múltiples retrievers
- ejemplo_supervisor_pattern.py

#### ⚠️ Errores Comunes

**Error 1: Usar `async with` y retornar el agente**
```python
# ❌ INCORRECTO
async def create_agent(...):
    async with AzureAIAgentClient(...) as client:
        agent = client.create_agent(...)
        return agent  # El cliente se cierra aquí!
    # 💥 Error: "Session is closed"
```

**Error 2: No cerrar clientes en cierre manual**
```python
# ❌ INCORRECTO
clients = []
client1 = AzureAIAgentClient(...)
clients.append(client1)
# ... usar agentes ...
# 💥 Sin cerrar, memory leak!

# ✅ CORRECTO
try:
    # ... crear y usar agentes ...
finally:
    for client in clients:
        await client.__aexit__(None, None, None)
```

**Error 3: Mezclar ambos enfoques**
```python
# ❌ INCORRECTO - Confuso
async with AzureAIAgentClient(...) as client1:
    client2 = AzureAIAgentClient(...)  # Sin async with
    # Inconsistente!
```

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: "Please provide an endpoint or a base_url"
**Causa**: Variables de entorno incorrectas para Azure AI Foundry

**Solución**:
```env
# ❌ INCORRECTO (para Azure OpenAI directo)
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=...

# ✅ CORRECTO (para Azure AI Foundry)
AZURE_AI_PROJECT_ENDPOINT=...
AZURE_AI_MODEL_DEPLOYMENT_NAME=...
```

**Cliente correcto**:
```python
# ❌ Para Azure OpenAI directo
from agent_framework.azure import AzureOpenAIChatClient

# ✅ Para Azure AI Foundry
from agent_framework_azure_ai import AzureAIAgentClient
```

### Problema 2: "Unclosed client session"
**Causa**: No se cierran las conexiones async correctamente

**Solución**: Usar `async with`
```python
# ✅ CORRECTO
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        # código

# ❌ INCORRECTO
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)
```

### Problema 3: Agent ID o Thread ID es None
**Causa**: Creación lazy del agente/thread

**Solución**:
```python
# ✅ CORRECTO - Ejecutar primero, luego obtener ID
result = await agent.run("Hola")
agent_id = agent.chat_client.agent_id  # Ahora tiene valor

# Para Thread ID, usar thread explícito
thread = agent.get_new_thread()
result = await agent.run("Hola", thread=thread)
thread_id = thread.service_thread_id  # ✅ Tiene valor
```

### Problema 4: AttributeError 'ChatAgent' object has no attribute
**Causa**: Acceso incorrecto a propiedades

**Solución**:
```python
# ✅ CORRECTO
agent.chat_client.agent_id      # Para obtener Agent ID
thread.service_thread_id        # Para obtener Thread ID

# ❌ INCORRECTO
agent.agent_id                  # No existe
agent.thread_id                 # No existe
result.conversation_id          # No existe en AgentRunResponse
```

---

## 📚 Patrones de Código Útiles

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
            instructions="Mismo prompt que antes",
            name="MismoNombre"
        )
        result = await agent.run("Nueva pregunta")
```

### Patrón 3: Conversación con Contexto (Nueva)
```python
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        agent_id=AGENT_ID
    ) as client:
        agent = client.create_agent(...)

        # Crear thread explícito
        thread = agent.get_new_thread()

        # Múltiples interacciones con contexto
        await agent.run("Me llamo Juan", thread=thread)
        await agent.run("¿Cómo me llamo?", thread=thread)  # Recordará "Juan"

        # Guardar Thread ID
        thread_id = thread.service_thread_id
        print(f"Thread ID: {thread_id}")
```

### Patrón 4: Continuar Conversación Existente
```python
AGENT_ID = "asst_xxx..."
THREAD_ID = "thread_xxx..."

async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        agent_id=AGENT_ID
    ) as client:
        agent = client.create_agent(...)

        # Reutilizar thread existente
        thread = agent.get_new_thread(service_thread_id=THREAD_ID)

        # Continuar conversación (recuerda contexto anterior)
        result = await agent.run("¿Qué recuerdas de mí?", thread=thread)
```

### Patrón 5: Streaming de Respuestas
```python
async for update in agent.run_stream("Tu pregunta aquí", thread=thread):
    if update.text:
        print(update.text, end="", flush=True)
print()  # Nueva línea al final
```

---

## 🔄 Flujo de Trabajo Típico

### Sesión 1: Crear y Configurar
1. Ejecutar `001_createandrunanagent.py`
2. Copiar el **Agent ID** que se muestra
3. Ejecutar `003_persistentconversation.py` (con el Agent ID)
4. Copiar el **Thread ID** que se muestra

### Sesión 2: Continuar Trabajo
1. Usar el **Agent ID** en script 002 para reutilizar el agente
2. Usar el **Thread ID** en script 004 para continuar la conversación
3. El agente recuerda todo el contexto anterior

### Sesión 3: Nueva Conversación con Mismo Agente
1. Usar el **Agent ID** existente
2. Crear un **nuevo thread** (no especificar `service_thread_id`)
3. Nueva conversación independiente con el mismo agente

---

## 🌐 Diferencias Clave: Azure OpenAI vs Azure AI Foundry

| Aspecto | Azure OpenAI | Azure AI Foundry |
|---------|--------------|------------------|
| **Cliente** | `AzureOpenAIChatClient` | `AzureAIAgentClient` |
| **Paquete** | `agent_framework.azure` | `agent_framework_azure_ai` |
| **Endpoint Env** | `AZURE_OPENAI_ENDPOINT` | `AZURE_AI_PROJECT_ENDPOINT` |
| **Model Env** | `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | `AZURE_AI_MODEL_DEPLOYMENT_NAME` |
| **Credential Param** | `credential` | `async_credential` |
| **Credential Type** | Sync o Async | Solo Async |
| **Formato Endpoint** | `https://xxx.openai.azure.com/` | `https://xxx.services.ai.azure.com/api/projects/xxx` |

---

## 💡 Tips y Mejores Prácticas

1. **Elegir el patrón de cierre correcto**: `async with` para workflows secuenciales, cierre manual para supervisores
2. **Threads explícitos para persistencia**: Si necesitas el Thread ID, crea el thread explícitamente
3. **Guardar IDs importantes**: Agent ID y Thread ID son necesarios para reutilizar recursos
4. **Verificar creación lazy**: Ejecutar `agent.run()` antes de intentar obtener IDs
5. **Un thread por conversación**: No mezclar contextos en el mismo thread
6. **Usar nombres descriptivos**: Facilita identificar agentes en Azure AI Foundry
7. **`should_cleanup_agent=False`**: Si quieres que el agente persista en Azure
8. **Factory pattern para executors**: Usar closures para dar acceso a agentes en workflows
9. **Context methods**: `ctx.send_message()` para pasar datos, `ctx.yield_output()` para salida final

---

## 📖 Referencias

- Microsoft Agent Framework: Framework para crear agentes de IA
- Azure AI Foundry: Plataforma de Azure para gestionar agentes
- Azure Identity: `DefaultAzureCredential` para autenticación
- Python asyncio: Para operaciones asíncronas

---

## 🔮 Próximos Pasos Sugeridos

1. ✅ **MCP Tools (Model Context Protocol)**: Conectar agentes a servicios externos (implementado en 015_agent_with_mcp_tools.py)
2. ✅ **Context Providers**: Proveer contexto dinámico al agente (implementado en 016_context_providers.py)
3. ✅ **Middleware**: Interceptar y modificar mensajes (implementado en 017_middleware.py)
4. ✅ **Observabilidad y Telemetría**: Monitoreo y métricas (implementado en 018_observability_telemetry.py)
5. ✅ **Workflows Secuenciales**: Orquestar múltiples agentes (implementado en 012_sequential_workflow.py y 013_sequential_workflow.py)
6. ✅ **Workflows Paralelos**: Implementar flujos con fan-out y fan-in (implementado en 014_parallel-workflow.py)
7. ✅ **Workflows Condicionales**: Implementar flujos con decisiones dinámicas (implementado en 019_conditional_workflows.py)
8. ✅ **Group Chat Workflows**: Panel de expertos con múltiples agentes (implementado en 020_group_chat_workflow.py)
9. ✅ **Supervisor Pattern**: Implementar patrón supervisor con múltiples agentes herramientas (implementado en 021_supervisor_pattern.py)
10. **RAG (Retrieval Augmented Generation)**: Integrar búsqueda de documentos
11. **Herramientas/Tools Personalizadas Avanzadas**: Streaming tools, async tools

---

**Última actualización**: 2025-12-01
**Agent ID Actual**: `asst_EkJeB3eaxhhwTsRxRp9JZBU4`
**Thread ID Actual**: `thread_7dLiIQQlgsCOCUw3neCkjMbr`

## 📚 Scripts Disponibles

### Agentes Básicos
- `001_createandrunanagent.py` - Crear agente básico
- `002_reuseexistingagent.py` - Reutilizar agente existente
- `003_persistentconversation.py` - Conversación con contexto
- `004_continuethreadconversation.py` - Continuar conversación existente

### Herramientas y MCP
- `015_agent_with_mcp_tools.py` - Agentes usando HostedMCPTool (Model Context Protocol)

### Conceptos Avanzados de Producción
- `016_context_providers.py` - Context Providers (contexto dinámico)
- `017_middleware.py` - Middleware (interceptores y cross-cutting concerns)
- `018_observability_telemetry.py` - Observabilidad y Telemetría (métricas y monitoreo)

### Workflows Básicos
- `012_sequential_workflow.py` - Workflow secuencial (cierre automático con `async with`)
- `013_sequential_workflow.py` - Workflow secuencial (cierre manual con `__aexit__()`)
- `014_parallel-workflow.py` - Workflow paralelo con fan-out y fan-in (cierre manual)

### Workflows Avanzados
- `019_conditional_workflows.py` - Workflows condicionales (if/else routing, retry logic, complexity routing)
- `020_group_chat_workflow.py` - Group Chat (round-robin, debate pattern, task-based selection)
- `021_supervisor_pattern.py` - Supervisor Pattern avanzado (jerárquico, paralelo, multi-nivel)

### Documentación
- `012_sequential_workflow_docs.html` - Documentación completa del workflow secuencial con diagramas
- `014_parallel-workflow_docs.html` - Documentación completa del workflow paralelo con diagramas

### Comparación Rápida: Workflows

#### 012 vs 013 (Secuencial)

> **Ambos producen el mismo resultado y son igualmente correctos.**

| Característica | 012 | 013 |
|---------------|-----|-----|
| Gestión de recursos | Automática (`async with`) | Manual (`__aexit__()`) |
| Líneas de código | Menos código | Más código |
| Uso típico | Workflows secuenciales | Patrones supervisor |
| Cierre de recursos | Python lo maneja | Developer lo controla |
| ¿Cuál usar? | **Cualquiera funciona - elige el que prefieras** ||

#### 013 vs 014 (Secuencial vs Paralelo)

| Característica | 013 (Secuencial) | 014 (Paralelo) |
|---------------|------------------|----------------|
| **Patrón de flujo** | Lineal (A → B) | Red (A → [B,C,D] → E) |
| **Número de agentes** | 2 | 5 |
| **Ejecución** | Secuencial | Paralela (fan-out/fan-in) |
| **Métodos workflow** | `.add_edge()` | `.add_fan_out_edges()` + `.add_fan_in_edges()` |
| **Input final executor** | `str` | `list[str]` |
| **Gestión recursos** | Manual (`__aexit__()`) | Manual (`__aexit__()`) |
| **Caso de uso** | Pipeline, transformaciones | Gather-scatter, aggregación |

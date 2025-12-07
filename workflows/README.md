# Workflows para DevUI

Esta carpeta contiene workflows que DevUI puede auto-descubrir.

## Estructura

```
workflows/
└── travel_planner/
    └── workflow.py          # Planificador de viajes (paralelo)
```

## Uso

### Iniciar DevUI

```bash
# Desde el directorio raiz del proyecto
devui ./workflows

# O desde esta carpeta
cd workflows
devui
```

Esto:
1. Escaneara todos los subdirectorios
2. Buscara archivos `workflow.py`
3. Cargara la variable `workflow` de cada archivo
4. Iniciara el servidor en http://localhost:8080
5. Abrira tu navegador automaticamente

### Crear Nuevos Workflows

Para agregar un nuevo workflow:

1. Crear carpeta: `workflows/mi_workflow/`
2. Crear archivo: `workflows/mi_workflow/workflow.py`
3. Definir variable `workflow` en el archivo

**Plantilla:**

```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import WorkflowBuilder, WorkflowContext, executor
from agent_framework_devui import register_cleanup
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()

# Crear agentes necesarios
client = AzureAIAgentClient(
    async_credential=credential,
    should_cleanup_agent=False
)

agent1 = client.create_agent(
    instructions="Instrucciones del agente 1",
    name="Agent1"
)

agent2 = client.create_agent(
    instructions="Instrucciones del agente 2",
    name="Agent2"
)

# Crear executors
@executor(id="executor1")
async def executor1_func(input: str, ctx: WorkflowContext[str]) -> None:
    response = await agent1.run(input)
    await ctx.send_message(str(response))

@executor(id="executor2")
async def executor2_func(input: str, ctx: WorkflowContext[str]) -> None:
    response = await agent2.run(input)
    await ctx.yield_output(str(response))

# IMPORTANTE: Debe llamarse 'workflow'
workflow = (
    WorkflowBuilder()
    .set_start_executor(executor1_func)
    .add_edge(executor1_func, executor2_func)
    .build()
)

register_cleanup(workflow, credential.close)
```

## Tipos de Workflows

### Workflow Secuencial

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(executor1)
    .add_edge(executor1, executor2)
    .add_edge(executor2, executor3)
    .build()
)
```

Flujo: `executor1 → executor2 → executor3`

### Workflow Paralelo (Fan-out/Fan-in)

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(selector)
    .add_fan_out_edges(
        selector,
        [executor1, executor2, executor3]  # Ejecucion PARALELA
    )
    .add_fan_in_edges(
        [executor1, executor2, executor3],  # Combina resultados
        aggregator
    )
    .build()
)
```

Flujo: `selector → [executor1, executor2, executor3] → aggregator`

**Nota**: El executor de fan-in recibe `list[str]` con todos los resultados.

### Workflow Condicional

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(router)
    .add_conditional_edge(
        router,
        lambda result: "path_a" if condition else "path_b"
    )
    .add_edge("path_a", executor_a)
    .add_edge("path_b", executor_b)
    .build()
)
```

Flujo: `router → executor_a` o `router → executor_b` (segun condicion)

## Probar

```bash
# Iniciar DevUI
devui ./workflows

# Ir a http://localhost:8080
# Seleccionar un workflow del dropdown
# Enviar un mensaje de entrada
# Ver la ejecucion del workflow!
```

## Diferencias con Agentes

| Aspecto | Agentes | Workflows |
|---------|---------|-----------|
| **Variable** | `agent` | `workflow` |
| **Tipo** | ChatAgent | Workflow |
| **Ejecucion** | Respuesta unica | Flujo de multiples pasos |
| **Visualizacion** | Chat directo | Ejecucion de executors |
| **Uso** | Conversacion simple | Orquestacion compleja |

## Ejemplos Disponibles

### Travel Planner (workflows/travel_planner/workflow.py)

**Tipo**: Workflow Paralelo (Fan-out/Fan-in)

**Agentes**:
- LocationSelector - Selecciona destino
- DestinationRecommender - Recomienda lugares
- WeatherAgent - Informacion del clima
- CuisineExpert - Sugerencias gastronomicas
- ItineraryPlanner - Planificador final

**Flujo**:
```
Input → LocationSelector
        ↓ (fan-out - paralelo)
        ├→ DestinationRecommender ┐
        ├→ WeatherAgent            ├→ (fan-in - combina)
        └→ CuisineExpert           ┘
                ↓
        ItineraryPlanner → Output
```

**Ejemplo de uso**:
```
Input: "Quiero viajar a un lugar con playa y clima calido"

Output: Itinerario completo con destinos, clima y comida
```

## Tips

1. **Nombres descriptivos**: Usa nombres claros para workflows y executors
2. **register_cleanup()**: SIEMPRE registrar cleanup para evitar memory leaks
3. **should_cleanup_agent=False**: Mantener agentes en Azure AI Foundry
4. **Factory pattern**: Usar closures para dar acceso a agentes en executors
5. **ctx.send_message()**: Enviar datos al siguiente executor
6. **ctx.yield_output()**: Producir output final del workflow
7. **Fan-in input**: El executor de fan-in recibe `list[str]`

## Referencias

- Documentacion de Workflows: CLAUDE.md (seccion Workflows)
- Ejemplo secuencial: 012_sequential_workflow.py
- Ejemplo paralelo: 014_parallel-workflow.py
- Guia de visualizacion: WORKFLOW_VISUALIZATION_GUIDE.md

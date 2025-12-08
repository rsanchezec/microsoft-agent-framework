# DevUI vs Producción - Comparación Completa

## 🎯 La Gran Diferencia

### DevUI (workflow.py)
**Propósito:** Archivo de DEFINICIÓN para auto-discovery
- Solo DEFINE el workflow
- NO lo ejecuta
- DevUI lo importa y ejecuta

### Producción (script.py)
**Propósito:** Script EJECUTABLE completo
- Define Y ejecuta el workflow
- Control total del flujo
- Integrable con tu aplicación

---

## 📋 Comparación Lado a Lado

### 1. workflow.py (DevUI)

```python
# workflows/travel_planner/workflow.py

from agent_framework import WorkflowBuilder
# ... imports ...

# Crear agentes
agent1 = client.create_agent(...)
agent2 = client.create_agent(...)

# Crear executors
@executor(id="executor1")
async def executor1_func(...):
    ...

# SOLO DEFINIR el workflow
workflow = (
    WorkflowBuilder()
    .set_start_executor(executor1_func)
    .build()
)

# ❌ NO hay async main()
# ❌ NO hay workflow.run()
# ❌ NO hay asyncio.run()
# ❌ NO hay if __name__ == "__main__"
```

**¿Cómo se ejecuta?**
```bash
devui ./workflows
# DevUI importa workflow.py
# Lee la variable 'workflow'
# Lo ejecuta cuando chateas
```

### 2. production_script.py (Producción)

```python
# production_script.py

from agent_framework import WorkflowBuilder
import asyncio
# ... imports ...

# Crear agentes (igual que DevUI)
async def create_agents(credential):
    agent1 = client.create_agent(...)
    agent2 = client.create_agent(...)
    return {'agent1': agent1, 'agent2': agent2}

# Crear executors (igual que DevUI)
def create_executors(agents):
    @executor(id="executor1")
    async def executor1_func(...):
        ...
    return {'executor1': executor1_func}

# ✅ MAIN - ejecuta el workflow
async def main():
    async with DefaultAzureCredential() as credential:
        # Crear agentes
        agents = await create_agents(credential)

        # Crear executors
        executors = create_executors(agents)

        # Construir workflow (igual que DevUI)
        workflow = (
            WorkflowBuilder()
            .set_start_executor(executors['executor1'])
            .build()
        )

        # ✅ EJECUTAR el workflow
        user_input = "input del usuario"
        async for event in workflow.run_stream(user_input):
            if isinstance(event, WorkflowOutputEvent):
                print(event.data)

# ✅ ENTRY POINT
if __name__ == "__main__":
    asyncio.run(main())
```

**¿Cómo se ejecuta?**
```bash
python production_script.py
# Se ejecuta directamente
# No necesita DevUI
```

---

## 🔍 Diferencias Clave

| Característica | workflow.py (DevUI) | production_script.py |
|---------------|---------------------|----------------------|
| **async main()** | ❌ No tiene | ✅ Sí tiene |
| **workflow.run()** | ❌ No (DevUI lo hace) | ✅ Sí (tú lo ejecutas) |
| **asyncio.run()** | ❌ No | ✅ Sí |
| **if __name__ == "__main__"** | ❌ No | ✅ Sí |
| **Input source** | Chat de DevUI | Código/API/CLI |
| **Output destination** | Navegador DevUI | Consola/logs/API |
| **Ejecución** | `devui ./workflows` | `python script.py` |
| **Propósito** | Testing/debugging | Producción/integración |

---

## 🏭 Cuándo Usar Cada Uno

### Usa DevUI (workflow.py)

✅ **Durante desarrollo:**
- Probar agentes interactivamente
- Debugging de flujos
- Experimentar con prompts
- Visualizar ejecución
- Demostrar a stakeholders

✅ **Características:**
- Inicio rápido (no código de ejecución)
- Interfaz visual
- Recarga en caliente
- Múltiples workflows en un lugar

❌ **NO usar para:**
- Producción
- APIs
- Integración con aplicaciones
- Pipelines automatizados

### Usa Script Producción

✅ **Para producción:**
- APIs backend
- Scheduled jobs (cron)
- Pipelines de datos
- Integración con sistemas
- Procesamiento batch

✅ **Características:**
- Control total del flujo
- Error handling robusto
- Logging personalizado
- Integración con tu stack
- Performance optimizado

❌ **NO usar para:**
- Testing rápido (DevUI es más rápido)
- Demos interactivas

---

## 🔄 Flujo de Desarrollo Típico

### Fase 1: Desarrollo con DevUI

```bash
# 1. Crear workflow.py
# workflows/mi_workflow/workflow.py
workflow = WorkflowBuilder()...

# 2. Probar con DevUI
devui ./workflows

# 3. Iterar rápidamente
# - Cambiar prompts
# - Ajustar flujos
# - Probar diferentes inputs
```

### Fase 2: Migrar a Producción

```bash
# 1. Copiar workflow.py → production_workflow.py
cp workflows/mi_workflow/workflow.py production_workflow.py

# 2. Agregar async main()
async def main():
    # ... setup ...
    workflow = WorkflowBuilder()...
    async for event in workflow.run_stream(input):
        # ... procesar ...

# 3. Agregar entry point
if __name__ == "__main__":
    asyncio.run(main())

# 4. Ejecutar
python production_workflow.py
```

---

## 💡 Ejemplo Completo: De DevUI a Producción

### Paso 1: workflow.py (DevUI)

```python
# workflows/hello/workflow.py

from agent_framework import WorkflowBuilder, executor

client = AzureAIAgentClient(...)
agent = client.create_agent(...)

@executor(id="greeter")
async def greeter(name: str, ctx):
    response = await agent.run(f"Say hello to {name}")
    await ctx.yield_output(str(response))

# SOLO definir
workflow = WorkflowBuilder().set_start_executor(greeter).build()
```

**Usar:**
```bash
devui ./workflows
# Escribes: "Alice"
# Output: "Hello Alice!"
```

### Paso 2: production_hello.py (Producción)

```python
# production_hello.py

import asyncio
from agent_framework import WorkflowBuilder, executor, WorkflowOutputEvent

async def main():
    client = AzureAIAgentClient(...)
    agent = client.create_agent(...)

    @executor(id="greeter")
    async def greeter(name: str, ctx):
        response = await agent.run(f"Say hello to {name}")
        await ctx.yield_output(str(response))

    # Definir workflow
    workflow = WorkflowBuilder().set_start_executor(greeter).build()

    # EJECUTAR workflow
    async for event in workflow.run_stream("Alice"):
        if isinstance(event, WorkflowOutputEvent):
            print(event.data)

if __name__ == "__main__":
    asyncio.run(main())
```

**Usar:**
```bash
python production_hello.py
# Output: "Hello Alice!"
```

---

## 🎓 Resumen

### DevUI (workflow.py)
- **Rol:** Herramienta de desarrollo
- **Estructura:** Solo definición
- **Ejecución:** DevUI lo hace
- **Uso:** `devui ./workflows`
- **Propósito:** Testing rápido

### Producción (script.py)
- **Rol:** Aplicación final
- **Estructura:** Definición + ejecución
- **Ejecución:** Tú la controlas
- **Uso:** `python script.py`
- **Propósito:** Integración real

---

## 📚 Archivos de Ejemplo

- `workflows/travel_planner/workflow.py` - Versión DevUI
- `production_travel_planner.py` - Versión producción (mismo workflow)

**Compáralos para ver las diferencias!**

---

**Conclusión:** DevUI es para desarrollo rápido. Para producción, necesitas un script completo con `async main()` y `asyncio.run()`.

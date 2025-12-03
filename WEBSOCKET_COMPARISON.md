# Comparación: WebSocket APIs - AIProjectClient vs Agent Framework

## 📋 Resumen

Este proyecto incluye dos implementaciones de API WebSocket para el asistente de Azure AI:

1. **assistant_websocket.py** - Usa `AIProjectClient` (Hub + Proyecto)
2. **assistant_websocket_agent_framework.py** - Usa `agent_framework_azure_ai` (Solo Proyecto)

---

## 🔑 Diferencias Clave

| Aspecto | AIProjectClient | Agent Framework |
|---------|-----------------|-----------------|
| **Archivo** | `assistant_websocket.py` | `assistant_websocket_agent_framework.py` |
| **Cliente** | `AIProjectClient` | `AzureAIAgentClient` |
| **Paquete** | `azure.ai.projects` | `agent_framework_azure_ai` |
| **Autenticación** | `DefaultAzureCredential()` | `DefaultAzureCredential()` (async) |
| **Conexión** | Connection String (Hub + Proyecto) | Endpoint del Proyecto (solo proyecto) |
| **Variable Env** | `PROJECT_CONNECTION_STRING` | `AZURE_AI_PROJECT_ENDPOINT` |
| **Patrón Async** | Sync con `with` | Async con `async with` |
| **Thread Creation** | `client.agents.create_thread()` | `agent.get_new_thread(service_thread_id=xxx)` |
| **Mensaje** | `client.agents.create_message(...)` | `await agent.run(message, thread=thread)` |
| **Ejecutar** | `client.agents.create_run(...)` | Incluido en `agent.run()` |
| **Polling** | Manual con loop `while run.status...` | Automático en `agent.run()` |

---

## 📁 Variables de Entorno Requeridas

### assistant_websocket.py (AIProjectClient)

```env
# Connection String que incluye hub y proyecto
PROJECT_CONNECTION_STRING=your-connection-string-from-azure

# Agent ID
AZURE_AGENT_ID=asst_EkJeB3eaxhhwTsRxRp9JZBU4

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### assistant_websocket_agent_framework.py (Agent Framework)

```env
# Endpoint del proyecto (sin hub)
AZURE_AI_PROJECT_ENDPOINT=https://agentframeworkproject.services.ai.azure.com/api/projects/proj-agentframework

# Nombre del modelo deployment
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Agent ID
AZURE_AGENT_ID=asst_EkJeB3eaxhhwTsRxRp9JZBU4

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🔄 Flujo de Trabajo

### AIProjectClient (assistant_websocket.py)

```python
# 1. Crear cliente
client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=connection_string
)

# 2. Crear thread
thread = client.agents.create_thread()
thread_id = thread.id

# 3. Crear mensaje
client.agents.create_message(
    thread_id=thread_id,
    role="user",
    content=message
)

# 4. Ejecutar asistente
run = client.agents.create_run(
    thread_id=thread_id,
    agent_id=agent_id
)

# 5. Polling manual
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = client.agents.get_run(thread_id=thread_id, run_id=run.id)

# 6. Obtener respuesta
messages = client.agents.list_messages(thread_id=thread_id)
response = messages.data[0].content[0].text.value
```

### Agent Framework (assistant_websocket_agent_framework.py)

```python
# 1. Crear cliente
async with AzureAIAgentClient(
    async_credential=DefaultAzureCredential(),
    agent_id=agent_id
) as client:

    # 2. Crear agente
    agent = client.create_agent(
        instructions="Tu prompt aquí",
        name="Assistant"
    )

    # 3. Crear/reutilizar thread
    thread = agent.get_new_thread(service_thread_id=thread_id)

    # 4. Ejecutar (automático: mensaje + run + polling)
    result = await agent.run(message, thread=thread)

    # 5. Obtener thread_id para persistencia
    thread_id = thread.service_thread_id

    # 6. Respuesta
    response = result.text
```

---

## 🎯 Cuándo Usar Cada Uno

### Usa AIProjectClient cuando:
- Ya tienes un Hub configurado en Azure
- Necesitas control granular del proceso (mensaje, run, polling por separado)
- Trabajas con múltiples proyectos dentro de un Hub
- Requieres acceso a funcionalidades específicas de Hub

### Usa Agent Framework cuando:
- Trabajas directamente con un proyecto (sin Hub)
- Prefieres una API más simple y de alto nivel
- Quieres menos código boilerplate
- Necesitas integración más directa con el Agent Framework

---

## 📊 Ventajas y Desventajas

### AIProjectClient

**Ventajas:**
- ✅ Control granular de cada paso
- ✅ Acceso a todas las funcionalidades de Hub
- ✅ Más opciones de configuración
- ✅ Patrón sync (más simple en algunos casos)

**Desventajas:**
- ❌ Más código boilerplate
- ❌ Polling manual requerido
- ❌ Requiere Connection String completo
- ❌ Más pasos para cada interacción

### Agent Framework

**Ventajas:**
- ✅ API más simple y concisa
- ✅ Polling automático
- ✅ Menos código para misma funcionalidad
- ✅ Patrón async nativo
- ✅ Integración directa con Agent Framework

**Desventajas:**
- ❌ Menos control granular
- ❌ Requiere async/await en toda la aplicación
- ❌ Solo proyectos (no Hubs)

---

## 🚀 Ejecutar los Servidores

### AIProjectClient
```bash
python assistant_websocket.py
```

### Agent Framework
```bash
python assistant_websocket_agent_framework.py
```

Ambos exponen los mismos endpoints:
- WebSocket: `ws://localhost:8000/ws/chat`
- Health: `http://localhost:8000/health`
- Stats: `http://localhost:8000/api/stats`
- Docs: `http://localhost:8000/docs`

---

## 🔧 Protocolo WebSocket (Idéntico en Ambos)

### 1. Inicializar sesión
```json
{
    "type": "init",
    "user_id": "usuario_123"
}
```

### 2. Enviar mensaje
```json
{
    "type": "message",
    "message": "Tu pregunta aquí"
}
```

### 3. Limpiar sesión
```json
{
    "type": "clear_session"
}
```

### 4. Obtener estadísticas
```json
{
    "type": "get_stats"
}
```

---

## 💡 Recomendaciones

1. **Para nuevos proyectos**: Usa `agent_framework_azure_ai` (más simple)
2. **Para proyectos existentes con Hub**: Usa `AIProjectClient`
3. **Para desarrollo rápido**: Usa `agent_framework_azure_ai`
4. **Para control máximo**: Usa `AIProjectClient`

---

## 📚 Referencias

- Scripts relacionados:
  - `001_createandrunanagent.py` - Crear agente con Agent Framework
  - `002_reuseexistingagent.py` - Reutilizar agente existente
  - `003_persistentconversation.py` - Conversaciones con thread persistente
  - `004_continuethreadconversation.py` - Continuar conversación existente

- Documentación:
  - `CLAUDE.md` - Documentación completa del proyecto
  - `README.md` - Introducción general

---

**Última actualización**: 2025-11-26
**Agent ID Usado**: `asst_EkJeB3eaxhhwTsRxRp9JZBU4`

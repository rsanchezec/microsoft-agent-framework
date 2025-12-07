# Guía Completa: Agent Framework DevUI

## 📋 ¿Qué es DevUI?

**DevUI** es una interfaz web interactiva de debugging y testing para Agent Framework que incluye:

- 🌐 **Interfaz Web** - UI moderna para interactuar con agentes
- 🔌 **API OpenAI-Compatible** - Endpoints REST compatibles con OpenAI
- 🔍 **Auto-Discovery** - Descubre agentes automáticamente en directorios
- 💬 **Conversaciones Persistentes** - Gestiona múltiples conversaciones
- 📊 **Tracing** - Integración con OpenTelemetry
- 🔐 **Autenticación** - Soporte para Bearer tokens
- 🔄 **Auto-Reload** - Recarga automática en desarrollo

---

## 🚀 Inicio Rápido

### Opción 1: CLI (Recomendado para explorar)

```bash
# Escanear directorio actual
devui

# Escanear directorio específico
devui ./agents

# Puerto personalizado
devui --port 8000

# Con auto-reload (desarrollo)
devui --reload
```

### Opción 2: Programático (Recomendado para producción)

```python
from agent_framework_devui import serve
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

# Crear agentes
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)
agent = client.create_agent(
    instructions="Eres un asistente útil",
    name="MyAgent"
)

# Inicializar agente
await agent.run("Hola")

# Iniciar DevUI
serve(
    entities=[agent],
    port=8080,
    auto_open=True
)
```

---

## 📁 Estructura para Auto-Discovery

DevUI puede auto-descubrir agentes en directorios siguiendo esta estructura:

```
agents/
├── general_assistant/
│   ├── agent.py          # ← Debe definir variable 'agent'
│   └── requirements.txt  # ← Dependencias (opcional)
├── researcher/
│   └── agent.py
└── writer/
    └── agent.py
```

### Ejemplo de `agent.py`:

```python
# agents/general_assistant/agent.py

from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup

# Crear credential y cliente
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)

# Crear agente
agent = client.create_agent(
    instructions="Eres un asistente útil que responde preguntas.",
    name="GeneralAssistant"
)

# IMPORTANTE: Registrar cleanup para cerrar recursos
register_cleanup(agent, credential.close)
```

Luego ejecutar:
```bash
devui ./agents
```

---

## 🔧 Comando CLI

### Sintaxis

```bash
devui [DIRECTORIO] [OPCIONES]
```

### Opciones Principales

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--port, -p` | Puerto del servidor | `8080` |
| `--host` | Host para bind | `127.0.0.1` |
| `--no-open` | No abrir navegador | `False` |
| `--headless` | Solo API, sin UI | `False` |
| `--reload` | Auto-reload en desarrollo | `False` |
| `--tracing` | OpenTelemetry tracing | `False` |
| `--mode` | `developer` o `user` | `developer` |
| `--auth` | Habilitar autenticación | `False` |
| `--auth-token` | Token personalizado | Auto-generado |
| `--log-level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

### Ejemplos de Uso

```bash
# Básico
devui

# Puerto personalizado
devui --port 8000

# Sin abrir navegador
devui --no-open

# Solo API (sin UI)
devui --headless

# Con auto-reload (desarrollo)
devui --reload

# Con tracing
devui --tracing

# Modo usuario (menos verbose)
devui --mode user

# Con autenticación (red)
devui --host 0.0.0.0 --auth

# Token personalizado
devui --auth --auth-token "mi-token-seguro"
```

---

## 📡 API Endpoints

DevUI expone una API REST compatible con OpenAI:

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Interfaz web |
| `GET` | `/v1/entities` | Lista de agentes disponibles |
| `POST` | `/v1/chat/completions` | Chat (compatible OpenAI) |
| `GET` | `/v1/conversations` | Lista de conversaciones |
| `POST` | `/v1/conversations` | Nueva conversación |
| `GET` | `/v1/conversations/{id}` | Detalles de conversación |
| `DELETE` | `/v1/conversations/{id}` | Eliminar conversación |

### Ejemplo: Listar Agentes

```bash
curl http://localhost:8080/v1/entities
```

**Respuesta:**
```json
{
  "entities": [
    {
      "id": "GeneralAssistant",
      "name": "GeneralAssistant",
      "type": "agent",
      "description": "Asistente general"
    }
  ]
}
```

### Ejemplo: Chat (Compatible OpenAI)

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GeneralAssistant",
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]
  }'
```

**Respuesta:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "GeneralAssistant",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "¡Hola! Estoy bien, gracias..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

---

## 🐍 API Programática

### Función `serve()`

```python
from agent_framework_devui import serve

serve(
    entities: list[Any] | None = None,
    entities_dir: str | None = None,
    port: int = 8080,
    host: str = "127.0.0.1",
    auto_open: bool = False,
    cors_origins: list[str] | None = None,
    ui_enabled: bool = True,
    tracing_enabled: bool = False,
    mode: str = "developer",
    auth_enabled: bool = False,
    auth_token: str | None = None
)
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `entities` | `list[Any]` | `None` | Lista de agentes/workflows en memoria |
| `entities_dir` | `str` | `None` | Directorio para auto-discovery |
| `port` | `int` | `8080` | Puerto del servidor |
| `host` | `str` | `"127.0.0.1"` | Host para bind |
| `auto_open` | `bool` | `False` | Abrir navegador automáticamente |
| `cors_origins` | `list[str]` | `None` | Orígenes CORS permitidos |
| `ui_enabled` | `bool` | `True` | Habilitar interfaz web |
| `tracing_enabled` | `bool` | `False` | OpenTelemetry tracing |
| `mode` | `str` | `"developer"` | `"developer"` o `"user"` |
| `auth_enabled` | `bool` | `False` | Habilitar autenticación |
| `auth_token` | `str` | `None` | Token personalizado |

### Función `register_cleanup()`

Registra funciones de limpieza que se ejecutan cuando DevUI se detiene:

```python
from agent_framework_devui import register_cleanup

# Single cleanup
register_cleanup(agent, credential.close)

# Multiple cleanups
register_cleanup(agent, credential.close, session.close, db.close)
```

---

## 🎯 Casos de Uso

### 1. Desarrollo Local - Exploración Rápida

```bash
# Crear estructura
mkdir agents
cd agents

# Crear agente simple
cat > my_agent/agent.py <<EOF
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup

credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)

agent = client.create_agent(
    instructions="Eres un asistente de prueba",
    name="TestAgent"
)

register_cleanup(agent, credential.close)
EOF

# Iniciar DevUI
devui .
```

### 2. Testing de Agentes

```python
# test_agent.py
from agent_framework_devui import serve
from my_agents import create_all_agents

async def main():
    agents = await create_all_agents()

    serve(
        entities=agents,
        port=8080,
        auto_open=True,
        mode="developer"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 3. Demo para Stakeholders

```bash
# Modo usuario (menos técnico)
devui ./agents --mode user --port 80
```

### 4. Integración con OpenAI SDK

DevUI es compatible con OpenAI SDK, permitiendo probar localmente antes de usar OpenAI:

```python
from openai import AsyncOpenAI

# Apuntar al DevUI local
client = AsyncOpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"  # DevUI no requiere API key por defecto
)

# Usar como OpenAI normal
response = await client.chat.completions.create(
    model="GeneralAssistant",  # Nombre de tu agente en DevUI
    messages=[
        {"role": "user", "content": "Hola"}
    ]
)

print(response.choices[0].message.content)
```

---

## 🔐 Seguridad

### ⚠️ IMPORTANTE

**Por defecto, DevUI solo escucha en localhost (`127.0.0.1`) y NO requiere autenticación.**

### Exposición a Red Local

Para exponer DevUI en red local (⚠️ SOLO en redes confiables):

```bash
# CON autenticación (RECOMENDADO)
devui --host 0.0.0.0 --auth

# Token personalizado
devui --host 0.0.0.0 --auth --auth-token "mi-token-muy-seguro"
```

### Producción / Deployment

**NUNCA exponer DevUI a internet sin autenticación.**

```bash
# Usar variable de entorno para token
export DEVUI_AUTH_TOKEN="token-super-seguro-aleatorio"

# Iniciar con autenticación
devui --host 0.0.0.0 --auth
```

En código:
```python
import os

serve(
    entities=agents,
    host="0.0.0.0",
    auth_enabled=True,
    auth_token=os.environ.get("DEVUI_AUTH_TOKEN")
)
```

### Usar con Autenticación

Cuando DevUI tiene autenticación habilitada:

```bash
# cURL
curl -H "Authorization: Bearer tu-token-aqui" \
  http://localhost:8080/v1/entities

# OpenAI SDK
client = AsyncOpenAI(
    base_url="http://localhost:8080/v1",
    api_key="tu-token-aqui"  # Token de DevUI
)
```

---

## 🔍 Debugging y Logging

### Niveles de Log

```bash
# DEBUG - Muy verbose
devui --log-level DEBUG

# INFO - Normal (default)
devui --log-level INFO

# WARNING - Solo advertencias
devui --log-level WARNING

# ERROR - Solo errores
devui --log-level ERROR
```

### Modos de Servidor

**Developer Mode (default):**
- Errores verbosos con stack traces
- Acceso a todos los endpoints
- Información de debugging en respuestas

```bash
devui --mode developer
# o
devui --dev
```

**User Mode:**
- Errores genéricos (no expone detalles internos)
- APIs restringidas
- Mensajes amigables

```bash
devui --mode user
# o
devui --no-dev
```

---

## 📊 Tracing con OpenTelemetry

DevUI soporta OpenTelemetry para tracing distribuido:

```bash
# Habilitar tracing
devui --tracing
```

En código:
```python
serve(
    entities=agents,
    tracing_enabled=True
)
```

Esto automáticamente establece:
```bash
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

**Integración con backends:**
- Jaeger
- Zipkin
- Azure Application Insights
- Datadog
- New Relic

---

## 🎨 Interfaz Web

La UI web de DevUI proporciona:

### Características

1. **Selector de Agentes** - Lista de todos los agentes disponibles
2. **Chat Interactivo** - Interfaz de chat con el agente seleccionado
3. **Historial de Conversaciones** - Ver conversaciones anteriores
4. **Panel de Estado** - Estado del servidor y agentes
5. **Documentación API** - Docs de endpoints disponibles

### Acceso

```
http://localhost:8080/
```

### Deshabilitar UI (solo API)

```bash
devui --headless
```

---

## ⚡ Auto-Reload (Desarrollo)

Para desarrollo activo, habilitar auto-reload:

```bash
devui --reload
```

DevUI recargará automáticamente cuando:
- Archivos `.py` cambien
- Se agreguen/eliminen agentes
- Se modifiquen configuraciones

---

## 🔄 CORS

Para permitir acceso desde otras aplicaciones web:

```python
serve(
    entities=agents,
    cors_origins=[
        "http://localhost:3000",  # React app
        "http://localhost:5173",  # Vite app
        "https://myapp.com"
    ]
)
```

---

## 📝 Ejemplos Completos

### Ejemplo 1: Múltiples Agentes

```python
from agent_framework_devui import serve
from my_agents import researcher, writer, reviewer

serve(
    entities=[researcher, writer, reviewer],
    port=8080,
    auto_open=True
)
```

### Ejemplo 2: Auto-Discovery con Workflows

```
project/
├── agents/
│   ├── researcher/
│   │   └── agent.py
│   └── writer/
│       └── agent.py
└── workflows/
    └── research_workflow/
        └── workflow.py
```

```bash
devui ./agents ./workflows
```

### Ejemplo 3: Testing con pytest

```python
# test_agent_with_devui.py
import pytest
from agent_framework_devui import serve
import threading
import time

@pytest.fixture(scope="module")
def devui_server():
    """Start DevUI server in background thread"""
    from my_agents import test_agent

    thread = threading.Thread(
        target=serve,
        kwargs={"entities": [test_agent], "port": 8081},
        daemon=True
    )
    thread.start()
    time.sleep(2)  # Wait for server to start
    yield "http://localhost:8081"

def test_agent_via_api(devui_server):
    import requests

    response = requests.post(
        f"{devui_server}/v1/chat/completions",
        json={
            "model": "TestAgent",
            "messages": [{"role": "user", "content": "test"}]
        }
    )

    assert response.status_code == 200
    assert "choices" in response.json()
```

---

## 🆚 Comparación: DevUI vs Otros Métodos

| Aspecto | Script Python | DevUI CLI | DevUI Programático |
|---------|---------------|-----------|-------------------|
| **Setup** | Simple | Muy simple | Moderado |
| **UI Interactiva** | ❌ | ✅ | ✅ |
| **API REST** | ❌ | ✅ | ✅ |
| **Auto-Discovery** | ❌ | ✅ | ❌ |
| **Conversaciones Persistentes** | Manual | ✅ | ✅ |
| **Compatible OpenAI** | ❌ | ✅ | ✅ |
| **Ideal para** | Desarrollo | Exploración | Producción/Testing |

---

## 📚 Recursos

- **Demo Script**: `023_devui_demo.py`
- **Versión Instalada**: `devui --version`
- **Ayuda**: `devui --help`
- **Agentes de Ejemplo**: `agents/` (con README)

---

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: "Event loop is closed" al Chatear

**Síntoma:**
```
ERROR] Error in agent execution: Event loop is closed
```

**Causa:**
Cuando creas agentes programáticamente con `asyncio.run()` dentro de `serve()`, el event loop se cierra antes de que DevUI pueda usar los agentes.

**Solución:**
✅ **Usar Auto-Discovery** (Recomendado):

```bash
# En lugar de crear agentes programáticamente
devui ./agents
```

Estructura:
```
agents/
├── mi_agente/
│   └── agent.py    # Define variable 'agent'
```

**Por qué funciona:**
DevUI maneja el ciclo de vida completo del event loop cuando usa auto-discovery.

---

### Problema 2: "No se encontraron agentes"

**Síntoma:**
DevUI inicia pero no muestra agentes en el dropdown.

**Causas Posibles:**

1. **Variable mal nombrada**
   ```python
   # ❌ Incorrecto
   my_agent = client.create_agent(...)

   # ✅ Correcto
   agent = client.create_agent(...)  # DEBE llamarse 'agent'
   ```

2. **Archivo mal ubicado**
   ```
   ❌ agents/agent.py              # No funciona
   ✅ agents/mi_agente/agent.py    # Correcto
   ```

3. **Error en el código del agente**
   - Revisar logs en consola donde corre DevUI
   - Buscar stack traces

---

### Problema 3: Confusión sobre Múltiples Agentes

**P: "¿Cuál agente se ejecuta si tengo varios?"**

**R: TODOS se cargan, TÚ eliges cuál usar.**

**Cómo funciona:**

```
1. DevUI escanea:
   agents/
   ├── agente_a/agent.py
   ├── agente_b/agent.py
   └── agente_c/agent.py

2. DevUI carga los 3:
   ✓ AgentA
   ✓ AgentB
   ✓ AgentC

3. En la UI web ves un dropdown:
   ┌──────────────────────┐
   │ Agente: [AgentA ▼]  │
   │         ├ AgentA     │ ← Selecciona este
   │         ├ AgentB     │ ← O este
   │         └ AgentC     │ ← O este
   └──────────────────────┘

4. Cada agente mantiene su PROPIA conversación
```

**Analogía:**
DevUI = WhatsApp Web
- Todos tus contactos están disponibles
- Seleccionas con quién chatear
- Cambias de contacto sin cerrar WhatsApp
- Cada chat mantiene su historial

---

## ✅ Mejores Prácticas

### 1. Usa Auto-Discovery (No Programático)

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| **Auto-Discovery** | ✅ Sin problemas de event loop<br>✅ Fácil agregar agentes<br>✅ Código más limpio | Requiere estructura de carpetas |
| **Programático** | Código en un solo lugar | ❌ Problemas con event loops<br>❌ Más complejo |

**Recomendación:** Siempre usa auto-discovery para DevUI.

---

### 2. Estructura de Carpetas Clara

```
✅ Buena estructura:
agents/
├── general_assistant/
│   ├── agent.py
│   └── README.md (opcional)
├── code_reviewer/
│   └── agent.py
└── translator/
    └── agent.py

❌ Mala estructura:
agents/
├── agent1.py        # No funciona
├── agent2.py        # No funciona
└── my_agent/
    └── my_file.py   # No funciona (debe ser agent.py)
```

---

### 3. Nombrar Agentes Descriptivamente

```python
# ❌ Mal
agent = client.create_agent(
    name="Agent1",           # Poco descriptivo
    instructions="..."
)

# ✅ Bien
agent = client.create_agent(
    name="CodeReviewer",     # Claro y descriptivo
    instructions="Eres un experto en revisar código..."
)
```

El nombre aparece en el dropdown de la UI.

---

### 4. Usar register_cleanup()

```python
from agent_framework_devui import register_cleanup

# Siempre registrar cleanup
register_cleanup(agent, credential.close)
```

**Por qué:**
- Evita memory leaks
- Cierra conexiones correctamente
- DevUI ejecuta cleanup al detenerse

---

### 5. Testing Local antes de DevUI

```python
# En agent.py, agregar bloque de testing
if __name__ == "__main__":
    import asyncio

    async def test():
        result = await agent.run("Test message")
        print(result.text)

    asyncio.run(test())
```

Probar con:
```bash
uv run python agents/mi_agente/agent.py
```

---

## 🎯 Workflow Recomendado

### Paso 1: Crear Agente

```bash
mkdir agents/mi_agente
nano agents/mi_agente/agent.py
```

### Paso 2: Escribir Código

```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)

agent = client.create_agent(
    instructions="Tu prompt aquí",
    name="MiAgente"
)

register_cleanup(agent, credential.close)
```

### Paso 3: Testing Individual

```bash
uv run python agents/mi_agente/agent.py
```

### Paso 4: Iniciar DevUI

```bash
devui ./agents
```

### Paso 5: Probar en UI

1. Abrir http://localhost:8080
2. Seleccionar "MiAgente" en dropdown
3. Chatear y probar

---

## ❓ FAQ

**P: ¿DevUI funciona con workflows?**
R: Sí, puedes pasar workflows en `entities=[workflow1, workflow2]`

**P: ¿Puedo usar DevUI en producción?**
R: DevUI está diseñado para desarrollo/testing. Para producción, considera un deployment apropiado con autenticación robusta.

**P: ¿La API es 100% compatible con OpenAI?**
R: Sí, para endpoints de chat. Puedes usar OpenAI SDK apuntando a DevUI.

**P: ¿Cómo cambio el modelo en la UI?**
R: El selector de agentes en la UI te permite cambiar entre agentes disponibles.

**P: ¿DevUI soporta streaming?**
R: Sí, tanto la API como la UI soportan streaming de respuestas.

**P: ¿Necesito Azure para usar DevUI?**
R: No, DevUI funciona con cualquier tipo de agente (Azure, OpenAI, local, etc.)

---

**Última actualización:** 2025-12-07
**Versión:** DevUI 1.0.0b251120

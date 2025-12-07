# Agentes para DevUI

Esta carpeta contiene agentes que DevUI puede auto-descubrir.

## Estructura

```
agents/
├── simple_agent/
│   └── agent.py          # Asistente general
└── joker_agent/
    └── agent.py          # Asistente de chistes
```

## Uso

### Iniciar DevUI

```bash
# Desde el directorio raíz del proyecto
devui ./agents

# O desde esta carpeta
cd agents
devui
```

Esto:
1. Escaneará todos los subdirectorios
2. Buscará archivos `agent.py`
3. Cargará la variable `agent` de cada archivo
4. Iniciará el servidor en http://localhost:8080
5. Abrirá tu navegador automáticamente

### Crear Nuevos Agentes

Para agregar un nuevo agente:

1. Crear carpeta: `agents/mi_agente/`
2. Crear archivo: `agents/mi_agente/agent.py`
3. Definir variable `agent` en el archivo

**Plantilla:**

```python
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework_devui import register_cleanup
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)

# IMPORTANTE: Debe llamarse 'agent'
agent = client.create_agent(
    instructions="Tu prompt aquí",
    name="MiAgente"
)

register_cleanup(agent, credential.close)
```

## Probar

```bash
# Iniciar DevUI
devui ./agents

# Ir a http://localhost:8080
# Seleccionar un agente del dropdown
# Chatear!
```

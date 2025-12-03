# Guía de Credenciales - Microsoft Agent Framework

> ⚠️ **ADVERTENCIA DE SEGURIDAD**
> Este documento contiene solo **ejemplos genéricos** para fines educativos.
> **NUNCA** commits credenciales reales, endpoints de producción, o secretos al control de versiones.
> Asegúrate de que tu archivo `.env` esté en `.gitignore`.

## 📋 Tabla de Contenidos
1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [DefaultAzureCredential](#defaultazurecredential)
3. [Opciones de Configuración](#opciones-de-configuración)
4. [Ejemplos de Código](#ejemplos-de-código)
5. [Mejores Prácticas](#mejores-prácticas)
6. [Casos de Uso](#casos-de-uso)

---

## 🎯 Conceptos Fundamentales

En el Microsoft Agent Framework con Azure AI, hay **DOS conceptos diferentes** que a menudo se confunden:

### 1. **Credenciales de Autenticación** (Azure Identity)
- **Propósito**: Autenticarte con Azure para acceder a los recursos
- **Componente**: `DefaultAzureCredential`, `ClientSecretCredential`, etc.
- **Variables de entorno que usa**:
  - `AZURE_TENANT_ID`
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_SECRET`
- **NO lee**: `AZURE_AI_PROJECT_ENDPOINT` ni `AZURE_AI_MODEL_DEPLOYMENT_NAME`

### 2. **Configuración del Cliente** (Endpoint y Modelo)
- **Propósito**: Indicar a qué proyecto de Azure AI Foundry conectarse y qué modelo usar
- **Componente**: `AzureAIAgentClient`
- **Variables de entorno que usa**:
  - `AZURE_AI_PROJECT_ENDPOINT`
  - `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- **NO lee**: Credenciales de autenticación (esas vienen del credential)

### Diagrama del Flujo

```
┌─────────────────────────────────────────────────┐
│  DefaultAzureCredential()                       │
│  Lee: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, etc │
│  ↓                                               │
│  Genera: Token de autenticación                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  AzureAIAgentClient(                            │
│      async_credential=credential,               │
│      endpoint=...,    ← Lee AZURE_AI_PROJECT_ENDPOINT
│      model_deployment_name=...  ← Lee AZURE_AI_MODEL_DEPLOYMENT_NAME
│  )                                               │
└─────────────────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │  Azure AI     │
            │  Foundry      │
            └───────────────┘
```

---

## 🔐 DefaultAzureCredential

### ¿Qué es?

`DefaultAzureCredential` es una clase de `azure.identity` que intenta **múltiples métodos de autenticación** en orden hasta encontrar uno que funcione.

### Cadena de Autenticación

Intenta en este orden:

1. **EnvironmentCredential**: Variables de entorno
   ```
   AZURE_TENANT_ID
   AZURE_CLIENT_ID
   AZURE_CLIENT_SECRET
   ```

2. **WorkloadIdentityCredential**: Para Kubernetes con workload identity

3. **ManagedIdentityCredential**: Managed Identity (en Azure VMs, App Service, etc.)

4. **AzureCliCredential**: Credenciales de Azure CLI
   ```bash
   az login  # Tus credenciales quedan almacenadas
   ```

5. **AzurePowerShellCredential**: Credenciales de Azure PowerShell

6. **AzureDeveloperCliCredential**: Azure Developer CLI

### Ventajas de DefaultAzureCredential

✅ **Funciona en múltiples entornos** sin cambiar código:
- Local: Usa `az login` o variables de entorno
- Azure VM: Usa Managed Identity automáticamente
- Azure App Service: Usa Managed Identity
- CI/CD: Usa Service Principal (variables de entorno)

✅ **No necesitas hardcodear credenciales** en el código

✅ **Más seguro**: Sigue mejores prácticas de Azure

### Código Básico

```python
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    # credential contiene el token de autenticación
    # pero NO contiene endpoint ni modelo
    pass
```

---

## ⚙️ Opciones de Configuración

### Opción 1: Variables de Entorno (Recomendado para desarrollo)

**Archivo `.env`:**
```env
# Credenciales de autenticación (opcional si usas az login)
AZURE_TENANT_ID=tu-tenant-id
AZURE_CLIENT_ID=tu-client-id
AZURE_CLIENT_SECRET=tu-client-secret

# Configuración del proyecto (REQUERIDO)
AZURE_AI_PROJECT_ENDPOINT=https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

**Código Python:**
```python
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient

load_dotenv()  # Carga el .env

async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        # Lee automáticamente del .env:
        # - AZURE_AI_PROJECT_ENDPOINT
        # - AZURE_AI_MODEL_DEPLOYMENT_NAME
    ) as client:
        agent = client.create_agent(...)
```

---

### Opción 2: Especificar Endpoint y Modelo en Código

**Útil cuando**: Quieres cambiar entre diferentes proyectos o modelos sin modificar `.env`

```python
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient

async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        endpoint="https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto",
        model_deployment_name="gpt-4o",
        should_cleanup_agent=True
    ) as client:
        agent = client.create_agent(
            instructions="Eres un asistente útil.",
            name="MiAgente"
        )
        result = await agent.run("Hola")
```

**Ventajas**:
- ✅ Control explícito del endpoint y modelo
- ✅ Fácil cambiar entre configuraciones
- ✅ Aún usa `DefaultAzureCredential` para autenticación (seguro)

**Desventajas**:
- ❌ Endpoint hardcodeado en el código

---

### Opción 3: Service Principal Explícito

**Útil cuando**: Tienes un Service Principal específico y quieres control total

```python
from azure.identity.aio import ClientSecretCredential
from agent_framework_azure_ai import AzureAIAgentClient

async with ClientSecretCredential(
    tenant_id="12345678-1234-1234-1234-123456789abc",
    client_id="87654321-4321-4321-4321-abcdefghijkl",
    client_secret="tu-secreto-aqui~no-compartir"
) as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        endpoint="https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto",
        model_deployment_name="gpt-4o"
    ) as client:
        agent = client.create_agent(...)
```

**Ventajas**:
- ✅ Control total sobre qué Service Principal usar
- ✅ Útil en CI/CD con múltiples service principals

**Desventajas**:
- ❌ Secretos hardcodeados (PELIGROSO si no se maneja bien)
- ❌ Menos flexible (no funciona con Managed Identity)

---

### Opción 4: Híbrido - Variables en Código

**Útil cuando**: Quieres control pero sin hardcodear directamente

```python
from azure.identity.aio import ClientSecretCredential
from agent_framework_azure_ai import AzureAIAgentClient
import os
from dotenv import load_dotenv

load_dotenv()

# Lee del .env pero las asigna a variables
AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

async def main():
    async with ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ) as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            endpoint=AZURE_ENDPOINT,
            model_deployment_name=AZURE_MODEL
        ) as client:
            agent = client.create_agent(...)
```

**Ventajas**:
- ✅ Sigue usando `.env` (seguro)
- ✅ Control explícito en el código
- ✅ Fácil de leer y mantener

---

### Opción 5: Azure CLI (Recomendado para Desarrollo Local)

**Útil cuando**: Desarrollo local sin Service Principal

```bash
# Una sola vez - autenticarse con tu cuenta de Azure
az login

# Seleccionar suscripción (si tienes varias)
az account set --subscription "nombre-o-id-de-suscripcion"
```

```python
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient

# DefaultAzureCredential usará automáticamente las credenciales de Azure CLI
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        endpoint="https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto",
        model_deployment_name="gpt-4o"
    ) as client:
        agent = client.create_agent(...)
```

**Ventajas**:
- ✅ Más simple para desarrollo local
- ✅ No necesitas Service Principal
- ✅ Usa tu cuenta personal de Azure
- ✅ No necesitas variables de entorno para credenciales

---

## 📝 Ejemplos de Código

### Ejemplo Completo 1: Desarrollo Local (Azure CLI + .env)

**Archivo `.env`:**
```env
AZURE_AI_PROJECT_ENDPOINT=https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

**Script Python:**
```python
import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

async def main():
    # DefaultAzureCredential usará az login automáticamente
    async with DefaultAzureCredential() as credential:
        # AzureAIAgentClient lee endpoint y modelo del .env
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=False
        ) as client:
            agent = client.create_agent(
                instructions="Eres un asistente útil.",
                name="MiAgente"
            )

            result = await agent.run("¿Qué hora es?")
            print(result.text)

asyncio.run(main())
```

**Pasos previos:**
```bash
az login  # Solo la primera vez
python script.py
```

---

### Ejemplo Completo 2: Service Principal (CI/CD)

**Archivo `.env` (en servidor CI/CD):**
```env
# Credenciales del Service Principal
AZURE_TENANT_ID=12345678-1234-1234-1234-123456789abc
AZURE_CLIENT_ID=87654321-4321-4321-4321-abcdefghijkl
AZURE_CLIENT_SECRET=tu-secreto-aqui

# Configuración del proyecto
AZURE_AI_PROJECT_ENDPOINT=https://tu-proyecto.services.ai.azure.com/api/projects/tu-proyecto
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

**Script Python (mismo código que Ejemplo 1):**
```python
# ¡El mismo código funciona!
# DefaultAzureCredential detecta automáticamente las variables de entorno
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential
    ) as client:
        agent = client.create_agent(...)
```

---

### Ejemplo Completo 3: Múltiples Proyectos

**Útil cuando**: Tienes varios proyectos de Azure AI Foundry

```python
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient
import asyncio

# Configuraciones de diferentes proyectos
PROJECTS = {
    "desarrollo": {
        "endpoint": "https://dev-project.services.ai.azure.com/api/projects/dev",
        "model": "gpt-4o"
    },
    "produccion": {
        "endpoint": "https://prod-project.services.ai.azure.com/api/projects/prod",
        "model": "gpt-4o"
    }
}

async def create_agent_for_project(project_name: str):
    config = PROJECTS[project_name]

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            endpoint=config["endpoint"],
            model_deployment_name=config["model"]
        ) as client:
            agent = client.create_agent(
                instructions="Eres un asistente útil.",
                name=f"Agente-{project_name}"
            )

            result = await agent.run("Hola")
            print(f"[{project_name}] {result.text}")

async def main():
    await create_agent_for_project("desarrollo")
    await create_agent_for_project("produccion")

asyncio.run(main())
```

---

## 🛡️ Mejores Prácticas

### ✅ Hacer

1. **Usar `.env` para desarrollo local**
   ```python
   load_dotenv()
   # Mantén secretos fuera del código
   ```

2. **Usar `DefaultAzureCredential` siempre que sea posible**
   ```python
   # Funciona en local, Azure VMs, App Service, etc.
   async with DefaultAzureCredential() as credential:
       ...
   ```

3. **Usar `az login` para desarrollo local**
   ```bash
   az login  # Simple y seguro
   ```

4. **Agregar `.env` al `.gitignore`**
   ```gitignore
   # Archivos de entorno con credenciales
   .env
   .env.local
   .env.*.local
   *.env

   # Otros archivos sensibles
   credentials.json
   secrets.yaml
   ```

   **Verificar que .env no esté en Git:**
   ```bash
   # Ver si .env está siendo rastreado
   git ls-files | grep .env

   # Si aparece, removerlo del historial
   git rm --cached .env
   git commit -m "Remove .env from version control"
   ```

5. **Usar Managed Identity en producción (Azure)**
   - En Azure App Service, Functions, VMs: Habilita Managed Identity
   - `DefaultAzureCredential` lo detectará automáticamente
   - No necesitas Service Principal

6. **Validar variables de entorno al inicio**
   ```python
   import os

   required_vars = [
       "AZURE_AI_PROJECT_ENDPOINT",
       "AZURE_AI_MODEL_DEPLOYMENT_NAME"
   ]

   for var in required_vars:
       if not os.getenv(var):
           raise ValueError(f"Falta variable de entorno: {var}")
   ```

---

### ❌ Evitar

1. **NO hardcodear secretos en el código**
   ```python
   # ❌ MAL
   client_secret = "mi-secreto-123"
   ```

2. **NO commitear `.env` al repositorio**
   ```bash
   # ✅ Agregar a .gitignore
   echo ".env" >> .gitignore
   ```

3. **NO usar `ClientSecretCredential` si no es necesario**
   ```python
   # ❌ Innecesario en desarrollo local
   ClientSecretCredential(...)

   # ✅ Mejor
   DefaultAzureCredential()  # Usa az login
   ```

4. **NO ignorar el context manager (`async with`)**
   ```python
   # ❌ MAL - Puede dejar conexiones abiertas
   credential = DefaultAzureCredential()

   # ✅ BIEN - Cierra automáticamente
   async with DefaultAzureCredential() as credential:
       ...
   ```

5. **NO mezclar credenciales en el código y `.env`**
   ```python
   # ❌ Confuso
   endpoint = "https://..."  # Hardcodeado
   model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")  # Del .env

   # ✅ Consistente
   endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
   model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
   ```

---

## 🎯 Casos de Uso

### Caso 1: Desarrollador Local

**Escenario**: Desarrollador trabajando en su laptop

**Solución**:
```bash
# Setup inicial (una sola vez)
az login
```

```python
# Código (sin credenciales explícitas)
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    ) as client:
        agent = client.create_agent(...)
```

---

### Caso 2: Pipeline CI/CD (GitHub Actions, Azure DevOps)

**Escenario**: Build automático en servidor

**Solución**:
```yaml
# GitHub Actions
env:
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
  AZURE_AI_PROJECT_ENDPOINT: ${{ secrets.AZURE_AI_PROJECT_ENDPOINT }}
  AZURE_AI_MODEL_DEPLOYMENT_NAME: ${{ secrets.AZURE_AI_MODEL_DEPLOYMENT_NAME }}
```

```python
# Código (mismo que desarrollo local)
# DefaultAzureCredential lee las variables de entorno automáticamente
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        agent = client.create_agent(...)
```

---

### Caso 3: Aplicación en Azure App Service

**Escenario**: Aplicación web en Azure

**Solución**:
1. Habilitar Managed Identity en App Service
2. Asignar permisos al Managed Identity en Azure AI Foundry

```python
# Código (sin Service Principal, usa Managed Identity automáticamente)
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        agent = client.create_agent(...)
```

**No necesitas**:
- ❌ `AZURE_CLIENT_ID`
- ❌ `AZURE_CLIENT_SECRET`
- ❌ `AZURE_TENANT_ID`

**Solo necesitas**:
- ✅ `AZURE_AI_PROJECT_ENDPOINT` (en configuración de App Service)
- ✅ `AZURE_AI_MODEL_DEPLOYMENT_NAME` (en configuración de App Service)

---

### Caso 4: Testing con Múltiples Configuraciones

**Escenario**: Tests que necesitan diferentes configuraciones

```python
import pytest
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient

@pytest.fixture
async def dev_client():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            endpoint="https://dev-project.services.ai.azure.com/...",
            model_deployment_name="gpt-4o"
        ) as client:
            yield client

@pytest.fixture
async def staging_client():
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            endpoint="https://staging-project.services.ai.azure.com/...",
            model_deployment_name="gpt-4o"
        ) as client:
            yield client

@pytest.mark.asyncio
async def test_agent_in_dev(dev_client):
    agent = dev_client.create_agent(...)
    result = await agent.run("test")
    assert result.text
```

---

## 🔍 Troubleshooting

### Error: "DefaultAzureCredential failed to retrieve a token"

**Causas posibles**:
1. No has hecho `az login`
2. No hay variables de entorno configuradas
3. No hay Managed Identity configurado

**Soluciones**:
```bash
# Opción 1: Login con Azure CLI
az login

# Opción 2: Configurar variables de entorno
export AZURE_TENANT_ID=...
export AZURE_CLIENT_ID=...
export AZURE_CLIENT_SECRET=...

# Opción 3: Verificar Managed Identity (en Azure)
az webapp identity show --name myapp --resource-group mygroup
```

---

### Error: "Please provide an endpoint or a base_url"

**Causa**: No se especificó el endpoint

**Soluciones**:
```python
# Opción 1: Variables de entorno
# Archivo .env
AZURE_AI_PROJECT_ENDPOINT=https://...

# Opción 2: Parámetro explícito
AzureAIAgentClient(
    async_credential=credential,
    endpoint="https://..."  # ← Agregar esto
)
```

---

### Error: "Unclosed client session"

**Causa**: No se cerró el credential o client

**Solución**: Usar `async with`
```python
# ✅ CORRECTO
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        ...

# ❌ INCORRECTO
credential = DefaultAzureCredential()
client = AzureAIAgentClient(async_credential=credential)
```

---

## 📚 Referencias

### Documentación Oficial

- [Azure Identity para Python](https://learn.microsoft.com/python/api/azure-identity/)
- [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Service Principal en Azure](https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal)
- [Managed Identity](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)

### Comparación de Credenciales

| Tipo | Uso | Ventajas | Desventajas |
|------|-----|----------|-------------|
| `DefaultAzureCredential` | Universal | Funciona en todos lados | Puede ser lento (prueba múltiples métodos) |
| `AzureCliCredential` | Desarrollo local | Simple, usa `az login` | Solo funciona si Azure CLI está instalado |
| `ClientSecretCredential` | CI/CD, Service Principal | Control total | Requiere gestionar secretos |
| `ManagedIdentityCredential` | Azure (VMs, App Service) | Sin secretos, muy seguro | Solo funciona en Azure |

---

## 🎓 Resumen

### Para Desarrollo Local (Recomendado)
```bash
az login  # Una sola vez
```

```python
# Archivo .env
AZURE_AI_PROJECT_ENDPOINT=https://...
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Código
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        agent = client.create_agent(...)
```

### Para Producción en Azure (Recomendado)
- Habilitar **Managed Identity** en el recurso de Azure
- `DefaultAzureCredential` lo detecta automáticamente
- Configurar solo `AZURE_AI_PROJECT_ENDPOINT` y `AZURE_AI_MODEL_DEPLOYMENT_NAME`

### Para CI/CD
- Usar **Service Principal** con secretos en el pipeline
- Variables de entorno: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
- `DefaultAzureCredential` las lee automáticamente

---

**Última actualización**: 2025-11-24

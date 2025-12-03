"""
015_agent_with_mcp_tools.py

Este script demuestra cómo usar HostedMCPTool (Model Context Protocol Tools)
con agentes en el Microsoft Agent Framework.

MCP Tools permiten a los agentes acceder a servicios externos como:
- Búsqueda web
- APIs personalizadas
- Bases de datos
- Servidores MCP alojados

Características Demostradas:
1. Crear HostedMCPTool básico
2. Configurar modos de aprobación (approval modes)
3. Filtrar herramientas permitidas (allowed_tools)
4. Usar headers para autenticación
5. Agente usando múltiples herramientas MCP
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import HostedMCPTool
from typing import Optional

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE HOSTED MCP TOOLS")
print("=" * 70)


# =============================================================================
# EJEMPLO 1: HostedMCPTool Básico
# =============================================================================
def example_basic_mcp_tool():
    """
    Ejemplo más simple: crear un HostedMCPTool con configuración mínima.

    Parámetros requeridos:
    - name: Nombre identificador de la herramienta
    - url: URL del servidor MCP
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: HostedMCPTool Básico")
    print("=" * 70)

    mcp_tool = HostedMCPTool(
        name="basic_mcp_tool",
        url="https://example.com/mcp"
    )

    print(f"✅ Herramienta MCP creada: {mcp_tool.name}")
    print(f"   URL: {mcp_tool.url}")
    print(f"   Descripción: {mcp_tool.description or 'Sin descripción'}")

    return mcp_tool


# =============================================================================
# EJEMPLO 2: MCP Tool con Descripción y Modo de Aprobación
# =============================================================================
def example_mcp_tool_with_approval():
    """
    MCP Tool con descripción y modo de aprobación.

    Modos de aprobación:
    - "always_require": Siempre requiere aprobación del usuario antes de ejecutar
    - "never_require": Nunca requiere aprobación (ejecución automática)
    - None: Comportamiento por defecto del servicio
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: MCP Tool con Aprobación")
    print("=" * 70)

    # Modo: Siempre requiere aprobación
    mcp_tool_safe = HostedMCPTool(
        name="safe_search_tool",
        description="Herramienta de búsqueda segura que siempre requiere aprobación",
        url="https://example.com/mcp/search",
        approval_mode="always_require"
    )

    print(f"✅ Herramienta creada: {mcp_tool_safe.name}")
    print(f"   Modo de aprobación: {mcp_tool_safe.approval_mode}")
    print(f"   Descripción: {mcp_tool_safe.description}")

    # Modo: Nunca requiere aprobación
    mcp_tool_auto = HostedMCPTool(
        name="auto_calculator",
        description="Calculadora que se ejecuta automáticamente sin aprobación",
        url="https://example.com/mcp/calculator",
        approval_mode="never_require"
    )

    print(f"\n✅ Herramienta creada: {mcp_tool_auto.name}")
    print(f"   Modo de aprobación: {mcp_tool_auto.approval_mode}")

    return [mcp_tool_safe, mcp_tool_auto]


# =============================================================================
# EJEMPLO 3: MCP Tool con Herramientas Permitidas (Allowed Tools)
# =============================================================================
def example_mcp_tool_with_allowed_tools():
    """
    MCP Tool que solo permite usar herramientas específicas del servidor MCP.

    Esto es útil cuando un servidor MCP ofrece múltiples herramientas pero
    solo quieres que el agente use algunas de ellas.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: MCP Tool con Herramientas Permitidas")
    print("=" * 70)

    mcp_tool = HostedMCPTool(
        name="filtered_api_tool",
        description="API con acceso limitado solo a herramientas seguras",
        url="https://example.com/mcp/api",
        allowed_tools=["get_data", "search", "calculate"],  # Solo estas 3
        approval_mode="never_require"
    )

    print(f"✅ Herramienta creada: {mcp_tool.name}")
    print(f"   Herramientas permitidas: {', '.join(mcp_tool.allowed_tools)}")
    print(f"   (El agente NO podrá usar otras herramientas del servidor MCP)")

    return mcp_tool


# =============================================================================
# EJEMPLO 4: MCP Tool con Autenticación (Headers)
# =============================================================================
def example_mcp_tool_with_authentication():
    """
    MCP Tool con headers personalizados para autenticación.

    Útil cuando el servidor MCP requiere autenticación mediante:
    - Bearer tokens
    - API keys
    - Headers personalizados
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 4: MCP Tool con Autenticación")
    print("=" * 70)

    # Ejemplo con Bearer Token
    mcp_tool_bearer = HostedMCPTool(
        name="authenticated_api",
        description="API que requiere Bearer token",
        url="https://api.example.com/mcp",
        headers={
            "Authorization": "Bearer your-secret-token-here",
            "Content-Type": "application/json"
        }
    )

    print(f"✅ Herramienta creada: {mcp_tool_bearer.name}")
    print(f"   Headers configurados: {list(mcp_tool_bearer.headers.keys())}")

    # Ejemplo con API Key
    mcp_tool_apikey = HostedMCPTool(
        name="api_key_service",
        description="Servicio que requiere API key",
        url="https://api.example.com/mcp",
        headers={
            "X-API-Key": "your-api-key-here"
        }
    )

    print(f"\n✅ Herramienta creada: {mcp_tool_apikey.name}")
    print(f"   Headers configurados: {list(mcp_tool_apikey.headers.keys())}")

    return [mcp_tool_bearer, mcp_tool_apikey]


# =============================================================================
# EJEMPLO 5: MCP Tool con Aprobación Específica
# =============================================================================
def example_mcp_tool_with_specific_approval():
    """
    MCP Tool con modo de aprobación específico por herramienta.

    Permite configurar qué herramientas específicas requieren aprobación
    y cuáles no, en lugar de aplicar la misma regla a todas.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 5: MCP Tool con Aprobación Específica")
    print("=" * 70)

    mcp_tool = HostedMCPTool(
        name="mixed_approval_tool",
        description="Herramienta con diferentes niveles de aprobación",
        url="https://example.com/mcp/mixed",
        approval_mode={
            "always_require_approval": ["delete_data", "send_email", "make_payment"],
            "never_require_approval": ["read_data", "search", "calculate"]
        }
    )

    print(f"✅ Herramienta creada: {mcp_tool.name}")
    print(f"   Siempre requieren aprobación:")
    for tool in mcp_tool.approval_mode.get("always_require_approval", []):
        print(f"      - {tool}")
    print(f"   Nunca requieren aprobación:")
    for tool in mcp_tool.approval_mode.get("never_require_approval", []):
        print(f"      - {tool}")

    return mcp_tool


# =============================================================================
# EJEMPLO 6: Crear Agente con MCP Tools
# =============================================================================
async def example_agent_with_mcp_tools():
    """
    Ejemplo completo: crear un agente que usa múltiples MCP Tools.

    NOTA IMPORTANTE:
    Para que este ejemplo funcione completamente, necesitas:
    1. URLs válidas de servidores MCP
    2. Tokens/API keys reales si las APIs requieren autenticación
    3. Los servidores MCP deben estar activos y accesibles

    Este ejemplo muestra la estructura correcta del código.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 6: Agente con MCP Tools")
    print("=" * 70)

    # Crear herramientas MCP para el agente
    # NOTA: Estas son URLs de ejemplo. Reemplaza con tus propios servidores MCP.

    # Herramienta 1: Búsqueda web (ejemplo ficticio)
    web_search_tool = HostedMCPTool(
        name="web_search",
        description="Busca información en la web",
        url="https://api.example.com/mcp/search",
        approval_mode="never_require"
    )

    # Herramienta 2: Calculadora (ejemplo ficticio)
    calculator_tool = HostedMCPTool(
        name="calculator",
        description="Realiza cálculos matemáticos complejos",
        url="https://api.example.com/mcp/calculator",
        approval_mode="never_require"
    )

    # Herramienta 3: Traductor (ejemplo ficticio)
    translator_tool = HostedMCPTool(
        name="translator",
        description="Traduce texto entre idiomas",
        url="https://api.example.com/mcp/translator",
        approval_mode="never_require",
        allowed_tools=["translate", "detect_language"]
    )

    print("\n📦 Herramientas MCP creadas:")
    print(f"   1. {web_search_tool.name} - {web_search_tool.description}")
    print(f"   2. {calculator_tool.name} - {calculator_tool.description}")
    print(f"   3. {translator_tool.name} - {translator_tool.description}")

    # Crear agente con las herramientas MCP
    print("\n🤖 Creando agente con MCP Tools...")

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            agent = client.create_agent(
                name="MCP-Enabled Agent",
                instructions="""
                Eres un asistente útil con acceso a herramientas externas vía MCP.

                Tienes acceso a:
                1. web_search - Para buscar información en la web
                2. calculator - Para realizar cálculos matemáticos
                3. translator - Para traducir texto entre idiomas

                Usa estas herramientas cuando sea necesario para responder preguntas del usuario.
                """,
                tools=[web_search_tool, calculator_tool, translator_tool]
            )

            print(f"✅ Agente creado: {agent.chat_client.name}")
            print(f"   Herramientas disponibles: {len([web_search_tool, calculator_tool, translator_tool])}")

            # Ejemplo de consulta al agente
            print("\n💬 Enviando consulta al agente...")
            query = "¿Cuánto es 15 * 37?"

            print(f"   Usuario: {query}")

            try:
                response = await agent.run(query)
                print(f"   Agente: {response}")
            except Exception as e:
                print(f"\n⚠️ NOTA: Este ejemplo requiere servidores MCP reales.")
                print(f"   Error (esperado con URLs de ejemplo): {e}")
                print(f"\n   Para usar MCP Tools en producción:")
                print(f"   1. Reemplaza las URLs con servidores MCP reales")
                print(f"   2. Configura autenticación si es necesaria")
                print(f"   3. Asegúrate de que los servidores estén activos")


# =============================================================================
# EJEMPLO 7: Comparación de Configuraciones
# =============================================================================
def example_comparison():
    """
    Tabla comparativa de diferentes configuraciones de MCP Tools.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 7: Comparación de Configuraciones")
    print("=" * 70)

    print("\n📊 Tabla Comparativa de HostedMCPTool:")
    print("-" * 70)
    print(f"{'Configuración':<25} | {'Cuándo Usarla':<40}")
    print("-" * 70)
    print(f"{'approval_mode:':<25} |")
    print(f"{'  always_require':<25} | {'APIs peligrosas/destructivas':<40}")
    print(f"{'  never_require':<25} | {'APIs seguras/solo lectura':<40}")
    print(f"{'  specific':<25} | {'Mix de operaciones seguras/peligrosas':<40}")
    print("-" * 70)
    print(f"{'allowed_tools':<25} | {'Limitar funcionalidad del servidor MCP':<40}")
    print("-" * 70)
    print(f"{'headers':<25} | {'Autenticación/Autorización':<40}")
    print("-" * 70)


# =============================================================================
# MAIN: Ejecutar todos los ejemplos
# =============================================================================
async def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "=" * 70)
    print("🚀 INICIANDO EJEMPLOS DE HOSTED MCP TOOLS")
    print("=" * 70)

    # Ejemplos de configuración (síncronos)
    example_basic_mcp_tool()
    example_mcp_tool_with_approval()
    example_mcp_tool_with_allowed_tools()
    example_mcp_tool_with_authentication()
    example_mcp_tool_with_specific_approval()
    example_comparison()

    # Ejemplo con agente (asíncrono)
    await example_agent_with_mcp_tools()

    print("\n" + "=" * 70)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 RESUMEN:")
    print("   - HostedMCPTool permite conectar agentes a servicios MCP externos")
    print("   - Soporta múltiples modos de aprobación para seguridad")
    print("   - Permite filtrar herramientas específicas (allowed_tools)")
    print("   - Soporta autenticación mediante headers")
    print("   - Ideal para extender capacidades de agentes con APIs externas")

    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Identifica qué servidores MCP necesitas")
    print("   2. Obtén las URLs y credenciales de autenticación")
    print("   3. Configura tus HostedMCPTool con los parámetros correctos")
    print("   4. Agrega las herramientas a tus agentes")
    print("   5. Prueba con consultas reales")

    print("\n📖 RECURSOS:")
    print("   - Model Context Protocol: https://modelcontextprotocol.io/")
    print("   - Microsoft Agent Framework Docs")
    print("   - Azure AI Foundry Documentation")


if __name__ == "__main__":
    asyncio.run(main())

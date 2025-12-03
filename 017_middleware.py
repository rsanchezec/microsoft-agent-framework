"""
017_middleware.py

Este script demuestra cómo usar Middleware en el Microsoft Agent Framework.

El Middleware permite interceptar y modificar el comportamiento de agentes,
funciones y chats sin modificar su código principal.

Tipos de Middleware:
1. Agent Middleware - Intercepta runs completos del agente
2. Function Middleware - Intercepta llamadas a funciones/tools
3. Chat Middleware - Intercepta mensajes de chat

Casos de Uso:
- Logging automático de conversaciones
- Filtrado de contenido sensible
- Rate limiting
- Validación de inputs/outputs
- Métricas y analytics
- Retry logic
- Caching
- Seguridad y permisos
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import (
    agent_middleware,
    function_middleware,
    chat_middleware,
    AgentRunContext,
    FunctionInvocationContext,
    ChatContext,
    ai_function
)
from typing import Annotated
from pydantic import Field
import time
from datetime import datetime

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE MIDDLEWARE")
print("=" * 70)


# =============================================================================
# HERRAMIENTAS DE EJEMPLO (para demostrar function middleware)
# =============================================================================

@ai_function
def calculate_sum(a: int, b: int) -> int:
    """Suma dos números enteros"""
    return a + b


@ai_function
def get_weather(
    location: Annotated[str, Field(description="La ciudad para obtener el clima")]
) -> str:
    """Obtiene el clima de una ubicación"""
    return f"El clima en {location} es soleado con 22°C"


# =============================================================================
# EJEMPLO 1: Agent Middleware - Logging Básico
# =============================================================================

@agent_middleware
async def logging_agent_middleware(context: AgentRunContext, next):
    """
    Middleware que logea cada run del agente.

    AgentRunContext contiene:
    - agent: El agente que se está ejecutando
    - messages: Los mensajes de entrada
    - result: El resultado (disponible después de next())
    """
    print(f"\n[AGENT MIDDLEWARE] 📥 Iniciando run del agente '{context.agent.name}'")
    print(f"[AGENT MIDDLEWARE] 📝 Mensajes de entrada: {len(context.messages)} mensaje(s)")

    # Ejecutar el agente
    await next(context)

    # Después de la ejecución
    print(f"[AGENT MIDDLEWARE] 📤 Run completado")
    print(f"[AGENT MIDDLEWARE] ✅ Resultado: {str(context.result)[:100]}...")


# =============================================================================
# EJEMPLO 2: Agent Middleware - Timing/Performance
# =============================================================================

@agent_middleware
async def timing_agent_middleware(context: AgentRunContext, next):
    """
    Middleware que mide el tiempo de ejecución del agente.
    """
    start_time = time.time()

    print(f"\n[TIMING] ⏱️ Iniciando medición...")

    # Ejecutar el agente
    await next(context)

    # Calcular tiempo
    elapsed = time.time() - start_time
    print(f"[TIMING] ⏱️ Tiempo de ejecución: {elapsed:.2f} segundos")

    # Agregar métrica al contexto (opcional)
    if not hasattr(context, 'metrics'):
        context.metrics = {}
    context.metrics['execution_time'] = elapsed


# =============================================================================
# EJEMPLO 3: Agent Middleware - Content Filtering
# =============================================================================

@agent_middleware
async def content_filter_middleware(context: AgentRunContext, next):
    """
    Middleware que filtra contenido sensible de las respuestas.

    NOTA: Este es un ejemplo simplificado. En producción usarías
    Azure Content Safety o similar.
    """
    print(f"\n[CONTENT FILTER] 🔍 Analizando contenido...")

    # Ejecutar el agente
    await next(context)

    # Filtrar contenido sensible en la respuesta (ejemplo simple)
    if context.result:
        result_text = str(context.result)

        # Lista de palabras sensibles (ejemplo)
        sensitive_words = ["contraseña", "password", "secret", "clave"]

        # Verificar si hay palabras sensibles
        found_sensitive = [word for word in sensitive_words if word.lower() in result_text.lower()]

        if found_sensitive:
            print(f"[CONTENT FILTER] ⚠️ Contenido sensible detectado: {found_sensitive}")
            print(f"[CONTENT FILTER] 🔒 Aplicando filtrado...")

            # En producción, podrías:
            # 1. Bloquear la respuesta
            # 2. Redactar las palabras sensibles
            # 3. Alertar al equipo de seguridad

            # Para este ejemplo, solo alertamos
            print(f"[CONTENT FILTER] ✅ Alerta generada")
        else:
            print(f"[CONTENT FILTER] ✅ Contenido seguro")


# =============================================================================
# EJEMPLO 4: Function Middleware - Logging de Tools
# =============================================================================

@function_middleware
async def logging_function_middleware(context: FunctionInvocationContext, next):
    """
    Middleware que logea cada llamada a una función/tool.

    FunctionInvocationContext contiene:
    - function: La función que se está llamando
    - arguments: Los argumentos de la función
    - result: El resultado (disponible después de next())
    """
    print(f"\n[FUNCTION MIDDLEWARE] 🔧 Llamando función: {context.function.name}")
    print(f"[FUNCTION MIDDLEWARE] 📋 Argumentos: {context.arguments}")

    # Ejecutar la función
    await next(context)

    # Después de la ejecución
    print(f"[FUNCTION MIDDLEWARE] ✅ Resultado: {context.result}")


# =============================================================================
# EJEMPLO 5: Function Middleware - Validación de Argumentos
# =============================================================================

@function_middleware
async def validation_function_middleware(context: FunctionInvocationContext, next):
    """
    Middleware que valida argumentos antes de ejecutar funciones.
    """
    print(f"\n[VALIDATION] 🔍 Validando argumentos de '{context.function.name}'...")

    # Ejemplo: Validar que los números no sean negativos para calculate_sum
    if context.function.name == "calculate_sum":
        args = context.arguments
        if 'a' in args and args['a'] < 0:
            print(f"[VALIDATION] ❌ Error: 'a' no puede ser negativo")
            # Podrías lanzar una excepción o modificar el argumento
            args['a'] = abs(args['a'])
            print(f"[VALIDATION] ✅ Corregido a valor absoluto: {args['a']}")

        if 'b' in args and args['b'] < 0:
            print(f"[VALIDATION] ❌ Error: 'b' no puede ser negativo")
            args['b'] = abs(args['b'])
            print(f"[VALIDATION] ✅ Corregido a valor absoluto: {args['b']}")

    # Ejecutar la función
    await next(context)

    print(f"[VALIDATION] ✅ Función ejecutada exitosamente")


# =============================================================================
# EJEMPLO 6: Function Middleware - Caching
# =============================================================================

# Cache global (en producción usarías Redis o similar)
_function_cache = {}


@function_middleware
async def caching_function_middleware(context: FunctionInvocationContext, next):
    """
    Middleware que cachea resultados de funciones.
    """
    # Crear cache key basado en función y argumentos
    cache_key = f"{context.function.name}:{str(sorted(context.arguments.items()))}"

    # Verificar si está en cache
    if cache_key in _function_cache:
        print(f"\n[CACHE] 💾 Hit! Resultado obtenido del cache")
        context.result = _function_cache[cache_key]
        return  # No ejecutar la función

    print(f"\n[CACHE] ❌ Miss. Ejecutando función...")

    # Ejecutar la función
    await next(context)

    # Guardar en cache
    _function_cache[cache_key] = context.result
    print(f"[CACHE] 💾 Resultado guardado en cache")


# =============================================================================
# EJEMPLO 7: Chat Middleware - Logging de Mensajes
# =============================================================================

@chat_middleware
async def logging_chat_middleware(context: ChatContext, next):
    """
    Middleware que logea mensajes de chat.

    ChatContext contiene:
    - messages: Los mensajes de la conversación
    - result: La respuesta (disponible después de next())
    """
    print(f"\n[CHAT MIDDLEWARE] 💬 Procesando {len(context.messages)} mensaje(s)")

    # Loguear último mensaje del usuario
    user_messages = [m for m in context.messages if m.get("role") == "user"]
    if user_messages:
        last_msg = user_messages[-1].get("content", "")
        print(f"[CHAT MIDDLEWARE] 👤 Usuario: {last_msg[:50]}...")

    # Ejecutar el chat
    await next(context)

    # Loguear respuesta del asistente
    if context.result:
        print(f"[CHAT MIDDLEWARE] 🤖 Asistente: {str(context.result)[:50]}...")


# =============================================================================
# EJEMPLO 8: Múltiples Middlewares en Cadena
# =============================================================================

@agent_middleware
async def auth_middleware(context: AgentRunContext, next):
    """Middleware de autenticación (primer middleware)"""
    print(f"\n[AUTH] 🔐 Verificando autenticación...")
    # En producción verificarías tokens, permisos, etc.
    print(f"[AUTH] ✅ Usuario autenticado")
    await next(context)


@agent_middleware
async def rate_limit_middleware(context: AgentRunContext, next):
    """Middleware de rate limiting (segundo middleware)"""
    print(f"\n[RATE LIMIT] 🚦 Verificando límite de requests...")
    # En producción verificarías cuota, requests por minuto, etc.
    print(f"[RATE LIMIT] ✅ Dentro del límite")
    await next(context)


@agent_middleware
async def audit_middleware(context: AgentRunContext, next):
    """Middleware de auditoría (tercer middleware)"""
    print(f"\n[AUDIT] 📊 Registrando actividad para auditoría...")
    timestamp = datetime.now().isoformat()
    # En producción guardarías en base de datos
    print(f"[AUDIT] ✅ Actividad registrada ({timestamp})")
    await next(context)


# =============================================================================
# EJEMPLOS DE USO
# =============================================================================

async def example_agent_middleware():
    """
    Ejemplo de agente con agent middleware.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Agent Middleware (Logging + Timing)")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            agent = client.create_agent(
                name="Assistant with Middleware",
                instructions="Eres un asistente útil.",
                middleware=[
                    logging_agent_middleware,
                    timing_agent_middleware,
                    content_filter_middleware
                ]  # ← Múltiples middlewares
            )

            response = await agent.run("¿Cuál es la capital de Francia?")
            print(f"\n📤 RESPUESTA FINAL: {response}")


async def example_function_middleware():
    """
    Ejemplo de agente con function middleware.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Function Middleware (Logging + Validation + Cache)")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            agent = client.create_agent(
                name="Calculator Agent",
                instructions="Eres un asistente que usa herramientas matemáticas.",
                tools=[calculate_sum, get_weather],
                middleware=[
                    logging_function_middleware,
                    validation_function_middleware,
                    caching_function_middleware
                ]  # ← Function middleware
            )

            # Primera llamada (no está en cache)
            print("\n📞 Primera llamada:")
            response1 = await agent.run("¿Cuánto es -5 más 10?")
            print(f"\n📤 Respuesta: {response1}")

            # Segunda llamada (debería usar cache)
            print("\n📞 Segunda llamada (misma operación):")
            response2 = await agent.run("¿Cuánto es -5 más 10?")
            print(f"\n📤 Respuesta: {response2}")


async def example_multiple_middleware_chain():
    """
    Ejemplo con cadena de múltiples middlewares.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Cadena de Middlewares (Auth + Rate Limit + Audit)")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            agent = client.create_agent(
                name="Secure Agent",
                instructions="Eres un asistente seguro.",
                middleware=[
                    auth_middleware,        # 1. Primero: Autenticación
                    rate_limit_middleware,  # 2. Segundo: Rate limiting
                    audit_middleware,       # 3. Tercero: Auditoría
                    logging_agent_middleware,  # 4. Cuarto: Logging
                    timing_agent_middleware    # 5. Quinto: Timing
                ]  # ← Los middlewares se ejecutan en ORDEN
            )

            response = await agent.run("Dame información del sistema")
            print(f"\n📤 RESPUESTA FINAL: {response}")

            print("\n✅ Nota: Los middlewares se ejecutaron en orden:")
            print("   1. Auth → 2. Rate Limit → 3. Audit → 4. Logging → 5. Timing")


# =============================================================================
# MAIN: Ejecutar todos los ejemplos
# =============================================================================

async def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "=" * 70)
    print("🚀 INICIANDO EJEMPLOS DE MIDDLEWARE")
    print("=" * 70)

    try:
        await example_agent_middleware()
        await example_function_middleware()
        await example_multiple_middleware_chain()
    except Exception as e:
        print(f"\n⚠️ Error en ejemplos: {e}")
        print("   Algunos middlewares pueden no estar completamente soportados")
        print("   dependiendo de la versión del framework.")

    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 TIPOS DE MIDDLEWARE:")
    print("   1. @agent_middleware - Intercepta runs completos del agente")
    print("   2. @function_middleware - Intercepta llamadas a funciones/tools")
    print("   3. @chat_middleware - Intercepta mensajes de chat")

    print("\n💡 CASOS DE USO COMUNES:")
    print("   • Logging y auditoría")
    print("   • Validación de inputs/outputs")
    print("   • Filtrado de contenido sensible")
    print("   • Rate limiting y cuotas")
    print("   • Autenticación y autorización")
    print("   • Métricas y analytics")
    print("   • Caching de resultados")
    print("   • Retry logic")
    print("   • Performance monitoring")

    print("\n🎯 VENTAJAS DE MIDDLEWARE:")
    print("   ✅ Separación de concerns")
    print("   ✅ Código reutilizable")
    print("   ✅ No modifica lógica del agente")
    print("   ✅ Fácil de activar/desactivar")
    print("   ✅ Composable (cadenas de middleware)")
    print("   ✅ Testeable independientemente")

    print("\n⚠️ IMPORTANTE:")
    print("   • Los middlewares se ejecutan en el ORDEN especificado")
    print("   • Siempre llamar await next(context) para continuar la cadena")
    print("   • Puedes modificar context antes o después de next()")
    print("   • Si no llamas next(), interrumpes la ejecución")


if __name__ == "__main__":
    asyncio.run(main())

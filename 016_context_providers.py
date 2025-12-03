"""
016_context_providers.py

Este script demuestra cómo usar Context Providers en el Microsoft Agent Framework.

Los Context Providers permiten inyectar contexto dinámico a los agentes
automáticamente antes de cada invocación, sin modificar las instrucciones base.

Casos de Uso:
- Agregar fecha/hora actual
- Inyectar información del usuario
- Contexto basado en reglas de negocio
- Información de sesión/estado
- Datos de sistemas externos

Ventajas:
- Separación de concerns (contexto vs lógica)
- Contexto dinámico que cambia por invocación
- Reutilizable entre múltiples agentes
- Combinable (múltiples providers)
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ContextProvider, Context
from datetime import datetime
from typing import Any

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE CONTEXT PROVIDERS")
print("=" * 70)


# =============================================================================
# EJEMPLO 1: Context Provider Simple - Fecha y Hora
# =============================================================================
class DateTimeContextProvider(ContextProvider):
    """
    Context Provider que inyecta la fecha y hora actual en cada invocación.

    Útil para que el agente siempre tenga contexto temporal actualizado.
    """

    async def invoking(self, messages: list[dict[str, Any]], **kwargs: Any) -> Context:
        """
        Método llamado ANTES de cada invocación al agente.

        Args:
            messages: Los mensajes actuales de la conversación
            **kwargs: Argumentos adicionales

        Returns:
            Context: Objeto con instructions, messages, tools adicionales
        """
        # Obtener fecha y hora actual
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        day_of_week = now.strftime("%A")

        # Crear instrucción con contexto temporal
        temporal_context = f"""
[CONTEXTO TEMPORAL]
- Fecha actual: {date_str}
- Hora actual: {time_str}
- Día de la semana: {day_of_week}

Usa esta información cuando sea relevante para la conversación.
"""

        return Context(
            instructions=temporal_context,
            messages=[],  # No agregamos mensajes adicionales
            tools=[]       # No agregamos herramientas
        )

    async def invoked(self, messages: list[dict[str, Any]], **kwargs: Any) -> None:
        """
        Método llamado DESPUÉS de cada invocación (opcional).

        Útil para logging, analytics, o actualizar estado.
        """
        print(f"[DateTime Provider] ✅ Contexto temporal inyectado")


# =============================================================================
# EJEMPLO 2: Context Provider - Información del Usuario
# =============================================================================
class UserContextProvider(ContextProvider):
    """
    Context Provider que inyecta información del usuario actual.

    En producción, obtendría esta info de:
    - Base de datos
    - Sistema de autenticación
    - Sesión del usuario
    """

    def __init__(self, user_id: str, user_name: str, user_role: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role

    async def invoking(self, messages: list[dict[str, Any]], **kwargs: Any) -> Context:
        """
        Inyecta información del usuario en cada invocación.
        """
        user_context = f"""
[INFORMACIÓN DEL USUARIO]
- ID: {self.user_id}
- Nombre: {self.user_name}
- Rol: {self.user_role}

Personaliza tus respuestas basándote en el nombre y rol del usuario.
"""

        return Context(
            instructions=user_context,
            messages=[],
            tools=[]
        )

    async def invoked(self, messages: list[dict[str, Any]], **kwargs: Any) -> None:
        print(f"[User Provider] ✅ Contexto de usuario '{self.user_name}' inyectado")


# =============================================================================
# EJEMPLO 3: Context Provider - Reglas de Negocio
# =============================================================================
class BusinessRulesContextProvider(ContextProvider):
    """
    Context Provider que inyecta reglas de negocio dinámicas.

    Útil para:
    - Políticas de la empresa
    - Restricciones temporales (horario de atención)
    - Límites y cuotas
    - Configuración dinámica
    """

    def __init__(self, business_hours: tuple[int, int] = (9, 18)):
        super().__init__()
        self.business_hours = business_hours

    async def invoking(self, messages: list[dict[str, Any]], **kwargs: Any) -> Context:
        """
        Inyecta reglas de negocio basadas en la hora actual.
        """
        current_hour = datetime.now().hour
        start_hour, end_hour = self.business_hours

        # Verificar si estamos en horario de atención
        is_business_hours = start_hour <= current_hour < end_hour

        if is_business_hours:
            rules = f"""
[REGLAS DE NEGOCIO]
- Horario de atención: {start_hour}:00 - {end_hour}:00
- Estado: ✅ DENTRO del horario de atención
- Puedes procesar solicitudes normalmente
- Tiempo de respuesta esperado: Inmediato
"""
        else:
            rules = f"""
[REGLAS DE NEGOCIO]
- Horario de atención: {start_hour}:00 - {end_hour}:00
- Estado: ⏰ FUERA del horario de atención
- Informa al usuario que el servicio está fuera de horario
- Las consultas urgentes serán procesadas al día siguiente
- No prometas tiempos de respuesta inmediatos
"""

        return Context(
            instructions=rules,
            messages=[],
            tools=[]
        )

    async def invoked(self, messages: list[dict[str, Any]], **kwargs: Any) -> None:
        current_hour = datetime.now().hour
        status = "ACTIVO" if self.business_hours[0] <= current_hour < self.business_hours[1] else "INACTIVO"
        print(f"[Business Rules Provider] ✅ Reglas de negocio aplicadas (Horario: {status})")


# =============================================================================
# EJEMPLO 4: Context Provider - Historial/Memoria
# =============================================================================
class ConversationMemoryProvider(ContextProvider):
    """
    Context Provider que mantiene memoria de conversaciones previas.

    Útil para:
    - Recordar preferencias del usuario
    - Mantener contexto entre sesiones
    - Personalización basada en historia
    """

    def __init__(self):
        super().__init__()
        self.conversation_count = 0
        self.topics_discussed = []

    async def invoking(self, messages: list[dict[str, Any]], **kwargs: Any) -> Context:
        """
        Inyecta resumen de conversaciones previas.
        """
        self.conversation_count += 1

        # Extraer tópicos de mensajes previos (simplificado)
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # Aquí podrías hacer análisis más sofisticado
                if content and content not in self.topics_discussed:
                    self.topics_discussed.append(content[:50])  # Primeros 50 chars

        memory_context = f"""
[MEMORIA DE CONVERSACIÓN]
- Número de interacciones: {self.conversation_count}
- Tópicos discutidos: {len(self.topics_discussed)}
- Últimos tópicos: {', '.join(self.topics_discussed[-3:]) if self.topics_discussed else 'Ninguno'}

Usa esta información para mantener coherencia en la conversación.
"""

        return Context(
            instructions=memory_context,
            messages=[],
            tools=[]
        )

    async def invoked(self, messages: list[dict[str, Any]], **kwargs: Any) -> None:
        print(f"[Memory Provider] ✅ Memoria actualizada (Interacción #{self.conversation_count})")


# =============================================================================
# EJEMPLO 5: Usar Context Provider con un Agente
# =============================================================================
async def example_single_context_provider():
    """
    Ejemplo usando UN solo context provider.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Agente con UN Context Provider")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Crear context provider
            datetime_provider = DateTimeContextProvider()

            # Crear agente CON context provider
            agent = client.create_agent(
                name="Time-Aware Assistant",
                instructions="""
                Eres un asistente útil que siempre está consciente del tiempo actual.
                Usa la información temporal que recibes para dar respuestas contextuales.
                """,
                context_providers=[datetime_provider]  # ← Aquí se inyecta
            )

            print("\n📅 Preguntando al agente sobre la fecha...")

            # Primera consulta
            response1 = await agent.run("¿Qué día es hoy?")
            print(f"\n👤 Usuario: ¿Qué día es hoy?")
            print(f"🤖 Agente: {response1}")

            # Segunda consulta
            response2 = await agent.run("¿Es un buen momento para trabajar?")
            print(f"\n👤 Usuario: ¿Es un buen momento para trabajar?")
            print(f"🤖 Agente: {response2}")

            print("\n✅ Nota: El agente recibió automáticamente el contexto temporal")


# =============================================================================
# EJEMPLO 6: Múltiples Context Providers (Aggregate)
# =============================================================================
async def example_multiple_context_providers():
    """
    Ejemplo usando MÚLTIPLES context providers simultáneamente.

    El framework combina automáticamente todos los contextos.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 6: Agente con MÚLTIPLES Context Providers")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Crear múltiples context providers
            datetime_provider = DateTimeContextProvider()
            user_provider = UserContextProvider(
                user_id="user_123",
                user_name="María García",
                user_role="Premium Customer"
            )
            business_provider = BusinessRulesContextProvider(
                business_hours=(9, 18)  # 9 AM - 6 PM
            )
            memory_provider = ConversationMemoryProvider()

            # Crear agente con TODOS los providers
            agent = client.create_agent(
                name="Contextual Assistant",
                instructions="""
                Eres un asistente de atención al cliente altamente contextual.
                Usa TODA la información de contexto que recibes para personalizar tus respuestas.
                """,
                context_providers=[
                    datetime_provider,
                    user_provider,
                    business_provider,
                    memory_provider
                ]  # ← Múltiples providers
            )

            print("\n🎯 El agente tiene 4 context providers activos:")
            print("   1. DateTime - Contexto temporal")
            print("   2. User - Información del usuario")
            print("   3. Business Rules - Reglas de negocio")
            print("   4. Memory - Historial de conversación")

            # Primera consulta
            print("\n" + "-" * 70)
            response1 = await agent.run("Hola, necesito ayuda con mi cuenta")
            print(f"\n👤 Usuario: Hola, necesito ayuda con mi cuenta")
            print(f"🤖 Agente: {response1}")

            # Segunda consulta
            print("\n" + "-" * 70)
            response2 = await agent.run("¿Cuál es el horario de atención?")
            print(f"\n👤 Usuario: ¿Cuál es el horario de atención?")
            print(f"🤖 Agente: {response2}")

            # Tercera consulta
            print("\n" + "-" * 70)
            response3 = await agent.run("¿Recuerdas de qué hablamos antes?")
            print(f"\n👤 Usuario: ¿Recuerdas de qué hablamos antes?")
            print(f"🤖 Agente: {response3}")

            print("\n✅ Nota: Todos los providers inyectaron su contexto automáticamente")


# =============================================================================
# EJEMPLO 7: Context Provider con Estado Dinámico
# =============================================================================
class DynamicPricingContextProvider(ContextProvider):
    """
    Context Provider con estado que cambia dinámicamente.

    Ejemplo de caso real: pricing dinámico basado en demanda.
    """

    def __init__(self):
        super().__init__()
        self.demand_level = "normal"  # low, normal, high
        self.discount_rate = 0.0

    def update_demand(self, level: str):
        """Método para actualizar el estado externamente"""
        self.demand_level = level
        if level == "low":
            self.discount_rate = 0.20  # 20% descuento
        elif level == "high":
            self.discount_rate = -0.10  # 10% aumento
        else:
            self.discount_rate = 0.0

    async def invoking(self, messages: list[dict[str, Any]], **kwargs: Any) -> Context:
        """
        Inyecta contexto de pricing dinámico.
        """
        pricing_context = f"""
[PRICING DINÁMICO]
- Nivel de demanda actual: {self.demand_level.upper()}
- Ajuste de precio: {self.discount_rate:+.0%}
- {"🎉 Aplica descuentos cuando sea apropiado" if self.discount_rate > 0 else ""}
- {"⚠️ Los precios están aumentados por alta demanda" if self.discount_rate < 0 else ""}
"""

        return Context(
            instructions=pricing_context,
            messages=[],
            tools=[]
        )


async def example_dynamic_context_provider():
    """
    Ejemplo de context provider con estado que cambia.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 7: Context Provider Dinámico (Pricing)")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Crear provider con estado
            pricing_provider = DynamicPricingContextProvider()

            agent = client.create_agent(
                name="Sales Assistant",
                instructions="Eres un asistente de ventas. Informa precios y ofertas.",
                context_providers=[pricing_provider]
            )

            # Escenario 1: Demanda normal
            print("\n📊 ESCENARIO 1: Demanda Normal")
            pricing_provider.update_demand("normal")
            response1 = await agent.run("¿Cuánto cuesta el producto X?")
            print(f"🤖 Agente: {response1}")

            # Escenario 2: Demanda baja (descuentos)
            print("\n📊 ESCENARIO 2: Demanda Baja (Descuentos Activos)")
            pricing_provider.update_demand("low")
            response2 = await agent.run("¿Hay ofertas disponibles?")
            print(f"🤖 Agente: {response2}")

            # Escenario 3: Demanda alta (precios aumentados)
            print("\n📊 ESCENARIO 3: Demanda Alta (Precios Aumentados)")
            pricing_provider.update_demand("high")
            response3 = await agent.run("¿Cuál es el precio del servicio Y?")
            print(f"🤖 Agente: {response3}")

            print("\n✅ Nota: El contexto cambió dinámicamente sin recrear el agente")


# =============================================================================
# MAIN: Ejecutar todos los ejemplos
# =============================================================================
async def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "=" * 70)
    print("🚀 INICIANDO EJEMPLOS DE CONTEXT PROVIDERS")
    print("=" * 70)

    # Ejecutar ejemplos
    await example_single_context_provider()
    await example_multiple_context_providers()
    await example_dynamic_context_provider()

    print("\n" + "=" * 70)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 RESUMEN DE CONTEXT PROVIDERS:")
    print("   1. DateTimeContextProvider - Contexto temporal automático")
    print("   2. UserContextProvider - Información del usuario")
    print("   3. BusinessRulesContextProvider - Reglas de negocio dinámicas")
    print("   4. ConversationMemoryProvider - Memoria de conversación")
    print("   5. DynamicPricingContextProvider - Estado dinámico")

    print("\n💡 VENTAJAS DE CONTEXT PROVIDERS:")
    print("   ✅ Separación de concerns (contexto vs lógica)")
    print("   ✅ Contexto dinámico que cambia por invocación")
    print("   ✅ Reutilizable entre múltiples agentes")
    print("   ✅ Combinable (múltiples providers trabajando juntos)")
    print("   ✅ Testeable independientemente")
    print("   ✅ No modifica las instrucciones base del agente")

    print("\n🎯 CASOS DE USO EN PRODUCCIÓN:")
    print("   • Información de usuario (perfil, preferencias)")
    print("   • Contexto temporal (fecha, hora, zona horaria)")
    print("   • Reglas de negocio (horarios, políticas)")
    print("   • Datos de sistemas externos (CRM, DB)")
    print("   • Estado de sesión (carrito, progreso)")
    print("   • Personalización (historial, comportamiento)")


if __name__ == "__main__":
    asyncio.run(main())

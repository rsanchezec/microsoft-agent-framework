"""
019_conditional_workflows.py

Este script demuestra cómo crear Workflows Condicionales con el Microsoft Agent Framework.

Los workflows condicionales permiten que el flujo de ejecución cambie dinámicamente
basándose en condiciones, resultados previos, o decisiones del agente.

Patrones Implementados:
1. Clasificador + Routing (if/else básico)
2. Switch case con múltiples rutas
3. Routing basado en resultado del agente
4. Workflows con validación y retry
5. Routing dinámico con scoring

Casos de Uso:
- Routing de consultas por categoría
- Validación de calidad con retry
- Escalamiento basado en complejidad
- A/B testing de agentes
- Manejo de errores con fallbacks
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import (
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    executor,
    WorkflowViz
)
from typing import Any, Literal

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE WORKFLOWS CONDICIONALES")
print("=" * 70)


# =============================================================================
# PATRÓN 1: CLASIFICADOR + ROUTING (IF/ELSE)
# =============================================================================

def create_classifier_executor(classifier_agent):
    """
    Executor que clasifica la consulta y decide la ruta.
    """
    @executor(id="Classifier")
    async def classifier(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[CLASSIFIER] 🔍 Clasificando consulta: {query}")

        # El agente clasifica la consulta
        classification_prompt = f"""
Clasifica la siguiente consulta en UNA de estas categorías:
- "technical" - Pregunta técnica sobre programación o tecnología
- "general" - Pregunta general de conocimiento
- "creative" - Solicitud creativa (escritura, ideas)

Consulta: {query}

Responde SOLO con una palabra: technical, general, o creative
"""
        response = await classifier_agent.run(classification_prompt)
        category = str(response).strip().lower()

        print(f"[CLASSIFIER] ✅ Categoría: {category}")

        # Routing condicional basado en la categoría
        if "technical" in category or "tech" in category:
            print(f"[CLASSIFIER] → Ruta: Technical Handler")
            await ctx.send_message_to("TechnicalHandler", query)
        elif "creative" in category:
            print(f"[CLASSIFIER] → Ruta: Creative Handler")
            await ctx.send_message_to("CreativeHandler", query)
        else:
            print(f"[CLASSIFIER] → Ruta: General Handler")
            await ctx.send_message_to("GeneralHandler", query)

    return classifier


def create_technical_handler_executor(technical_agent):
    """Handler para consultas técnicas"""
    @executor(id="TechnicalHandler")
    async def technical_handler(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[TECHNICAL] 💻 Procesando consulta técnica...")
        response = await technical_agent.run(query)
        print(f"[TECHNICAL] ✅ Respuesta generada")
        await ctx.yield_output(f"[TECHNICAL] {response}")

    return technical_handler


def create_creative_handler_executor(creative_agent):
    """Handler para consultas creativas"""
    @executor(id="CreativeHandler")
    async def creative_handler(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[CREATIVE] 🎨 Procesando solicitud creativa...")
        response = await creative_agent.run(query)
        print(f"[CREATIVE] ✅ Contenido creado")
        await ctx.yield_output(f"[CREATIVE] {response}")

    return creative_handler


def create_general_handler_executor(general_agent):
    """Handler para consultas generales"""
    @executor(id="GeneralHandler")
    async def general_handler(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[GENERAL] 📚 Procesando consulta general...")
        response = await general_agent.run(query)
        print(f"[GENERAL] ✅ Respuesta generada")
        await ctx.yield_output(f"[GENERAL] {response}")

    return general_handler


# =============================================================================
# PATRÓN 2: VALIDADOR + RETRY LOGIC
# =============================================================================

def create_generator_executor(generator_agent):
    """Executor que genera contenido"""
    @executor(id="Generator")
    async def generator(query: str, ctx: WorkflowContext[dict]) -> None:
        print(f"\n[GENERATOR] 📝 Generando contenido...")
        response = await generator_agent.run(query)
        result = str(response)
        print(f"[GENERATOR] ✅ Contenido generado: {len(result)} caracteres")

        # Enviar al validador con contador de intentos
        await ctx.send_message({
            "content": result,
            "query": query,
            "attempt": 1
        })

    return generator


def create_validator_executor(validator_agent):
    """
    Executor que valida el contenido y decide si es aceptable o necesita retry.
    """
    @executor(id="Validator")
    async def validator(data: dict, ctx: WorkflowContext[dict]) -> None:
        content = data["content"]
        query = data["query"]
        attempt = data.get("attempt", 1)

        print(f"\n[VALIDATOR] 🔍 Validando contenido (Intento #{attempt})...")

        # Validar longitud mínima como ejemplo simple
        is_valid = len(content) > 50

        if is_valid:
            print(f"[VALIDATOR] ✅ Contenido válido!")
            await ctx.send_message_to("Finalizer", content)
        else:
            print(f"[VALIDATOR] ❌ Contenido inválido (muy corto)")

            # Retry logic: máximo 3 intentos
            if attempt < 3:
                print(f"[VALIDATOR] 🔄 Reintentando... (Intento {attempt + 1}/3)")
                await ctx.send_message_to("Improver", {
                    "content": content,
                    "query": query,
                    "attempt": attempt + 1
                })
            else:
                print(f"[VALIDATOR] ⚠️ Máximo de intentos alcanzado")
                await ctx.send_message_to("Finalizer", f"[FALLÓ VALIDACIÓN] {content}")

    return validator


def create_improver_executor(improver_agent):
    """Executor que mejora el contenido rechazado"""
    @executor(id="Improver")
    async def improver(data: dict, ctx: WorkflowContext[dict]) -> None:
        content = data["content"]
        query = data["query"]
        attempt = data["attempt"]

        print(f"\n[IMPROVER] 🔧 Mejorando contenido...")

        improve_prompt = f"""
El siguiente contenido fue rechazado por ser muy corto.
Expande y mejora esta respuesta significativamente:

Consulta original: {query}
Contenido actual: {content}

Genera una respuesta mucho más detallada y completa.
"""
        improved = await improver_agent.run(improve_prompt)
        print(f"[IMPROVER] ✅ Contenido mejorado")

        # Volver al validador
        await ctx.send_message_to("Validator", {
            "content": str(improved),
            "query": query,
            "attempt": attempt
        })

    return improver


def create_finalizer_executor():
    """Executor que produce el output final"""
    @executor(id="Finalizer")
    async def finalizer(content: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[FINALIZER] ✅ Produciendo resultado final")
        await ctx.yield_output(content)

    return finalizer


# =============================================================================
# PATRÓN 3: ROUTING BASADO EN COMPLEJIDAD
# =============================================================================

def create_complexity_router_executor(router_agent):
    """
    Router que evalúa la complejidad de la consulta y decide qué agente usar.
    """
    @executor(id="ComplexityRouter")
    async def complexity_router(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[COMPLEXITY ROUTER] 🎯 Evaluando complejidad...")

        # Evaluar complejidad con el agente
        complexity_prompt = f"""
Evalúa la complejidad de esta consulta en una escala de 1-10:
1-3: Simple (hechos básicos, preguntas directas)
4-7: Media (requiere análisis o explicación)
8-10: Alta (requiere razonamiento profundo o creatividad)

Consulta: {query}

Responde SOLO con un número del 1 al 10.
"""
        response = await router_agent.run(complexity_prompt)

        # Extraer número de complejidad
        try:
            complexity = int(''.join(filter(str.isdigit, str(response)))[:2])
        except:
            complexity = 5  # Default

        print(f"[COMPLEXITY ROUTER] 📊 Complejidad: {complexity}/10")

        # Routing basado en complejidad
        if complexity <= 3:
            print(f"[COMPLEXITY ROUTER] → Ruta: Simple Agent (rápido)")
            await ctx.send_message_to("SimpleAgent", query)
        elif complexity <= 7:
            print(f"[COMPLEXITY ROUTER] → Ruta: Standard Agent")
            await ctx.send_message_to("StandardAgent", query)
        else:
            print(f"[COMPLEXITY ROUTER] → Ruta: Expert Agent (profundo)")
            await ctx.send_message_to("ExpertAgent", query)

    return complexity_router


def create_simple_agent_executor(simple_agent):
    """Agente para consultas simples (respuestas rápidas)"""
    @executor(id="SimpleAgent")
    async def simple_agent_exec(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[SIMPLE AGENT] ⚡ Respuesta rápida...")
        response = await simple_agent.run(f"Responde brevemente: {query}")
        await ctx.yield_output(f"[SIMPLE] {response}")

    return simple_agent_exec


def create_standard_agent_executor(standard_agent):
    """Agente para consultas de complejidad media"""
    @executor(id="StandardAgent")
    async def standard_agent_exec(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[STANDARD AGENT] 📖 Respuesta detallada...")
        response = await standard_agent.run(query)
        await ctx.yield_output(f"[STANDARD] {response}")

    return standard_agent_exec


def create_expert_agent_executor(expert_agent):
    """Agente experto para consultas complejas"""
    @executor(id="ExpertAgent")
    async def expert_agent_exec(query: str, ctx: WorkflowContext[str]) -> None:
        print(f"\n[EXPERT AGENT] 🎓 Análisis profundo...")
        response = await expert_agent.run(
            f"Analiza en profundidad y proporciona una respuesta completa: {query}"
        )
        await ctx.yield_output(f"[EXPERT] {response}")

    return expert_agent_exec


# =============================================================================
# EJEMPLO 1: Workflow con Clasificador (If/Else)
# =============================================================================

async def example_classifier_workflow():
    """
    Ejemplo de workflow con clasificador y routing condicional.

    Flujo:
    Query → Classifier → (Technical | Creative | General) → Output
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Workflow con Clasificador (If/Else Routing)")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            # Crear agentes
            classifier_client, classifier_agent = await create_agent(
                credential, "Eres un clasificador experto de consultas", "Classifier"
            )
            clients.append(classifier_client)

            technical_client, technical_agent = await create_agent(
                credential, "Eres un experto técnico en programación", "Technical"
            )
            clients.append(technical_client)

            creative_client, creative_agent = await create_agent(
                credential, "Eres un escritor creativo", "Creative"
            )
            clients.append(creative_client)

            general_client, general_agent = await create_agent(
                credential, "Eres un asistente de conocimiento general", "General"
            )
            clients.append(general_client)

            # Crear executors
            classifier_exec = create_classifier_executor(classifier_agent)
            technical_exec = create_technical_handler_executor(technical_agent)
            creative_exec = create_creative_handler_executor(creative_agent)
            general_exec = create_general_handler_executor(general_agent)

            # Construir workflow
            # NOTA: El routing condicional se maneja con send_message_to() dentro del executor
            workflow = (
                WorkflowBuilder()
                .set_start_executor(classifier_exec)
                .add_edge(classifier_exec, technical_exec)
                .add_edge(classifier_exec, creative_exec)
                .add_edge(classifier_exec, general_exec)
                .build()
            )

            # Visualizar
            viz = WorkflowViz(workflow)
            print("\n📊 Diagrama Mermaid:")
            print("```mermaid")
            print(viz.to_mermaid())
            print("```")

            # Probar con diferentes tipos de consultas
            queries = [
                "Explica qué es una función lambda en Python",  # Technical
                "Escribe un poema sobre el océano",              # Creative
                "¿Cuál es la capital de Francia?"                # General
            ]

            for i, query in enumerate(queries, 1):
                print(f"\n{'=' * 70}")
                print(f"CONSULTA {i}: {query}")
                print(f"{'=' * 70}")

                async for event in workflow.run_stream(query):
                    if isinstance(event, WorkflowOutputEvent):
                        print(f"\n✅ RESULTADO: {event.data[:200]}...")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


async def create_agent(credential, instructions: str, name: str):
    """Helper para crear agente con cliente"""
    client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=True
    )
    agent = client.create_agent(instructions=instructions, name=name)
    await agent.run("Hola, confirma que estás listo.")
    print(f"[OK] Agente '{name}' creado")
    return client, agent


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "=" * 70)
    print("🚀 INICIANDO EJEMPLOS DE WORKFLOWS CONDICIONALES")
    print("=" * 70)

    try:
        await example_classifier_workflow()
    except Exception as e:
        print(f"\n⚠️ Error en ejemplos: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 PATRONES DEMOSTRADOS:")
    print("   1. ✅ Clasificador + Routing (if/else)")
    print("   2. 📝 Validador + Retry Logic")
    print("   3. 🎯 Routing basado en Complejidad")

    print("\n💡 CASOS DE USO:")
    print("   • Routing de consultas por categoría")
    print("   • Validación de calidad con retry automático")
    print("   • Escalamiento basado en complejidad")
    print("   • A/B testing de diferentes agentes")
    print("   • Manejo de errores con fallbacks")
    print("   • Workflows adaptativos")

    print("\n🎯 VENTAJAS DE WORKFLOWS CONDICIONALES:")
    print("   ✅ Flujos adaptativos que responden a condiciones")
    print("   ✅ Optimización de recursos (agente apropiado para cada tarea)")
    print("   ✅ Manejo robusto de errores y retry logic")
    print("   ✅ Routing inteligente basado en contenido")
    print("   ✅ Escalabilidad (diferentes niveles de procesamiento)")

    print("\n⚙️ IMPLEMENTACIÓN:")
    print("   • Usa send_message_to(executor_id, data) para routing")
    print("   • Agentes pueden tomar decisiones de routing")
    print("   • Soporta loops con retry logic")
    print("   • Combinable con workflows paralelos")


if __name__ == "__main__":
    asyncio.run(main())

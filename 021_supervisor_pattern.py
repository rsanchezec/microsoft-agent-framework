"""
021_supervisor_pattern.py

Este script demuestra patrones avanzados de Supervisor con el Microsoft Agent Framework.

El patrón Supervisor es una arquitectura jerárquica donde un agente "supervisor"
coordina múltiples agentes especializados (workers) para completar tareas complejas.

Patrones Implementados:
1. Basic Supervisor (1 supervisor → N workers)
2. Hierarchical Supervisor (Supervisor → Sub-supervisors → Workers)
3. Parallel Delegation (Supervisor delega a múltiples workers simultáneamente)
4. Sequential Workflow Supervisor (Supervisor orquesta workflow A→B→C)

Casos de Uso:
- Coordinación de equipos especializados
- Delegación inteligente de tareas
- Orquestación multi-nivel
- Síntesis de resultados de múltiples fuentes
- Gestión de workflows complejos

Diferencias con Group Chat:
- Group Chat: Agentes peer-to-peer con manager externo
- Supervisor: Jerarquía clara con supervisor central que delega
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Optional

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE SUPERVISOR PATTERN")
print("=" * 70)


# =============================================================================
# PATRÓN 1: BASIC SUPERVISOR (1 Supervisor → N Workers)
# =============================================================================

async def example_basic_supervisor():
    """
    Ejemplo de supervisor básico que delega a agentes especializados.

    Arquitectura:
                    [User]
                      ↓
                 [Supervisor]
                 ↙    ↓    ↘
            [Research] [Analysis] [Writing]
                 ↘    ↓    ↙
                 [Supervisor]
                      ↓
                   [User]

    El supervisor analiza la tarea y decide qué especialista(s) usar.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Basic Supervisor Pattern")
    print("=" * 70)
    print("\n📋 Arquitectura: 1 Supervisor → 3 Workers (Research, Analysis, Writing)")
    print("🎯 El supervisor delega sub-tareas y sintetiza resultados\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            print("🔧 Creando workers especializados...\n")

            # Crear workers
            research_client, research_agent = await create_agent(
                credential,
                "Eres un investigador experto. Recopilas hechos y datos relevantes sobre cualquier tema.",
                "research_worker"
            )
            clients.append(research_client)

            analysis_client, analysis_agent = await create_agent(
                credential,
                "Eres un analista experto. Analizas datos y encuentras patrones e insights.",
                "analysis_worker"
            )
            clients.append(analysis_client)

            writing_client, writing_agent = await create_agent(
                credential,
                "Eres un escritor experto. Conviertes información técnica en contenido claro.",
                "writing_worker"
            )
            clients.append(writing_client)

            # Crear funciones wrapper (closures que capturan los workers)
            async def delegate_research(topic: str) -> str:
                """Delega investigación de un tema. Usa cuando necesites hechos o datos."""
                print(f"\n  [📞 SUPERVISOR → RESEARCH]: Investigando '{topic}'")
                response = await research_agent.run(f"Investiga y recopila datos sobre: {topic}")
                result = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"  [✅ RESEARCH → SUPERVISOR]: Completado")
                return response.text

            async def delegate_analysis(data: str) -> str:
                """Delega análisis de datos. Usa cuando necesites identificar patrones o insights."""
                print(f"\n  [📞 SUPERVISOR → ANALYSIS]: Analizando datos")
                response = await analysis_agent.run(f"Analiza estos datos y encuentra insights: {data}")
                result = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"  [✅ ANALYSIS → SUPERVISOR]: Completado")
                return response.text

            async def delegate_writing(content: str) -> str:
                """Delega escritura. Usa cuando necesites crear un artículo o resumen."""
                print(f"\n  [📞 SUPERVISOR → WRITING]: Escribiendo contenido")
                response = await writing_agent.run(f"Escribe un artículo claro basado en: {content}")
                result = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"  [✅ WRITING → SUPERVISOR]: Completado")
                return response.text

            print("🔧 Creando supervisor...\n")

            # Crear supervisor con acceso a los workers
            supervisor_client, supervisor_agent = await create_agent(
                credential,
                """Eres un supervisor inteligente que coordina un equipo de especialistas.

Analiza la tarea del usuario y delega apropiadamente:
- delegate_research: Para investigar temas y recopilar datos
- delegate_analysis: Para analizar datos y encontrar insights
- delegate_writing: Para escribir contenido claro

Puedes usar múltiples especialistas en secuencia. Por ejemplo:
1. Research para obtener datos
2. Analysis para analizarlos
3. Writing para crear el artículo final

Sintetiza los resultados de tus especialistas en una respuesta coherente.""",
                "supervisor",
                tools=[delegate_research, delegate_analysis, delegate_writing]
            )
            clients.append(supervisor_client)

            print("🚀 Ejecutando tarea...\n")

            # Ejecutar tarea compleja que requiere múltiples especialistas
            task = "Crea un artículo sobre las tendencias de inteligencia artificial en 2024"
            print(f"[USER → SUPERVISOR]: {task}\n")

            result = await supervisor_agent.run(task)

            print(f"\n{'=' * 70}")
            print("RESULTADO FINAL")
            print(f"{'=' * 70}")
            print(f"{result.text[:500]}...\n")

            print("✅ Supervisor completó la tarea delegando a múltiples especialistas")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# PATRÓN 2: HIERARCHICAL SUPERVISOR (Multi-nivel)
# =============================================================================

async def example_hierarchical_supervisor():
    """
    Ejemplo de supervisión jerárquica con múltiples niveles.

    Arquitectura:
                        [User]
                          ↓
                   [Chief Supervisor]
                      ↙       ↘
            [Tech Supervisor]  [Content Supervisor]
                 ↙  ↘               ↙  ↘
          [Backend][Frontend]  [Writer][Editor]

    El Chief Supervisor delega a sub-supervisores, que a su vez delegan a workers.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Hierarchical Supervisor Pattern (Multi-nivel)")
    print("=" * 70)
    print("\n📋 Arquitectura: Chief → Sub-supervisors → Workers")
    print("🏢 Organización jerárquica de 3 niveles\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            print("🔧 Creando workers de nivel 3 (bottom layer)...\n")

            # NIVEL 3: Workers especializados
            backend_client, backend_agent = await create_agent(
                credential,
                "Eres un desarrollador backend experto en Python, APIs y bases de datos.",
                "backend_dev"
            )
            clients.append(backend_client)

            frontend_client, frontend_agent = await create_agent(
                credential,
                "Eres un desarrollador frontend experto en React, UI/UX.",
                "frontend_dev"
            )
            clients.append(frontend_client)

            writer_client, writer_agent = await create_agent(
                credential,
                "Eres un escritor técnico que crea documentación clara.",
                "tech_writer"
            )
            clients.append(writer_client)

            editor_client, editor_agent = await create_agent(
                credential,
                "Eres un editor que revisa y mejora la calidad del contenido.",
                "content_editor"
            )
            clients.append(editor_client)

            print("🔧 Creando sub-supervisores de nivel 2 (middle layer)...\n")

            # NIVEL 2: Closures para workers
            async def ask_backend(task: str) -> str:
                """Consulta al backend developer."""
                print(f"    [Tech Supervisor → Backend]: {task[:50]}...")
                response = await backend_agent.run(task)
                return response.text

            async def ask_frontend(task: str) -> str:
                """Consulta al frontend developer."""
                print(f"    [Tech Supervisor → Frontend]: {task[:50]}...")
                response = await frontend_agent.run(task)
                return response.text

            async def ask_writer(task: str) -> str:
                """Consulta al technical writer."""
                print(f"    [Content Supervisor → Writer]: {task[:50]}...")
                response = await writer_agent.run(task)
                return response.text

            async def ask_editor(task: str) -> str:
                """Consulta al content editor."""
                print(f"    [Content Supervisor → Editor]: {task[:50]}...")
                response = await editor_agent.run(task)
                return response.text

            # NIVEL 2: Sub-supervisores
            tech_supervisor_client, tech_supervisor_agent = await create_agent(
                credential,
                """Eres el Technical Supervisor. Coordinas desarrollo backend y frontend.
Delega tareas técnicas apropiadamente y sintetiza respuestas.""",
                "tech_supervisor",
                tools=[ask_backend, ask_frontend]
            )
            clients.append(tech_supervisor_client)

            content_supervisor_client, content_supervisor_agent = await create_agent(
                credential,
                """Eres el Content Supervisor. Coordinas escritura y edición de contenido.
Delega tareas de contenido apropiadamente y sintetiza respuestas.""",
                "content_supervisor",
                tools=[ask_writer, ask_editor]
            )
            clients.append(content_supervisor_client)

            print("🔧 Creando Chief Supervisor de nivel 1 (top layer)...\n")

            # NIVEL 1: Closures para sub-supervisores
            async def delegate_to_tech(task: str) -> str:
                """Delega tareas técnicas (desarrollo, arquitectura) al Tech Supervisor."""
                print(f"\n  [Chief → Tech Supervisor]: {task[:50]}...")
                response = await tech_supervisor_agent.run(task)
                print(f"  [Tech Supervisor → Chief]: Completado")
                return response.text

            async def delegate_to_content(task: str) -> str:
                """Delega tareas de contenido (escritura, documentación) al Content Supervisor."""
                print(f"\n  [Chief → Content Supervisor]: {task[:50]}...")
                response = await content_supervisor_agent.run(task)
                print(f"  [Content Supervisor → Chief]: Completado")
                return response.text

            # NIVEL 1: Chief Supervisor
            chief_client, chief_agent = await create_agent(
                credential,
                """Eres el Chief Supervisor que coordina todo el proyecto.

Analiza la tarea y delega a los supervisores apropiados:
- delegate_to_tech: Para tareas de desarrollo, arquitectura técnica
- delegate_to_content: Para tareas de documentación, escritura

Sintetiza los resultados de ambos departamentos en una respuesta coherente.""",
                "chief_supervisor",
                tools=[delegate_to_tech, delegate_to_content]
            )
            clients.append(chief_client)

            print("🚀 Ejecutando tarea...\n")

            # Tarea que requiere ambos departamentos
            task = "Crea una aplicación web de blog y documenta su arquitectura"
            print(f"[USER → CHIEF]: {task}\n")

            result = await chief_agent.run(task)

            print(f"\n{'=' * 70}")
            print("RESULTADO FINAL")
            print(f"{'=' * 70}")
            print(f"{result.text[:400]}...\n")

            print("✅ Jerarquía de 3 niveles ejecutada exitosamente")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# PATRÓN 3: PARALLEL DELEGATION
# =============================================================================

async def example_parallel_delegation():
    """
    Ejemplo donde el supervisor delega a múltiples agentes en paralelo
    y sintetiza los resultados.

    Arquitectura:
                    [Supervisor]
                  ↙  ↓  ↓  ↘
              [A] [B] [C] [D]  ← Ejecutan en paralelo
                  ↘  ↓  ↓  ↙
                [Supervisor] ← Sintetiza resultados

    El supervisor pregunta a múltiples expertos simultáneamente y combina sus respuestas.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Parallel Delegation Pattern")
    print("=" * 70)
    print("\n📋 Patrón: Supervisor → Múltiples workers (paralelo) → Síntesis")
    print("⚡ Delegación simultánea a 4 expertos diferentes\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            print("🔧 Creando 4 expertos especializados...\n")

            # Crear 4 expertos con diferentes perspectivas
            security_client, security_agent = await create_agent(
                credential,
                "Eres un experto en seguridad. Evalúas riesgos y vulnerabilidades.",
                "security_expert"
            )
            clients.append(security_client)

            performance_client, performance_agent = await create_agent(
                credential,
                "Eres un experto en rendimiento. Analizas optimización y escalabilidad.",
                "performance_expert"
            )
            clients.append(performance_client)

            ux_client, ux_agent = await create_agent(
                credential,
                "Eres un experto en UX. Evalúas usabilidad y experiencia de usuario.",
                "ux_expert"
            )
            clients.append(ux_client)

            cost_client, cost_agent = await create_agent(
                credential,
                "Eres un experto en costos. Analizas presupuestos y ROI.",
                "cost_expert"
            )
            clients.append(cost_client)

            # Crear closures para delegación
            async def consult_security(question: str) -> str:
                """Consulta al experto en seguridad."""
                print(f"  [🔐 Security Expert]: Analizando seguridad...")
                response = await security_agent.run(question)
                print(f"  [✅ Security]: Completado")
                return f"SEGURIDAD: {response.text}"

            async def consult_performance(question: str) -> str:
                """Consulta al experto en rendimiento."""
                print(f"  [⚡ Performance Expert]: Analizando rendimiento...")
                response = await performance_agent.run(question)
                print(f"  [✅ Performance]: Completado")
                return f"RENDIMIENTO: {response.text}"

            async def consult_ux(question: str) -> str:
                """Consulta al experto en UX."""
                print(f"  [🎨 UX Expert]: Analizando experiencia de usuario...")
                response = await ux_agent.run(question)
                print(f"  [✅ UX]: Completado")
                return f"UX: {response.text}"

            async def consult_cost(question: str) -> str:
                """Consulta al experto en costos."""
                print(f"  [💰 Cost Expert]: Analizando costos...")
                response = await cost_agent.run(question)
                print(f"  [✅ Cost]: Completado")
                return f"COSTOS: {response.text}"

            print("🔧 Creando supervisor...\n")

            # Crear supervisor que puede consultar múltiples expertos
            supervisor_client, supervisor_agent = await create_agent(
                credential,
                """Eres un supervisor que evalúa propuestas consultando múltiples expertos.

Tienes acceso a 4 especialistas:
- consult_security: Evalúa riesgos y vulnerabilidades
- consult_performance: Analiza rendimiento y escalabilidad
- consult_ux: Evalúa experiencia de usuario
- consult_cost: Analiza presupuesto y ROI

Para evaluaciones completas, consulta a TODOS los expertos y sintetiza sus
opiniones en una recomendación final balanceada.""",
                "evaluation_supervisor",
                tools=[consult_security, consult_performance, consult_ux, consult_cost]
            )
            clients.append(supervisor_client)

            print("🚀 Ejecutando evaluación multi-experto...\n")

            # Tarea que requiere múltiples perspectivas
            task = "Evalúa la propuesta de migrar nuestra aplicación a la nube (AWS)"
            print(f"[USER → SUPERVISOR]: {task}\n")

            result = await supervisor_agent.run(task)

            print(f"\n{'=' * 70}")
            print("EVALUACIÓN FINAL (Síntesis de 4 expertos)")
            print(f"{'=' * 70}")
            print(f"{result.text[:500]}...\n")

            print("✅ Supervisor sintetizó perspectivas de múltiples expertos")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def create_agent(credential, instructions: str, name: str, tools: Optional[list] = None):
    """
    Helper para crear un agente con cliente.

    Args:
        credential: Azure credential
        instructions: Instrucciones del agente
        name: Nombre del agente
        tools: Lista opcional de herramientas

    Returns:
        Tuple (client, agent)
    """
    client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=True
    )

    params = {
        "instructions": instructions,
        "name": name
    }
    if tools:
        params["tools"] = tools

    agent = client.create_agent(**params)

    # Warm-up
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
    print("🚀 INICIANDO EJEMPLOS DE SUPERVISOR PATTERN")
    print("=" * 70)

    try:
        # Ejecutar ejemplos
        await example_basic_supervisor()
        await example_hierarchical_supervisor()
        await example_parallel_delegation()

    except Exception as e:
        print(f"\n⚠️ Error en ejemplos: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 PATRONES DEMOSTRADOS:")
    print("   1. ✅ Basic Supervisor (1 supervisor → N workers)")
    print("   2. ✅ Hierarchical Supervisor (Multi-nivel)")
    print("   3. ✅ Parallel Delegation (Síntesis multi-experto)")

    print("\n💡 CASOS DE USO:")
    print("   • Coordinación de equipos especializados")
    print("   • Delegación inteligente de tareas complejas")
    print("   • Orquestación jerárquica (organización empresarial)")
    print("   • Síntesis de múltiples perspectivas")
    print("   • Evaluación multi-dimensional")
    print("   • Gestión de workflows complejos")

    print("\n🎯 VENTAJAS DEL SUPERVISOR PATTERN:")
    print("   ✅ Jerarquía clara y organizada")
    print("   ✅ Delegación inteligente a especialistas")
    print("   ✅ Síntesis de resultados múltiples")
    print("   ✅ Escalabilidad (agregar más workers fácilmente)")
    print("   ✅ Separación de responsabilidades")
    print("   ✅ Reutilización de workers especializados")

    print("\n⚙️ COMPONENTES CLAVE:")
    print("   • Supervisor Agent: Coordina y delega tareas")
    print("   • Worker Agents: Especializados en dominios específicos")
    print("   • Closure Functions: Wrapper para exponer workers como tools")
    print("   • Tools Parameter: Lista de funciones disponibles para supervisor")
    print("   • Multi-nivel: Sub-supervisores para jerarquías complejas")

    print("\n📐 ARQUITECTURAS:")
    print("   1. Flat: 1 Supervisor → N Workers")
    print("   2. Hierarchical: Supervisor → Sub-supervisors → Workers")
    print("   3. Parallel: Supervisor → [A, B, C] paralelo → Síntesis")
    print("   4. Sequential: Supervisor → A → B → C (workflow)")

    print("\n🔄 SUPERVISOR vs GROUP CHAT:")
    print("   Supervisor:")
    print("     • Jerarquía explícita (supervisor → workers)")
    print("     • Supervisor toma decisiones centralizadas")
    print("     • Workers no conversan entre sí")
    print("     • Ideal para delegación y síntesis")
    print("   ")
    print("   Group Chat:")
    print("     • Agentes peer-to-peer")
    print("     • Manager externo decide quién habla")
    print("     • Agentes pueden responder a otros agentes")
    print("     • Ideal para colaboración y debate")

    print("\n⚠️ MEJORES PRÁCTICAS:")
    print("   • Definir roles claros para cada worker")
    print("   • Usar closures para capturar agents en tools")
    print("   • Instrucciones del supervisor deben describir cuándo usar cada worker")
    print("   • Considerar límites de tokens al sintetizar resultados múltiples")
    print("   • Mantener referencias a todos los clients para cerrarlos correctamente")

    print("\n💡 CUÁNDO USAR SUPERVISOR:")
    print("   ✅ Tareas que requieren múltiples especialistas")
    print("   ✅ Necesitas delegar sub-tareas dinámicamente")
    print("   ✅ Quieres sintetizar perspectivas diferentes")
    print("   ✅ Jerarquía organizacional clara")
    print("   ✅ Workers son independientes (no necesitan conversar)")


if __name__ == "__main__":
    asyncio.run(main())

"""
020_group_chat_workflow.py

Este script demuestra cómo usar Group Chat Workflows con el Microsoft Agent Framework.

Group Chat permite que múltiples agentes participen en una conversación colaborativa,
donde un "manager" decide qué agente habla en cada turno.

Patrones Implementados:
1. Function-based selection (Round-robin)
2. LLM-based orchestration (Prompt-based manager)
3. Conditional selection (Debate pattern)
4. Task-based speaker selection

Casos de Uso:
- Panel de expertos discutiendo un tema
- Debate entre perspectivas diferentes
- Investigación colaborativa
- Revisión multi-etapa de contenido
- Simulación de equipos de trabajo
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import (
    GroupChatBuilder,
    GroupChatStateSnapshot,
)
from typing import Optional

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE GROUP CHAT WORKFLOWS")
print("=" * 70)


# =============================================================================
# PATRÓN 1: ROUND-ROBIN (Selección por Función)
# =============================================================================

def round_robin_selector(state: GroupChatStateSnapshot) -> Optional[str]:
    """
    Selector simple que rota entre participantes en orden circular.

    Patrón: researcher → analyst → writer → researcher → ...

    Args:
        state: Snapshot del estado actual con task, participants, conversation, history, round_index

    Returns:
        Nombre del siguiente participante o None para terminar
    """
    # Limitar a 9 rondas (3 rondas completas de 3 agentes)
    if state["round_index"] >= 9:
        print(f"[SELECTOR] 🛑 Límite de rondas alcanzado ({state['round_index']}/9)")
        return None

    # Obtener último speaker
    history = state["history"]
    last_speaker = history[-1].speaker if history else None

    # Definir orden de rotación
    rotation = ["researcher", "analyst", "writer"]

    # Determinar siguiente speaker
    if last_speaker is None or last_speaker not in rotation:
        next_speaker = rotation[0]
    else:
        current_index = rotation.index(last_speaker)
        next_index = (current_index + 1) % len(rotation)
        next_speaker = rotation[next_index]

    print(f"[SELECTOR] 🔄 Round {state['round_index'] + 1}: {last_speaker or 'START'} → {next_speaker}")

    return next_speaker


# =============================================================================
# PATRÓN 2: CONDITIONAL SELECTION (Debate Pattern)
# =============================================================================

def debate_selector(state: GroupChatStateSnapshot) -> Optional[str]:
    """
    Selector para debates: alterna entre dos perspectivas opuestas.

    Patrón:
    1. optimist habla primero
    2. pessimist responde
    3. Se alternan hasta que ambos hayan hablado 3 veces cada uno
    4. moderator da conclusiones finales
    """
    history = state["history"]
    round_index = state["round_index"]

    # Contar cuántas veces habló cada agente
    optimist_count = sum(1 for turn in history if turn.speaker == "optimist")
    pessimist_count = sum(1 for turn in history if turn.speaker == "pessimist")
    moderator_count = sum(1 for turn in history if turn.speaker == "moderator")

    # Fase 1: Debate (máximo 3 turnos por debatiente)
    if optimist_count < 3 or pessimist_count < 3:
        last_speaker = history[-1].speaker if history else None

        if last_speaker == "optimist" and pessimist_count < 3:
            print(f"[DEBATE] 🗣️ Optimist habló → Turno de Pessimist (Round {round_index + 1})")
            return "pessimist"
        elif last_speaker == "pessimist" and optimist_count < 3:
            print(f"[DEBATE] 🗣️ Pessimist habló → Turno de Optimist (Round {round_index + 1})")
            return "optimist"
        else:
            # Primer turno o default
            print(f"[DEBATE] 🎤 Iniciando debate → Optimist habla primero (Round {round_index + 1})")
            return "optimist"

    # Fase 2: Moderador da conclusiones (solo una vez)
    if moderator_count == 0:
        print(f"[DEBATE] 🎙️ Debate completo → Moderator da conclusiones (Round {round_index + 1})")
        return "moderator"

    # Fase 3: Terminar
    print(f"[DEBATE] ✅ Debate finalizado después de {round_index} rondas")
    return None


# =============================================================================
# PATRÓN 3: TASK-BASED SELECTION
# =============================================================================

def task_based_selector(state: GroupChatStateSnapshot) -> Optional[str]:
    """
    Selector basado en la tarea: analiza el contenido y decide qué experto es apropiado.

    Flujo:
    1. coordinator analiza la tarea y decide
    2. specialist (code/data/design) ejecuta
    3. coordinator resume y decide siguiente paso
    4. Continúa hasta que coordinator termina
    """
    history = state["history"]
    round_index = state["round_index"]
    conversation = state["conversation"]

    # Límite de seguridad
    if round_index >= 10:
        print(f"[TASK-SELECTOR] 🛑 Límite de rondas alcanzado")
        return None

    # Obtener último speaker
    last_speaker = history[-1].speaker if history else None

    # Analizar el contenido de la conversación para decisiones básicas
    recent_text = " ".join(
        msg.text.lower() for msg in conversation[-3:] if msg.text
    )

    # Reglas de selección
    if last_speaker is None:
        # Primer turno: coordinator analiza
        print(f"[TASK-SELECTOR] 🎯 Iniciando → Coordinator analiza tarea")
        return "coordinator"

    if last_speaker == "coordinator":
        # Después de coordinator, seleccionar especialista apropiado
        if "code" in recent_text or "programming" in recent_text or "python" in recent_text:
            print(f"[TASK-SELECTOR] 💻 Tarea de código detectada → code_specialist")
            return "code_specialist"
        elif "data" in recent_text or "analysis" in recent_text or "analytics" in recent_text:
            print(f"[TASK-SELECTOR] 📊 Tarea de datos detectada → data_specialist")
            return "data_specialist"
        elif "design" in recent_text or "ui" in recent_text or "ux" in recent_text:
            print(f"[TASK-SELECTOR] 🎨 Tarea de diseño detectada → design_specialist")
            return "design_specialist"
        else:
            # Default: usar code specialist
            print(f"[TASK-SELECTOR] 💻 Tarea genérica → code_specialist")
            return "code_specialist"

    # Si habló un especialista, volver a coordinator
    if last_speaker in ["code_specialist", "data_specialist", "design_specialist"]:
        specialist_count = sum(
            1 for turn in history
            if turn.speaker in ["code_specialist", "data_specialist", "design_specialist"]
        )

        # Después de 2 especialistas, terminar
        if specialist_count >= 2:
            print(f"[TASK-SELECTOR] ✅ Dos especialistas han contribuido → Finalizando")
            return None
        else:
            print(f"[TASK-SELECTOR] 🔄 Especialista terminó → Coordinator decide siguiente paso")
            return "coordinator"

    # Default: terminar si hay lógica inesperada
    print(f"[TASK-SELECTOR] ⚠️ Estado inesperado → Finalizando")
    return None


# =============================================================================
# EJEMPLO 1: Round-Robin Panel de Expertos
# =============================================================================

async def example_round_robin_panel():
    """
    Ejemplo de panel de expertos con rotación round-robin.

    Flujo:
    User task → researcher → analyst → writer → researcher → ... (9 rondas)
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Round-Robin Panel de Expertos")
    print("=" * 70)
    print("\n📋 Patrón: researcher → analyst → writer (rotación circular)")
    print("🔄 Límite: 9 rondas (3 ciclos completos)\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            # Crear 3 agentes expertos
            researcher_client, researcher_agent = await create_agent(
                credential,
                "Eres un investigador experto. Recopila datos y hechos relevantes.",
                "researcher"
            )
            clients.append(researcher_client)

            analyst_client, analyst_agent = await create_agent(
                credential,
                "Eres un analista experto. Analiza datos y encuentra patrones.",
                "analyst"
            )
            clients.append(analyst_client)

            writer_client, writer_agent = await create_agent(
                credential,
                "Eres un escritor experto. Sintetiza información en contenido claro.",
                "writer"
            )
            clients.append(writer_client)

            # Construir workflow con selector round-robin
            workflow = (
                GroupChatBuilder()
                .select_speakers(
                    round_robin_selector,
                    display_name="RoundRobinManager"
                )
                .participants(
                    researcher=researcher_agent,
                    analyst=analyst_agent,
                    writer=writer_agent
                )
                .build()
            )

            # Ejecutar
            task = "Analicen las tendencias de IA en 2024"
            print(f"📝 Tarea: {task}\n")

            async for event in workflow.run_stream(task):
                if hasattr(event, 'text') and event.text:
                    # Mostrar resumen de cada mensaje
                    author = getattr(event, 'author_name', 'Unknown')
                    text_preview = event.text[:150] + "..." if len(event.text) > 150 else event.text
                    print(f"\n💬 [{author}]: {text_preview}")

            print("\n✅ Panel completado")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# EJEMPLO 2: Debate con Selector Condicional
# =============================================================================

async def example_debate_pattern():
    """
    Ejemplo de debate entre dos perspectivas con moderador.

    Flujo:
    optimist ⟷ pessimist (3 turnos cada uno) → moderator (conclusión)
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Debate Pattern (Conditional Selection)")
    print("=" * 70)
    print("\n🗣️ Patrón: optimist ⟷ pessimist → moderator")
    print("🔄 Límite: 3 turnos por debatiente + conclusión del moderador\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            # Crear agentes para debate
            optimist_client, optimist_agent = await create_agent(
                credential,
                "Eres un optimista. Resalta los aspectos positivos y oportunidades.",
                "optimist"
            )
            clients.append(optimist_client)

            pessimist_client, pessimist_agent = await create_agent(
                credential,
                "Eres un pesimista. Identifica riesgos y desafíos potenciales.",
                "pessimist"
            )
            clients.append(pessimist_client)

            moderator_client, moderator_agent = await create_agent(
                credential,
                "Eres un moderador neutral. Sintetiza ambos puntos de vista y concluye.",
                "moderator"
            )
            clients.append(moderator_client)

            # Construir workflow con selector de debate
            workflow = (
                GroupChatBuilder()
                .select_speakers(
                    debate_selector,
                    display_name="DebateModerator"
                )
                .participants(
                    optimist=optimist_agent,
                    pessimist=pessimist_agent,
                    moderator=moderator_agent
                )
                .build()
            )

            # Ejecutar
            task = "¿Cuál es el futuro del trabajo remoto?"
            print(f"📝 Tópico de debate: {task}\n")

            async for event in workflow.run_stream(task):
                if hasattr(event, 'text') and event.text:
                    author = getattr(event, 'author_name', 'Unknown')
                    text_preview = event.text[:200] + "..." if len(event.text) > 200 else event.text
                    print(f"\n🎤 [{author}]: {text_preview}")

            print("\n✅ Debate completado")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# EJEMPLO 3: Task-Based Selection
# =============================================================================

async def example_task_based_selection():
    """
    Ejemplo de selección basada en la tarea.

    Flujo:
    coordinator analiza → selecciona especialista apropiado → coordinator resume
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Task-Based Selection")
    print("=" * 70)
    print("\n🎯 Patrón: coordinator → specialist (apropiado) → coordinator")
    print("📊 El coordinator decide qué especialista usar basado en el contenido\n")

    async with DefaultAzureCredential() as credential:
        clients = []
        try:
            # Crear coordinator
            coordinator_client, coordinator_agent = await create_agent(
                credential,
                "Eres un coordinador. Analiza tareas y delega a especialistas apropiados.",
                "coordinator"
            )
            clients.append(coordinator_client)

            # Crear especialistas
            code_client, code_agent = await create_agent(
                credential,
                "Eres un especialista en programación y desarrollo de software.",
                "code_specialist"
            )
            clients.append(code_client)

            data_client, data_agent = await create_agent(
                credential,
                "Eres un especialista en análisis de datos y estadística.",
                "data_specialist"
            )
            clients.append(data_client)

            design_client, design_agent = await create_agent(
                credential,
                "Eres un especialista en diseño UI/UX.",
                "design_specialist"
            )
            clients.append(design_client)

            # Construir workflow
            workflow = (
                GroupChatBuilder()
                .select_speakers(
                    task_based_selector,
                    display_name="TaskCoordinator"
                )
                .participants(
                    coordinator=coordinator_agent,
                    code_specialist=code_agent,
                    data_specialist=data_agent,
                    design_specialist=design_agent
                )
                .build()
            )

            # Ejecutar
            task = "Necesito crear una aplicación web de análisis de datos con Python"
            print(f"📝 Tarea: {task}\n")

            async for event in workflow.run_stream(task):
                if hasattr(event, 'text') and event.text:
                    author = getattr(event, 'author_name', 'Unknown')
                    text_preview = event.text[:200] + "..." if len(event.text) > 200 else event.text
                    print(f"\n💼 [{author}]: {text_preview}")

            print("\n✅ Tarea completada")

        finally:
            for client in clients:
                await client.__aexit__(None, None, None)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def create_agent(credential, instructions: str, name: str):
    """
    Helper para crear un agente con cliente.

    Args:
        credential: Azure credential
        instructions: Instrucciones del agente
        name: Nombre del agente

    Returns:
        Tuple (client, agent)
    """
    client = AzureAIAgentClient(
        async_credential=credential,
        should_cleanup_agent=True
    )
    agent = client.create_agent(
        instructions=instructions,
        name=name
    )
    # Warm-up del agente
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
    print("🚀 INICIANDO EJEMPLOS DE GROUP CHAT WORKFLOWS")
    print("=" * 70)

    try:
        # Ejecutar ejemplos
        await example_round_robin_panel()
        await example_debate_pattern()
        await example_task_based_selection()

    except Exception as e:
        print(f"\n⚠️ Error en ejemplos: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📚 PATRONES DEMOSTRADOS:")
    print("   1. ✅ Round-Robin Selection")
    print("   2. ✅ Debate Pattern (Conditional Selection)")
    print("   3. ✅ Task-Based Selection")

    print("\n💡 CASOS DE USO:")
    print("   • Panel de expertos colaborando en investigación")
    print("   • Debates entre perspectivas diferentes")
    print("   • Coordinación de especialistas por tarea")
    print("   • Revisión multi-etapa de contenido")
    print("   • Simulación de equipos de trabajo")
    print("   • Brainstorming colaborativo")

    print("\n🎯 VENTAJAS DE GROUP CHAT:")
    print("   ✅ Colaboración natural entre múltiples agentes")
    print("   ✅ Orquestación flexible (function-based o LLM-based)")
    print("   ✅ Conversaciones estructuradas con history tracking")
    print("   ✅ Control fino sobre quién habla y cuándo")
    print("   ✅ Patrones reutilizables (round-robin, debate, task-based)")
    print("   ✅ Límites de seguridad con max_rounds")

    print("\n⚙️ COMPONENTES CLAVE:")
    print("   • GroupChatBuilder: Constructor del workflow")
    print("   • select_speakers(): Selector basado en función")
    print("   • set_prompt_based_manager(): Orquestador LLM (no usado aquí)")
    print("   • GroupChatStateSnapshot: Estado inmutable del chat")
    print("   • Selector function: Decide siguiente speaker o None (finish)")

    print("\n📖 ESTRUCTURA DE GroupChatStateSnapshot:")
    print("   • task: ChatMessage - Tarea original del usuario")
    print("   • participants: dict[str, str] - Nombres → descripciones")
    print("   • conversation: tuple[ChatMessage, ...] - Historial completo")
    print("   • history: tuple[GroupChatTurn, ...] - Turnos con speakers")
    print("   • round_index: int - Número de ronda actual")
    print("   • pending_agent: str | None - Agente activo actualmente")

    print("\n💡 SELECTOR PATTERNS:")
    print("   1. Round-Robin: Rotación circular entre participantes")
    print("   2. Conditional: Decisiones if/else basadas en estado")
    print("   3. Task-Based: Analiza contenido y selecciona apropiado")
    print("   4. Finish Condition: Retornar None para terminar")

    print("\n⚠️ IMPORTANTE:")
    print("   • Selector retorna str (nombre) para continuar, None para terminar")
    print("   • Usar max_rounds o lógica en selector para evitar loops infinitos")
    print("   • GroupChatStateSnapshot es inmutable (snapshot del estado)")
    print("   • Nombres de participantes deben coincidir exactamente")


if __name__ == "__main__":
    asyncio.run(main())

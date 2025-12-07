"""
Script que demuestra todas las herramientas de visualizacion y debugging
disponibles en Agent Framework para workflows.

Herramientas cubiertas:
1. WorkflowViz - Visualizacion de workflows
2. Workflow Events - Tracking de ejecucion en tiempo real
3. Export a diferentes formatos (SVG, PNG, PDF, DOT)
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
from agent_framework._workflows._events import (
    ExecutorInvokedEvent,
    ExecutorCompletedEvent,
    ExecutorFailedEvent,
    WorkflowStartedEvent,
    WorkflowFailedEvent,
    AgentRunEvent,
    WorkflowWarningEvent,
    WorkflowErrorEvent
)

load_dotenv()

print("=" * 80)
print("DEMOSTRACION: VISUALIZACION Y DEBUGGING DE WORKFLOWS")
print("=" * 80)


# ==============================================================================
# PARTE 1: CREAR UN WORKFLOW SIMPLE PARA DEMOSTRAR
# ==============================================================================

@executor(id="step_1")
async def step_1(input_data: str, ctx: WorkflowContext[str]) -> None:
    """Primer paso del workflow"""
    print(f"  [STEP 1] Procesando: {input_data}")
    result = f"Procesado por Step 1: {input_data}"
    await ctx.send_message(result)


@executor(id="step_2")
async def step_2(input_data: str, ctx: WorkflowContext[str]) -> None:
    """Segundo paso del workflow"""
    print(f"  [STEP 2] Procesando: {input_data}")
    result = f"Procesado por Step 2: {input_data}"
    await ctx.send_message(result)


@executor(id="step_3")
async def step_3(input_data: str, ctx: WorkflowContext[str]) -> None:
    """Tercer paso del workflow (final)"""
    print(f"  [STEP 3] Procesando: {input_data}")
    result = f"RESULTADO FINAL: {input_data}"
    await ctx.yield_output(result)


async def main():
    # Construir workflow
    print("\n" + "=" * 80)
    print("1. CONSTRUYENDO WORKFLOW SECUENCIAL")
    print("=" * 80)

    workflow = (
        WorkflowBuilder()
        .set_start_executor(step_1)
        .add_edge(step_1, step_2)
        .add_edge(step_2, step_3)
        .build()
    )

    print("Workflow creado con 3 pasos: step_1 -> step_2 -> step_3")

    # ==============================================================================
    # PARTE 2: VISUALIZACION CON WorkflowViz
    # ==============================================================================

    print("\n" + "=" * 80)
    print("2. VISUALIZACION CON WorkflowViz")
    print("=" * 80)

    viz = WorkflowViz(workflow)

    # 2.1 Generar diagrama Mermaid
    print("\n--- 2.1 Diagrama Mermaid ---")
    mermaid_diagram = viz.to_mermaid()
    print("```mermaid")
    print(mermaid_diagram)
    print("```")

    # 2.2 Generar Graphviz DOT
    print("\n--- 2.2 Diagrama Graphviz (DOT format) ---")
    dot_diagram = viz.to_digraph()
    print(dot_diagram)

    # 2.3 Exportar a archivo SVG
    print("\n--- 2.3 Exportar a SVG ---")
    try:
        svg_path = viz.export(format='svg', filename='workflow_diagram.svg')
        print(f"Diagrama SVG guardado en: {svg_path}")
    except Exception as e:
        print(f"Error al exportar SVG: {e}")
        print("(Puede requerir Graphviz instalado en el sistema)")

    # 2.4 Exportar a PNG
    print("\n--- 2.4 Exportar a PNG ---")
    try:
        png_path = viz.save_png('workflow_diagram.png')
        print(f"Diagrama PNG guardado en: {png_path}")
    except Exception as e:
        print(f"Error al exportar PNG: {e}")
        print("(Requiere Graphviz instalado: 'choco install graphviz' en Windows)")

    # 2.5 Exportar a PDF
    print("\n--- 2.5 Exportar a PDF ---")
    try:
        pdf_path = viz.save_pdf('workflow_diagram.pdf')
        print(f"Diagrama PDF guardado en: {pdf_path}")
    except Exception as e:
        print(f"Error al exportar PDF: {e}")
        print("(Requiere Graphviz instalado)")

    # ==============================================================================
    # PARTE 3: DEBUGGING CON WORKFLOW EVENTS
    # ==============================================================================

    print("\n" + "=" * 80)
    print("3. DEBUGGING CON WORKFLOW EVENTS")
    print("=" * 80)
    print("\nMonitoreando todos los eventos del workflow en tiempo real...\n")

    # Ejecutar workflow y capturar TODOS los eventos
    async for event in workflow.run_stream("Datos de entrada"):

        # WorkflowStartedEvent - Inicio del workflow
        if isinstance(event, WorkflowStartedEvent):
            print(f"[WORKFLOW STARTED] Workflow iniciado")

        # ExecutorInvokedEvent - Cuando se invoca un executor
        elif isinstance(event, ExecutorInvokedEvent):
            print(f"[EXECUTOR INVOKED] Ejecutando: {event.executor_id}")
            print(f"                   Input: {event.data}")

        # ExecutorCompletedEvent - Cuando un executor termina
        elif isinstance(event, ExecutorCompletedEvent):
            print(f"[EXECUTOR COMPLETED] Completado: {event.executor_id}")
            print(f"                     Output: {event.data}")

        # ExecutorFailedEvent - Cuando un executor falla
        elif isinstance(event, ExecutorFailedEvent):
            print(f"[EXECUTOR FAILED] Error en: {event.executor_id}")
            print(f"                  Error: {event.error}")

        # WorkflowOutputEvent - Output final del workflow
        elif isinstance(event, WorkflowOutputEvent):
            print(f"[WORKFLOW OUTPUT] Resultado final:")
            print(f"                  {event.data}")

        # WorkflowFailedEvent - Cuando el workflow falla
        elif isinstance(event, WorkflowFailedEvent):
            print(f"[WORKFLOW FAILED] Workflow fallo")
            print(f"                  Error: {event.error}")

        # WorkflowWarningEvent - Warnings
        elif isinstance(event, WorkflowWarningEvent):
            print(f"[WORKFLOW WARNING] {event.message}")

        # WorkflowErrorEvent - Errores
        elif isinstance(event, WorkflowErrorEvent):
            print(f"[WORKFLOW ERROR] {event.message}")

        # AgentRunEvent - Eventos de ejecucion de agentes
        elif isinstance(event, AgentRunEvent):
            print(f"[AGENT RUN] Agente ejecutandose...")

        # Otros eventos
        else:
            event_type = type(event).__name__
            print(f"[{event_type}] Evento: {event}")

    # ==============================================================================
    # PARTE 4: RESUMEN DE CAPACIDADES
    # ==============================================================================

    print("\n" + "=" * 80)
    print("4. RESUMEN DE HERRAMIENTAS DE VISUALIZACION Y DEBUGGING")
    print("=" * 80)

    print("\n=== WorkflowViz - Visualizacion ===")
    print("  1. to_mermaid()      - Genera diagrama Mermaid (para GitHub, docs)")
    print("  2. to_digraph()      - Genera diagrama Graphviz DOT")
    print("  3. export('svg')     - Exporta a SVG (vectorial)")
    print("  4. save_png()        - Exporta a PNG (imagen)")
    print("  5. save_pdf()        - Exporta a PDF (documento)")
    print("  6. export('dot')     - Exporta archivo DOT")

    print("\n=== Workflow Events - Debugging ===")
    print("  1. WorkflowStartedEvent      - Workflow inicia")
    print("  2. ExecutorInvokedEvent      - Executor se invoca")
    print("  3. ExecutorCompletedEvent    - Executor termina")
    print("  4. ExecutorFailedEvent       - Executor falla")
    print("  5. WorkflowOutputEvent       - Output final")
    print("  6. WorkflowFailedEvent       - Workflow falla")
    print("  7. WorkflowWarningEvent      - Warnings")
    print("  8. WorkflowErrorEvent        - Errores")
    print("  9. AgentRunEvent             - Ejecucion de agentes")

    print("\n=== Usos Recomendados ===")
    print("  - Desarrollo:    Usar eventos para debugging detallado")
    print("  - Documentacion: Exportar a Mermaid/SVG para documentar flujos")
    print("  - Presentacion:  Exportar a PNG/PDF para presentaciones")
    print("  - CI/CD:         Generar diagramas automaticamente en builds")
    print("  - Monitoreo:     Capturar eventos para logging y analytics")

    print("\n" + "=" * 80)
    print("DEMO COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

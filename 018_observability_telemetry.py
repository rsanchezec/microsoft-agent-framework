"""
018_observability_telemetry.py

Este script demuestra cómo implementar Observabilidad y Telemetría
en aplicaciones con Microsoft Agent Framework.

La observabilidad es crítica para aplicaciones de producción y permite:
- Monitorear el comportamiento de los agentes
- Debuggear problemas en producción
- Medir rendimiento y costos
- Detectar anomalías y errores
- Analizar patrones de uso

Conceptos Cubiertos:
1. Logging estructurado
2. Métricas de rendimiento
3. Tracking de tokens y costos
4. Rastreo de errores
5. Analytics de conversaciones
6. Visualización de métricas

NOTA: Este ejemplo usa logging estándar de Python.
En producción, considera usar:
- OpenTelemetry (tracing distribuido)
- Azure Application Insights
- Prometheus + Grafana
- DataDog, New Relic, etc.
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ai_function
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 70)
print("EJEMPLOS DE OBSERVABILIDAD Y TELEMETRÍA")
print("=" * 70)


# =============================================================================
# CONFIGURACIÓN DE LOGGING ESTRUCTURADO
# =============================================================================

def setup_structured_logging():
    """
    Configura logging estructurado con formato JSON.

    En producción, esto se enviaría a:
    - Azure Application Insights
    - CloudWatch Logs
    - Elasticsearch
    - Splunk, etc.
    """
    # Crear logger personalizado
    logger = logging.getLogger("AgentFrameworkObservability")
    logger.setLevel(logging.INFO)

    # Handler para consola con formato JSON
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formato estructurado (JSON)
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }

            # Agregar campos adicionales si existen
            if hasattr(record, 'extra_data'):
                log_data.update(record.extra_data)

            return json.dumps(log_data, indent=2)

    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    return logger


# Logger global
logger = setup_structured_logging()


# =============================================================================
# CLASE PARA MÉTRICAS
# =============================================================================

@dataclass
class AgentMetrics:
    """
    Clase para almacenar métricas de un agente.
    """
    agent_name: str
    total_runs: int = 0
    total_errors: int = 0
    total_execution_time: float = 0.0
    total_tokens_prompt: int = 0
    total_tokens_completion: int = 0
    total_cost_usd: float = 0.0
    run_history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.run_history is None:
            self.run_history = []

    @property
    def avg_execution_time(self) -> float:
        """Tiempo promedio de ejecución"""
        if self.total_runs == 0:
            return 0.0
        return self.total_execution_time / self.total_runs

    @property
    def total_tokens(self) -> int:
        """Total de tokens usados"""
        return self.total_tokens_prompt + self.total_tokens_completion

    @property
    def success_rate(self) -> float:
        """Tasa de éxito"""
        if self.total_runs == 0:
            return 0.0
        return (self.total_runs - self.total_errors) / self.total_runs * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convierte métricas a diccionario"""
        return asdict(self)

    def print_summary(self):
        """Imprime resumen de métricas"""
        print("\n" + "=" * 70)
        print(f"📊 MÉTRICAS DEL AGENTE: {self.agent_name}")
        print("=" * 70)
        print(f"Total de ejecuciones:      {self.total_runs}")
        print(f"Errores:                   {self.total_errors}")
        print(f"Tasa de éxito:             {self.success_rate:.1f}%")
        print(f"Tiempo total:              {self.total_execution_time:.2f}s")
        print(f"Tiempo promedio:           {self.avg_execution_time:.2f}s")
        print(f"Tokens (prompt):           {self.total_tokens_prompt:,}")
        print(f"Tokens (completion):       {self.total_tokens_completion:,}")
        print(f"Tokens totales:            {self.total_tokens:,}")
        print(f"Costo estimado:            ${self.total_cost_usd:.4f}")
        print("=" * 70)


# =============================================================================
# COLLECTOR DE MÉTRICAS
# =============================================================================

class MetricsCollector:
    """
    Collector centralizado de métricas para múltiples agentes.
    """

    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
        self.global_metrics = {
            'total_agents': 0,
            'total_runs': 0,
            'total_errors': 0,
            'total_tokens': 0,
            'total_cost': 0.0
        }

    def get_or_create_metrics(self, agent_name: str) -> AgentMetrics:
        """Obtiene o crea métricas para un agente"""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
            self.global_metrics['total_agents'] += 1
        return self.metrics[agent_name]

    def record_run(
        self,
        agent_name: str,
        execution_time: float,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        cost_usd: float = 0.0,
        error: bool = False,
        query: str = "",
        response: str = ""
    ):
        """
        Registra una ejecución del agente.
        """
        metrics = self.get_or_create_metrics(agent_name)

        # Actualizar métricas
        metrics.total_runs += 1
        metrics.total_execution_time += execution_time
        metrics.total_tokens_prompt += tokens_prompt
        metrics.total_tokens_completion += tokens_completion
        metrics.total_cost_usd += cost_usd

        if error:
            metrics.total_errors += 1

        # Guardar en historial
        metrics.run_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'execution_time': execution_time,
            'tokens_prompt': tokens_prompt,
            'tokens_completion': tokens_completion,
            'cost_usd': cost_usd,
            'error': error,
            'query': query[:100],  # Primeros 100 chars
            'response': response[:100]
        })

        # Actualizar métricas globales
        self.global_metrics['total_runs'] += 1
        self.global_metrics['total_tokens'] += tokens_prompt + tokens_completion
        self.global_metrics['total_cost'] += cost_usd
        if error:
            self.global_metrics['total_errors'] += 1

        # Log estructurado
        logger.info(
            "Agent run completed",
            extra={'extra_data': {
                'agent_name': agent_name,
                'execution_time': execution_time,
                'tokens': tokens_prompt + tokens_completion,
                'cost': cost_usd,
                'error': error
            }}
        )

    def print_global_summary(self):
        """Imprime resumen global de todas las métricas"""
        print("\n" + "=" * 70)
        print("🌐 MÉTRICAS GLOBALES")
        print("=" * 70)
        print(f"Total de agentes:          {self.global_metrics['total_agents']}")
        print(f"Total de ejecuciones:      {self.global_metrics['total_runs']}")
        print(f"Total de errores:          {self.global_metrics['total_errors']}")
        print(f"Total de tokens:           {self.global_metrics['total_tokens']:,}")
        print(f"Costo total estimado:      ${self.global_metrics['total_cost']:.4f}")
        print("=" * 70)

    def export_metrics(self, filename: str = "metrics_export.json"):
        """
        Exporta todas las métricas a un archivo JSON.
        """
        export_data = {
            'global_metrics': self.global_metrics,
            'agent_metrics': {
                name: metrics.to_dict()
                for name, metrics in self.metrics.items()
            },
            'export_timestamp': datetime.utcnow().isoformat()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Métricas exportadas a: {filename}")


# Instancia global del collector
metrics_collector = MetricsCollector()


# =============================================================================
# WRAPPER OBSERVÁVEL PARA AGENTES
# =============================================================================

class ObservableAgent:
    """
    Wrapper que agrega observabilidad automática a cualquier agente.
    """

    def __init__(self, agent, agent_name: str, cost_per_1k_tokens: float = 0.001):
        self.agent = agent
        self.agent_name = agent_name
        self.cost_per_1k_tokens = cost_per_1k_tokens

    async def run(self, query: str, **kwargs) -> Any:
        """
        Ejecuta el agente con observabilidad automática.
        """
        start_time = time.time()
        error = False
        response = None
        tokens_prompt = 0
        tokens_completion = 0

        try:
            # Log inicio
            logger.info(
                f"Starting agent run: {self.agent_name}",
                extra={'extra_data': {
                    'agent_name': self.agent_name,
                    'query': query[:100]
                }}
            )

            # Ejecutar agente
            response = await self.agent.run(query, **kwargs)

            # NOTA: En producción, extraerías tokens del response
            # Para este ejemplo, usamos valores estimados
            tokens_prompt = len(query.split()) * 1.3  # Estimación
            tokens_completion = len(str(response).split()) * 1.3

        except Exception as e:
            error = True
            logger.error(
                f"Agent run failed: {self.agent_name}",
                extra={'extra_data': {
                    'agent_name': self.agent_name,
                    'error': str(e),
                    'query': query[:100]
                }}
            )
            raise

        finally:
            # Calcular métricas
            execution_time = time.time() - start_time
            total_tokens = tokens_prompt + tokens_completion
            cost_usd = (total_tokens / 1000) * self.cost_per_1k_tokens

            # Registrar métricas
            metrics_collector.record_run(
                agent_name=self.agent_name,
                execution_time=execution_time,
                tokens_prompt=int(tokens_prompt),
                tokens_completion=int(tokens_completion),
                cost_usd=cost_usd,
                error=error,
                query=query,
                response=str(response) if response else ""
            )

        return response


# =============================================================================
# HERRAMIENTAS DE EJEMPLO
# =============================================================================

@ai_function
def calculate(expression: str) -> str:
    """Evalúa una expresión matemática simple"""
    try:
        # SEGURIDAD: En producción usa una librería segura
        result = eval(expression)
        return f"El resultado es: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# EJEMPLOS DE USO
# =============================================================================

async def example_basic_observability():
    """
    Ejemplo básico de observabilidad con un agente.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Observabilidad Básica")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Crear agente normal
            base_agent = client.create_agent(
                name="Assistant",
                instructions="Eres un asistente útil."
            )

            # Wrappear con observabilidad
            observable_agent = ObservableAgent(
                agent=base_agent,
                agent_name="ObservableAssistant"
            )

            # Ejecutar varias consultas
            queries = [
                "¿Cuál es la capital de Francia?",
                "Explica qué es la fotosíntesis",
                "Dame 3 consejos para dormir mejor"
            ]

            for i, query in enumerate(queries, 1):
                print(f"\n📝 Consulta {i}/{len(queries)}: {query}")
                response = await observable_agent.run(query)
                print(f"✅ Respuesta: {str(response)[:100]}...")

            # Mostrar métricas
            metrics = metrics_collector.get_or_create_metrics("ObservableAssistant")
            metrics.print_summary()


async def example_multiple_agents_observability():
    """
    Ejemplo con múltiples agentes monitoreados.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Múltiples Agentes con Observabilidad")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Crear varios agentes especializados
            researcher = ObservableAgent(
                agent=client.create_agent(
                    name="Researcher",
                    instructions="Eres un investigador experto."
                ),
                agent_name="ResearcherAgent"
            )

            writer = ObservableAgent(
                agent=client.create_agent(
                    name="Writer",
                    instructions="Eres un escritor creativo."
                ),
                agent_name="WriterAgent"
            )

            calculator = ObservableAgent(
                agent=client.create_agent(
                    name="Calculator",
                    instructions="Eres un asistente matemático.",
                    tools=[calculate]
                ),
                agent_name="CalculatorAgent"
            )

            # Usar los agentes
            print("\n🔬 Usando Researcher Agent:")
            await researcher.run("Investiga sobre inteligencia artificial")

            print("\n✍️ Usando Writer Agent:")
            await writer.run("Escribe un poema sobre el mar")

            print("\n🔢 Usando Calculator Agent:")
            await calculator.run("Calcula 15 * 23")

            # Ejecutar múltiples veces
            for i in range(2):
                await researcher.run(f"Investiga sobre tema {i+1}")

            # Mostrar métricas individuales
            for agent_name in ["ResearcherAgent", "WriterAgent", "CalculatorAgent"]:
                metrics = metrics_collector.get_or_create_metrics(agent_name)
                metrics.print_summary()

            # Mostrar métricas globales
            metrics_collector.print_global_summary()


async def example_error_tracking():
    """
    Ejemplo de tracking de errores.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Tracking de Errores")
    print("=" * 70)

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            observable_agent = ObservableAgent(
                agent=client.create_agent(
                    name="TestAgent",
                    instructions="Eres un agente de prueba."
                ),
                agent_name="ErrorTrackingAgent"
            )

            # Ejecutar consultas (algunas pueden fallar)
            queries = [
                "Consulta normal 1",
                "Consulta normal 2",
                "Consulta normal 3"
            ]

            for query in queries:
                try:
                    await observable_agent.run(query)
                except Exception as e:
                    print(f"❌ Error capturado: {e}")

            # Mostrar métricas con tracking de errores
            metrics = metrics_collector.get_or_create_metrics("ErrorTrackingAgent")
            metrics.print_summary()

            print("\n💡 Nota: Tasa de éxito y errores son rastreados automáticamente")


# =============================================================================
# MAIN: Ejecutar todos los ejemplos
# =============================================================================

async def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "=" * 70)
    print("🚀 INICIANDO EJEMPLOS DE OBSERVABILIDAD")
    print("=" * 70)

    try:
        await example_basic_observability()
        await example_multiple_agents_observability()
        await example_error_tracking()

        # Exportar métricas
        metrics_collector.export_metrics("agent_metrics.json")

    except Exception as e:
        print(f"\n⚠️ Error en ejemplos: {e}")

    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 70)

    print("\n📊 MÉTRICAS DISPONIBLES:")
    print("   • Total de ejecuciones")
    print("   • Tiempo de ejecución (total y promedio)")
    print("   • Uso de tokens (prompt y completion)")
    print("   • Costos estimados")
    print("   • Tasa de éxito/errores")
    print("   • Historial de runs")

    print("\n💡 EN PRODUCCIÓN, INTEGRA CON:")
    print("   • OpenTelemetry (tracing distribuido)")
    print("   • Azure Application Insights")
    print("   • Prometheus + Grafana (métricas)")
    print("   • ELK Stack (logs)")
    print("   • DataDog, New Relic, etc.")

    print("\n🎯 VENTAJAS DE OBSERVABILIDAD:")
    print("   ✅ Debugging de problemas en producción")
    print("   ✅ Análisis de costos y optimización")
    print("   ✅ Monitoreo de rendimiento")
    print("   ✅ Detección de anomalías")
    print("   ✅ Análisis de patrones de uso")
    print("   ✅ Compliance y auditoría")

    print("\n🔍 DATOS QUE DEBERÍAS RASTREAR:")
    print("   • Latencia y tiempo de respuesta")
    print("   • Uso de tokens y costos")
    print("   • Tasas de error")
    print("   • Patrones de consultas")
    print("   • Uso de herramientas/tools")
    print("   • Satisfacción del usuario")


if __name__ == "__main__":
    asyncio.run(main())

"""
024_custom_tools_advanced.py

Este script demuestra herramientas personalizadas avanzadas en el Microsoft Agent Framework.

Temas Cubiertos:
1. Herramientas con validación avanzada
2. Herramientas asíncronas (async)
3. Herramientas con estado/contexto
4. Herramientas con retry logic y manejo de errores
5. Herramientas con múltiples tipos de retorno
6. Herramientas compuestas (que usan otras herramientas)
7. Herramientas con rate limiting
8. Herramientas con caching
9. Herramientas con logging y telemetría
10. Mejores prácticas y patrones

Conceptos Clave:
- Typing avanzado con Annotated y Field
- Validación de entrada con Pydantic
- Manejo robusto de errores
- Async/await para operaciones I/O
- Estado compartido entre invocaciones
- Decoradores personalizados
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Annotated, Optional, List, Dict, Any, Union, Literal
from pydantic import Field, validator
from agent_framework import ai_function
import time
import json
from datetime import datetime, timedelta
from functools import wraps
import aiohttp
import sys

load_dotenv()

# Configurar codificacion UTF-8 para Windows (evitar problemas con acentos)
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

print("=" * 80)
print("HERRAMIENTAS PERSONALIZADAS AVANZADAS")
print("=" * 80)


# =============================================================================
# EJEMPLO 1: Herramienta Básica vs Avanzada
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 1: Herramienta Básica vs Avanzada")
print("=" * 80)

# Herramienta básica
def calculate_basic(a: int, b: int) -> int:
    """Suma dos números (herramienta básica)."""
    return a + b

# Herramienta avanzada con validación y documentación rica
@ai_function(
    name="calculate_advanced",
    description="Realiza operaciones matemáticas avanzadas con validación y logging."
)
def calculate_advanced(
    a: Annotated[float, Field(description="Primer número (puede ser decimal)", ge=-1000, le=1000)],
    b: Annotated[float, Field(description="Segundo número (puede ser decimal)", ge=-1000, le=1000)],
    operation: Annotated[
        Literal["add", "subtract", "multiply", "divide"],
        Field(description="Operación a realizar: add, subtract, multiply, divide")
    ] = "add"
) -> Dict[str, Any]:
    """
    Realiza operaciones matemáticas con validación de entrada.

    Características:
    - Validación de rangos (ge=-1000, le=1000)
    - Múltiples operaciones
    - Manejo de división por cero
    - Retorna resultado estructurado con metadata
    """
    print(f"[TOOL] calculate_advanced: {a} {operation} {b}")

    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {
                    "success": False,
                    "error": "División por cero no permitida",
                    "result": None
                }
            result = a / b
        else:
            return {
                "success": False,
                "error": f"Operación desconocida: {operation}",
                "result": None
            }

        return {
            "success": True,
            "result": result,
            "operation": operation,
            "inputs": {"a": a, "b": b},
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

print("[OK] Herramienta basica: calculate_basic(a, b)")
print("[OK] Herramienta avanzada: calculate_advanced(a, b, operation)")
print("   - Validación de rangos (ge=-1000, le=1000)")
print("   - Múltiples operaciones (add, subtract, multiply, divide)")
print("   - Manejo de errores (división por cero)")
print("   - Retorno estructurado con metadata")


# =============================================================================
# EJEMPLO 2: Herramientas Asíncronas (Async Tools)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 2: Herramientas Asíncronas")
print("=" * 80)

async def fetch_url_async(
    url: Annotated[str, Field(description="URL a consultar (debe empezar con http/https)")],
    timeout: Annotated[int, Field(description="Timeout en segundos", ge=1, le=60)] = 10
) -> Dict[str, Any]:
    """
    Consulta una URL de forma asíncrona (operación I/O no bloqueante).

    Ventajas de async:
    - No bloquea el thread principal
    - Permite múltiples requests concurrentes
    - Mejor rendimiento para I/O
    """
    print(f"[ASYNC TOOL] Fetching URL: {url} (timeout: {timeout}s)")

    # Validación básica
    if not url.startswith(("http://", "https://")):
        return {
            "success": False,
            "error": "URL debe empezar con http:// o https://"
        }

    try:
        # Simulación de request HTTP async
        await asyncio.sleep(0.5)  # Simular latencia de red

        # En producción, usar aiohttp:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url, timeout=timeout) as response:
        #         content = await response.text()
        #         return {"success": True, "status": response.status, "content": content}

        return {
            "success": True,
            "url": url,
            "status": 200,
            "content": f"Contenido simulado de {url}",
            "fetched_at": datetime.now().isoformat()
        }

    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": f"Timeout después de {timeout} segundos"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

print("[OK] Herramienta async: fetch_url_async(url, timeout)")
print("   - Operación I/O no bloqueante")
print("   - Validación de URL")
print("   - Manejo de timeout")
print("   - Uso típico: APIs externas, bases de datos, file I/O")


# =============================================================================
# EJEMPLO 3: Herramientas con Estado/Contexto
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 3: Herramientas con Estado (Stateful Tools)")
print("=" * 80)

class DatabaseSimulator:
    """Simulador de base de datos con estado compartido."""

    def __init__(self):
        self.records: Dict[str, Any] = {}
        self.operation_count = 0

    def save_record(
        self,
        key: Annotated[str, Field(description="Clave única del registro")],
        value: Annotated[str, Field(description="Valor a guardar")]
    ) -> Dict[str, Any]:
        """Guarda un registro en la base de datos simulada."""
        self.operation_count += 1
        self.records[key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "operation_number": self.operation_count
        }

        print(f"[STATEFUL TOOL] Guardado: {key} = {value} (op #{self.operation_count})")

        return {
            "success": True,
            "key": key,
            "value": value,
            "total_records": len(self.records),
            "operation_count": self.operation_count
        }

    def get_record(
        self,
        key: Annotated[str, Field(description="Clave del registro a obtener")]
    ) -> Dict[str, Any]:
        """Obtiene un registro de la base de datos simulada."""
        self.operation_count += 1

        if key not in self.records:
            return {
                "success": False,
                "error": f"Registro '{key}' no encontrado",
                "available_keys": list(self.records.keys())
            }

        print(f"[STATEFUL TOOL] Recuperado: {key} (op #{self.operation_count})")

        return {
            "success": True,
            "key": key,
            "record": self.records[key],
            "operation_count": self.operation_count
        }

    def list_records(self) -> Dict[str, Any]:
        """Lista todos los registros en la base de datos."""
        self.operation_count += 1

        print(f"[STATEFUL TOOL] Listando registros (op #{self.operation_count})")

        return {
            "success": True,
            "total_records": len(self.records),
            "keys": list(self.records.keys()),
            "operation_count": self.operation_count
        }

# Crear instancia global (compartida entre invocaciones)
db_simulator = DatabaseSimulator()

print("[OK] Herramientas con estado: DatabaseSimulator")
print("   - save_record(key, value)")
print("   - get_record(key)")
print("   - list_records()")
print("   - Estado compartido: self.records, self.operation_count")
print("   - Útil para: sesiones, cache, historiales")


# =============================================================================
# EJEMPLO 4: Herramientas con Retry Logic
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 4: Herramientas con Retry Logic")
print("=" * 80)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorador que agrega retry logic a funciones asíncronas.

    Args:
        max_retries: Número máximo de reintentos
        delay: Segundos entre reintentos
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)

                    # Si el resultado indica fallo, reintentar
                    if isinstance(result, dict) and not result.get("success", True):
                        raise Exception(result.get("error", "Unknown error"))

                    return result

                except Exception as e:
                    last_exception = e
                    print(f"[RETRY] Intento {attempt + 1}/{max_retries} falló: {e}")

                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))  # Backoff exponencial
                    else:
                        break

            # Todos los reintentos fallaron
            return {
                "success": False,
                "error": f"Falló después de {max_retries} intentos: {last_exception}",
                "retries": max_retries
            }

        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=0.5)
async def unreliable_api_call(
    endpoint: Annotated[str, Field(description="Endpoint de la API")],
    fail_probability: Annotated[float, Field(description="Probabilidad de fallo (0.0-1.0)", ge=0.0, le=1.0)] = 0.5
) -> Dict[str, Any]:
    """
    Simula una API poco confiable que puede fallar aleatoriamente.

    El decorador @retry_on_failure reintentará automáticamente si falla.
    """
    import random

    print(f"[RETRY TOOL] Llamando a API: {endpoint}")

    # Simular fallo aleatorio
    if random.random() < fail_probability:
        raise Exception("Error aleatorio de la API")

    return {
        "success": True,
        "endpoint": endpoint,
        "data": f"Datos de {endpoint}",
        "timestamp": datetime.now().isoformat()
    }

print("[OK] Decorador retry_on_failure(max_retries, delay)")
print("[OK] Herramienta: unreliable_api_call(endpoint, fail_probability)")
print("   - Reintentos automáticos en caso de error")
print("   - Backoff exponencial (1s, 2s, 3s, ...)")
print("   - Útil para: APIs externas, operaciones de red")


# =============================================================================
# EJEMPLO 5: Herramientas con Rate Limiting
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 5: Herramientas con Rate Limiting")
print("=" * 80)

class RateLimiter:
    """Rate limiter simple basado en ventana deslizante."""

    def __init__(self, max_calls: int, time_window: float):
        """
        Args:
            max_calls: Número máximo de llamadas permitidas
            time_window: Ventana de tiempo en segundos
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: List[float] = []

    def check_rate_limit(self) -> bool:
        """Verifica si se excedió el rate limit."""
        now = time.time()

        # Limpiar llamadas fuera de la ventana
        self.calls = [t for t in self.calls if now - t < self.time_window]

        # Verificar límite
        if len(self.calls) >= self.max_calls:
            return False

        # Registrar llamada
        self.calls.append(now)
        return True

    def get_status(self) -> Dict[str, Any]:
        """Retorna estado actual del rate limiter."""
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.time_window]

        return {
            "calls_in_window": len(self.calls),
            "max_calls": self.max_calls,
            "remaining_calls": self.max_calls - len(self.calls),
            "time_window_seconds": self.time_window
        }

# Rate limiter global: 5 llamadas por 10 segundos
api_rate_limiter = RateLimiter(max_calls=5, time_window=10.0)

def rate_limited_api_call(
    endpoint: Annotated[str, Field(description="Endpoint de la API")]
) -> Dict[str, Any]:
    """
    API call con rate limiting.

    Límite: 5 llamadas por 10 segundos.
    """
    print(f"[RATE LIMITED TOOL] Intentando llamar a: {endpoint}")

    if not api_rate_limiter.check_rate_limit():
        status = api_rate_limiter.get_status()
        return {
            "success": False,
            "error": "Rate limit excedido",
            "rate_limit_status": status,
            "retry_after_seconds": api_rate_limiter.time_window
        }

    return {
        "success": True,
        "endpoint": endpoint,
        "data": f"Datos de {endpoint}",
        "rate_limit_status": api_rate_limiter.get_status()
    }

print("[OK] Clase RateLimiter(max_calls, time_window)")
print("[OK] Herramienta: rate_limited_api_call(endpoint)")
print("   - Límite: 5 llamadas por 10 segundos")
print("   - Ventana deslizante (sliding window)")
print("   - Retorna estado del rate limit")


# =============================================================================
# EJEMPLO 6: Herramientas con Caching
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 6: Herramientas con Caching")
print("=" * 80)

class SimpleCache:
    """Cache simple con TTL (time-to-live)."""

    def __init__(self, ttl_seconds: float = 60.0):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache si no expiró."""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            # Cache expirado
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any) -> None:
        """Guarda valor en el cache."""
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }

    def clear(self) -> None:
        """Limpia todo el cache."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del cache."""
        return {
            "total_entries": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
            "keys": list(self.cache.keys())
        }

# Cache global: TTL de 30 segundos
expensive_operation_cache = SimpleCache(ttl_seconds=30.0)

async def expensive_operation(
    input_data: Annotated[str, Field(description="Datos de entrada para procesamiento")]
) -> Dict[str, Any]:
    """
    Operación costosa con caching automático.

    - Cache TTL: 30 segundos
    - Ahorra tiempo en consultas repetidas
    """
    cache_key = f"expensive_op:{input_data}"

    # Verificar cache
    cached_result = expensive_operation_cache.get(cache_key)
    if cached_result is not None:
        print(f"[CACHED TOOL] Cache HIT para: {input_data}")
        return {
            "success": True,
            "result": cached_result,
            "from_cache": True,
            "cache_stats": expensive_operation_cache.get_stats()
        }

    print(f"[CACHED TOOL] Cache MISS para: {input_data} - Ejecutando operación...")

    # Simular operación costosa (3 segundos)
    await asyncio.sleep(3)

    result = f"Resultado procesado de '{input_data}'"

    # Guardar en cache
    expensive_operation_cache.set(cache_key, result)

    return {
        "success": True,
        "result": result,
        "from_cache": False,
        "execution_time_seconds": 3,
        "cache_stats": expensive_operation_cache.get_stats()
    }

print("[OK] Clase SimpleCache(ttl_seconds)")
print("[OK] Herramienta: expensive_operation(input_data)")
print("   - Cache automático con TTL de 30 segundos")
print("   - Ahorra tiempo en consultas repetidas")
print("   - Retorna estadísticas del cache")


# =============================================================================
# EJEMPLO 7: Herramientas Compuestas
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 7: Herramientas Compuestas (que usan otras herramientas)")
print("=" * 80)

def analyze_text(
    text: Annotated[str, Field(description="Texto a analizar")]
) -> Dict[str, Any]:
    """Analiza un texto y retorna estadísticas básicas."""
    words = text.split()

    return {
        "character_count": len(text),
        "word_count": len(words),
        "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "unique_words": len(set(words))
    }

def translate_text(
    text: Annotated[str, Field(description="Texto a traducir")],
    target_language: Annotated[str, Field(description="Idioma destino (en, es, fr, de)")] = "en"
) -> Dict[str, Any]:
    """Simula traducción de texto."""
    # Simulación simple
    translations = {
        "en": f"[EN] {text}",
        "es": f"[ES] {text}",
        "fr": f"[FR] {text}",
        "de": f"[DE] {text}"
    }

    return {
        "original": text,
        "translated": translations.get(target_language, text),
        "target_language": target_language
    }

def analyze_and_translate(
    text: Annotated[str, Field(description="Texto a analizar y traducir")],
    target_language: Annotated[str, Field(description="Idioma destino")] = "en"
) -> Dict[str, Any]:
    """
    Herramienta compuesta que:
    1. Analiza el texto
    2. Lo traduce
    3. Combina ambos resultados

    Este patrón es útil para workflows complejos.
    """
    print(f"[COMPOSITE TOOL] Analizando y traduciendo: '{text}' -> {target_language}")

    # Usar otras herramientas
    analysis = analyze_text(text)
    translation = translate_text(text, target_language)

    return {
        "success": True,
        "original_text": text,
        "analysis": analysis,
        "translation": translation,
        "combined_info": f"El texto tiene {analysis['word_count']} palabras y fue traducido a {target_language}"
    }

print("[OK] Herramientas individuales:")
print("   - analyze_text(text)")
print("   - translate_text(text, target_language)")
print("[OK] Herramienta compuesta:")
print("   - analyze_and_translate(text, target_language)")
print("   - Combina análisis + traducción")
print("   - Patrón útil para workflows complejos")


# =============================================================================
# EJEMPLO 8: Herramientas con Logging y Telemetría
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 8: Herramientas con Logging y Telemetría")
print("=" * 80)

class ToolMetrics:
    """Recolector de métricas para herramientas."""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def record_call(
        self,
        tool_name: str,
        execution_time: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Registra una invocación de herramienta."""
        if tool_name not in self.metrics:
            self.metrics[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_execution_time": 0.0,
                "errors": []
            }

        metrics = self.metrics[tool_name]
        metrics["total_calls"] += 1
        metrics["total_execution_time"] += execution_time

        if success:
            metrics["successful_calls"] += 1
        else:
            metrics["failed_calls"] += 1
            if error:
                metrics["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                })

    def get_metrics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene métricas de una herramienta o todas."""
        if tool_name:
            if tool_name not in self.metrics:
                return {"error": f"No hay métricas para {tool_name}"}

            metrics = self.metrics[tool_name]
            return {
                "tool_name": tool_name,
                **metrics,
                "average_execution_time": (
                    metrics["total_execution_time"] / metrics["total_calls"]
                    if metrics["total_calls"] > 0 else 0
                ),
                "success_rate": (
                    metrics["successful_calls"] / metrics["total_calls"] * 100
                    if metrics["total_calls"] > 0 else 0
                )
            }

        return {
            "total_tools": len(self.metrics),
            "tools": self.metrics
        }

# Metrics collector global
tool_metrics = ToolMetrics()

def monitored_tool(func):
    """Decorador que agrega monitoreo automático a herramientas."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        success = True
        error = None

        try:
            result = await func(*args, **kwargs)

            # Verificar si el resultado indica fallo
            if isinstance(result, dict) and not result.get("success", True):
                success = False
                error = result.get("error")

            return result

        except Exception as e:
            success = False
            error = str(e)
            raise

        finally:
            execution_time = time.time() - start_time
            tool_metrics.record_call(tool_name, execution_time, success, error)

            print(f"[TELEMETRY] {tool_name}: {execution_time:.3f}s (success={success})")

    return wrapper

@monitored_tool
async def monitored_api_call(
    endpoint: Annotated[str, Field(description="Endpoint de la API")]
) -> Dict[str, Any]:
    """API call con monitoreo automático de métricas."""
    await asyncio.sleep(0.2)  # Simular latencia

    return {
        "success": True,
        "endpoint": endpoint,
        "data": f"Datos de {endpoint}"
    }

def get_tool_metrics(
    tool_name: Annotated[Optional[str], Field(description="Nombre de la herramienta (opcional)")] = None
) -> Dict[str, Any]:
    """Obtiene métricas de herramientas monitoreadas."""
    return tool_metrics.get_metrics(tool_name)

print("[OK] Clase ToolMetrics() - Recolector de métricas")
print("[OK] Decorador @monitored_tool - Monitoreo automático")
print("[OK] Herramienta: monitored_api_call(endpoint)")
print("[OK] Herramienta: get_tool_metrics(tool_name)")
print("   - Registra: llamadas totales, éxitos, fallos, tiempos")
print("   - Calcula: success rate, avg execution time")


# =============================================================================
# EJEMPLO 9: Mejores Prácticas
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 9: Mejores Prácticas para Herramientas Personalizadas")
print("=" * 80)

# [OK] BUENA PRÁCTICA 1: Documentación clara
@ai_function(
    name="best_practice_tool",
    description="Ejemplo de herramienta siguiendo mejores prácticas"
)
def best_practice_tool(
    required_param: Annotated[str, Field(description="Parámetro obligatorio (descripción clara)")],
    optional_param: Annotated[int, Field(description="Parámetro opcional con valor por defecto", ge=0, le=100)] = 50
) -> Dict[str, Any]:
    """
    Herramienta que sigue mejores prácticas.

    Mejores Prácticas:
    1. [OK] Documentación clara (docstring + descripción en Field)
    2. [OK] Validación de entrada (ge, le, regex, etc.)
    3. [OK] Tipo de retorno estructurado (Dict[str, Any])
    4. [OK] Manejo de errores explícito
    5. [OK] Logging de operaciones importantes
    6. [OK] Valores por defecto sensatos
    7. [OK] Nombres descriptivos

    Args:
        required_param: Descripción detallada del parámetro
        optional_param: Otro parámetro con rango [0, 100]

    Returns:
        Dict con estructura:
        - success: bool
        - result: Any (resultado de la operación)
        - error: Optional[str] (si success=False)
        - metadata: Dict (información adicional)
    """
    try:
        # Logging
        print(f"[TOOL] best_practice_tool llamada con: {required_param}, {optional_param}")

        # Validación adicional (más allá de Pydantic)
        if not required_param.strip():
            return {
                "success": False,
                "error": "required_param no puede estar vacío",
                "result": None
            }

        # Operación principal
        result = f"Procesado: {required_param} con parámetro {optional_param}"

        # Retorno estructurado
        return {
            "success": True,
            "result": result,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "params": {
                    "required_param": required_param,
                    "optional_param": optional_param
                }
            }
        }

    except Exception as e:
        # Manejo de errores
        print(f"[ERROR] best_practice_tool falló: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

print("[OK] Mejores Prácticas Implementadas:")
print("   1. Documentación clara (docstring + Field descriptions)")
print("   2. Validación de entrada (Pydantic + validación custom)")
print("   3. Tipo de retorno estructurado (Dict[str, Any])")
print("   4. Manejo de errores explícito (try/except)")
print("   5. Logging de operaciones")
print("   6. Valores por defecto sensatos")
print("   7. Nombres descriptivos")


# =============================================================================
# EJEMPLO 10: Comparación de Patrones
# =============================================================================
print("\n" + "=" * 80)
print("TABLA COMPARATIVA: Patrones de Herramientas")
print("=" * 80)

comparison_table = """
+----------------------------+-------------------+----------------------------------+
| Patron                     | Cuando Usar       | Ejemplo                          |
+----------------------------+-------------------+----------------------------------+
| Herramienta Basica         | Operacion simple  | calculate_basic(a, b)            |
| Herramienta Avanzada       | Validacion/logging| calculate_advanced(a, b, op)     |
| Async Tools                | I/O no bloqueante | fetch_url_async(url)             |
| Stateful Tools             | Estado compartido | DatabaseSimulator.save_record()  |
| Retry Logic                | APIs poco fiables | @retry_on_failure                |
| Rate Limiting              | Limite de llamadas| RateLimiter(max_calls, window)   |
| Caching                    | Ops costosas      | SimpleCache(ttl_seconds)         |
| Composite Tools            | Workflows complejos| analyze_and_translate()         |
| Monitored Tools            | Produccion/metricas| @monitored_tool                 |
+----------------------------+-------------------+----------------------------------+
"""
print(comparison_table)


# =============================================================================
# DEMO INTERACTIVO
# =============================================================================
print("\n" + "=" * 80)
print("DEMO INTERACTIVO")
print("=" * 80)

async def run_demo():
    """Ejecuta un demo interactivo con un agente usando herramientas avanzadas."""

    print("\n* Creando agente con herramientas avanzadas...\n")

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Seleccionar herramientas para el demo
            tools = [
                calculate_advanced,
                fetch_url_async,
                db_simulator.save_record,
                db_simulator.get_record,
                db_simulator.list_records,
                unreliable_api_call,
                rate_limited_api_call,
                expensive_operation,
                analyze_and_translate,
                monitored_api_call,
                get_tool_metrics
            ]

            agent = client.create_agent(
                instructions="""
                Eres un asistente avanzado con acceso a herramientas personalizadas.

                Herramientas disponibles:
                - calculate_advanced: Operaciones matemáticas con validación
                - fetch_url_async: Consultar URLs de forma asíncrona
                - save_record/get_record/list_records: Base de datos simulada
                - unreliable_api_call: API con retry automático
                - rate_limited_api_call: API con rate limiting
                - expensive_operation: Operación con caching
                - analyze_and_translate: Análisis y traducción de texto
                - monitored_api_call: API con métricas automáticas
                - get_tool_metrics: Ver métricas de herramientas

                Usa las herramientas apropiadas para cada tarea.
                """,
                name="AdvancedToolsAgent",
                tools=tools
            )

            # Test 1: Operación matemática avanzada
            print("\n" + "-" * 80)
            print("TEST 1: Operación Matemática Avanzada")
            print("-" * 80)
            query = "Calcula 25 dividido entre 5 usando calculate_advanced"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 2: Base de datos con estado
            print("\n" + "-" * 80)
            print("TEST 2: Base de Datos con Estado")
            print("-" * 80)
            query = "Guarda un registro con key='user1' y value='John Doe', luego lista todos los registros"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 3: Operación con caching
            print("\n" + "-" * 80)
            print("TEST 3: Operación con Caching")
            print("-" * 80)
            query = "Ejecuta expensive_operation dos veces con el mismo input 'test data'. La segunda debería ser del cache."
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 4: Herramienta compuesta
            print("\n" + "-" * 80)
            print("TEST 4: Herramienta Compuesta")
            print("-" * 80)
            query = "Analiza y traduce al inglés el texto: 'Hola mundo desde Python'"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 5: Ver métricas
            print("\n" + "-" * 80)
            print("TEST 5: Métricas de Herramientas")
            print("-" * 80)
            query = "Muéstrame las métricas de la herramienta monitored_api_call"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            print("\n" + "=" * 80)
            print("[OK] Demo completado")
            print("=" * 80)


# =============================================================================
# GUÍA DE SELECCIÓN DE PATRONES
# =============================================================================
print("\n" + "=" * 80)
print("GUÍA: ¿Qué Patrón Usar?")
print("=" * 80)

selection_guide = """
+-----------------------------------------------------------------------------+
| SELECCION DE PATRON SEGUN CASO DE USO                                      |
+-----------------------------------------------------------------------------+
|                                                                             |
| 1. OPERACION SIMPLE (calculo, formateo)                                    |
|    -> Herramienta Basica                                                   |
|    Ejemplo: def suma(a, b): return a + b                                   |
|                                                                             |
| 2. NECESITAS VALIDACION DE ENTRADA                                         |
|    -> Herramienta Avanzada con Annotated + Field                           |
|    Ejemplo: Field(ge=0, le=100, description="...")                         |
|                                                                             |
| 3. OPERACION I/O (API, DB, file)                                           |
|    -> Async Tools (async def)                                              |
|    Ejemplo: async def fetch_api(url): ...                                  |
|                                                                             |
| 4. NECESITAS MEMORIA ENTRE LLAMADAS                                        |
|    -> Stateful Tools (class con self.state)                                |
|    Ejemplo: class Database con self.records                                |
|                                                                             |
| 5. API EXTERNA POCO CONFIABLE                                              |
|    -> Retry Logic (@retry_on_failure)                                      |
|    Ejemplo: @retry_on_failure(max_retries=3)                               |
|                                                                             |
| 6. LIMITE DE LLAMADAS POR TIEMPO                                           |
|    -> Rate Limiting (RateLimiter)                                          |
|    Ejemplo: RateLimiter(max_calls=10, time_window=60)                      |
|                                                                             |
| 7. OPERACION COSTOSA/LENTA                                                 |
|    -> Caching (SimpleCache con TTL)                                        |
|    Ejemplo: SimpleCache(ttl_seconds=300)                                   |
|                                                                             |
| 8. WORKFLOW MULTI-PASO                                                     |
|    -> Composite Tools (funcion que llama otras tools)                      |
|    Ejemplo: def analyze_and_save(): analyze() + save()                     |
|                                                                             |
| 9. PRODUCCION CON MONITOREO                                                |
|    -> Monitored Tools (@monitored_tool + ToolMetrics)                      |
|    Ejemplo: @monitored_tool async def api_call(): ...                      |
|                                                                             |
+-----------------------------------------------------------------------------+
"""
print(selection_guide)


# =============================================================================
# ANTI-PATRONES (Qué NO Hacer)
# =============================================================================
print("\n" + "=" * 80)
print("[!]  ANTI-PATRONES: Qué NO Hacer")
print("=" * 80)

antipatterns = """
[X] ANTI-PATRÓN 1: Herramienta sin validación
def bad_tool(url):  # <- Sin typing, sin validación
    return requests.get(url)  # <- Puede fallar sin manejo de error

[OK] CORRECTO:
def good_tool(url: Annotated[str, Field(description="...", regex="^https?://")]):
    try:
        return requests.get(url, timeout=10)
    except Exception as e:
        return {"success": False, "error": str(e)}

────────────────────────────────────────────────────────────────────────────

[X] ANTI-PATRÓN 2: Bloquear con operaciones síncronas en async
async def bad_async_tool():
    time.sleep(5)  # <- Bloquea el event loop!
    return result

[OK] CORRECTO:
async def good_async_tool():
    await asyncio.sleep(5)  # <- No bloqueante
    return result

────────────────────────────────────────────────────────────────────────────

[X] ANTI-PATRÓN 3: Herramienta que retorna tipos inconsistentes
def bad_tool(x):
    if x > 0:
        return x * 2  # <- Retorna int
    else:
        return {"error": "negative"}  # <- Retorna dict!

[OK] CORRECTO:
def good_tool(x) -> Dict[str, Any]:
    if x > 0:
        return {"success": True, "result": x * 2}
    else:
        return {"success": False, "error": "negative"}

────────────────────────────────────────────────────────────────────────────

[X] ANTI-PATRÓN 4: Estado global mutable sin thread-safety
counter = 0  # <- Global mutable

def bad_stateful_tool():
    global counter
    counter += 1  # <- Race condition en async!
    return counter

[OK] CORRECTO:
class Counter:
    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self):
        async with self.lock:
            self.value += 1
            return self.value

────────────────────────────────────────────────────────────────────────────

[X] ANTI-PATRÓN 5: Logging sin contexto
def bad_tool(data):
    print("Error")  # <- ¿Qué error? ¿Dónde?
    return None

[OK] CORRECTO:
def good_tool(data):
    print(f"[TOOL] good_tool called with data='{data}'")
    try:
        # ...
    except Exception as e:
        print(f"[ERROR] good_tool failed: {e}")
        return {"success": False, "error": str(e)}
"""
print(antipatterns)


# =============================================================================
# EJECUTAR DEMO
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EJECUTANDO DEMO INTERACTIVO")
    print("=" * 80)

    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n[!]  Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n[X] Error en demo: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("FIN DEL SCRIPT")
    print("=" * 80)

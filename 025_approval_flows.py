"""
025_approval_flows.py

Este script demuestra flujos de aprobación humana en el Microsoft Agent Framework.

Los flujos de aprobación permiten que ciertas operaciones requieran confirmación
humana antes de ejecutarse, agregando una capa de seguridad y control.

Temas Cubiertos:
1. Aprobaciones básicas (always_require)
2. Aprobaciones condicionales (basadas en criterios)
3. Aprobaciones específicas por herramienta
4. Aprobaciones con timeout
5. Aprobaciones con contexto/metadata
6. Workflows con múltiples puntos de aprobación
7. Patrones de aprobación (auto, manual, delegada)
8. Logging y auditoría de aprobaciones
9. Aprobaciones en operaciones destructivas
10. Mejores prácticas y patrones

Conceptos Clave:
- approval_mode: "always_require", "never_require"
- Validación de operaciones antes de ejecutar
- Control granular por herramienta
- Timeout y fallback automático
- Auditoría completa de decisiones
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from typing import Annotated, Optional, List, Dict, Any, Callable
from pydantic import Field
from agent_framework import ai_function
import time
from datetime import datetime
from enum import Enum
import sys

load_dotenv()

# Configurar codificacion UTF-8 para Windows (evitar problemas con acentos)
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

print("=" * 80)
print("FLUJOS DE APROBACION HUMANA")
print("=" * 80)


# =============================================================================
# EJEMPLO 1: Conceptos Básicos de Aprobación
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 1: Conceptos Basicos de Aprobacion")
print("=" * 80)

print("""
MODOS DE APROBACION:

1. "always_require"
   - Siempre requiere aprobación del usuario antes de ejecutar
   - Uso: Operaciones destructivas, costosas, o sensibles
   - Ejemplo: Eliminar datos, enviar emails, realizar pagos

2. "never_require"
   - Nunca requiere aprobación (ejecución automática)
   - Uso: Operaciones seguras, solo lectura, baratas
   - Ejemplo: Consultas, cálculos, búsquedas

3. Aprobación específica por herramienta (dict)
   - Modo mixto: algunas herramientas requieren aprobación, otras no
   - Uso: Granularidad fina en control de operaciones
   - Ejemplo: {"delete": "always_require", "read": "never_require"}

COMPONENTES DE UN FLUJO DE APROBACION:
- Tool/Function: La operación que requiere aprobación
- Approval Hook: Intercepta la ejecución antes de ejecutar
- Decision: Usuario aprueba (approve) o rechaza (reject)
- Execution: Si aprobado, ejecuta; si rechazado, cancela
- Audit Log: Registra todas las decisiones para auditoría
""")

print("[OK] Conceptos basicos explicados")


# =============================================================================
# EJEMPLO 2: Herramienta con Aprobación Siempre Requerida
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 2: Herramienta con Aprobacion Siempre Requerida")
print("=" * 80)

class ApprovalDecision(Enum):
    """Decisiones posibles en un flujo de aprobación."""
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

class ApprovalRequest:
    """Representa una solicitud de aprobación pendiente."""

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        description: str,
        risk_level: str = "medium"
    ):
        self.tool_name = tool_name
        self.arguments = arguments
        self.description = description
        self.risk_level = risk_level
        self.timestamp = datetime.now()
        self.decision: Optional[ApprovalDecision] = None
        self.approved_by: Optional[str] = None
        self.approved_at: Optional[datetime] = None

    def approve(self, approver: str = "user"):
        """Aprueba la solicitud."""
        self.decision = ApprovalDecision.APPROVED
        self.approved_by = approver
        self.approved_at = datetime.now()

    def reject(self, approver: str = "user"):
        """Rechaza la solicitud."""
        self.decision = ApprovalDecision.REJECTED
        self.approved_by = approver
        self.approved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para logging."""
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "description": self.description,
            "risk_level": self.risk_level,
            "timestamp": self.timestamp.isoformat(),
            "decision": self.decision.value if self.decision else None,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }


class ApprovalManager:
    """Gestiona solicitudes de aprobación con auditoría."""

    def __init__(self):
        self.pending_requests: List[ApprovalRequest] = []
        self.history: List[ApprovalRequest] = []
        self.auto_approve_mode = False  # Para testing

    def create_request(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        description: str,
        risk_level: str = "medium"
    ) -> ApprovalRequest:
        """Crea una nueva solicitud de aprobación."""
        request = ApprovalRequest(tool_name, arguments, description, risk_level)
        self.pending_requests.append(request)
        return request

    async def request_approval(
        self,
        request: ApprovalRequest,
        timeout: float = 30.0
    ) -> ApprovalDecision:
        """
        Solicita aprobación del usuario con timeout.

        En producción, esto mostraría un prompt al usuario.
        Para este demo, simulamos la aprobación.
        """
        print(f"\n[APROBACION REQUERIDA]")
        print(f"Herramienta: {request.tool_name}")
        print(f"Argumentos: {request.arguments}")
        print(f"Descripcion: {request.description}")
        print(f"Nivel de riesgo: {request.risk_level}")
        print(f"Timeout: {timeout}s")

        # En producción: mostrar prompt real al usuario
        # En demo: auto-aprobar o simular decisión
        if self.auto_approve_mode:
            print("[DEMO] Auto-aprobando (modo testing)...")
            await asyncio.sleep(0.5)  # Simular tiempo de decisión
            request.approve("demo_user")
        else:
            # Simulación de decisión humana
            print("[SIMULACION] Usuario revisando...")
            await asyncio.sleep(1)

            # Criterio de aprobación simulado: aprobar si riesgo bajo/medio
            if request.risk_level in ["low", "medium"]:
                request.approve("simulated_user")
            else:
                request.reject("simulated_user")

        # Mover a historial
        self.pending_requests.remove(request)
        self.history.append(request)

        print(f"Decision: {request.decision.value.upper()}")
        return request.decision

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Obtiene el log completo de auditoría."""
        return [req.to_dict() for req in self.history]


# Gestor global de aprobaciones
approval_manager = ApprovalManager()
approval_manager.auto_approve_mode = True  # Para demo


def delete_user(
    user_id: Annotated[str, Field(description="ID del usuario a eliminar")]
) -> Dict[str, Any]:
    """
    Elimina un usuario del sistema (operación DESTRUCTIVA).

    Esta operación SIEMPRE requiere aprobación humana.
    """
    print(f"[TOOL] delete_user ejecutandose: user_id={user_id}")

    # En producción, aquí iría la lógica de eliminación
    return {
        "success": True,
        "message": f"Usuario {user_id} eliminado exitosamente",
        "user_id": user_id,
        "deleted_at": datetime.now().isoformat()
    }


async def delete_user_with_approval(
    user_id: Annotated[str, Field(description="ID del usuario a eliminar")]
) -> Dict[str, Any]:
    """
    Versión con aprobación de delete_user.

    Requiere aprobación humana antes de eliminar.
    """
    # Crear solicitud de aprobación
    request = approval_manager.create_request(
        tool_name="delete_user",
        arguments={"user_id": user_id},
        description=f"Eliminar usuario {user_id} del sistema",
        risk_level="high"
    )

    # Solicitar aprobación
    decision = await approval_manager.request_approval(request, timeout=30.0)

    if decision == ApprovalDecision.APPROVED:
        # Ejecutar operación
        return delete_user(user_id)
    else:
        # Operación rechazada/timeout
        return {
            "success": False,
            "error": f"Operacion rechazada o timeout: {decision.value}",
            "user_id": user_id
        }


print("[OK] Herramienta delete_user_with_approval creada")
print("   - Requiere aprobacion SIEMPRE (risk_level='high')")
print("   - Operacion destructiva")
print("   - Timeout de 30 segundos")


# =============================================================================
# EJEMPLO 3: Aprobaciones Condicionales
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 3: Aprobaciones Condicionales")
print("=" * 80)

async def transfer_money_conditional(
    from_account: Annotated[str, Field(description="Cuenta origen")],
    to_account: Annotated[str, Field(description="Cuenta destino")],
    amount: Annotated[float, Field(description="Monto a transferir", gt=0)]
) -> Dict[str, Any]:
    """
    Transferencia de dinero con aprobación CONDICIONAL.

    Criterios:
    - amount <= 100: No requiere aprobación (auto-aprobado)
    - amount > 100 y <= 1000: Requiere aprobación (riesgo medio)
    - amount > 1000: Requiere aprobación (riesgo alto)
    """
    print(f"\n[TOOL] transfer_money: ${amount} de {from_account} a {to_account}")

    # Determinar si requiere aprobación
    requires_approval = amount > 100

    if not requires_approval:
        print("[INFO] Monto <= $100, no requiere aprobacion (auto-aprobado)")
        # Ejecutar directamente
        return {
            "success": True,
            "message": f"Transferencia de ${amount} completada",
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "approved": "auto",
            "timestamp": datetime.now().isoformat()
        }

    # Determinar nivel de riesgo
    if amount > 1000:
        risk_level = "high"
    else:
        risk_level = "medium"

    # Crear solicitud de aprobación
    request = approval_manager.create_request(
        tool_name="transfer_money",
        arguments={"from": from_account, "to": to_account, "amount": amount},
        description=f"Transferir ${amount} de {from_account} a {to_account}",
        risk_level=risk_level
    )

    # Solicitar aprobación
    decision = await approval_manager.request_approval(request, timeout=30.0)

    if decision == ApprovalDecision.APPROVED:
        return {
            "success": True,
            "message": f"Transferencia de ${amount} completada",
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "approved": "manual",
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "error": f"Transferencia rechazada: {decision.value}",
            "amount": amount
        }


print("[OK] Herramienta transfer_money_conditional creada")
print("   - amount <= $100: Auto-aprobado")
print("   - amount > $100 y <= $1000: Requiere aprobacion (riesgo medio)")
print("   - amount > $1000: Requiere aprobacion (riesgo alto)")


# =============================================================================
# EJEMPLO 4: Decorador de Aprobación Reutilizable
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 4: Decorador de Aprobacion Reutilizable")
print("=" * 80)

def require_approval(
    risk_level: str = "medium",
    timeout: float = 30.0,
    condition: Optional[Callable] = None
):
    """
    Decorador que agrega aprobación automática a funciones.

    Args:
        risk_level: Nivel de riesgo de la operación
        timeout: Timeout para la aprobación
        condition: Función que determina si requiere aprobación
                   Si None, siempre requiere aprobación
                   Si Callable, debe retornar bool
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Si hay condición, evaluar
            if condition is not None:
                requires = condition(*args, **kwargs)
                if not requires:
                    print(f"[INFO] Condicion no cumplida, ejecutando sin aprobacion")
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            # Crear solicitud
            request = approval_manager.create_request(
                tool_name=func.__name__,
                arguments={f"arg{i}": arg for i, arg in enumerate(args)},
                description=func.__doc__ or f"Ejecutar {func.__name__}",
                risk_level=risk_level
            )

            # Solicitar aprobación
            decision = await approval_manager.request_approval(request, timeout=timeout)

            if decision == ApprovalDecision.APPROVED:
                # Ejecutar función
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Operacion rechazada: {decision.value}"
                }

        return wrapper
    return decorator


@require_approval(risk_level="high", timeout=30.0)
def send_email_to_all_users(subject: str, body: str) -> Dict[str, Any]:
    """Envia email a TODOS los usuarios (operacion sensible)."""
    print(f"[TOOL] send_email_to_all_users: subject='{subject}'")

    return {
        "success": True,
        "message": "Email enviado a todos los usuarios",
        "subject": subject,
        "recipients": "all_users",
        "sent_at": datetime.now().isoformat()
    }


# Condición personalizada: solo requiere aprobación si file_size > 1GB
def large_file_condition(*args, **kwargs) -> bool:
    """Condición: requiere aprobación si file_size > 1GB."""
    file_size_mb = kwargs.get("file_size_mb", args[0] if args else 0)
    return file_size_mb > 1024  # > 1GB


@require_approval(
    risk_level="medium",
    timeout=20.0,
    condition=large_file_condition
)
def upload_file(file_size_mb: float) -> Dict[str, Any]:
    """Sube un archivo. Requiere aprobacion si > 1GB."""
    print(f"[TOOL] upload_file: {file_size_mb}MB")

    return {
        "success": True,
        "message": f"Archivo de {file_size_mb}MB subido exitosamente",
        "file_size_mb": file_size_mb,
        "uploaded_at": datetime.now().isoformat()
    }


print("[OK] Decorador @require_approval creado")
print("   - risk_level: Nivel de riesgo de la operacion")
print("   - timeout: Tiempo maximo para decidir")
print("   - condition: Funcion opcional para determinar si requiere aprobacion")
print("\n[OK] Ejemplo: @require_approval(risk_level='high')")
print("[OK] Ejemplo con condicion: @require_approval(condition=large_file_condition)")


# =============================================================================
# EJEMPLO 5: Workflow con Múltiples Puntos de Aprobación
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 5: Workflow con Multiples Puntos de Aprobacion")
print("=" * 80)

async def deploy_to_production_workflow() -> Dict[str, Any]:
    """
    Workflow de deployment con múltiples puntos de aprobación.

    Pasos:
    1. Ejecutar tests -> Auto-aprobado
    2. Build de producción -> Requiere aprobación (riesgo medio)
    3. Deploy a producción -> Requiere aprobación (riesgo alto)
    4. Notificar equipo -> Auto-aprobado
    """
    results = []

    # Paso 1: Tests (no requiere aprobación)
    print("\n[WORKFLOW STEP 1] Ejecutando tests...")
    results.append({
        "step": "tests",
        "success": True,
        "approval_required": False
    })

    # Paso 2: Build (requiere aprobación - riesgo medio)
    print("\n[WORKFLOW STEP 2] Build de produccion")
    request = approval_manager.create_request(
        tool_name="build_production",
        arguments={},
        description="Generar build de produccion",
        risk_level="medium"
    )
    decision = await approval_manager.request_approval(request, timeout=30.0)

    if decision != ApprovalDecision.APPROVED:
        return {
            "success": False,
            "error": f"Build rechazado en paso 2: {decision.value}",
            "completed_steps": results
        }

    results.append({
        "step": "build",
        "success": True,
        "approval_required": True,
        "decision": decision.value
    })

    # Paso 3: Deploy (requiere aprobación - riesgo alto)
    print("\n[WORKFLOW STEP 3] Deploy a produccion")
    request = approval_manager.create_request(
        tool_name="deploy_production",
        arguments={},
        description="Deploy a ambiente de produccion",
        risk_level="high"
    )
    decision = await approval_manager.request_approval(request, timeout=60.0)

    if decision != ApprovalDecision.APPROVED:
        return {
            "success": False,
            "error": f"Deploy rechazado en paso 3: {decision.value}",
            "completed_steps": results
        }

    results.append({
        "step": "deploy",
        "success": True,
        "approval_required": True,
        "decision": decision.value
    })

    # Paso 4: Notificación (no requiere aprobación)
    print("\n[WORKFLOW STEP 4] Notificando al equipo...")
    results.append({
        "step": "notification",
        "success": True,
        "approval_required": False
    })

    return {
        "success": True,
        "message": "Deploy completado exitosamente",
        "steps": results,
        "total_approvals": 2
    }


print("[OK] Workflow deploy_to_production_workflow creado")
print("   - 4 pasos totales")
print("   - 2 puntos de aprobacion (build y deploy)")
print("   - Falla si cualquier aprobacion es rechazada")


# =============================================================================
# EJEMPLO 6: Sistema de Auditoría
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 6: Sistema de Auditoria de Aprobaciones")
print("=" * 80)

class ApprovalAuditor:
    """Sistema de auditoría para aprobaciones."""

    def __init__(self, approval_manager: ApprovalManager):
        self.approval_manager = approval_manager

    def generate_report(self) -> Dict[str, Any]:
        """Genera reporte de auditoría completo."""
        history = self.approval_manager.history

        if not history:
            return {
                "total_requests": 0,
                "message": "No hay solicitudes en el historial"
            }

        # Estadísticas
        total = len(history)
        approved = sum(1 for req in history if req.decision == ApprovalDecision.APPROVED)
        rejected = sum(1 for req in history if req.decision == ApprovalDecision.REJECTED)
        timeout = sum(1 for req in history if req.decision == ApprovalDecision.TIMEOUT)

        # Por nivel de riesgo
        by_risk = {}
        for req in history:
            risk = req.risk_level
            if risk not in by_risk:
                by_risk[risk] = {"total": 0, "approved": 0, "rejected": 0}
            by_risk[risk]["total"] += 1
            if req.decision == ApprovalDecision.APPROVED:
                by_risk[risk]["approved"] += 1
            elif req.decision == ApprovalDecision.REJECTED:
                by_risk[risk]["rejected"] += 1

        return {
            "total_requests": total,
            "approved": approved,
            "rejected": rejected,
            "timeout": timeout,
            "approval_rate": f"{(approved / total * 100):.1f}%",
            "by_risk_level": by_risk,
            "recent_requests": [req.to_dict() for req in history[-5:]]
        }

    def export_audit_log(self, filename: str = "approval_audit.json") -> str:
        """Exporta log de auditoría a archivo JSON."""
        import json

        audit_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_requests": len(self.approval_manager.history),
            "requests": self.approval_manager.get_audit_log()
        }

        # En producción, escribir a archivo
        # with open(filename, "w") as f:
        #     json.dump(audit_data, f, indent=2)

        return json.dumps(audit_data, indent=2)


auditor = ApprovalAuditor(approval_manager)

print("[OK] ApprovalAuditor creado")
print("   - generate_report(): Estadisticas de aprobaciones")
print("   - export_audit_log(): Exporta log completo a JSON")
print("   - Tracking por nivel de riesgo")
print("   - Approval rate calculado")


# =============================================================================
# EJEMPLO 7: Tabla Comparativa de Patrones
# =============================================================================
print("\n" + "=" * 80)
print("TABLA COMPARATIVA: Patrones de Aprobacion")
print("=" * 80)

comparison_table = """
+------------------------+------------------------+----------------------------------+
| Patron                 | Cuando Usar            | Ejemplo                          |
+------------------------+------------------------+----------------------------------+
| Always Require         | Ops destructivas       | delete_user, drop_database       |
| Never Require          | Ops seguras/lectura    | get_user, list_items             |
| Condicional (monto)    | Basado en valor        | transfer_money (> $100)          |
| Condicional (tamano)   | Basado en tamano       | upload_file (> 1GB)              |
| Decorador reutilizable | Aplicar a multiples    | @require_approval()              |
| Workflow multi-punto   | Proceso complejo       | deploy_to_production             |
| Por nivel de riesgo    | Clasificacion riesgo   | low/medium/high                  |
+------------------------+------------------------+----------------------------------+
"""
print(comparison_table)


# =============================================================================
# EJEMPLO 8: Mejores Prácticas
# =============================================================================
print("\n" + "=" * 80)
print("MEJORES PRACTICAS: Flujos de Aprobacion")
print("=" * 80)

best_practices = """
1. CLASIFICAR OPERACIONES POR RIESGO
   [OK] Definir niveles: low, medium, high, critical
   [OK] Asignar nivel apropiado a cada operación
   [OK] Documentar criterios de clasificación

2. TIMEOUTS APROPIADOS
   [OK] Operaciones críticas: 60-120 segundos
   [OK] Operaciones estándar: 30 segundos
   [OK] Timeout claro al usuario

3. AUDITORIA COMPLETA
   [OK] Registrar TODAS las decisiones
   [OK] Incluir: timestamp, usuario, operación, decisión
   [OK] Log inmutable para compliance

4. CONTEXTO RICO EN SOLICITUD
   [OK] Descripción clara de la operación
   [OK] Argumentos visibles al aprobador
   [OK] Consecuencias de aprobar/rechazar

5. FALLBACK AUTOMATICO
   [OK] Timeout -> rechazar por defecto
   [OK] No dejar operaciones en limbo
   [OK] Notificar al usuario del timeout

6. GRANULARIDAD APROPIADA
   [OK] No requerir aprobación para TODO
   [OK] Balance entre seguridad y usabilidad
   [OK] Aprobaciones condicionales cuando sea posible

7. TESTING Y SIMULACION
   [OK] Modo auto-approve para testing
   [OK] Modo de simulación para demos
   [OK] No usar en producción sin validar

8. DELEGACION Y ROLES
   [OK] Diferentes aprobadores según operación
   [OK] Matriz de autorización (quien aprueba qué)
   [OK] Escalamiento automático si timeout
"""
print(best_practices)


# =============================================================================
# EJEMPLO 9: Anti-Patrones
# =============================================================================
print("\n" + "=" * 80)
print("[!] ANTI-PATRONES: Que NO Hacer")
print("=" * 80)

antipatterns = """
[X] ANTI-PATRON 1: Requerir aprobacion para TODO
Problema: Fatiga de aprobaciones, usuarios aprueban sin leer
Solucion: Solo operaciones realmente sensibles/destructivas

[X] ANTI-PATRON 2: Sin timeout
Problema: Operaciones quedan en limbo indefinidamente
Solucion: Siempre timeout con fallback a rechazo

[X] ANTI-PATRON 3: Contexto insuficiente
Problema: Usuario no sabe que esta aprobando
Solucion: Descripcion clara, argumentos visibles, consecuencias

[X] ANTI-PATRON 4: Sin auditoria
Problema: No hay registro de quien aprobo que
Solucion: Log completo, inmutable, con timestamps

[X] ANTI-PATRON 5: Aprobaciones sin validacion
Problema: Aprobar operaciones invalidas
Solucion: Validar argumentos ANTES de solicitar aprobacion

[X] ANTI-PATRON 6: Bloquear operaciones criticas
Problema: Operacion urgente bloqueada por aprobacion
Solucion: Override de emergencia con justificacion y auditoria

[X] ANTI-PATRON 7: No comunicar decision
Problema: Usuario no sabe si fue aprobado/rechazado
Solucion: Notificacion clara del resultado
"""
print(antipatterns)


# =============================================================================
# EJEMPLO 10: Casos de Uso Comunes
# =============================================================================
print("\n" + "=" * 80)
print("CASOS DE USO COMUNES")
print("=" * 80)

use_cases = """
1. OPERACIONES FINANCIERAS
   - Transferencias > umbral
   - Pagos a proveedores
   - Reembolsos

2. GESTION DE USUARIOS
   - Eliminar usuarios
   - Cambiar permisos/roles
   - Desactivar cuentas

3. INFRAESTRUCTURA
   - Deploy a produccion
   - Cambios de configuracion
   - Escalado de recursos

4. DATOS SENSIBLES
   - Eliminar datos
   - Exportar datos personales
   - Cambios masivos

5. COMUNICACIONES
   - Emails masivos
   - Notificaciones push
   - SMS

6. COMPLIANCE
   - Acceso a datos auditados
   - Operaciones reguladas
   - Cambios con impacto legal
"""
print(use_cases)


# =============================================================================
# DEMO INTERACTIVO
# =============================================================================
print("\n" + "=" * 80)
print("DEMO INTERACTIVO")
print("=" * 80)

async def run_demo():
    """Ejecuta demo interactivo de flujos de aprobación."""

    print("\n* Creando demos de aprobaciones...\n")

    # Demo 1: Aprobación siempre requerida
    print("\n" + "-" * 80)
    print("DEMO 1: Aprobacion Siempre Requerida (delete_user)")
    print("-" * 80)
    result = await delete_user_with_approval("user_12345")
    print(f"Resultado: {result}\n")

    # Demo 2: Aprobación condicional - auto-aprobado
    print("\n" + "-" * 80)
    print("DEMO 2: Aprobacion Condicional - Monto Pequeno (auto-aprobado)")
    print("-" * 80)
    result = await transfer_money_conditional("ACC001", "ACC002", 50.0)
    print(f"Resultado: {result}\n")

    # Demo 3: Aprobación condicional - requiere aprobación
    print("\n" + "-" * 80)
    print("DEMO 3: Aprobacion Condicional - Monto Grande (requiere aprobacion)")
    print("-" * 80)
    result = await transfer_money_conditional("ACC001", "ACC002", 500.0)
    print(f"Resultado: {result}\n")

    # Demo 4: Decorador con condición - no requiere aprobación
    print("\n" + "-" * 80)
    print("DEMO 4: Decorador con Condicion - Archivo Pequeno")
    print("-" * 80)
    result = await upload_file(500.0)  # 500MB < 1GB
    print(f"Resultado: {result}\n")

    # Demo 5: Decorador con condición - requiere aprobación
    print("\n" + "-" * 80)
    print("DEMO 5: Decorador con Condicion - Archivo Grande")
    print("-" * 80)
    result = await upload_file(2048.0)  # 2GB > 1GB
    print(f"Resultado: {result}\n")

    # Demo 6: Workflow completo
    print("\n" + "-" * 80)
    print("DEMO 6: Workflow de Deploy con Multiples Aprobaciones")
    print("-" * 80)
    result = await deploy_to_production_workflow()
    print(f"Resultado: {result}\n")

    # Demo 7: Reporte de auditoría
    print("\n" + "-" * 80)
    print("DEMO 7: Reporte de Auditoria")
    print("-" * 80)
    report = auditor.generate_report()
    print("Reporte de Auditoria:")
    import json
    print(json.dumps(report, indent=2))

    print("\n" + "=" * 80)
    print("[OK] Demo completado exitosamente")
    print("=" * 80)


# =============================================================================
# EJEMPLO CON AGENTE DE AZURE AI
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO: Agente con Herramientas que Requieren Aprobacion")
print("=" * 80)

async def run_agent_demo():
    """
    Demo de agente de Azure AI con herramientas que requieren aprobación.

    NOTA: Este ejemplo usa aprobaciones simuladas. En producción,
    las aprobaciones se manejan a través de la UI o callbacks.
    """

    print("\n* Creando agente con herramientas de aprobacion...\n")

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:

            # Herramientas para el agente
            tools = [
                delete_user_with_approval,
                transfer_money_conditional,
                upload_file
            ]

            agent = client.create_agent(
                instructions="""
                Eres un asistente administrativo con acceso a operaciones sensibles.

                Herramientas disponibles:
                - delete_user_with_approval: Eliminar usuario (SIEMPRE requiere aprobacion)
                - transfer_money_conditional: Transferir dinero (requiere aprobacion si > $100)
                - upload_file: Subir archivo (requiere aprobacion si > 1GB)

                IMPORTANTE:
                - Informa al usuario cuando una operacion requiere aprobacion
                - Explica por que requiere aprobacion (monto, tamano, riesgo)
                - Confirma cuando la aprobacion fue exitosa o rechazada
                """,
                name="ApprovalFlowAgent",
                tools=tools
            )

            # Test 1: Operación que requiere aprobación
            print("\n" + "-" * 80)
            print("TEST 1: Solicitar eliminacion de usuario")
            print("-" * 80)
            query = "Elimina el usuario user_12345 del sistema"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 2: Operación condicional - auto-aprobada
            print("\n" + "-" * 80)
            print("TEST 2: Transferencia pequena (auto-aprobada)")
            print("-" * 80)
            query = "Transfiere $50 de ACC001 a ACC002"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            # Test 3: Operación condicional - requiere aprobación
            print("\n" + "-" * 80)
            print("TEST 3: Transferencia grande (requiere aprobacion)")
            print("-" * 80)
            query = "Transfiere $5000 de ACC001 a ACC002"
            print(f"Query: {query}")
            result = await agent.run(query)
            print(f"Resultado: {result.text}\n")

            print("\n" + "=" * 80)
            print("[OK] Demo de agente completado")
            print("=" * 80)


# =============================================================================
# EJECUTAR DEMOS
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EJECUTANDO DEMOS")
    print("=" * 80)

    try:
        # Demo de aprobaciones básicas
        print("\n=== DEMO 1: Flujos de Aprobacion Basicos ===")
        asyncio.run(run_demo())

        # Demo con agente (opcional, requiere Azure credentials)
        print("\n=== DEMO 2: Agente con Aprobaciones ===")
        print("[INFO] Demo de agente requiere credenciales de Azure")
        print("[INFO] Descomentar asyncio.run(run_agent_demo()) para ejecutar")
        # asyncio.run(run_agent_demo())

    except KeyboardInterrupt:
        print("\n\n[!] Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n[X] Error en demo: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("FIN DEL SCRIPT")
    print("=" * 80)

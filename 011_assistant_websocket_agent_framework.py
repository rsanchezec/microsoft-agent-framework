"""
assistant_websocket_agent_framework.py - API WebSocket con Agent Framework Azure AI

Este archivo usa agent_framework_azure_ai (proyectos directos, sin hub) en lugar de AIProjectClient.
Mantiene conversaciones persistentes usando threads del Agent Framework.

Basado en:
- assistant_websocket.py (estructura FastAPI/WebSocket)
- 002_reuseexistingagent.py (reutilizar agente con agent_framework_azure_ai)
- 003_persistentconversation.py (threads persistentes)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import json
import uvicorn
import os
import logging
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging para producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Assistant API (Agent Framework)",
    description="WebSocket API para asistente AI con Azure Agent Framework",
    version="1.0.0"
)

# Configurar CORS con soporte para múltiples orígenes
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

logger.info(f"🌐 CORS configurado para orígenes: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentFrameworkChatManager:
    """
    Gestor de sesiones de chat persistentes con Agent Framework Azure AI

    Usa agent_framework_azure_ai que trabaja directamente con proyectos (sin hub)
    """

    def __init__(self):
        # Configuración esencial de Azure AI
        # Para agent_framework_azure_ai se usa AZURE_AI_PROJECT_ENDPOINT
        self.agent_id = os.getenv("AZURE_AGENT_ID")

        # Validar configuración requerida
        if not self.agent_id:
            logger.error("❌ AZURE_AGENT_ID no está configurado")
            raise ValueError("AZURE_AGENT_ID es requerido")

        # Validar que existe AZURE_AI_PROJECT_ENDPOINT
        if not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
            logger.error("❌ AZURE_AI_PROJECT_ENDPOINT no está configurado")
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT es requerido en .env")

        # Gestión de sesiones persistentes
        self.user_threads: Dict[str, str] = {}  # {user_id: thread_id}
        self.active_connections: Dict[str, WebSocket] = {}  # {user_id: websocket}

        # Mantener una referencia al credential para reutilizarlo
        self.credential = None

        logger.info(f"✅ Chat Manager inicializado | Agent: {self.agent_id}")

    async def _get_agent_client(self):
        """
        Crea o reutiliza el cliente de Agent Framework
        Usa async context manager como en los scripts 002 y 003
        """
        if not self.credential:
            self.credential = DefaultAzureCredential()

        # Retorna el context manager para usar con async with
        return AzureAIAgentClient(
            async_credential=self.credential,
            agent_id=self.agent_id  # Reutiliza el agente existente
        )

    async def connect(self, websocket: WebSocket, user_id: str):
        """Conecta usuario y crea/recupera su sesión persistente (thread)"""
        try:
            self.active_connections[user_id] = websocket

            # Si ya tiene un thread, usar el existente
            if user_id in self.user_threads:
                thread_id = self.user_threads[user_id]
                logger.info(f"📂 Sesión recuperada: {user_id} | Thread: {thread_id}")
            else:
                # Si no tiene thread, se creará en la primera interacción
                thread_id = None
                logger.info(f"🆕 Nueva sesión: {user_id} | Thread se creará en primera interacción")

            return thread_id

        except Exception as e:
            logger.error(f"❌ Error en conexión para {user_id}: {e}")
            return None

    def disconnect(self, user_id: str):
        """Desconecta usuario pero mantiene su sesión persistente"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"🔌 Usuario {user_id} desconectado")

    async def send_to_assistant(self, user_id: str, message: str) -> Optional[str]:
        """
        Envía mensaje al asistente y obtiene respuesta
        Usa el patrón de agent_framework_azure_ai con threads persistentes
        """
        try:
            # Obtener thread_id existente o None para crear uno nuevo
            thread_id = self.user_threads.get(user_id, None)

            async with await self._get_agent_client() as client:
                # Crear el agente (reutiliza el existente por agent_id)
                agent = client.create_agent(
                    instructions="Eres un asistente útil que recuerda el contexto de la conversación.",
                    name="Assistant"
                )

                # Crear o reutilizar thread (patrón del script 003)
                thread = agent.get_new_thread(service_thread_id=thread_id)

                # Ejecutar la pregunta en el thread
                result = await agent.run(message, thread=thread)

                # Si es un thread nuevo, guardar el thread_id
                if user_id not in self.user_threads:
                    new_thread_id = thread.service_thread_id
                    self.user_threads[user_id] = new_thread_id
                    logger.info(f"💾 Nuevo thread creado para {user_id}: {new_thread_id}")

                logger.info(f"✅ Respuesta generada para {user_id}")
                return result.text

        except Exception as e:
            logger.error(f"❌ Error enviando mensaje para {user_id}: {e}")
            return None

    def cleanup_user_session(self, user_id: str):
        """
        Elimina la sesión de un usuario
        Nota: Agent Framework no tiene método explícito para eliminar threads,
        simplemente eliminamos la referencia local
        """
        try:
            if user_id not in self.user_threads:
                return False

            thread_id = self.user_threads[user_id]
            del self.user_threads[user_id]
            logger.info(f"🗑️ Sesión eliminada localmente: {user_id} | Thread: {thread_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error limpiando sesión {user_id}: {e}")
            return False

    def get_stats(self) -> dict:
        """Obtiene estadísticas del sistema"""
        return {
            "agent_id": self.agent_id,
            "active_threads": len(self.user_threads),
            "active_connections": len(self.active_connections),
            "users": list(self.user_threads.keys())
        }


# Crear instancia global del gestor de chat persistente
chat_manager = AgentFrameworkChatManager()


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    environment = os.getenv("ENVIRONMENT", "development")
    return {
        "service": "AI Assistant API (Agent Framework)",
        "version": "1.0.0",
        "status": "online",
        "environment": environment,
        "framework": "agent_framework_azure_ai",
        "endpoints": {
            "websocket": "/ws/chat",
            "health": "/health",
            "stats": "/api/stats",
            "docs": "/docs"
        },
        "active_connections": len(chat_manager.active_connections),
        "persistent_sessions": len(chat_manager.user_threads)
    }


@app.get("/health")
async def health():
    """
    Health check endpoint para Azure Container Apps
    """
    try:
        stats = chat_manager.get_stats()
        return {
            "status": "healthy",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/stats")
async def get_stats():
    """Endpoint para obtener estadísticas detalladas"""
    return chat_manager.get_stats()


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para chat persistente con el asistente de Azure AI

    PROTOCOLO DE COMUNICACIÓN:

    1. Cliente se conecta e inicializa sesión:
    {
        "type": "init",
        "user_id": "usuario_123"
    }

    Respuesta:
    {
        "type": "session_ready",
        "message": "Sesión iniciada/recuperada",
        "thread_id": "thread_abc123" o null,
        "is_new_session": true/false
    }

    2. Cliente envía mensaje:
    {
        "type": "message",
        "message": "Tu pregunta aquí"
    }

    Respuesta:
    {
        "type": "bot_message",
        "message": "Respuesta del asistente...",
        "status": "success"
    }

    3. Cliente solicita limpiar sesión (opcional):
    {
        "type": "clear_session"
    }

    Respuesta:
    {
        "type": "session_cleared",
        "message": "Tu historial ha sido eliminado"
    }
    """

    current_user_id = None

    try:
        # Aceptar la conexión WebSocket primero
        await websocket.accept()

        # Esperar mensaje de inicialización
        data = await websocket.receive_text()

        try:
            init_data = json.loads(data)

            if init_data.get("type") != "init":
                error_response = {
                    "type": "error",
                    "message": "Debes enviar un mensaje 'init' primero con tu user_id"
                }
                await websocket.send_text(json.dumps(error_response))
                await websocket.close()
                return

            user_id = init_data.get("user_id", "anonymous_user")
            current_user_id = user_id

            # Verificar si es una sesión existente
            is_new_session = user_id not in chat_manager.user_threads

            # Conectar y crear/recuperar sesión
            thread_id = await chat_manager.connect(websocket, user_id)

            response = {
                "type": "session_ready",
                "message": "Sesión recuperada. Tu historial está disponible." if not is_new_session else "Nueva sesión creada.",
                "thread_id": thread_id,
                "is_new_session": is_new_session,
                "status": "success"
            }

            await websocket.send_text(json.dumps(response))

        except json.JSONDecodeError:
            error_response = {
                "type": "error",
                "message": "Formato JSON inválido"
            }
            await websocket.send_text(json.dumps(error_response))
            await websocket.close()
            return

        # Loop principal de mensajes
        while True:
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "")

                # Procesar mensaje del usuario
                if message_type == "message":
                    user_message = message_data.get("message", "")

                    if not user_message:
                        response = {
                            "type": "error",
                            "message": "Mensaje vacío"
                        }
                        await websocket.send_text(json.dumps(response))
                        continue

                    # Enviar indicador de procesamiento
                    processing_response = {
                        "type": "processing",
                        "message": "Procesando tu mensaje..."
                    }
                    await websocket.send_text(json.dumps(processing_response))

                    # Obtener respuesta del asistente
                    bot_response = await chat_manager.send_to_assistant(current_user_id, user_message)

                    if bot_response:
                        response = {
                            "type": "bot_message",
                            "message": bot_response,
                            "status": "success"
                        }
                    else:
                        response = {
                            "type": "error",
                            "message": "No se pudo obtener respuesta del asistente",
                            "status": "error"
                        }

                    await websocket.send_text(json.dumps(response))

                # Limpiar sesión del usuario
                elif message_type == "clear_session":
                    success = chat_manager.cleanup_user_session(current_user_id)

                    if success:
                        response = {
                            "type": "session_cleared",
                            "message": "Tu historial de conversación ha sido eliminado permanentemente."
                        }
                    else:
                        response = {
                            "type": "error",
                            "message": "No se pudo limpiar la sesión"
                        }

                    await websocket.send_text(json.dumps(response))

                # Obtener estadísticas
                elif message_type == "get_stats":
                    stats = chat_manager.get_stats()
                    response = {
                        "type": "stats",
                        "data": stats
                    }
                    await websocket.send_text(json.dumps(response))

                # Tipo desconocido
                else:
                    response = {
                        "type": "error",
                        "message": f"Tipo de mensaje desconocido: {message_type}"
                    }
                    await websocket.send_text(json.dumps(response))

            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "message": "Formato JSON inválido"
                }
                await websocket.send_text(json.dumps(error_response))

            except Exception as e:
                error_response = {
                    "type": "error",
                    "message": f"Error procesando mensaje: {str(e)}"
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        logger.info(f"🔌 Cliente desconectado: {current_user_id}")
        if current_user_id:
            chat_manager.disconnect(current_user_id)

    except Exception as e:
        logger.error(f"❌ Error en WebSocket para {current_user_id}: {e}")
        if current_user_id:
            chat_manager.disconnect(current_user_id)


if __name__ == "__main__":
    # Configuración desde variables de entorno
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    environment = os.getenv("ENVIRONMENT", "development")
    reload = environment == "development"

    logger.info("\n" + "="*60)
    logger.info("🚀 AI Assistant - Agent Framework API")
    logger.info("="*60)
    logger.info(f"📍 Environment: {environment}")
    logger.info(f"📍 Host: {host}")
    logger.info(f"📍 Port: {port}")
    logger.info(f"🔌 WebSocket: ws://{host}:{port}/ws/chat")
    logger.info(f"📊 Health: http://{host}:{port}/health")
    logger.info(f"📈 Stats: http://{host}:{port}/api/stats")
    logger.info(f"📚 Docs: http://{host}:{port}/docs")
    logger.info("="*60)
    logger.info("💾 Las conversaciones se mantienen entre sesiones")
    logger.info("🔄 Usa agent_framework_azure_ai (proyectos directos)")
    logger.info("="*60 + "\n")

    uvicorn.run(
        "011_assistant_websocket_agent_framework:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

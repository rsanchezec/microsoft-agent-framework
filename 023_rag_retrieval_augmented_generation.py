"""
023_rag_retrieval_augmented_generation.py

Este script demuestra cómo implementar RAG (Retrieval Augmented Generation)
en el Microsoft Agent Framework.

RAG combina:
1. Retrieval: Buscar información relevante en una base de conocimiento
2. Augmentation: Aumentar el contexto del agente con esa información
3. Generation: Generar respuestas basadas en el contexto aumentado

Casos de Uso:
- Búsqueda en documentación técnica
- Q&A sobre bases de conocimiento corporativas
- Asistentes con información actualizada
- Chat sobre documentos/PDFs
- Búsqueda semántica en catálogos

Estrategias Implementadas:
1. RAG básico con búsqueda por keywords
2. RAG con embeddings y similitud semántica
3. RAG con chunking de documentos
4. RAG con context providers (inyección dinámica)
5. RAG con herramientas/tools personalizadas
"""

import os
from dotenv import load_dotenv
import asyncio
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ContextProvider, Context
from typing import List, Dict, Any, Tuple, Annotated
from pydantic import Field
import re
from dataclasses import dataclass

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_MODEL = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

print("=" * 80)
print("RAG - RETRIEVAL AUGMENTED GENERATION")
print("=" * 80)


# =============================================================================
# EJEMPLO 1: Base de Conocimiento Simple (In-Memory)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 1: Base de Conocimiento Simple")
print("=" * 80)

# Base de conocimiento de ejemplo sobre el framework
KNOWLEDGE_BASE = [
    {
        "id": 1,
        "title": "¿Qué es Azure AI Foundry?",
        "content": """Azure AI Foundry es una plataforma de Microsoft Azure para
        construir, entrenar y desplegar agentes de IA. Proporciona herramientas
        para gestionar agentes, conversaciones persistentes y herramientas personalizadas."""
    },
    {
        "id": 2,
        "title": "Threads y Conversaciones",
        "content": """Un Thread representa una conversación persistente en Azure AI Foundry.
        Cada thread tiene un thread_id único que permite mantener el contexto entre
        múltiples interacciones. Los threads se pueden crear explícitamente con
        agent.get_new_thread() o implícitamente en la primera llamada a agent.run()."""
    },
    {
        "id": 3,
        "title": "Agent ID y Persistencia",
        "content": """El Agent ID (formato asst_xxx) identifica un agente en Azure.
        Para que un agente persista después de cerrar el cliente, usa
        should_cleanup_agent=False. El Agent ID se obtiene con agent.chat_client.agent_id
        después de la primera ejecución."""
    },
    {
        "id": 4,
        "title": "Workflows y Orquestación",
        "content": """El framework soporta workflows para orquestar múltiples agentes.
        Tipos de workflows: Secuencial (A → B → C), Paralelo (fan-out/fan-in),
        Condicional (if/else routing), y Group Chat (múltiples agentes en debate).
        Se usa WorkflowBuilder para construir workflows."""
    },
    {
        "id": 5,
        "title": "Context Providers",
        "content": """Los Context Providers inyectan contexto dinámico antes de cada
        invocación del agente. Implementan los métodos invoking() (antes) y
        invoked() (después). Son útiles para inyectar fecha/hora, información del
        usuario, reglas de negocio, etc. sin modificar las instrucciones base."""
    },
    {
        "id": 6,
        "title": "Middleware",
        "content": """El Middleware intercepta y modifica el comportamiento de los agentes.
        Tipos: Agent Middleware (runs completos), Function Middleware (llamadas a tools),
        Chat Middleware (mensajes). Se usa para logging, validación, caching,
        autenticación, etc."""
    }
]


# =============================================================================
# EJEMPLO 2: Búsqueda por Keywords (Simple)
# =============================================================================
def search_by_keywords(query: str, documents: List[Dict], top_k: int = 2) -> List[Dict]:
    """
    Búsqueda simple por keywords en documentos.

    Args:
        query: Consulta del usuario
        documents: Lista de documentos
        top_k: Número de resultados a retornar

    Returns:
        Lista de documentos más relevantes
    """
    query_lower = query.lower()
    query_terms = set(re.findall(r'\w+', query_lower))

    # Calcular score para cada documento
    scores = []
    for doc in documents:
        text = f"{doc['title']} {doc['content']}".lower()
        text_terms = set(re.findall(r'\w+', text))

        # Score = número de términos en común
        common_terms = query_terms & text_terms
        score = len(common_terms)

        scores.append((score, doc))

    # Ordenar por score y retornar top_k
    scores.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scores[:top_k]]


print("\n[BUSQUEDA] Búsqueda Simple por Keywords:")
query = "¿Cómo funciona el thread en conversaciones?"
results = search_by_keywords(query, KNOWLEDGE_BASE, top_k=2)

print(f"\nQuery: {query}")
print(f"Resultados encontrados: {len(results)}\n")

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc['title']}")
    print(f"   {doc['content'][:100]}...\n")


# =============================================================================
# EJEMPLO 3: Embeddings y Similitud Semántica (Simulado)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 3: Embeddings y Similitud Semántica")
print("=" * 80)

def simple_embedding(text: str) -> List[float]:
    """
    Simulación de embeddings. En producción, usar Azure OpenAI Embeddings API.

    Esta implementación simple usa características básicas del texto:
    - Longitud del texto
    - Número de palabras clave
    - Frecuencia de términos

    En producción, reemplazar con:
        from openai import AzureOpenAI
        client = AzureOpenAI(...)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    """
    # Features simples (en producción usar embeddings reales)
    text_lower = text.lower()
    length = len(text)
    word_count = len(text.split())

    # Contar presencia de términos clave
    features = [
        length / 1000,  # Normalizado
        word_count / 100,  # Normalizado
        text_lower.count('agent') / 10,
        text_lower.count('thread') / 10,
        text_lower.count('workflow') / 10,
        text_lower.count('context') / 10,
    ]

    return features


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calcular similitud coseno entre dos vectores."""
    import math

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def search_by_embeddings(query: str, documents: List[Dict], top_k: int = 2) -> List[Tuple[float, Dict]]:
    """
    Búsqueda semántica usando embeddings.

    Args:
        query: Consulta del usuario
        documents: Lista de documentos
        top_k: Número de resultados a retornar

    Returns:
        Lista de tuplas (score, documento) ordenadas por relevancia
    """
    query_embedding = simple_embedding(query)

    # Calcular embeddings de documentos y similitud
    scores = []
    for doc in documents:
        doc_text = f"{doc['title']} {doc['content']}"
        doc_embedding = simple_embedding(doc_text)

        similarity = cosine_similarity(query_embedding, doc_embedding)
        scores.append((similarity, doc))

    # Ordenar por similitud
    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]


print("\n[BUSQUEDA SEMANTICA] Búsqueda Semántica con Embeddings (Simulados):")
query = "Explicar persistencia de agentes"
results = search_by_embeddings(query, KNOWLEDGE_BASE, top_k=2)

print(f"\nQuery: {query}")
print(f"Resultados encontrados: {len(results)}\n")

for i, (score, doc) in enumerate(results, 1):
    print(f"{i}. {doc['title']} (Score: {score:.3f})")
    print(f"   {doc['content'][:100]}...\n")


# =============================================================================
# EJEMPLO 4: Chunking de Documentos Largos
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 4: Chunking de Documentos Largos")
print("=" * 80)

@dataclass
class DocumentChunk:
    """Representa un fragmento de un documento."""
    chunk_id: str
    document_id: int
    title: str
    content: str
    start_pos: int
    end_pos: int


def chunk_document(doc: Dict, chunk_size: int = 200, overlap: int = 50) -> List[DocumentChunk]:
    """
    Divide un documento en chunks con overlap.

    Args:
        doc: Documento a dividir
        chunk_size: Tamaño de cada chunk en caracteres
        overlap: Overlap entre chunks consecutivos

    Returns:
        Lista de chunks del documento
    """
    content = doc['content']
    chunks = []
    start = 0
    chunk_num = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))

        # Intentar cortar en un espacio para no partir palabras
        if end < len(content):
            last_space = content.rfind(' ', start, end)
            if last_space > start:
                end = last_space

        chunk = DocumentChunk(
            chunk_id=f"{doc['id']}_chunk_{chunk_num}",
            document_id=doc['id'],
            title=doc['title'],
            content=content[start:end].strip(),
            start_pos=start,
            end_pos=end
        )

        chunks.append(chunk)
        chunk_num += 1
        start = end - overlap  # Overlap

    return chunks


# Crear chunks de todos los documentos
print("\n[CHUNKING] Creando chunks de documentos:")
all_chunks = []
for doc in KNOWLEDGE_BASE:
    chunks = chunk_document(doc, chunk_size=150, overlap=30)
    all_chunks.extend(chunks)
    print(f"- {doc['title']}: {len(chunks)} chunks")

print(f"\nTotal de chunks: {len(all_chunks)}")


# =============================================================================
# EJEMPLO 5: RAG Context Provider (Inyección Automática)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 5: RAG Context Provider")
print("=" * 80)

class RAGContextProvider(ContextProvider):
    """
    Context Provider que implementa RAG.

    Busca automáticamente información relevante en la base de conocimiento
    y la inyecta como contexto antes de cada invocación del agente.
    """

    def __init__(self, documents: List[Dict], top_k: int = 2):
        """
        Args:
            documents: Base de conocimiento
            top_k: Número de documentos a recuperar
        """
        self.documents = documents
        self.top_k = top_k

    async def invoking(self, messages: List[Dict[str, Any]], **kwargs) -> Context:
        """
        Llamado ANTES de cada invocación del agente.

        Busca información relevante y la inyecta como contexto.
        """
        # Extraer la última pregunta del usuario
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return Context(instructions="", messages=[], tools=[])

        last_query = user_messages[-1].get("content", "")

        # Buscar documentos relevantes
        results = search_by_keywords(last_query, self.documents, self.top_k)

        # Construir contexto RAG
        if results:
            rag_context = "Información relevante de la base de conocimiento:\n\n"
            for i, doc in enumerate(results, 1):
                rag_context += f"[Documento {i}] {doc['title']}\n"
                rag_context += f"{doc['content']}\n\n"

            rag_context += "Usa esta información para responder la pregunta del usuario."

            print(f"\n[RAG] Se encontraron {len(results)} documentos relevantes")
        else:
            rag_context = ""

        return Context(
            instructions=rag_context,
            messages=[],
            tools=[]
        )

    async def invoked(self, messages: List[Dict[str, Any]], **kwargs) -> None:
        """Llamado DESPUÉS de cada invocación (opcional)."""
        pass


# =============================================================================
# EJEMPLO 6: RAG Tool (Herramienta de Búsqueda)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 6: RAG como Tool/Herramienta")
print("=" * 80)

def create_rag_search_tool(documents: List[Dict]):
    """
    Crea una herramienta de búsqueda RAG que el agente puede invocar.

    A diferencia del Context Provider (que se ejecuta automáticamente),
    esta herramienta solo se usa cuando el agente decide que necesita
    buscar información específica.
    """

    def search_knowledge_base(
        query: Annotated[str, Field(description="Consulta de búsqueda en la base de conocimiento")],
        max_results: Annotated[int, Field(description="Número máximo de resultados")] = 2
    ) -> str:
        """Busca información en la base de conocimiento."""
        results = search_by_keywords(query, documents, top_k=max_results)

        if not results:
            return "No se encontró información relevante."

        output = f"Encontré {len(results)} documento(s) relevante(s):\n\n"
        for i, doc in enumerate(results, 1):
            output += f"[{i}] {doc['title']}\n"
            output += f"{doc['content']}\n\n"

        return output

    return search_knowledge_base


# =============================================================================
# EJEMPLO 7: Agente con RAG Context Provider
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 7: Agente con RAG Context Provider (Automático)")
print("=" * 80)


async def example_agent_with_rag_provider():
    """
    Demuestra un agente que usa RAG Context Provider.

    El provider busca automáticamente información relevante antes de
    cada invocación y la inyecta como contexto.
    """
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:
            # Crear RAG Context Provider
            rag_provider = RAGContextProvider(
                documents=KNOWLEDGE_BASE,
                top_k=2
            )

            # Crear agente con RAG provider
            agent = client.create_agent(
                name="RAG Assistant",
                instructions="""Eres un asistente experto en el Microsoft Agent Framework.
                Responde preguntas basándote en la información proporcionada en el contexto.
                Si la información está en el contexto, úsala. Si no, indica que no tienes
                esa información específica.""",
                context_providers=[rag_provider]  # ← RAG automático
            )

            # Test 1: Pregunta sobre threads
            print("\n[TEST 1] Pregunta sobre threads")
            query1 = "¿Qué es un thread y para qué sirve?"
            print(f"Usuario: {query1}")

            response1 = await agent.run(query1)
            print(f"Agente: {response1}\n")

            # Test 2: Pregunta sobre workflows
            print("\n[TEST 2] Pregunta sobre workflows")
            query2 = "¿Qué tipos de workflows existen?"
            print(f"Usuario: {query2}")

            response2 = await agent.run(query2)
            print(f"Agente: {response2}\n")


# =============================================================================
# EJEMPLO 8: Agente con RAG Tool (Búsqueda Manual)
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 8: Agente con RAG Tool (Búsqueda Manual)")
print("=" * 80)


async def example_agent_with_rag_tool():
    """
    Demuestra un agente que usa RAG como herramienta.

    El agente decide cuándo buscar información usando la herramienta.
    """
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(
            async_credential=credential,
            should_cleanup_agent=True
        ) as client:
            # Crear herramienta RAG
            search_tool = create_rag_search_tool(KNOWLEDGE_BASE)

            # Crear agente con RAG tool
            agent = client.create_agent(
                name="RAG Tool Assistant",
                instructions="""Eres un asistente experto en el Microsoft Agent Framework.
                Cuando necesites información específica, usa la herramienta search_knowledge_base
                para buscar en la base de conocimiento. Responde basándote en la información
                encontrada.""",
                tools=[search_tool]  # ← RAG como herramienta
            )

            # Test 1: Pregunta que requiere búsqueda
            print("\n[TEST 1] Pregunta sobre Agent ID")
            query1 = "¿Cómo obtener el Agent ID y hacerlo persistente?"
            print(f"Usuario: {query1}")

            response1 = await agent.run(query1)
            print(f"Agente: {response1}\n")

            # Test 2: Pregunta general
            print("\n[TEST 2] Pregunta general")
            query2 = "Dame un resumen de lo que puedes hacer"
            print(f"Usuario: {query2}")

            response2 = await agent.run(query2)
            print(f"Agente: {response2}\n")


# =============================================================================
# EJEMPLO 9: Comparación de Estrategias RAG
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 9: Comparación de Estrategias RAG")
print("=" * 80)

print("""
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPARACIÓN DE ESTRATEGIAS RAG                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ 1. RAG Context Provider (Automático)                                     │
│    ✅ Ventajas:                                                          │
│       - Inyección automática antes de cada invocación                   │
│       - El agente siempre tiene contexto relevante                       │
│       - Transparente para el agente                                      │
│    ⚠️  Consideraciones:                                                  │
│       - Siempre busca, incluso si no es necesario                        │
│       - Puede agregar latencia                                           │
│       - Mayor uso de tokens                                              │
│                                                                           │
│ 2. RAG Tool (Manual)                                                     │
│    ✅ Ventajas:                                                          │
│       - El agente decide cuándo buscar                                   │
│       - Más eficiente (solo busca cuando necesita)                       │
│       - Menor latencia en casos simples                                  │
│    ⚠️  Consideraciones:                                                  │
│       - Depende de que el agente use la herramienta correctamente        │
│       - Requiere instrucciones claras                                    │
│                                                                           │
│ 3. Búsqueda por Keywords                                                 │
│    ✅ Ventajas:                                                          │
│       - Rápida y simple                                                  │
│       - No requiere embeddings                                           │
│       - Funciona bien para búsquedas exactas                             │
│    ⚠️  Consideraciones:                                                  │
│       - No captura similitud semántica                                   │
│       - Sensible a sinónimos y variaciones                               │
│                                                                           │
│ 4. Búsqueda Semántica (Embeddings)                                       │
│    ✅ Ventajas:                                                          │
│       - Captura significado semántico                                    │
│       - Funciona con sinónimos y paráfrasis                              │
│       - Mejor para búsquedas complejas                                   │
│    ⚠️  Consideraciones:                                                  │
│       - Requiere API de embeddings                                       │
│       - Mayor costo computacional                                        │
│       - Necesita índice vectorial en producción                          │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
""")


# =============================================================================
# EJEMPLO 10: Mejores Prácticas y Recomendaciones
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 10: Mejores Prácticas RAG en Producción")
print("=" * 80)

print("""
📋 MEJORES PRÁCTICAS PARA RAG EN PRODUCCIÓN:

1. 🗄️ ALMACENAMIENTO DE VECTORES
   - Usar Azure AI Search con búsqueda vectorial
   - Alternativas: Pinecone, Weaviate, Qdrant, FAISS
   - Indexar documentos con embeddings de Azure OpenAI

   Ejemplo de Azure AI Search:
   ```python
   from azure.search.documents import SearchClient
   from azure.search.documents.indexes.models import (
       SearchIndex, VectorSearch, HnswAlgorithmConfiguration
   )

   # Crear índice con búsqueda vectorial
   index = SearchIndex(
       name="knowledge-base",
       fields=[...],
       vector_search=VectorSearch(
           algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")]
       )
   )
   ```

2. 📊 EMBEDDINGS
   - Usar Azure OpenAI text-embedding-3-small o text-embedding-3-large
   - Cachear embeddings de documentos (no recalcular en cada búsqueda)
   - Normalizar vectores para consistencia

   Ejemplo con Azure OpenAI:
   ```python
   from openai import AzureOpenAI

   client = AzureOpenAI(...)
   response = client.embeddings.create(
       input="tu texto aquí",
       model="text-embedding-3-small"
   )
   embedding = response.data[0].embedding
   ```

3. 📄 CHUNKING STRATEGIES
   - Chunk size: 200-500 tokens para texto general
   - Overlap: 10-20% del chunk size
   - Respetar límites semánticos (párrafos, secciones)
   - Incluir metadata (título, fuente, fecha)

   Estrategias avanzadas:
   - Sentence splitting (NLTK, spaCy)
   - Recursive character splitting
   - Semantic chunking (basado en coherencia)

4. 🔍 RETRIEVAL STRATEGIES
   - Hybrid search: Combinar búsqueda vectorial + keywords
   - Re-ranking: Usar modelo de re-ranking después de búsqueda inicial
   - Multi-query: Generar múltiples variaciones de la query
   - Metadata filtering: Filtrar por fecha, categoría, etc.

5. 🎯 RELEVANCE TUNING
   - Experimentar con top_k (típicamente 3-5 documentos)
   - Umbral de similitud (e.g., score > 0.7)
   - A/B testing de diferentes estrategias
   - Feedback loop: Aprender de queries sin buenos resultados

6. ⚡ OPTIMIZACIÓN
   - Cachear resultados de búsquedas frecuentes
   - Batch processing de embeddings
   - Asynchronous retrieval
   - Lazy loading de documentos grandes

7. 📈 MONITOREO
   - Track query latency
   - Monitor retrieval quality (precision, recall)
   - Log queries sin buenos resultados
   - Métricas de satisfacción del usuario

8. 🔒 SEGURIDAD Y PRIVACIDAD
   - Filtrar contenido sensible antes de indexar
   - Row-level security en índices
   - Auditoría de accesos
   - Cumplimiento con GDPR/regulaciones

9. 💡 CUANDO USAR RAG vs FINE-TUNING

   Usar RAG cuando:
   ✅ Información actualizada frecuentemente
   ✅ Base de conocimiento grande (> 100K documentos)
   ✅ Necesitas citar fuentes
   ✅ Información factual específica

   Usar Fine-Tuning cuando:
   ✅ Cambiar estilo/tono del modelo
   ✅ Enseñar formato de salida específico
   ✅ Mejorar performance en tarea específica
   ✅ Información estática que cabe en contexto

10. 🌐 ARQUITECTURA DE REFERENCIA

    Production RAG Pipeline:

    User Query
        ↓
    Query Preprocessing (expansión, corrección)
        ↓
    Embedding Generation (Azure OpenAI)
        ↓
    Hybrid Search (Azure AI Search)
        ↓
    Re-ranking & Filtering
        ↓
    Context Injection (Top-K docs)
        ↓
    LLM Generation (Azure OpenAI GPT-4)
        ↓
    Post-processing & Citation
        ↓
    Response to User
""")


# =============================================================================
# EJEMPLO 11: Template de Producción
# =============================================================================
print("\n" + "=" * 80)
print("EJEMPLO 11: Template para RAG en Producción")
print("=" * 80)

print("""
💼 TEMPLATE DE CÓDIGO PARA PRODUCCIÓN:

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from agent_framework import ContextProvider, Context
from typing import List, Dict, Any

class ProductionRAGProvider(ContextProvider):
    '''RAG Provider con Azure AI Search y Azure OpenAI Embeddings'''

    def __init__(
        self,
        search_endpoint: str,
        search_key: str,
        index_name: str,
        openai_client: AzureOpenAI,
        embedding_model: str = "text-embedding-3-small",
        top_k: int = 3,
        score_threshold: float = 0.7
    ):
        # Azure AI Search client
        self.search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key)
        )

        # OpenAI client para embeddings
        self.openai_client = openai_client
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.score_threshold = score_threshold

    def _get_embedding(self, text: str) -> List[float]:
        '''Genera embedding usando Azure OpenAI'''
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def _search(self, query: str) -> List[Dict[str, Any]]:
        '''Búsqueda híbrida en Azure AI Search'''
        query_vector = self._get_embedding(query)

        # Búsqueda híbrida (vectorial + texto)
        results = self.search_client.search(
            search_text=query,
            vector_queries=[{
                "vector": query_vector,
                "k_nearest_neighbors": self.top_k,
                "fields": "contentVector"
            }],
            select=["id", "title", "content", "metadata"],
            top=self.top_k
        )

        # Filtrar por score
        docs = []
        for result in results:
            if result['@search.score'] >= self.score_threshold:
                docs.append({
                    'title': result['title'],
                    'content': result['content'],
                    'score': result['@search.score'],
                    'metadata': result.get('metadata', {})
                })

        return docs

    async def invoking(self, messages: List[Dict[str, Any]], **kwargs) -> Context:
        '''Inyecta contexto RAG antes de cada invocación'''
        # Extraer última pregunta
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return Context(instructions="", messages=[], tools=[])

        query = user_messages[-1].get("content", "")

        # Buscar documentos relevantes
        docs = self._search(query)

        if not docs:
            return Context(instructions="", messages=[], tools=[])

        # Construir contexto
        context_text = "Información relevante:\\n\\n"
        for i, doc in enumerate(docs, 1):
            context_text += f"[Fuente {i}] {doc['title']}\\n"
            context_text += f"{doc['content']}\\n"
            context_text += f"(Relevancia: {doc['score']:.2f})\\n\\n"

        context_text += "Responde basándote en esta información y cita las fuentes."

        return Context(
            instructions=context_text,
            messages=[],
            tools=[]
        )

# Uso:
rag_provider = ProductionRAGProvider(
    search_endpoint="https://your-search.search.windows.net",
    search_key="your-key",
    index_name="knowledge-base",
    openai_client=openai_client,
    top_k=3
)

agent = client.create_agent(
    name="Production RAG Assistant",
    instructions="...",
    context_providers=[rag_provider]
)
```
""")


# =============================================================================
# MAIN - Ejecutar Ejemplos
# =============================================================================
async def main():
    """Ejecuta los ejemplos de RAG con agentes."""

    print("\n" + "=" * 80)
    print("EJECUTANDO EJEMPLOS CON AGENTES")
    print("=" * 80)

    # Ejemplo 7: RAG Context Provider
    await example_agent_with_rag_provider()

    # Ejemplo 8: RAG Tool
    await example_agent_with_rag_tool()

    print("\n" + "=" * 80)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 80)

    print("""

📚 RECURSOS ADICIONALES:

- Azure AI Search: https://learn.microsoft.com/azure/search/
- Azure OpenAI Embeddings: https://learn.microsoft.com/azure/ai-services/openai/
- LangChain RAG: https://python.langchain.com/docs/use_cases/question_answering/
- Semantic Kernel: https://learn.microsoft.com/semantic-kernel/

💡 PRÓXIMOS PASOS:

1. Implementar índice en Azure AI Search
2. Integrar Azure OpenAI Embeddings
3. Experimentar con chunking strategies
4. Implementar re-ranking
5. Agregar telemetría y monitoreo
6. A/B testing de estrategias de retrieval
    """)


if __name__ == "__main__":
    # Los ejemplos 7 y 8 requieren conexión a Azure AI
    # Descomentar la siguiente línea para ejecutar ejemplos con agentes reales
    # asyncio.run(main())

    print("\n" + "=" * 80)
    print("EJEMPLOS INFORMATIVOS COMPLETADOS")
    print("=" * 80)
    print("""
Los ejemplos 1-6 demuestran los conceptos de RAG sin conexión a Azure.

Para ejecutar los ejemplos 7-8 con agentes reales:
1. Asegúrate de tener configurado Azure AI Foundry
2. Descomenta la línea 'asyncio.run(main())' en este archivo
3. Vuelve a ejecutar el script

Recursos adicionales:
- Azure AI Search: https://learn.microsoft.com/azure/search/
- Azure OpenAI Embeddings: https://learn.microsoft.com/azure/ai-services/openai/
- LangChain RAG: https://python.langchain.com/docs/use_cases/question_answering/

Próximos pasos:
1. Implementar índice en Azure AI Search
2. Integrar Azure OpenAI Embeddings
3. Experimentar con chunking strategies
4. Implementar re-ranking
5. Agregar telemetría y monitoreo
    """)
    print("=" * 80)

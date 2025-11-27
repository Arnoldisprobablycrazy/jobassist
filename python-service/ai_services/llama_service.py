"""
Main LlamaIndex service for JobAssist AI functionality.
Orchestrates LLM, embeddings, and vector database operations.
"""
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, ServiceContext, Document, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobAssistAI:
    """
    Main AI service class that coordinates all AI operations for JobAssist.
    """
    
    def __init__(self):
        """Initialize the AI service with LLM, embeddings, and vector store."""
        self._setup_services()
        self._setup_vector_stores()
        
    def _setup_services(self):
        """Setup LLM and embedding services."""
        try:
            # Initialize Groq LLM with temperature for variation
            # Using llama-3.1-8b-instant (replaces deprecated llama3-8b-8192)
            self.llm = Groq(
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.8,  # Higher temperature for more creative/varied output
                max_tokens=2048
            )
            
            # Initialize Cohere embeddings
            self.embed_model = CohereEmbedding(
                model_name=os.getenv("COHERE_MODEL", "embed-english-v3.0"),
                api_key=os.getenv("COHERE_API_KEY")
            )
            
            # Configure global settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            
            logger.info("AI services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            raise
    
    def _setup_vector_stores(self):
        """Setup Qdrant vector database connections."""
        try:
            # Initialize Qdrant client (Cloud or Self-hosted)
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if qdrant_url and qdrant_api_key:
                # Use Qdrant Cloud
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                )
                logger.info("Connected to Qdrant Cloud")
            else:
                # Fallback to local Qdrant (if running locally)
                self.qdrant_client = QdrantClient(
                    host=os.getenv("QDRANT_HOST", "localhost"),
                    port=int(os.getenv("QDRANT_PORT", 6333)),
                )
                logger.info("Connected to local Qdrant instance")
            
            # Collection configurations
            self.collections = {
                "resumes": "resumes_collection",
                "jobs": "jobs_collection", 
                "cover_letters": "cover_letters_collection",
                "skills": "skills_collection"
            }
            
            # Create collections if they don't exist
            self._create_collections()
            
            logger.info("Vector stores initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector stores: {e}")
            raise
    
    def _create_collections(self):
        """Create Qdrant collections if they don't exist."""
        vector_size = int(os.getenv("QDRANT_COLLECTION_SIZE", 1024))
        
        for collection_name in self.collections.values():
            try:
                # Check if collection exists
                collections = self.qdrant_client.get_collections()
                existing_names = [col.name for col in collections.collections]
                
                if collection_name not in existing_names:
                    self.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=vector_size,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    
            except Exception as e:
                logger.error(f"Error creating collection {collection_name}: {e}")
    
    def get_vector_store(self, collection_name: str) -> QdrantVectorStore:
        """Get a vector store for a specific collection."""
        if collection_name not in self.collections:
            raise ValueError(f"Unknown collection: {collection_name}")
            
        return QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collections[collection_name]
        )
    
    def create_index_from_documents(self, documents: List[Document], collection_name: str) -> VectorStoreIndex:
        """Create a vector index from documents."""
        vector_store = self.get_vector_store(collection_name)
        
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store
        )
        
        return index
    
    def get_query_engine(self, collection_name: str, similarity_top_k: int = 5):
        """Get a query engine for a specific collection."""
        vector_store = self.get_vector_store(collection_name)
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        return index.as_query_engine(
            similarity_top_k=similarity_top_k,
            response_mode="compact"
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all AI services."""
        status = {
            "llm_status": False,
            "embedding_status": False,
            "vector_db_status": False,
            "collections": {}
        }
        
        try:
            # Check LLM
            test_response = self.llm.complete("Hello")
            status["llm_status"] = True if test_response else False
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
        
        try:
            # Check embeddings
            test_embedding = self.embed_model.get_text_embedding("test")
            status["embedding_status"] = True if test_embedding else False
        except Exception as e:
            logger.error(f"Embedding health check failed: {e}")
        
        try:
            # Check vector database
            collections = self.qdrant_client.get_collections()
            status["vector_db_status"] = True
            for collection in collections.collections:
                info = self.qdrant_client.get_collection(collection.name)
                status["collections"][collection.name] = {
                    "points_count": info.points_count,
                    "status": info.status
                }
        except Exception as e:
            logger.error(f"Vector DB health check failed: {e}")
        
        return status

# Global instance
ai_service = None

def get_ai_service() -> JobAssistAI:
    """Get the global AI service instance."""
    global ai_service
    if ai_service is None:
        ai_service = JobAssistAI()
    return ai_service
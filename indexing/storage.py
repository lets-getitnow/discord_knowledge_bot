"""
ChromaDB storage module for Discord Knowledge Bot.
Handles vector database operations and document storage using LlamaIndex.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from utils.config import config
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

logger = logging.getLogger(__name__)

class ChromaStorage:
    """ChromaDB storage manager for Discord content using LlamaIndex."""
    
    def __init__(self, persist_directory: str = "./data", collection_name: str = "discord_knowledge"):
        """Initialize ChromaDB storage with LlamaIndex."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.vector_store = None
        self.embed_model = None
        self.index = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and LlamaIndex components."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Initialize local embedding model
            self.embed_model = HuggingFaceEmbedding(
                model_name=config['embeddings']['model_name']
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Discord server knowledge base"}
            )
            
            # Create LlamaIndex ChromaVectorStore
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Try to load existing index, otherwise create empty one
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    embed_model=self.embed_model
                )
            except:
                # Create empty index if none exists
                self.index = VectorStoreIndex(
                    nodes=[],
                    storage_context=storage_context,
                    embed_model=self.embed_model
                )
            
            logger.info(f"ChromaDB initialized with local embeddings ({config['embeddings']['model_name']}) and collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the collection using LlamaIndex."""
        try:
            # Create LlamaIndex Document objects
            llama_docs = []
            for i, doc_text in enumerate(documents):
                llama_doc = Document(
                    text=doc_text,
                    metadata=metadatas[i] if i < len(metadatas) else {},
                    doc_id=ids[i] if i < len(ids) else None
                )
                llama_docs.append(llama_doc)
            
            # Add documents to the index
            for doc in llama_docs:
                self.index.insert(doc)
            
            logger.info(f"Added {len(documents)} documents to collection with local embeddings")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using local embeddings."""
        try:
            # Use LlamaIndex retriever for semantic search
            retriever = self.index.as_retriever(similarity_top_k=n_results)
            nodes = retriever.retrieve(query)
            
            # Format results to match expected interface
            formatted_results = []
            for node in nodes:
                formatted_results.append({
                    'document': node.text,
                    'metadata': node.metadata,
                    'distance': 1 - node.score if node.score else 0,  # Convert score to distance
                    'score': node.score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            # Delete and recreate collection
            self.client.delete_collection(self.collection_name)
            
            # Recreate collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Discord server knowledge base"}
            )
            
            # Recreate LlamaIndex components
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Create new empty index
            self.index = VectorStoreIndex(
                nodes=[],
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise 
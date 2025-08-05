"""
ChromaDB storage module for Discord Knowledge Bot.
Handles vector database operations and document storage.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import logging
from utils.config import config

logger = logging.getLogger(__name__)

class ChromaStorage:
    """ChromaDB storage manager for Discord content."""
    
    def __init__(self, persist_directory: str = "./data", collection_name: str = "discord_knowledge"):
        """Initialize ChromaDB storage."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create OpenAI embedding function
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=config['openai']['api_key'],
                model_name=config['openai']['embedding_model']
            )
            
            # Get or create collection with OpenAI embeddings
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=openai_ef,
                metadata={"description": "Discord server knowledge base"}
            )
            
            logger.info(f"ChromaDB initialized with OpenAI embeddings and collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the collection."""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to collection with OpenAI embeddings")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using OpenAI embeddings."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = {}
                    if results['metadatas'] and results['metadatas'][0] and i < len(results['metadatas'][0]):
                        metadata = results['metadatas'][0][i]
                    
                    distance = 0
                    if results['distances'] and results['distances'][0] and i < len(results['distances'][0]):
                        distance = results['distances'][0][i]
                    
                    formatted_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'distance': distance
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
            self.client.delete_collection(self.collection_name)
            
            # Create OpenAI embedding function
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=config['openai']['api_key'],
                model_name=config['openai']['embedding_model']
            )
            
            # Recreate collection with OpenAI embeddings
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=openai_ef,
                metadata={"description": "Discord server knowledge base"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise 
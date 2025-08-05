"""
Data processing module for Discord Knowledge Bot.
MVP text processing functionality.
"""

import openai
from typing import List, Dict, Any
import logging
from utils.helpers import clean_text, chunk_text, format_message_metadata
from utils.config import config

logger = logging.getLogger(__name__)

class TextProcessor:
    """MVP text processor for Discord messages."""
    
    def __init__(self):
        """Initialize the text processor."""
        self.openai_client = openai.OpenAI(api_key=config['openai']['api_key'])
        self.embedding_model = config['openai']['embedding_model']
        self.chunk_size = config['indexing']['chunk_size']
    
    def process_message(self, message) -> List[Dict[str, Any]]:
        """Process a single Discord message into indexed documents."""
        # Extract and clean text
        text = clean_text(message.content)
        if not text:
            return []
        
        # Get metadata
        metadata = format_message_metadata(message)
        
        # Chunk text if needed
        chunks = chunk_text(text, self.chunk_size)
        
        # Create documents for each chunk
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                doc_id = f"{metadata['message_id']}_chunk_{i}"
                doc_metadata = metadata.copy()
                doc_metadata['chunk_index'] = i
                doc_metadata['total_chunks'] = len(chunks)
                
                documents.append({
                    'id': doc_id,
                    'text': chunk,
                    'metadata': doc_metadata
                })
        
        return documents
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def process_messages_batch(self, messages: List) -> List[Dict[str, Any]]:
        """Process a batch of messages."""
        all_documents = []
        
        for message in messages:
            documents = self.process_message(message)
            all_documents.extend(documents)
        
        return all_documents 
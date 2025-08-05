"""
AI interface module for Discord Knowledge Bot.
Handles OpenAI chat interactions and context building.
"""

import openai
from typing import List, Dict, Any, Optional
import logging
from utils.config import config

logger = logging.getLogger(__name__)

class AIInterface:
    """OpenAI chat interface for Discord Knowledge Bot."""
    
    def __init__(self):
        """Initialize the AI interface."""
        self.openai_client = openai.OpenAI(api_key=config['openai']['api_key'])
        self.model = config['openai']['model']
        self.max_tokens = config['openai']['max_tokens']
        self.temperature = config['openai']['temperature']
    
    def build_context_prompt(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """Build a context-aware prompt for the AI."""
        if not relevant_docs:
            return f"User question: {query}\n\nPlease answer based on your general knowledge."
        
        # Build context from relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs[:3]):  # Limit to top 3 results
            metadata = doc.get('metadata', {})
            author = metadata.get('author_name', 'Unknown')
            channel = metadata.get('channel_name', 'Unknown')
            timestamp = metadata.get('timestamp', 'Unknown')
            
            context_parts.append(f"Message {i+1} (from {author} in #{channel} at {timestamp}):\n{doc['document']}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a helpful AI assistant with access to Discord server content. 
Use the following context from the server to answer the user's question. 
If the context doesn't contain relevant information, use your general knowledge.

Context from Discord server:
{context}

User question: {query}

Please provide a helpful and accurate response based on the context above."""
        
        return prompt
    
    async def get_response(self, query: str, relevant_docs: List[Dict[str, Any]] = None) -> str:
        """Get AI response for a user query."""
        try:
            # Build context-aware prompt
            prompt = self.build_context_prompt(query, relevant_docs or [])
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that answers questions based on Discord server content and general knowledge."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        if not results:
            return "No relevant content found in the server."
        
        formatted_results = []
        for i, result in enumerate(results[:3]):  # Limit to top 3
            metadata = result.get('metadata', {})
            author = metadata.get('author_name', 'Unknown')
            channel = metadata.get('channel_name', 'Unknown')
            timestamp = metadata.get('timestamp', 'Unknown')
            
            # Truncate document content for display
            content = result.get('document', '')[:200] + "..." if len(result.get('document', '')) > 200 else result.get('document', '')
            
            formatted_results.append(f"**{i+1}. From {author} in #{channel} ({timestamp})**\n{content}")
        
        return "\n\n".join(formatted_results) 
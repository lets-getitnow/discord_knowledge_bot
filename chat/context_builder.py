"""
Context builder module for Discord Knowledge Bot.
Manages conversation context and search integration.
"""

from typing import List, Dict, Any, Optional
import logging
from indexing.storage import ChromaStorage

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Builds context for AI conversations using indexed content."""
    
    def __init__(self, storage: ChromaStorage):
        """Initialize the context builder."""
        self.storage = storage
    
    def search_relevant_content(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant content based on user query."""
        try:
            results = self.storage.search(query, n_results)
            logger.info(f"Found {len(results)} relevant documents for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search for relevant content: {e}")
            return []
    
    def build_conversation_context(self, query: str, include_search_results: bool = True) -> Dict[str, Any]:
        """Build context for AI conversation."""
        context = {
            'query': query,
            'relevant_docs': [],
            'search_performed': False
        }
        
        if include_search_results:
            try:
                relevant_docs = self.search_relevant_content(query)
                context['relevant_docs'] = relevant_docs
                context['search_performed'] = True
                logger.info(f"Built context with {len(relevant_docs)} relevant documents")
            except Exception as e:
                logger.error(f"Failed to build conversation context: {e}")
        
        return context
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Get a summary of the conversation context."""
        if not context.get('relevant_docs'):
            return "No relevant server content found for this query."
        
        doc_count = len(context['relevant_docs'])
        return f"Found {doc_count} relevant messages from the server to help answer your question."
    
    def should_use_server_context(self, query: str) -> bool:
        """Determine if the query should use server context."""
        # Simple heuristic - if query mentions server-specific terms, use context
        server_terms = ['server', 'channel', 'message', 'discord', 'here', 'this']
        query_lower = query.lower()
        
        return any(term in query_lower for term in server_terms) 
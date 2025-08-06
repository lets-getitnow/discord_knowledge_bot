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
    
    def search_relevant_content(self, query: str, n_results: int = 5, channel_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for relevant content based on user query."""
        if channel_id:
            # Search within specific channel
            results = self.storage.search(query, n_results, filter_metadata={"channel_id": str(channel_id)})
            logger.info(f"Found {len(results)} relevant documents for query '{query}' in channel {channel_id}")
        else:
            # Search across all channels
            results = self.storage.search(query, n_results)
            logger.info(f"Found {len(results)} relevant documents for query '{query}' across all channels")
        return results
    
    def build_conversation_context(self, query: str, include_search_results: bool = True, channel_id: Optional[int] = None) -> Dict[str, Any]:
        """Build context for AI conversation."""
        context = {
            'query': query,
            'relevant_docs': [],
            'search_performed': False,
            'search_scope': 'channel' if channel_id else 'server'
        }
        
        if include_search_results:
            relevant_docs = self.search_relevant_content(query, channel_id=channel_id)
            context['relevant_docs'] = relevant_docs
            context['search_performed'] = True
            context['search_scope'] = 'channel' if channel_id else 'server'
            logger.info(f"Built context with {len(relevant_docs)} relevant documents (scope: {context['search_scope']})")
        
        return context
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Get a summary of the conversation context."""
        if 'relevant_docs' not in context or not context['relevant_docs']:
            scope = context.get('search_scope', 'server')
            return f"No relevant {scope} content found for this query."
        
        doc_count = len(context['relevant_docs'])
        scope = context.get('search_scope', 'server')
        return f"Found {doc_count} relevant messages from the {scope} to help answer your question."
    
    def should_use_server_context(self, query: str) -> bool:
        """Determine if the query should use server context."""
        # Simple heuristic - if query mentions server-specific terms, use context
        server_terms = ['server', 'channel', 'message', 'discord', 'here', 'this']
        query_lower = query.lower()
        
        return any(term in query_lower for term in server_terms) 
"""
Helper utilities for Discord Knowledge Bot.
Text processing and common operations.
"""

import re
import asyncio
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove Discord formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
    text = re.sub(r'__(.*?)__', r'\1', text)      # Underline
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of specified size."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for word in text.split():
        if len(current_chunk) + len(word) + 1 <= chunk_size:
            current_chunk += (word + " ")
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = word + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def rate_limit_delay(delay: float = 1.0):
    """Simple rate limiting delay."""
    await asyncio.sleep(delay)

def format_message_metadata(message) -> Dict[str, Any]:
    """Extract metadata from a Discord message."""
    return {
        'message_id': str(message.id),
        'author_id': str(message.author.id),
        'author_name': message.author.display_name,
        'channel_id': str(message.channel.id),
        'channel_name': message.channel.name,
        'timestamp': message.created_at.isoformat(),
        'guild_id': str(message.guild.id) if message.guild else '',
        'guild_name': message.guild.name if message.guild else ''
    } 
"""
Content collector module for Discord Knowledge Bot.
Handles message collection with pagination and rate limiting.
"""

import discord
from typing import List, Optional, AsyncGenerator
import asyncio
import logging
from utils.helpers import rate_limit_delay
from utils.config import config

logger = logging.getLogger(__name__)

class MessageCollector:
    """Collects Discord messages with pagination and rate limiting."""
    
    def __init__(self):
        """Initialize the message collector."""
        self.max_messages_per_request = config['indexing']['max_messages_per_request']
        self.rate_limit_delay = config['indexing']['rate_limit_delay']
    
    async def collect_channel_messages(self, channel, limit: Optional[int] = None) -> List[discord.Message]:
        """Collect all messages from a channel with pagination."""
        messages = []
        last_message_id = None
        
        try:
            while True:
                # Calculate how many messages to fetch
                if limit:
                    remaining = limit - len(messages)
                    fetch_limit = min(self.max_messages_per_request, remaining)
                else:
                    fetch_limit = self.max_messages_per_request
                
                if limit and len(messages) >= limit:
                    break
                
                # Fetch messages
                if last_message_id:
                    channel_messages = await channel.history(
                        limit=fetch_limit,
                        before=last_message_id
                    ).flatten()
                else:
                    channel_messages = await channel.history(
                        limit=fetch_limit
                    ).flatten()
                
                if not channel_messages:
                    break
                
                # Add messages to collection
                messages.extend(channel_messages)
                last_message_id = channel_messages[-1].id
                
                logger.info(f"Collected {len(channel_messages)} messages from {channel.name} (total: {len(messages)})")
                
                # Rate limiting
                await rate_limit_delay(self.rate_limit_delay)
                
        except Exception as e:
            logger.error(f"Error collecting messages from {channel.name}: {e}")
            raise
        
        return messages
    
    async def collect_server_messages(self, guild, limit_per_channel: Optional[int] = None) -> List[discord.Message]:
        """Collect messages from all text channels in a server."""
        all_messages = []
        
        # Get all text channels
        text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
        
        logger.info(f"Found {len(text_channels)} text channels in {guild.name}")
        
        for channel in text_channels:
            logger.info(f"Collecting messages from {channel.name}")
            channel_messages = await self.collect_channel_messages(channel, limit_per_channel)
            all_messages.extend(channel_messages)
            
            logger.info(f"Collected {len(channel_messages)} messages from {channel.name}")
        
        logger.info(f"Total messages collected from {guild.name}: {len(all_messages)}")
        return all_messages
    
    async def collect_messages_generator(self, channel, limit: Optional[int] = None) -> AsyncGenerator[List[discord.Message], None]:
        """Generator for collecting messages in batches."""
        last_message_id = None
        total_collected = 0
        
        while True:
            if limit and total_collected >= limit:
                break
            
            # Calculate batch size
            if limit:
                remaining = limit - total_collected
                batch_size = min(self.max_messages_per_request, remaining)
            else:
                batch_size = self.max_messages_per_request
            
            # Fetch messages
            if last_message_id:
                channel_messages = await channel.history(
                    limit=batch_size,
                    before=last_message_id
                ).flatten()
            else:
                channel_messages = await channel.history(
                    limit=batch_size
                ).flatten()
            
            if not channel_messages:
                break
            
            total_collected += len(channel_messages)
            last_message_id = channel_messages[-1].id
            
            yield channel_messages
            
            # Rate limiting
            await rate_limit_delay(self.rate_limit_delay)
    
    def filter_text_messages(self, messages: List[discord.Message]) -> List[discord.Message]:
        """Filter messages to only include those with text content."""
        return [msg for msg in messages if msg.content and msg.content.strip()] 
"""
Main Discord bot for Discord Knowledge Bot.
Handles bot initialization and core functionality.
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional
from asyncio import TimeoutError

from utils.config import config
from utils.error_handler import log_error_with_context, validate_object, safe_execute
from indexing.storage import ChromaStorage
from indexing.collector import MessageCollector
from chat.ai_interface import AIInterface
from chat.context_builder import ContextBuilder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiscordKnowledgeBot(commands.Bot):
    """Main Discord Knowledge Bot class."""
    
    def __init__(self):
        """Initialize the bot with proper intents."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        
        super().__init__(
            command_prefix=config['bot']['prefix'],
            intents=intents
        )
        
        # Initialize components
        self.storage = ChromaStorage(
            persist_directory=config['chromadb']['persist_directory'],
            collection_name=config['chromadb']['collection_name']
        )
        self.collector = MessageCollector()
        self.ai_interface = AIInterface()
        self.context_builder = ContextBuilder(self.storage)
        
        # Indexing status
        self.is_indexing = False
        self.indexing_progress = {}
        
        # Add a simple test command
        @self.command(name="ping")
        async def ping(ctx):
            """Test command to verify bot is working."""
            await ctx.send("🏓 Pong!")
    
    async def setup_hook(self):
        """Set up bot components."""
        logger.info("Setting up Discord Knowledge Bot...")
        
        # Load command cogs
        await self.load_extension('bot.commands.indexing_commands')
        await self.load_extension('bot.commands.chat_commands')
        await self.load_extension('bot.commands.management_commands')
        
        # Log loaded commands
        logger.info(f"Loaded {len(self.commands)} commands:")
        for command in self.commands:
            logger.info(f"  - {command.name}: {command.help or 'No description'}")
        
        # Sync slash commands with Discord API
        logger.info("Syncing slash commands with Discord...")
        await self.tree.sync()
        logger.info("Slash commands synced successfully!")
        
        logger.info("Bot setup complete!")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guild(s)')
        
        # Log available commands
        logger.info(f"Available commands: {[cmd.name for cmd in self.commands]}")
        
        # Set bot status
        await self.change_presence(activity=discord.Game(name="Indexing Knowledge"))
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot messages
        if message.author == self.user:
            return
        
        # Debug: Log all messages that start with prefix
        if message.content.startswith(config['bot']['prefix']):
            logger.info(f"Command received: {message.content}")
        
        # Handle commands
        await self.process_commands(message)
        
        # Handle chat (non-command messages)
        if not message.content.startswith(config['bot']['prefix']):
            await self.handle_chat(message)
    
    async def handle_chat(self, message):
        """Handle natural language chat with the bot."""
        try:
            # Build context
            context = self.context_builder.build_conversation_context(message.content)
            
            # Get AI response
            response = await self.ai_interface.get_response(
                message.content, 
                context['relevant_docs']
            )
            
            # Send response
            await message.channel.send(response)
            
        except Exception as e:
            logger.error(f"Error handling chat: {e}")
            raise
    
    async def start_indexing(self, guild_id: int, channel_id: Optional[int] = None):
        """Start indexing process."""
        if self.is_indexing:
            return False, "Indexing already in progress"
        
        self.is_indexing = True
        self.indexing_progress = {'status': 'Starting...', 'processed': 0, 'total': 0}
        
        try:
            guild = self.get_guild(guild_id)
            if not guild:
                return False, "Guild not found"
            
            if channel_id:
                # Index specific channel
                channel = guild.get_channel(channel_id)
                if not channel:
                    return False, "Channel not found"
                
                await self._index_channel(channel)
            else:
                # Index entire server
                await self._index_server(guild)
            
            return True, "Indexing completed successfully"
            
        except Exception as e:
            log_error_with_context(e, "indexing process")
            return False, f"Indexing failed: {str(e)}"
        finally:
            self.is_indexing = False
            self.indexing_progress = {}
    
    async def _index_server(self, guild):
        """Index all text channels in a server."""
        logger.info(f"Starting server indexing for {guild.name}")
        
        # Collect all messages
        messages = await self.collector.collect_server_messages(guild)
        text_messages = self.collector.filter_text_messages(messages)
        
        self.indexing_progress['total'] = len(text_messages)
        self.indexing_progress['status'] = 'Processing messages...'
        
        # Process messages in batches
        batch_size = 50
        for i in range(0, len(text_messages), batch_size):
            batch = text_messages[i:i + batch_size]
            
            # Prepare documents for storage
            documents = []
            for j, message in enumerate(batch):
                # Validate message object
                if not validate_object(message, ['guild', 'channel', 'id'], f"processing message {j}"):
                    continue
                
                try:
                    doc_id = f"{message.guild.id}_{message.channel.id}_{message.id}"
                    metadata = {
                        'guild_id': message.guild.id,
                        'guild_name': message.guild.name,
                        'channel_id': message.channel.id,
                        'channel_name': message.channel.name,
                        'message_id': message.id,
                        'author_id': message.author.id,
                        'author_name': message.author.display_name,
                        'timestamp': message.created_at.isoformat(),
                        'content': message.content
                    }
                    
                    documents.append({
                        'text': message.content,
                        'metadata': metadata,
                        'id': doc_id
                    })
                except Exception as e:
                    log_error_with_context(e, f"processing message {j}", {
                        'message_type': type(message),
                        'message_content': str(message)
                    })
                    continue
            
            if documents:
                # Prepare for storage
                texts = [doc['text'] for doc in documents]
                metadatas = [doc['metadata'] for doc in documents]
                ids = [doc['id'] for doc in documents]
                
                # Store in ChromaDB
                self.storage.add_documents(texts, metadatas, ids)
            
            self.indexing_progress['processed'] = min(i + batch_size, len(text_messages))
            self.indexing_progress['status'] = f'Processed {self.indexing_progress["processed"]}/{self.indexing_progress["total"]} messages'
            
            # Rate limiting
            await asyncio.sleep(0.1)
        
        logger.info(f"Server indexing completed for {guild.name}")
    
    async def _index_channel(self, channel):
        """Index a specific channel."""
        logger.info(f"Starting channel indexing for {channel.name}")
        
        # Collect messages
        messages = await self.collector.collect_channel_messages(channel)
        text_messages = self.collector.filter_text_messages(messages)
        
        self.indexing_progress['total'] = len(text_messages)
        self.indexing_progress['status'] = 'Processing messages...'
        
        # Prepare documents for storage
        documents = []
        for message in text_messages:
            # Validate message object
            if not validate_object(message, ['guild', 'channel', 'id'], "processing channel message"):
                continue
            
            try:
                doc_id = f"{message.guild.id}_{message.channel.id}_{message.id}"
                metadata = {
                    'guild_id': message.guild.id,
                    'guild_name': message.guild.name,
                    'channel_id': message.channel.id,
                    'channel_name': message.channel.name,
                    'message_id': message.id,
                    'author_id': message.author.id,
                    'author_name': message.author.display_name,
                    'timestamp': message.created_at.isoformat(),
                    'content': message.content
                }
                
                documents.append({
                    'text': message.content,
                    'metadata': metadata,
                    'id': doc_id
                })
            except Exception as e:
                log_error_with_context(e, "processing channel message", {
                    'message_type': type(message),
                    'message_content': str(message)
                })
                continue
        
        if documents:
            # Prepare for storage
            texts = [doc['text'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            ids = [doc['id'] for doc in documents]
            
            # Store in ChromaDB
            self.storage.add_documents(texts, metadatas, ids)
        
        self.indexing_progress['processed'] = len(text_messages)
        self.indexing_progress['status'] = f'Processed {len(text_messages)} messages'
        
        logger.info(f"Channel indexing completed for {channel.name}")

def run_bot():
    """Run the Discord bot."""
    logger.info("Initializing Discord Knowledge Bot...")
    
    try:
        # Log token information before attempting connection
        token = config['bot']['token']
        token_preview = token[:10] + "..." + token[-10:] if len(token) > 20 else "***"
        logger.info(f"Attempting to connect with token: {token_preview}")
        logger.info(f"Token length: {len(token)} characters")
        
        bot = DiscordKnowledgeBot()
        logger.info("Bot instance created successfully")
        
        logger.info("Attempting to connect to Discord...")
        bot.run(token)
        
    except discord.LoginFailure as e:
        logger.error("Discord login failed - this usually means the token is invalid")
        logger.error(f"Login failure details: {e}")
        logger.error("Please check that your DISCORD_TOKEN is correct and not expired")
        raise
    except discord.HTTPException as e:
        logger.error(f"Discord HTTP error occurred: {e}")
        logger.error(f"HTTP status: {e.status}")
        logger.error(f"HTTP response: {e.response}")
        raise
    except discord.ConnectionClosed as e:
        logger.error(f"Discord connection was closed: {e}")
        logger.error(f"Close code: {e.code}")
        logger.error(f"Close reason: {e.reason}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during bot startup: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        raise

if __name__ == "__main__":
    run_bot() 
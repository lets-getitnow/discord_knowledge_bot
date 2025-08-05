"""
Indexing commands for Discord Knowledge Bot.
Handles server and channel indexing operations.
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class IndexingCommands(commands.Cog):
    """Indexing commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the indexing commands."""
        self.bot = bot
    
    @commands.command(name="index-server")
    async def index_server(self, ctx):
        """Index all text channels in the server."""
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        await ctx.send("🔄 Starting server indexing... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(ctx.guild.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"Error in index_server command: {e}")
            await ctx.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @commands.command(name="index-channel")
    async def index_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Index a specific channel. If no channel is specified, indexes the current channel."""
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        target_channel = channel or ctx.channel
        
        await ctx.send(f"🔄 Starting channel indexing for #{target_channel.name}... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(ctx.guild.id, target_channel.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"Error in index_channel command: {e}")
            await ctx.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @commands.command(name="reindex-server")
    async def reindex_server(self, ctx):
        """Clear existing index and reindex all text channels in the server."""
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # Confirm the action
        confirm_msg = await ctx.send("⚠️ This will clear all existing indexed data and reindex the entire server. Are you sure? (yes/no)")
        
        try:
            response = await self.bot.wait_for(
                'message',
                timeout=30.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            
            if response.content.lower() not in ['yes', 'y']:
                await ctx.send("❌ Reindexing cancelled.")
                return
                
        except TimeoutError:
            await ctx.send("❌ Reindexing cancelled due to timeout.")
            return
        
        await ctx.send("🔄 Clearing existing index and starting server reindexing... This may take a while.")
        
        try:
            # Clear existing index
            self.bot.storage.clear_collection()
            await ctx.send("🗑️ Cleared existing index.")
            
            # Start reindexing
            success, message = await self.bot.start_indexing(ctx.guild.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"Error in reindex_server command: {e}")
            await ctx.send(f"❌ An error occurred during reindexing: {str(e)}")
    
    @commands.command(name="reindex-channel")
    async def reindex_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Clear existing index and reindex a specific channel. If no channel is specified, reindexes the current channel."""
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        target_channel = channel or ctx.channel
        
        # Confirm the action
        confirm_msg = await ctx.send(f"⚠️ This will clear all existing indexed data and reindex #{target_channel.name}. Are you sure? (yes/no)")
        
        try:
            response = await self.bot.wait_for(
                'message',
                timeout=30.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            
            if response.content.lower() not in ['yes', 'y']:
                await ctx.send("❌ Reindexing cancelled.")
                return
                
        except TimeoutError:
            await ctx.send("❌ Reindexing cancelled due to timeout.")
            return
        
        await ctx.send(f"🔄 Clearing existing index and starting channel reindexing for #{target_channel.name}... This may take a while.")
        
        try:
            # Clear existing index
            self.bot.storage.clear_collection()
            await ctx.send("🗑️ Cleared existing index.")
            
            # Start reindexing
            success, message = await self.bot.start_indexing(ctx.guild.id, target_channel.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"Error in reindex_channel command: {e}")
            await ctx.send(f"❌ An error occurred during reindexing: {str(e)}")
    
    @index_server.error
    @index_channel.error
    @reindex_server.error
    @reindex_channel.error
    async def indexing_error(self, ctx, error):
        """Handle errors in indexing commands."""
        logger.error(f"Error in indexing command: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")

async def setup(bot):
    """Set up the indexing commands cog."""
    await bot.add_cog(IndexingCommands(bot)) 
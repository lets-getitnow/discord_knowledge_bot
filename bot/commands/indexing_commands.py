"""
Indexing commands for Discord Knowledge Bot.
Handles server and channel indexing operations.
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
from utils.error_handler import log_error_with_context

logger = logging.getLogger(__name__)

class IndexingCommands(commands.Cog):
    """Indexing commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the indexing commands."""
        self.bot = bot
    
    def get_target_guild(self, ctx):
        """Get the target guild for indexing operations."""
        # If in a server, use that server
        if ctx.guild:
            return ctx.guild
        
        # If in DM, use the first available server
        if len(self.bot.guilds) == 0:
            return None
        elif len(self.bot.guilds) == 1:
            return self.bot.guilds[0]
        else:
            # Multiple servers - could prompt user to choose
            # For now, use the first one
            return self.bot.guilds[0]
    
    @commands.command(name="index-server")
    @commands.has_permissions(administrator=True)
    async def index_server(self, ctx):
        """Index all text channels in the server."""
        # Get target guild
        target_guild = self.get_target_guild(ctx)
        if not target_guild:
            await ctx.send("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        await ctx.send(f"🔄 Starting server indexing for {target_guild.name}... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(target_guild.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "index_server command")
            await ctx.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @commands.command(name="index-channel")
    @commands.has_permissions(administrator=True)
    async def index_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Index a specific channel. If no channel is specified, indexes the current channel."""
        # Get target guild
        target_guild = self.get_target_guild(ctx)
        if not target_guild:
            await ctx.send("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # If in DM and no channel specified, we can't index a specific channel
        if ctx.guild is None and channel is None:
            await ctx.send("❌ Please specify a channel when using this command in DMs.")
            return
        
        target_channel = channel or ctx.channel
        
        await ctx.send(f"🔄 Starting channel indexing for #{target_channel.name}... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(target_guild.id, target_channel.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "index_channel command")
            await ctx.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @commands.command(name="reindex-server")
    @commands.has_permissions(administrator=True)
    async def reindex_server(self, ctx):
        """Clear existing index and reindex all text channels in the server."""
        # Get target guild
        target_guild = self.get_target_guild(ctx)
        if not target_guild:
            await ctx.send("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # Confirm the action
        confirm_msg = await ctx.send(f"⚠️ This will clear all existing indexed data and reindex {target_guild.name}. Are you sure? (yes/no)")
        
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
        
        await ctx.send(f"🔄 Clearing existing index and starting server reindexing for {target_guild.name}... This may take a while.")
        
        try:
            # Clear existing index
            self.bot.storage.clear_collection()
            await ctx.send("🗑️ Cleared existing index.")
            
            # Start reindexing
            success, message = await self.bot.start_indexing(target_guild.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "reindex_server command")
            await ctx.send(f"❌ An error occurred during reindexing: {str(e)}")
    
    @commands.command(name="reindex-channel")
    @commands.has_permissions(administrator=True)
    async def reindex_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Clear existing index and reindex a specific channel. If no channel is specified, reindexes the current channel."""
        # Get target guild
        target_guild = self.get_target_guild(ctx)
        if not target_guild:
            await ctx.send("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing:
            await ctx.send("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # If in DM and no channel specified, we can't reindex a specific channel
        if ctx.guild is None and channel is None:
            await ctx.send("❌ Please specify a channel when using this command in DMs.")
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
            success, message = await self.bot.start_indexing(target_guild.id, target_channel.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await ctx.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await ctx.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "reindex_channel command")
            await ctx.send(f"❌ An error occurred during reindexing: {str(e)}")
    
    @index_server.error
    @index_channel.error
    @reindex_server.error
    @reindex_channel.error
    async def indexing_error(self, ctx, error):
        """Handle errors in indexing commands."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ **Permission Denied**: You need Administrator permissions to use indexing commands.")
        else:
            log_error_with_context(error, "indexing command error handler")
            await ctx.send(f"❌ An error occurred: {str(error)}")

async def setup(bot):
    """Set up the indexing commands cog."""
    await bot.add_cog(IndexingCommands(bot)) 
"""
Indexing commands for Discord Knowledge Bot.
Handles server and channel indexing operations.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from utils.error_handler import log_error_with_context
from utils.permissions import has_permission

logger = logging.getLogger(__name__)

class IndexingCommands(commands.Cog):
    """Indexing commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the indexing commands."""
        self.bot = bot
    
    def get_target_guild(self, interaction):
        """Get the target guild for indexing operations."""
        # If in a server, use that server
        if interaction.guild:
            return interaction.guild
        
        # If in DM, use the first available server
        if len(self.bot.guilds) == 0:
            return None
        elif len(self.bot.guilds) == 1:
            return self.bot.guilds[0]
        else:
            # Multiple servers - could prompt user to choose
            # For now, use the first one
            return self.bot.guilds[0]
    
    @app_commands.command(name="index-server", description="Index all text channels in the server.")
    @app_commands.default_permissions(administrator=True)
    async def index_server(self, interaction: discord.Interaction):
        """Index all text channels in the server."""
        # Check if user has administrator permissions or is superuser
        if not has_permission(interaction.user.id, interaction.user.guild_permissions, "administrator"):
            await interaction.response.send_message("❌ **Permission Denied**: You need Administrator permissions to use indexing commands.")
            return
        
        # Get target guild
        target_guild = self.get_target_guild(interaction)
        if not target_guild:
            await interaction.response.send_message("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing_in_progress():
            await interaction.response.send_message("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        await interaction.response.send_message(f"🔄 Starting server indexing for {target_guild.name}... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(target_guild.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await interaction.followup.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await interaction.followup.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "index_server command")
            await interaction.followup.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @app_commands.command(name="index-channel", description="Index a specific channel.")
    @app_commands.describe(channel="The channel to index (optional)")
    @app_commands.default_permissions(administrator=True)
    async def index_channel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Index a specific channel. If no channel is specified, indexes the current channel."""
        # Check if user has administrator permissions or is superuser
        if not has_permission(interaction.user.id, interaction.user.guild_permissions, "administrator"):
            await interaction.response.send_message("❌ **Permission Denied**: You need Administrator permissions to use indexing commands.")
            return
        
        # Get target guild
        target_guild = self.get_target_guild(interaction)
        if not target_guild:
            await interaction.response.send_message("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing_in_progress():
            await interaction.response.send_message("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # If in DM and no channel specified, we can't index a specific channel
        if interaction.guild is None and channel is None:
            await interaction.response.send_message("❌ Please specify a channel when using this command in DMs.")
            return
        
        target_channel = channel or interaction.channel
        
        await interaction.response.send_message(f"🔄 Starting channel indexing for #{target_channel.name}... This may take a while.")
        
        try:
            success, message = await self.bot.start_indexing(target_guild.id, target_channel.id)
            
            if success:
                stats = self.bot.storage.get_collection_stats()
                await interaction.followup.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
            else:
                await interaction.followup.send(f"❌ {message}")
                
        except Exception as e:
            log_error_with_context(e, "index_channel command")
            await interaction.followup.send(f"❌ An error occurred during indexing: {str(e)}")
    
    @app_commands.command(name="reindex-server", description="Clear and reindex all text channels.")
    @app_commands.default_permissions(administrator=True)
    async def reindex_server(self, interaction: discord.Interaction):
        """Clear existing index and reindex all text channels in the server."""
        # Check if user has administrator permissions or is superuser
        if not has_permission(interaction.user.id, interaction.user.guild_permissions, "administrator"):
            await interaction.response.send_message("❌ **Permission Denied**: You need Administrator permissions to use indexing commands.")
            return
        
        # Get target guild
        target_guild = self.get_target_guild(interaction)
        if not target_guild:
            await interaction.response.send_message("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing_in_progress():
            await interaction.response.send_message("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # Create confirmation view
        class ReindexConfirmView(discord.ui.View):
            def __init__(self, bot, target_guild):
                super().__init__(timeout=30.0)
                self.bot = bot
                self.target_guild = target_guild
            
            @discord.ui.button(label="Yes, Reindex Server", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message(f"🔄 Clearing existing index and starting server reindexing for {self.target_guild.name}... This may take a while.")
                
                try:
                    # Clear existing index
                    self.bot.storage.clear_collection()
                    await button_interaction.followup.send("🗑️ Cleared existing index.")
                    
                    # Start reindexing
                    success, message = await self.bot.start_indexing(self.target_guild.id)
                    
                    if success:
                        stats = self.bot.storage.get_collection_stats()
                        await button_interaction.followup.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
                    else:
                        await button_interaction.followup.send(f"❌ {message}")
                        
                except Exception as e:
                    log_error_with_context(e, "reindex_server command")
                    await button_interaction.followup.send(f"❌ An error occurred during reindexing: {str(e)}")
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("❌ Reindexing cancelled.")
                self.stop()
        
        view = ReindexConfirmView(self.bot, target_guild)
        await interaction.response.send_message(f"⚠️ This will clear all existing indexed data and reindex {target_guild.name}. Are you sure?", view=view)
    
    @app_commands.command(name="reindex-channel", description="Clear and reindex a specific channel.")
    @app_commands.describe(channel="The channel to reindex (optional)")
    @app_commands.default_permissions(administrator=True)
    async def reindex_channel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Clear existing index and reindex a specific channel. If no channel is specified, reindexes the current channel."""
        # Check if user has administrator permissions or is superuser
        if not has_permission(interaction.user.id, interaction.user.guild_permissions, "administrator"):
            await interaction.response.send_message("❌ **Permission Denied**: You need Administrator permissions to use indexing commands.")
            return
        
        # Get target guild
        target_guild = self.get_target_guild(interaction)
        if not target_guild:
            await interaction.response.send_message("❌ No servers available for indexing.")
            return
        
        if self.bot.is_indexing_in_progress():
            await interaction.response.send_message("❌ Indexing is already in progress. Please wait for it to complete.")
            return
        
        # If in DM and no channel specified, we can't reindex a specific channel
        if interaction.guild is None and channel is None:
            await interaction.response.send_message("❌ Please specify a channel when using this command in DMs.")
            return
        
        target_channel = channel or interaction.channel
        
        # Create confirmation view
        class ReindexChannelConfirmView(discord.ui.View):
            def __init__(self, bot, target_guild, target_channel):
                super().__init__(timeout=30.0)
                self.bot = bot
                self.target_guild = target_guild
                self.target_channel = target_channel
            
            @discord.ui.button(label="Yes, Reindex Channel", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message(f"🔄 Clearing existing index and starting channel reindexing for #{self.target_channel.name}... This may take a while.")
                
                try:
                    # Clear existing index
                    self.bot.storage.clear_collection()
                    await button_interaction.followup.send("🗑️ Cleared existing index.")
                    
                    # Start reindexing
                    success, message = await self.bot.start_indexing(self.target_guild.id, self.target_channel.id)
                    
                    if success:
                        stats = self.bot.storage.get_collection_stats()
                        await button_interaction.followup.send(f"✅ {message}\n📊 Total documents indexed: {stats['total_documents']}")
                    else:
                        await button_interaction.followup.send(f"❌ {message}")
                        
                except Exception as e:
                    log_error_with_context(e, "reindex_channel command")
                    await button_interaction.followup.send(f"❌ An error occurred during reindexing: {str(e)}")
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("❌ Reindexing cancelled.")
                self.stop()
        
        view = ReindexChannelConfirmView(self.bot, target_guild, target_channel)
        await interaction.response.send_message(f"⚠️ This will clear all existing indexed data and reindex #{target_channel.name}. Are you sure?", view=view)

async def setup(bot):
    """Set up the indexing commands cog."""
    await bot.add_cog(IndexingCommands(bot)) 
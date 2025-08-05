"""
Management commands for Discord Knowledge Bot.
Handles status, stats, and clear operations.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.error_handler import log_error_with_context

logger = logging.getLogger(__name__)

class ManagementCommands(commands.Cog):
    """Management commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the management commands."""
        self.bot = bot
    
    @app_commands.command(name="status", description="Show the current status of the bot and indexing.")
    async def status(self, interaction: discord.Interaction):
        """Show the current status of the bot and indexing."""
        try:
            # Get collection stats
            stats = self.bot.storage.get_collection_stats()
            
            # Build status message
            status_msg = "🤖 **Discord Knowledge Bot Status**\n\n"
            
            # Indexing status
            if self.bot.is_indexing:
                progress = self.bot.indexing_progress
                status_msg += f"🔄 **Indexing Status**: In Progress\n"
                status_msg += f"📊 **Progress**: {progress['status']}\n"
                if progress['total'] > 0:
                    percentage = (progress['processed'] / progress['total']) * 100
                    status_msg += f"📈 **Completion**: {percentage:.1f}%\n"
            else:
                status_msg += "✅ **Indexing Status**: Idle\n"
            
            # Collection stats
            status_msg += f"\n📚 **Knowledge Base**:\n"
            status_msg += f"📄 **Total Documents**: {stats['total_documents']}\n"
            status_msg += f"🗂️ **Collection**: {stats['collection_name']}\n"
            
            # Bot status
            status_msg += f"\n🤖 **Bot Status**:\n"
            status_msg += f"🟢 **Status**: Online\n"
            status_msg += f"📡 **Latency**: {round(self.bot.latency * 1000)}ms\n"
            status_msg += f"🏠 **Guilds**: {len(self.bot.guilds)}\n"
            
            await interaction.response.send_message(status_msg)
            
        except Exception as e:
            log_error_with_context(e, "status command")
            await interaction.response.send_message(f"❌ An error occurred while getting status: {str(e)}")
    
    @app_commands.command(name="stats", description="Show detailed statistics about the indexed content.")
    async def stats(self, interaction: discord.Interaction):
        """Show detailed statistics about the indexed content."""
        try:
            # Get collection stats
            stats = self.bot.storage.get_collection_stats()
            
            # Build stats message
            stats_msg = "📊 **Knowledge Base Statistics**\n\n"
            stats_msg += f"📄 **Total Documents**: {stats['total_documents']}\n"
            stats_msg += f"🗂️ **Collection Name**: {stats['collection_name']}\n"
            
            if stats['total_documents'] > 0:
                stats_msg += f"\n💾 **Storage**: Active\n"
                stats_msg += f"🔍 **Search**: Available\n"
                stats_msg += f"🤖 **AI Chat**: Available\n"
            else:
                stats_msg += f"\n💾 **Storage**: Empty\n"
                stats_msg += f"🔍 **Search**: Not available\n"
                stats_msg += f"🤖 **AI Chat**: Limited (no server context)\n"
            
            # Add indexing status
            if self.bot.is_indexing:
                progress = self.bot.indexing_progress
                stats_msg += f"\n🔄 **Current Indexing**:\n"
                stats_msg += f"📊 **Status**: {progress['status']}\n"
                if progress['total'] > 0:
                    percentage = (progress['processed'] / progress['total']) * 100
                    stats_msg += f"📈 **Progress**: {percentage:.1f}% ({progress['processed']}/{progress['total']})\n"
            
            await interaction.response.send_message(stats_msg)
            
        except Exception as e:
            log_error_with_context(e, "stats command")
            await interaction.response.send_message(f"❌ An error occurred while getting stats: {str(e)}")
    
    @app_commands.command(name="invite", description="Generate an invite URL for the bot.")
    async def invite(self, interaction: discord.Interaction):
        """Generate an invite URL for the bot."""
        try:
            # Calculate required permissions
            # Read Message History (for indexing)
            # Send Messages (for responses)
            # Read Messages (for chat functionality)
            required_permissions = discord.Permissions(
                read_message_history=True,
                send_messages=True,
                read_messages=True
            )
            
            # Generate invite URL
            invite_url = discord.utils.oauth_url(
                self.bot.user.id,
                permissions=required_permissions,
                scopes=("bot", "applications.commands")
            )
            
            # Build invite message
            invite_msg = "🔗 **Invite Discord Knowledge Bot**\n\n"
            invite_msg += f"**Invite URL**: {invite_url}\n\n"
            invite_msg += "**Required Permissions**:\n"
            invite_msg += "• Read Message History (for indexing)\n"
            invite_msg += "• Send Messages (for responses)\n"
            invite_msg += "• Read Messages (for chat)\n\n"
            invite_msg += "**Features**:\n"
            invite_msg += "• AI-powered chat with server context\n"
            invite_msg += "• Server content indexing\n"
            invite_msg += "• Knowledge base search\n"
            
            await interaction.response.send_message(invite_msg)
            
        except Exception as e:
            log_error_with_context(e, "invite command")
            await interaction.response.send_message(f"❌ An error occurred while generating invite URL: {str(e)}")
    
    @app_commands.command(name="clear", description="Clear all indexed data.")
    @app_commands.default_permissions(administrator=True)
    async def clear(self, interaction: discord.Interaction):
        """Clear all indexed data."""
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ **Permission Denied**: You need Administrator permissions to clear indexed data.")
            return
        
        # Create confirmation button
        class ConfirmView(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=30.0)
                self.bot = bot
            
            @discord.ui.button(label="Yes, Clear All Data", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # Clear the collection
                    self.bot.storage.clear_collection()
                    await button_interaction.response.send_message("🗑️ All indexed data has been cleared successfully.")
                except Exception as e:
                    log_error_with_context(e, "clear command")
                    await button_interaction.response.send_message(f"❌ An error occurred while clearing data: {str(e)}")
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("❌ Clear operation cancelled.")
                self.stop()
        
        view = ConfirmView(self.bot)
        await interaction.response.send_message("⚠️ This will permanently delete all indexed data. Are you sure?", view=view)

async def setup(bot):
    """Set up the management commands cog."""
    await bot.add_cog(ManagementCommands(bot)) 
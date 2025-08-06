"""
Management commands for Discord Knowledge Bot.
Handles status, stats, and clear operations.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.error_handler import log_error_with_context
from utils.permissions import has_permission

logger = logging.getLogger(__name__)

class ManagementCommands(commands.Cog):
    """Management commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the management commands."""
        self.bot = bot
    
    @app_commands.command(name="help", description="Show help information and available commands.")
    async def help(self, interaction: discord.Interaction):
        """Show help information and available commands."""
        try:
            help_msg = "🤖 **Discord Knowledge Bot Help**\n\n"
            
            help_msg += "**📚 Indexing Commands (Admin Only)**\n"
            help_msg += "• `/index-server` - Index all text channels in the server\n"
            help_msg += "• `/index-channel [channel]` - Index a specific channel (or current channel)\n"
            help_msg += "• `/reindex-server` - Clear and reindex all text channels\n"
            help_msg += "• `/reindex-channel [channel]` - Clear and reindex a specific channel\n\n"
            
            help_msg += "**💬 Chat Commands**\n"
            help_msg += "• `/ask <question>` - Ask a question about **this channel's** content\n"
            help_msg += "• `/ask-server <question>` - Ask a question about the **entire server's** content\n"
            help_msg += "• **Natural Chat**: Simply send a message to chat with the AI!\n\n"
            
            help_msg += "**⚙️ Management Commands**\n"
            help_msg += "• `/status` - Show bot and indexing status\n"
            help_msg += "• `/stats` - Show detailed statistics\n"
            help_msg += "• `/clear` - Clear all indexed data (Admin only)\n"
            help_msg += "• `/ping` - Test command to verify bot is working\n\n"
            
            help_msg += "**🔍 Search Types**\n"
            help_msg += "• **Channel-Specific** (`/ask`): Searches only within the current channel\n"
            help_msg += "• **Server-Wide** (`/ask-server`): Searches across all indexed channels\n\n"
            
            help_msg += "**📋 Permissions**\n"
            help_msg += "• Indexing commands require Administrator permissions\n"
            help_msg += "• Chat commands work for everyone\n"
            help_msg += "• Bot needs 'Read Message History' permission to index channels\n\n"
            
            help_msg += "**💡 Tips**\n"
            help_msg += "• Index your server first with `/index-server`\n"
            help_msg += "• Use `/ask` for channel-specific questions\n"
            help_msg += "• Use `/ask-server` for server-wide questions\n"
            help_msg += "• Send regular messages to chat naturally with the AI"
            
            await interaction.response.send_message(help_msg)
            
        except Exception as e:
            log_error_with_context(e, "help command")
            await interaction.response.send_message(f"❌ An error occurred while getting help: {str(e)}")
    
    @app_commands.command(name="ping", description="Test command to verify bot is working.")
    async def ping(self, interaction: discord.Interaction):
        """Test command to verify bot is working."""
        await interaction.response.send_message("🏓 Pong!")
    
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
    
    @app_commands.command(name="clear", description="Clear all indexed data.")
    @app_commands.default_permissions(administrator=True)
    async def clear(self, interaction: discord.Interaction):
        """Clear all indexed data."""
        # Check if user has administrator permissions or is superuser
        if not has_permission(interaction.user.id, interaction.user.guild_permissions, "administrator"):
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
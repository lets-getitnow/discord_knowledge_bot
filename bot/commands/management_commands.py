"""
Management commands for Discord Knowledge Bot.
Handles status, stats, and clear operations.
"""

import discord
from discord.ext import commands
import logging
from utils.error_handler import log_error_with_context

logger = logging.getLogger(__name__)

class ManagementCommands(commands.Cog):
    """Management commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the management commands."""
        self.bot = bot
    
    @commands.command(name="status")
    async def status(self, ctx):
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
            
            await ctx.send(status_msg)
            
        except Exception as e:
            log_error_with_context(e, "status command")
            await ctx.send(f"❌ An error occurred while getting status: {str(e)}")
    
    @commands.command(name="stats")
    async def stats(self, ctx):
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
            
            await ctx.send(stats_msg)
            
        except Exception as e:
            log_error_with_context(e, "stats command")
            await ctx.send(f"❌ An error occurred while getting stats: {str(e)}")
    
    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        """Clear all indexed data."""
        # Confirm the action
        confirm_msg = await ctx.send("⚠️ This will permanently delete all indexed data. Are you sure? (yes/no)")
        
        try:
            response = await self.bot.wait_for(
                'message',
                timeout=30.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            
            if response.content.lower() not in ['yes', 'y']:
                await ctx.send("❌ Clear operation cancelled.")
                return
                
        except TimeoutError:
            await ctx.send("❌ Clear operation cancelled due to timeout.")
            return
        
        try:
            # Clear the collection
            self.bot.storage.clear_collection()
            await ctx.send("🗑️ All indexed data has been cleared successfully.")
            
        except Exception as e:
            log_error_with_context(e, "clear command")
            await ctx.send(f"❌ An error occurred while clearing data: {str(e)}")
    

    
    @clear.error
    async def clear_error(self, ctx, error):
        """Handle errors in clear command."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ **Permission Denied**: You need Administrator permissions to clear indexed data.")
        else:
            log_error_with_context(error, "clear command error handler")
            await ctx.send(f"❌ An error occurred: {str(error)}")

async def setup(bot):
    """Set up the management commands cog."""
    await bot.add_cog(ManagementCommands(bot)) 
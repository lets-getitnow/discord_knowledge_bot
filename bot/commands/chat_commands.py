"""
Chat commands for Discord Knowledge Bot.
Handles AI chat interactions.
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class ChatCommands(commands.Cog):
    """Chat commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the chat commands."""
        self.bot = bot
    
    @commands.command(name="ask")
    async def ask(self, ctx, *, question: str):
        """Ask a question and get an AI response based on indexed content."""
        try:
            # Build context
            context = self.bot.context_builder.build_conversation_context(question)
            
            # Get AI response
            response = await self.bot.ai_interface.get_response(question, context['relevant_docs'])
            
            # Send response
            if len(response) > 2000:
                # Split long responses
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"🤖 **AI Response (Part {i+1}/{len(chunks)})**\n{chunk}")
            else:
                await ctx.send(f"🤖 **AI Response**\n{response}")
                
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            await ctx.send(f"❌ An error occurred while processing your question: {str(e)}")

async def setup(bot):
    """Set up the chat commands cog."""
    await bot.add_cog(ChatCommands(bot)) 
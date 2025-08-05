"""
Chat commands for Discord Knowledge Bot.
Handles AI chat interactions.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.error_handler import log_error_with_context

logger = logging.getLogger(__name__)

class ChatCommands(commands.Cog):
    """Chat commands for the Discord Knowledge Bot."""
    
    def __init__(self, bot):
        """Initialize the chat commands."""
        self.bot = bot
    
    @app_commands.command(name="ask", description="Ask a question and get an AI response.")
    @app_commands.describe(question="Your question to ask the AI")
    async def ask(self, interaction: discord.Interaction, question: str):
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
                await interaction.response.send_message(f"🤖 **AI Response (Part 1/{len(chunks)})**\n{chunks[0]}")
                for i, chunk in enumerate(chunks[1:], 2):
                    await interaction.followup.send(f"🤖 **AI Response (Part {i}/{len(chunks)})**\n{chunk}")
            else:
                await interaction.response.send_message(f"🤖 **AI Response**\n{response}")
                
        except Exception as e:
            log_error_with_context(e, "ask command")
            await interaction.response.send_message(f"❌ An error occurred while processing your question: {str(e)}")

async def setup(bot):
    """Set up the chat commands cog."""
    await bot.add_cog(ChatCommands(bot)) 
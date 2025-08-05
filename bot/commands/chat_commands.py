"""
Chat commands for Discord Knowledge Bot.
Handles AI chat interactions and search functionality.
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
    
    @commands.command(name="search")
    async def search(self, ctx, *, query: str):
        """Search for relevant content in the indexed knowledge base."""
        try:
            # Search for relevant documents
            results = self.bot.storage.search(query, n_results=5)
            
            if not results:
                await ctx.send("🔍 No relevant content found for your search query.")
                return
            
            # Format and send results
            formatted_results = self.bot.ai_interface.format_search_results(results)
            
            # Split long responses if needed
            if len(formatted_results) > 2000:
                # Split into chunks
                chunks = [formatted_results[i:i+1900] for i in range(0, len(formatted_results), 1900)]
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"🔍 **Search Results (Part {i+1}/{len(chunks)})**\n{chunk}")
            else:
                await ctx.send(f"🔍 **Search Results**\n{formatted_results}")
                
        except Exception as e:
            logger.error(f"Error in search command: {e}")
            await ctx.send(f"❌ An error occurred during search: {str(e)}")
    
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
    
    @commands.command(name="context")
    async def context(self, ctx, *, query: str):
        """Show what context the AI would use for a given query."""
        try:
            # Search for relevant documents
            results = self.bot.storage.search(query, n_results=3)
            
            if not results:
                await ctx.send("🔍 No relevant context found for your query.")
                return
            
            # Build context summary
            context_summary = self.bot.context_builder.get_context_summary({'relevant_docs': results})
            
            # Format results
            formatted_results = self.bot.ai_interface.format_search_results(results)
            
            response = f"🔍 **Context for: {query}**\n\n{context_summary}\n\n**Relevant Content:**\n{formatted_results}"
            
            # Send response
            if len(response) > 2000:
                # Split long responses
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"🔍 **Context (Part {i+1}/{len(chunks)})**\n{chunk}")
            else:
                await ctx.send(response)
                
        except Exception as e:
            logger.error(f"Error in context command: {e}")
            await ctx.send(f"❌ An error occurred while getting context: {str(e)}")

async def setup(bot):
    """Set up the chat commands cog."""
    await bot.add_cog(ChatCommands(bot)) 
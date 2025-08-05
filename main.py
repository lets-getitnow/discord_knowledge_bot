"""
Main entry point for Discord Knowledge Bot.
Run this file to start the bot.
"""

import os
import sys
import logging
from bot.main import run_bot
import discord

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def generate_invite_link(app_id):
    """Generate Discord bot invite link."""
    permissions = "8"  # Administrator permissions
    scopes = "bot%20applications.commands"
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope={scopes}"

def main():
    """Main entry point for the Discord Knowledge Bot."""
    print("🤖 Starting Discord Knowledge Bot...")
    
    # Check for required environment variables
    required_vars = ['DISCORD_TOKEN', 'DISCORD_APP_ID', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("Example .env file:")
        print("DISCORD_TOKEN=your_discord_bot_token_here")
        print("DISCORD_APP_ID=your_discord_application_id_here")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        sys.exit(1)
    
    # Log environment variable status
    print("✅ Environment variables found:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show preview of the value for debugging
            preview = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print(f"   - {var}: {preview} ({len(value)} chars)")
        else:
            print(f"   - {var}: Missing")
    
    # Generate and print invite link
    app_id = os.getenv('DISCORD_APP_ID')
    if app_id:
        invite_link = generate_invite_link(app_id)
        print(f"\n🔗 **Invite Link:**")
        print(f"{invite_link}")
        print(f"\n📋 **Instructions:**")
        print(f"1. Copy the invite link above")
        print(f"2. Open it in your browser")
        print(f"3. Select your server and authorize the bot")
        print(f"4. The bot will then appear in your server!")
    
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
    except discord.LoginFailure as e:
        print(f"❌ Discord login failed: {e}")
        print("This usually means your Discord token is invalid or expired.")
        print("Please check your DISCORD_TOKEN in your .env file.")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Check the logs above for more detailed information.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
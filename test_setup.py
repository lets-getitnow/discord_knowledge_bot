"""
Test setup script for Discord Knowledge Bot.
Validates configuration and provides detailed debugging information.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_discord_token(token):
    """Validate Discord token format and provide detailed error information."""
    print(f"\n🔍 Validating Discord token...")
    
    if not token:
        print("❌ Token is None or empty")
        return False
    
    if not isinstance(token, str):
        print(f"❌ Token is not a string, got {type(token)}")
        return False
    
    token = token.strip()
    if not token:
        print("❌ Token is empty after stripping whitespace")
        return False
    
    print(f"✅ Token is a string with {len(token)} characters")
    
    # Discord tokens are typically 59 characters long and contain dots
    if len(token) < 50:
        print(f"⚠️  Token seems too short ({len(token)} chars), Discord tokens are typically ~59 characters")
    elif len(token) > 100:
        print(f"⚠️  Token seems too long ({len(token)} chars), Discord tokens are typically ~59 characters")
    else:
        print(f"✅ Token length looks reasonable ({len(token)} chars)")
    
    # Check for basic Discord token format (contains dots)
    if '.' not in token:
        print("⚠️  Token doesn't contain dots, which is unusual for Discord tokens")
    else:
        print("✅ Token contains dots (typical for Discord tokens)")
    
    # Show token preview for debugging
    preview = token[:10] + "..." + token[-10:] if len(token) > 20 else "***"
    print(f"📝 Token preview: {preview}")
    
    return True

def check_environment():
    """Check environment setup and provide detailed information."""
    print("🔧 Checking environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("   Create a .env file with your Discord token and app ID")
    
    # Check required environment variables
    required_vars = ['DISCORD_TOKEN', 'DISCORD_APP_ID', 'OPENAI_API_KEY']
    missing_vars = []
    
    print("\n📋 Environment variables:")
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Present ({len(value)} chars)")
            if var == 'DISCORD_TOKEN':
                validate_discord_token(value)
        else:
            print(f"   ❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add your credentials:")
        print("   DISCORD_TOKEN=your_discord_bot_token_here")
        print("   DISCORD_APP_ID=your_discord_application_id_here")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    return True

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n📦 Checking dependencies...")
    
    # Map pip package names to their actual import names
    package_imports = {
        'discord.py': 'discord',
        'chromadb': 'chromadb',
        'pyyaml': 'yaml',
        'python-dotenv': 'dotenv',
        'llama-index-core': 'llama_index.core',
        'llama-index-vector-stores-chroma': 'llama_index.vector_stores.chroma',
        'llama-index-embeddings-huggingface': 'llama_index.embeddings.huggingface',
        'sentence-transformers': 'sentence_transformers',
        'openai': 'openai'
    }
    
    missing_packages = []
    
    # Check required packages
    for pip_name, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"   ✅ {pip_name}")
        except ImportError:
            print(f"   ❌ {pip_name}")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run the test setup."""
    print("🧪 Discord Knowledge Bot - Test Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check environment
    env_ok = check_environment()
    
    print("\n" + "=" * 50)
    if deps_ok and env_ok:
        print("✅ Setup looks good! You can now run the bot with: python main.py")
    else:
        print("❌ Setup has issues. Please fix the problems above before running the bot.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
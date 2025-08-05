"""
Test script to verify Discord Knowledge Bot setup.
Run this to check if all dependencies and configurations are correct.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import discord
        print("✅ discord.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import discord.py: {e}")
        return False
    
    try:
        import chromadb
        print("✅ chromadb imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chromadb: {e}")
        return False
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import openai: {e}")
        return False
    
    try:
        import yaml
        print("✅ pyyaml imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pyyaml: {e}")
        return False
    
    return True

def test_config():
    """Test if configuration can be loaded."""
    print("\n🔍 Testing configuration...")
    
    try:
        from utils.config import config
        print("✅ Configuration loaded successfully")
        
        # Check required config sections
        required_sections = ['bot', 'openai', 'chromadb', 'indexing']
        for section in required_sections:
            if section in config:
                print(f"✅ {section} configuration found")
            else:
                print(f"❌ {section} configuration missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

def test_environment():
    """Test if environment variables are set."""
    print("\n🔍 Testing environment variables...")
    
    required_vars = ['DISCORD_TOKEN', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with these variables:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    return True

def test_modules():
    """Test if custom modules can be imported."""
    print("\n🔍 Testing custom modules...")
    
    try:
        from indexing.storage import ChromaStorage
        print("✅ ChromaStorage imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ChromaStorage: {e}")
        return False
    
    try:
        from indexing.processor import TextProcessor
        print("✅ TextProcessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import TextProcessor: {e}")
        return False
    
    try:
        from chat.ai_interface import AIInterface
        print("✅ AIInterface imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AIInterface: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🤖 Discord Knowledge Bot Setup Test\n")
    
    tests = [
        test_imports,
        test_config,
        test_environment,
        test_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot should be ready to run.")
        print("Run 'python main.py' to start the bot.")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the bot.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
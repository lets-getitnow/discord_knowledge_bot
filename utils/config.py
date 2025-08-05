"""
Configuration management for Discord Knowledge Bot.
Loads settings from config.yaml and environment variables.
"""

import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from config.yaml and environment variables."""
    config_path = "config.yaml"
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override with environment variables
    config['bot']['token'] = os.getenv('DISCORD_TOKEN')
    config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    
    return config

# Global config instance
config = load_config() 
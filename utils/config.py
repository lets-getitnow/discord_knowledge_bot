"""
Configuration management for Discord Knowledge Bot.
Loads settings from config.yaml and environment variables.
"""

import os
import yaml
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def validate_discord_token(token):
    """Check if Discord token exists and is not empty."""
    if not token:
        return False, "Token is None or empty"
    
    if not isinstance(token, str):
        return False, f"Token is not a string, got {type(token)}"
    
    token = token.strip()
    if not token:
        return False, "Token is empty after stripping whitespace"
    
    return True, "Token is present"

def load_config():
    """Load configuration from config.yaml and environment variables."""
    config_path = "config.yaml"
    
    logger.info("Loading configuration...")
    
    # Check if config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    logger.info("Configuration file loaded successfully")
    
    # Load and validate Discord token
    discord_token = os.getenv('DISCORD_TOKEN')
    logger.info(f"Discord token loaded from environment: {'Present' if discord_token else 'Missing'}")
    
    if discord_token:
        # Log token details (safely)
        token_preview = discord_token[:10] + "..." + discord_token[-10:] if len(discord_token) > 20 else "***"
        logger.info(f"Token preview: {token_preview}")
        logger.info(f"Token length: {len(discord_token)} characters")
        
        # Validate token format
        is_valid, validation_msg = validate_discord_token(discord_token)
        if not is_valid:
            logger.error(f"Discord token validation failed: {validation_msg}")
            raise ValueError(f"Invalid Discord token: {validation_msg}")
        else:
            logger.info(f"Discord token validation passed: {validation_msg}")
    else:
        logger.error("DISCORD_TOKEN environment variable is not set")
        raise ValueError("DISCORD_TOKEN environment variable is required")
    
    # Load OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    logger.info(f"OpenAI API key loaded from environment: {'Present' if openai_key else 'Missing'}")
    
    if not openai_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Override config with environment variables
    config['bot']['token'] = discord_token
    config['openai']['api_key'] = openai_key
    
    logger.info("Configuration loaded successfully")
    return config

# Global config instance
config = load_config() 
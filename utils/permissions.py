"""
Permission management for Discord Knowledge Bot.
Handles superuser permissions and permission checks.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_superuser_id() -> Optional[str]:
    """Get the superuser Discord ID from environment variables."""
    superuser_id = os.getenv('SUPERUSER_DISCORD_ID')
    if superuser_id:
        logger.info(f"Superuser ID loaded: {superuser_id}")
    else:
        logger.info("No superuser ID configured")
    return superuser_id

def is_superuser(user_id: int) -> bool:
    """Check if a user is a superuser based on their Discord ID."""
    superuser_id = get_superuser_id()
    if not superuser_id:
        return False
    
    try:
        # Convert to int for comparison
        superuser_id_int = int(superuser_id)
        return user_id == superuser_id_int
    except ValueError:
        logger.error(f"Invalid superuser ID format: {superuser_id}")
        return False

def has_permission(user_id: int, guild_permissions, required_permission: str = "administrator") -> bool:
    """
    Check if a user has the required permission.
    
    Args:
        user_id: The Discord user ID
        guild_permissions: The user's guild permissions object
        required_permission: The permission to check (default: "administrator")
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Superusers have all permissions
    if is_superuser(user_id):
        logger.info(f"User {user_id} is superuser - granting all permissions")
        return True
    
    # Check guild permissions
    if hasattr(guild_permissions, required_permission):
        has_perm = getattr(guild_permissions, required_permission)
        logger.info(f"User {user_id} has {required_permission}: {has_perm}")
        return has_perm
    
    logger.warning(f"Unknown permission: {required_permission}")
    return False 
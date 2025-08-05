"""
Error handling utilities for Discord Knowledge Bot.
Provides consistent error logging and handling across the project.
"""

import logging
import traceback
import sys
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def log_error_with_context(error: Exception, context: str = "", additional_info: dict = None) -> None:
    """
    Log an error with full context including traceback and additional information.
    
    Args:
        error: The exception that occurred
        context: Human-readable context about where the error occurred
        additional_info: Optional dictionary of additional debugging information
    """
    logger.error(f"Error in {context}: {error}")
    logger.error(f"Error type: {type(error).__name__}")
    logger.error(f"Error occurred at line {error.__traceback__.tb_lineno if error.__traceback__ else 'unknown'}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    
    if additional_info:
        logger.error(f"Additional context: {additional_info}")

def handle_async_errors(func: Callable) -> Callable:
    """
    Decorator to handle async function errors with consistent logging.
    
    Args:
        func: The async function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            context = f"{func.__module__}.{func.__name__}"
            log_error_with_context(e, context)
            raise
    return wrapper

def handle_sync_errors(func: Callable) -> Callable:
    """
    Decorator to handle sync function errors with consistent logging.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"{func.__module__}.{func.__name__}"
            log_error_with_context(e, context)
            raise
    return wrapper

def safe_execute(func: Callable, *args, default_return: Any = None, context: str = "", **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        default_return: Value to return if function fails
        context: Context string for error logging
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Function result or default_return if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error_with_context(e, context)
        return default_return

async def safe_execute_async(func: Callable, *args, default_return: Any = None, context: str = "", **kwargs) -> Any:
    """
    Safely execute an async function with error handling.
    
    Args:
        func: Async function to execute
        default_return: Value to return if function fails
        context: Context string for error logging
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Function result or default_return if error occurs
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        log_error_with_context(e, context)
        return default_return

def validate_object(obj: Any, required_attrs: list, context: str = "") -> bool:
    """
    Validate that an object has required attributes.
    
    Args:
        obj: Object to validate
        required_attrs: List of required attribute names
        context: Context string for error logging
        
    Returns:
        True if object has all required attributes, False otherwise
    """
    missing_attrs = []
    for attr in required_attrs:
        if not hasattr(obj, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        logger.warning(f"Object missing required attributes in {context}: {missing_attrs}")
        logger.warning(f"Object type: {type(obj)}")
        logger.warning(f"Object content: {obj}")
        return False
    
    return True 
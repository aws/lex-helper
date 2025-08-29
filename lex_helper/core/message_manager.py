"""
Message Manager for Lex Helper Library.

This module provides centralized message management for Lambda functions
using the lex-helper library. It loads messages from a YAML file in the
Lambda function's directory structure.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class MessageManager:
    """
    Singleton class for managing messages from YAML files with locale support.
    
    Automatically loads messages from locale-specific files:
    - messages_{localeId}.yaml (e.g., messages_en_US.yaml, messages_es_ES.yaml)
    - Falls back to messages.yaml if locale-specific file not found
    
    Search locations:
    1. Custom path from MESSAGES_YAML_PATH environment variable
    2. Lambda function root directory
    3. Common subdirectories: messages/, config/, resources/, data/
    4. Relative paths from current working directory
    """
    _messages: Dict[str, Dict[str, str]] = {}  # {locale: messages}
    _current_locale: str = "en_US"
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def _load_messages(cls, locale: str = None) -> None:
        """Load messages from YAML file for specified locale."""
        if locale is None:
            locale = cls._current_locale
            
        try:
            # Generate search paths for locale-specific and fallback files
            base_dirs = [
                Path(os.getcwd()),
                Path(os.getcwd()) / 'messages',
                Path(os.getcwd()) / 'config',
                Path(os.getcwd()) / 'resources',
                Path(os.getcwd()) / 'data',
                Path('.'),
                Path('messages'),
                Path('config'),
                Path('resources'),
                Path('data'),
            ]
            
            # Check environment variable for custom directory
            custom_path = os.environ.get('MESSAGES_YAML_PATH')
            if custom_path:
                base_dirs.insert(0, Path(custom_path))
            
            # Try locale-specific file first, then fallback to default
            filenames = [f'messages_{locale}.yaml', 'messages.yaml']
            
            yaml_path = None
            for base_dir in base_dirs:
                for filename in filenames:
                    path = base_dir / filename
                    if path.exists():
                        yaml_path = path
                        break
                if yaml_path:
                    break
            
            if yaml_path:
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    messages = yaml.safe_load(file) or {}
                cls._messages[locale] = messages
                logger.info(f"Messages loaded for locale '{locale}' from {yaml_path}")
            else:
                logger.warning(f"No messages file found for locale '{locale}', using empty message store")
                cls._messages[locale] = {}
                
        except Exception as e:
            logger.error(f"Failed to load messages for locale '{locale}': {str(e)}")
            cls._messages[locale] = {}
    
    @classmethod
    def set_locale(cls, locale: str) -> None:
        """Set the current locale and load messages for it."""
        cls._current_locale = locale
        if locale not in cls._messages:
            cls._load_messages(locale)
    
    @classmethod
    def get_message(cls, key: str, default: Optional[str] = None, locale: str = None) -> str:
        """
        Get message by key, supporting nested keys with dot notation.
        
        Args:
            key: Message key to lookup (e.g., "agent.confirmation")
            default: Optional default value if key not found
            locale: Optional locale override (uses current locale if not specified)
            
        Returns:
            The message string
            
        Example:
            >>> MessageManager.set_locale("en_US")
            >>> MessageManager.get_message("greeting")
            "Hello! How can I assist you today?"
            
            >>> MessageManager.get_message("greeting", locale="es_ES")
            "¡Hola! ¿Cómo puedo ayudarte hoy?"
        """
        try:
            target_locale = locale or cls._current_locale
            
            # Load messages for locale if not already loaded
            if target_locale not in cls._messages:
                cls._load_messages(target_locale)
            
            # Handle nested keys with dot notation
            keys = key.split('.')
            value = cls._messages.get(target_locale, {})
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    value = None
                    break
            
            if value is None:
                if default is not None:
                    logger.debug(f"Message key not found: {key} for locale {target_locale}, using default")
                    return default
                logger.warning(f"Message key not found: {key} for locale {target_locale}")
                return f"Message not found: {key}"
                
            return str(value)
            
        except Exception as e:
            logger.error(f"Error getting message for key {key}: {str(e)}")
            return default if default is not None else f"Error getting message: {key}"
    
    @classmethod
    def reload_messages(cls) -> None:
        """Reload messages from YAML file."""
        cls._load_messages()
    
    @classmethod
    def get_all_messages(cls) -> Dict[str, str]:
        """Get all loaded messages."""
        if not cls._messages:
            cls._load_messages()
        return cls._messages.copy()


# Convenience functions for easy import
def set_locale(locale: str) -> None:
    """Set the current locale for message loading."""
    MessageManager.set_locale(locale)

def get_message(key: str, default: Optional[str] = None, locale: str = None) -> str:
    """
    Convenience function to get a message.
    
    Args:
        key: Message key to lookup
        default: Optional default value if key not found
        locale: Optional locale override
        
    Returns:
        The message string
    """
    return MessageManager.get_message(key, default, locale)
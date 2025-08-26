# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Text formatting utilities."""

import re
from typing import Dict, Optional


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text.
    
    Args:
        text: Text containing HTML tags
        
    Returns:
        Clean text with HTML tags removed
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def replace_special_characters(text: str, replacement: Optional[str] = None) -> str:
    """Replace special characters in text.
    
    Args:
        text: Text containing special characters
        replacement: Character to use as replacement (defaults to empty string)
        
    Returns:
        Text with special characters replaced
    """
    if replacement is None:
        replacement = ''
    return re.sub(r'[^a-zA-Z0-9\s]', replacement, text)


def substitute_keys_in_text(text: str, substitutions: Dict[str, str]) -> str:
    """Substitute keys in text with their values.
    
    Args:
        text: Text containing keys to substitute
        substitutions: Dictionary of key-value pairs for substitution
        
    Returns:
        Text with keys replaced by their values
    
    Example:
        >>> text = "Hello {name}!"
        >>> subs = {"name": "World"}
        >>> substitute_keys_in_text(text, subs)
        'Hello World!'
    """
    result = text
    for key, value in substitutions.items():
        pattern = r'\{' + re.escape(key) + r'\}'
        result = re.sub(pattern, str(value), result)
    return result


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of resulting text (including suffix)
        suffix: String to append to truncated text
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Replaces multiple spaces, tabs, and newlines with single spaces
    and strips leading/trailing whitespace.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    return ' '.join(text.split())


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    # Basic sentence splitting - could be enhanced for edge cases
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]  # Remove empty strings

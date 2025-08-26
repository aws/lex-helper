# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""URL formatting utilities."""

from typing import Optional
from urllib.parse import ParseResult, urlparse, urlunparse


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url: str, default_scheme: str = "https") -> str:
    """Normalize a URL by adding scheme if missing.
    
    Args:
        url: URL to normalize
        default_scheme: Scheme to add if missing (default: "https")
        
    Returns:
        Normalized URL
    """
    if not url:
        return url
    
    try:
        result = urlparse(url)
        if not result.scheme:
            # Add scheme if missing
            url = f"{default_scheme}://{url}"
            result = urlparse(url)
        return urlunparse(result)
    except:
        return url


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name or None if URL is invalid
    """
    try:
        result = urlparse(url)
        return result.netloc or None
    except:
        return None


def build_url(
    scheme: str,
    netloc: str,
    path: str = "",
    params: str = "",
    query: str = "",
    fragment: str = "",
) -> str:
    """Build a URL from components.
    
    Args:
        scheme: URL scheme (e.g., "https")
        netloc: Network location/hostname
        path: URL path
        params: URL parameters
        query: Query string
        fragment: Fragment identifier
        
    Returns:
        Complete URL
    """
    components = ParseResult(
        scheme=scheme,
        netloc=netloc,
        path=path,
        params=params,
        query=query,
        fragment=fragment,
    )
    return urlunparse(components)


def clean_url(url: str) -> str:
    """Clean a URL by removing unnecessary components.
    
    Removes fragments, normalizes scheme, ensures single slashes.
    
    Args:
        url: URL to clean
        
    Returns:
        Cleaned URL
    """
    try:
        result = urlparse(url)
        cleaned = ParseResult(
            scheme=result.scheme or "https",
            netloc=result.netloc,
            path=result.path.replace('//', '/'),
            params=result.params,
            query=result.query,
            fragment='',  # Remove fragment
        )
        return urlunparse(cleaned)
    except:
        return url

"""Test version accessibility."""

import re


def test_version_is_accessible():
    """Test that __version__ is accessible from the package."""
    import lex_helper
    
    assert hasattr(lex_helper, '__version__')
    assert isinstance(lex_helper.__version__, str)
    assert len(lex_helper.__version__) > 0


def test_version_format():
    """Test that __version__ follows semantic versioning format."""
    import lex_helper
    
    # Basic semantic versioning pattern (allows pre-release suffixes)
    version_pattern = r'^\d+\.\d+\.\d+(?:[a-zA-Z0-9\-\.]+)?$'
    assert re.match(version_pattern, lex_helper.__version__), f"Version {lex_helper.__version__} doesn't match expected format"


def test_version_in_all():
    """Test that __version__ is exported in __all__."""
    import lex_helper
    
    assert '__version__' in lex_helper.__all__
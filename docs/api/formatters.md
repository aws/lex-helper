# Formatters API

The formatters module provides utilities for formatting messages, handling text processing, creating interactive elements like buttons, and managing URLs. These utilities help create well-formatted responses across different channels.

## Text Formatting

Utilities for processing and formatting text content.

::: lex_helper.formatters.text
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Button Formatting

Create interactive buttons and quick replies for supported channels.

### Single Button

::: lex_helper.formatters.button
    options:
      filters: ["!^_"]
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Multiple Buttons

::: lex_helper.formatters.buttons
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Button Formatting Utilities

::: lex_helper.formatters.format_buttons
    options:
      filters: ["!^_"]
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## URL Handling

Utilities for processing and formatting URLs.

### URL Formatting

::: lex_helper.formatters.url
    options:
      filters: ["!^_"]
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### URL Validation

::: lex_helper.formatters.is_valid_url
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

### URL Conversion

::: lex_helper.formatters.string_to_http_url
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

## Text Processing Utilities

Additional text processing and cleaning utilities.

### HTML Tag Removal

::: lex_helper.formatters.remove_html_tags
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

### Special Character Handling

::: lex_helper.formatters.replace_special_characters
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

### Template Substitution

::: lex_helper.formatters.substitute_keys_in_text
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

## Usage Examples

### Text Formatting

```python
from lex_helper.formatters.text import remove_html_tags, substitute_keys_in_text

# Clean HTML from text
clean_text = remove_html_tags("<p>Hello <b>world</b>!</p>")
# Result: "Hello world!"

# Substitute variables in text
template = "Hello {name}, your order #{order_id} is ready!"
substitutions = {"name": "Alice", "order_id": "12345"}
message = substitute_keys_in_text(template, substitutions)
# Result: "Hello Alice, your order #12345 is ready!"
```

### Button Creation

```python
from lex_helper.formatters.buttons import create_buttons
from lex_helper.formatters.button import create_button

# Create a single button
button = create_button("Click me", "button_value")

# Create multiple buttons
buttons = create_buttons([
    ("Option 1", "value1"),
    ("Option 2", "value2"),
    ("Option 3", "value3")
])
```

### URL Processing

```python
from lex_helper.formatters.url import format_url
from lex_helper.formatters.is_valid_url import is_valid_url

# Validate URL
if is_valid_url("https://example.com"):
    formatted = format_url("https://example.com", "Visit Example")
```

## Channel Compatibility

Different formatters work with different channels:

- **Text formatters**: Work with all channels
- **Button formatters**: Work with Lex and web channels, fallback to text for SMS
- **URL formatters**: Automatically adapt based on channel capabilities

---

**Next**: Explore the [Exceptions API](exceptions.md) for error handling utilities.

# Channels API

The channels module provides functionality for formatting responses across different communication channels like SMS, web chat, and voice interfaces. Each channel has specific constraints and capabilities that are handled automatically.

## Overview

lex-helper supports multiple channels with automatic formatting based on the channel's capabilities:

- **SMS**: Text-only with length constraints and link handling
- **Web/Lex**: Rich formatting with buttons, cards, and media
- **Voice**: Speech-optimized responses with SSML support

## Channel Formatting

The main entry point for channel-aware formatting.

::: lex_helper.channels.channel_formatting
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Base Channel

Abstract base class for all channel implementations.

::: lex_helper.channels.base
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Lex Channel

Default Lex channel with full rich formatting support.

::: lex_helper.channels.lex
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## SMS Channel

SMS-specific formatting with text constraints and optimizations.

::: lex_helper.channels.sms
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Usage Examples

### Basic Channel Formatting

```python
from lex_helper.channels.channel_formatting import format_for_channel
from lex_helper.core.types import LexResponse

# Create a response
response = LexResponse(...)

# Format for SMS (will strip rich formatting)
sms_response = format_for_channel(response, "sms")

# Format for web (preserves rich formatting)
web_response = format_for_channel(response, "lex")
```

### Channel-Specific Responses

```python
from lex_helper.channels.sms import SmsChannel
from lex_helper.channels.lex import LexChannel

# SMS channel automatically handles text length limits
sms_channel = SmsChannel()
formatted_sms = sms_channel.format_response(response)

# Lex channel supports rich formatting
lex_channel = LexChannel()
formatted_lex = lex_channel.format_response(response)
```

## Channel Detection

The library automatically detects the channel from the Lex request and applies appropriate formatting. You can also explicitly specify the channel when needed.

---

**Next**: Explore the [Formatters API](formatters.md) for message formatting utilities.

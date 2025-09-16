# Core API

The core module contains the main functionality for handling Amazon Lex requests, managing dialog state, and processing session attributes. This is where you'll find the primary `LexHelper` class and essential utilities.

## Main Handler

### LexHelper

::: lex_helper.core.handler.LexHelper
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true

### Configuration

::: lex_helper.core.handler.Config
    options:
      show_root_heading: true
      show_source: true
      show_signature_annotations: true
      separate_signature: true

## Dialog Utilities

The dialog module provides essential functions for managing conversation flow and dialog state.

::: lex_helper.core.dialog
    options:
      filters: ["!^_", "!^PydanticEncoder"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Session Management

Session attributes provide type-safe state management across conversation turns.

::: lex_helper.core.session
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Type Definitions

Core type definitions used throughout the library.

::: lex_helper.core.types
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source
      show_inheritance_diagram: false

## Disambiguation

Smart disambiguation functionality for handling ambiguous user input using AI.

### Disambiguation Handler

::: lex_helper.core.disambiguation.handler
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Disambiguation Analyzer

::: lex_helper.core.disambiguation.analyzer
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Bedrock Generator

::: lex_helper.core.disambiguation.bedrock_generator
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Disambiguation Types

::: lex_helper.core.disambiguation.types
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Utility Functions

Additional core utilities for common operations.

### Intent Name Utilities

::: lex_helper.core.intent_name
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

### Bedrock Integration

::: lex_helper.core.invoke_bedrock
    options:
      filters: ["!^_"]
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Message Manager

::: lex_helper.core.message_manager
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

### Logging Utilities

::: lex_helper.core.logging_utils
    options:
      show_root_heading: false
      show_signature_annotations: true
      separate_signature: true

---

**Next**: Explore the [Channels API](channels.md) for channel-specific formatting functionality.
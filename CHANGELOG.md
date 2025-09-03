# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-01-03

### Added

- **Core Features**
  - Type-safe session attributes with Pydantic models
  - Simplified intent management with automatic file-based routing
  - Comprehensive dialog utilities (get_intent, get_slot, set_slot, elicit_intent, etc.)
  - Channel-aware formatting for SMS, Lex console, and other channels
  - Automatic request/response handling for Lex fulfillment lambdas

- **Message Management**
  - Centralized message management with locale support
  - YAML-based message files with automatic fallback
  - Support for multiple locales (messages_{localeId}.yaml)

- **Bedrock Integration**
  - Direct integration with Amazon Bedrock models
  - Support for multiple model families (Claude, Titan, Jurassic, Cohere, Llama)
  - Converse API and InvokeModel API support
  - Automatic fallback between on-demand and inference profile modes

- **Developer Experience**
  - Full type hint support with py.typed
  - Comprehensive error handling and exception management
  - Modern Python tooling (uv, ruff, pytest)
  - Extensive documentation and examples

- **Package Infrastructure**
  - Professional PyPI package with comprehensive metadata
  - Automated CI/CD with GitHub Actions
  - Dynamic version management
  - Optional dependencies for flexible installation

### Documentation

- Complete README with quick start guide
- Best practices guide
- Testing guide
- Lambda layer deployment guide
- Development and migration guides
- Comprehensive examples including sample airline bot

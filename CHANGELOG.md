# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 0.0.2

### Added

- **Enhanced Exception Handling**
  - Enhanced `handle_exceptions` function with optional custom error messages
  - Support for both message keys and direct strings in error handling
  - Automatic localization fallback when message keys are not found
  - Comprehensive unit tests for exception handling scenarios

- **Automatic Message Manager Initialization**
  - Added `auto_initialize_messages` configuration option to Config class
  - Automatic MessageManager initialization with locale from Lex request
  - Eliminates need for manual `initialize_message_manager()` calls in Lambda functions
  - Graceful error handling for MessageManager initialization failures

- **Automatic Exception Handling in Lambda Functions**
  - Added `auto_handle_exceptions` configuration option to Config class
  - Automatic exception handling and error response generation
  - Custom error message configuration via `error_message` parameter
  - Eliminates need for try/catch blocks in Lambda functions
  - Maintains proper Lex response formatting for all error scenarios

- **Message Consistency Testing Framework**
  - Comprehensive test suite for message key consistency across locales
  - Validates all YAML message files have identical keys
  - Parameter consistency validation for message templates
  - Placeholder detection to prevent incomplete translations
  - Required message category validation
  - Integration with existing test infrastructure

- **Dynamic Locale Detection in CDK**
  - Automatic locale detection based on Lex bot export structure
  - Dynamic generation of bot locale configurations
  - Eliminates hardcoded locale lists in CDK stack
  - Reads confidence thresholds from BotLocale.json files
  - Automatic fallback to en_US if no locales detected

- **Enhanced Deployment Scripts**
  - Improved deployment script with better error handling
  - Automatic cleanup of old wheel files to prevent hash conflicts
  - Targeted uv cache cleaning for specific packages
  - Lock file regeneration to avoid dependency conflicts
  - Validation of required tools and directory structure

### Changed

- **Dependency Management Migration**
  - Migrated sample airline bot from Poetry to uv for faster dependency resolution and installation
  - Updated `pyproject.toml` to use PEP 621 standard format instead of Poetry-specific configuration
  - Replaced `poetry.lock` with `uv.lock` for dependency locking
  - Updated CDK bundling configuration to automatically detect and use uv for Lambda packaging
  - Modified deployment scripts to use `uv sync` instead of `poetry lock`

- **Simplified Lambda Function Structure**
  - Reduced Lambda function boilerplate by ~50% through automatic handling
  - Eliminated manual MessageManager initialization calls
  - Removed manual exception handling try/catch blocks
  - Streamlined configuration through enhanced Config class

- **Enhanced Config Class**
  - Added `auto_initialize_messages` (default: True)
  - Added `auto_handle_exceptions` (default: True)
  - Added `error_message` for custom error message configuration
  - Maintains backward compatibility with existing configurations

### Fixed

- **Exception Handling Improvements**
  - Fixed SessionState validation errors in error responses
  - Improved error message localization with proper fallbacks
  - Enhanced error response formatting for all channels

- **Deployment Reliability**
  - Fixed hash mismatch issues in uv dependency resolution
  - Improved wheel file management in deployment pipeline
  - Enhanced error handling in deployment scripts

### Technical Details

- Changed build system from `poetry-core` to `hatchling` for better PEP 621 compatibility
- Updated Python version constraints to be compatible with all dependencies (`>=3.12,<4.0`)
- Configured CDK `PythonFunction` and `PythonLayerVersion` to properly detect uv configuration
- Added comprehensive test coverage for new exception handling features
- Implemented dynamic locale detection using filesystem scanning
- Enhanced error response creation with proper Lex formatting
- Maintained all existing functionality while improving developer experience

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

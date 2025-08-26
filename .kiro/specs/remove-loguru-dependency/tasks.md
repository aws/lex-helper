# Implementation Plan

- [x] 1. Create logging infrastructure module
  - Create `lex_helper/core/logging_config.py` with centralized logger configuration
  - Implement context management using ContextVar for session information
  - Create structured logger adapter that mimics Loguru functionality
  - Add comprehensive unit tests for logging configuration and context management
  - _Requirements: 2.1, 2.2, 3.1, 3.2_

- [x] 2. Implement context filter and structured logging
  - Create `SessionContextFilter` class to add session context to log records
  - Implement context setter and getter functions for session data
  - Add structured logging formatter that includes session information
  - Write tests to verify context propagation and filtering
  - _Requirements: 2.3, 2.4, 3.1_

- [x] 3. Replace Loguru in call_handler_for_file.py
  - Remove `from loguru import logger` import
  - Import and configure native Python logger using new logging infrastructure
  - Replace all `logger.debug()`, `logger.error()`, and `logger.exception()` calls
  - Ensure exception logging maintains stack trace information
  - _Requirements: 1.1, 2.1, 2.2, 4.1_

- [x] 4. Replace Loguru in callback_original_intent_handler.py
  - Remove Loguru import and replace with native logging
  - Update all logging calls to use new logger instance
  - Maintain debug level logging for callback event handling
  - Preserve existing log message content and formatting
  - _Requirements: 1.1, 2.1, 4.1_

- [x] 5. Replace Loguru in call_method_for_file.py
  - Remove Loguru import and implement native logging
  - Replace `logger.exception()` and `logger.error()` calls
  - Ensure error handling and exception logging behavior is preserved
  - Update import error logging to maintain same information level
  - _Requirements: 1.1, 2.1, 2.2, 4.1_

- [ ] 6. Replace Loguru in make_request.py
  - Remove Loguru import and configure native logger
  - Replace `logger.error()` calls in error handling functions
  - Maintain JSON error logging format and content
  - Preserve error message structure and information
  - _Requirements: 1.1, 2.1, 4.1_

- [ ] 7. Replace Loguru in handler.py with context management
  - Remove Loguru import and implement native logging with context support
  - Replace `logger.contextualize()` with new context management system
  - Update all logging calls (trace, debug, exception) to use native logger
  - Implement session context setting in the handler method
  - Ensure context propagation throughout the request lifecycle
  - _Requirements: 1.1, 2.1, 2.3, 2.4, 4.1_

- [ ] 8. Update project dependencies
  - Remove `loguru (>=0.7.3,<0.8.0)` from pyproject.toml dependencies
  - Run `poetry lock --no-update` to update poetry.lock file
  - Verify no remaining Loguru references in dependency files
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 9. Create integration tests for logging behavior
  - Write tests that verify logging output matches expected format
  - Test context propagation through the complete request flow
  - Validate exception logging includes proper stack traces
  - Test logging behavior with and without session context
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 10. Validate migration and run existing tests
  - Run existing test suite to ensure no regressions
  - Verify all logging functionality works as expected
  - Test that public APIs remain unchanged
  - Confirm backward compatibility is maintained
  - _Requirements: 4.1, 4.2, 4.3, 4.4_
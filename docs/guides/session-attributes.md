# Session Attributes

Master type-safe session attribute management with lex-helper. This guide covers how to define, use, and manage session state with full type safety and validation.

## Overview

Session attributes in lex-helper are built on Pydantic models, providing type safety, validation, and excellent IDE support. Unlike raw Lex session attributes (which are just string key-value pairs), lex-helper session attributes are strongly typed and validated at runtime.

## Defining Session Attributes

### Basic Session Attributes

Create a custom session attributes class by inheriting from `SessionAttributes`. These attributes should be global to your entire chatbot, not specific to individual intents:

```python
from lex_helper import SessionAttributes

class ChatbotSessionAttributes(SessionAttributes):
    # User identification and authentication
    user_id: str = ""
    user_name: str = ""
    user_authenticated: bool = False
    
    # User preferences (global across all intents)
    preferred_language: str = "en"
    notification_preferences: dict[str, bool] = {}
    
    # Current conversation context
    current_intent_category: str = ""  # "booking", "support", "account"
    conversation_step: str = "initial"
    
    # Temporary data that any intent might need
    temp_data: dict[str, str] = {}
    
    # Error tracking
    error_count: int = 0
    last_error_intent: str = ""
```

### Advanced Type Definitions

Use Pydantic's advanced features for complex validation:

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field, validator

class UserRole(str, Enum):
    GUEST = "guest"
    MEMBER = "member"
    PREMIUM = "premium"
    ADMIN = "admin"

class ConversationState(str, Enum):
    GREETING = "greeting"
    COLLECTING_INFO = "collecting_info"
    PROCESSING = "processing"
    CONFIRMING = "confirming"
    COMPLETED = "completed"

class ChatbotSessionAttributes(SessionAttributes):
    # User information with validation
    user_email: str = Field(default="", regex=r'^[^@]+@[^@]+\.[^@]+$')
    user_role: UserRole = UserRole.GUEST
    
    # Conversation state management
    conversation_state: ConversationState = ConversationState.GREETING
    
    # Session timing
    session_start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_activity_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # User preferences
    contact_preferences: dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "sms": False,
        "phone": False
    })
    
    @validator('user_email')
    def validate_email_format(cls, v):
        if v and '@' not in v:
            raise ValueError('Please provide a valid email address')
        return v.lower() if v else v
    
    @validator('last_activity_time', always=True)
    def update_activity_time(cls, v):
        return datetime.now().isoformat()
```

### Configuration Options

Configure your session attributes with Pydantic's `ConfigDict`:

```python
from pydantic import ConfigDict

class ChatbotSessionAttributes(SessionAttributes):
    model_config = ConfigDict(
        # Allow extra fields for flexibility (useful for dynamic data)
        extra="allow",
        # Validate on assignment (catch errors immediately)
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Exclude None values when serializing
        exclude_none=True
    )
    
    # Core chatbot attributes
    user_id: str = ""
    current_flow: str = ""
    temp_storage: dict[str, str] = {}
```

## Using Session Attributes

### In Intent Handlers

Access session attributes with full type safety in your intent handlers. All intents share the same global session attributes:

```python
def book_flight_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    # Type-safe access to global session attributes
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Check user authentication (used across all intents)
    if not session_attrs.user_authenticated:
        return redirect_to_authentication(lex_request)
    
    # Update conversation context
    session_attrs.current_intent_category = "booking"
    session_attrs.conversation_step = "collecting_flight_info"
    
    # Store temporary data that other intents might need
    session_attrs.temp_data["booking_type"] = "flight"
    session_attrs.temp_data["departure_city"] = dialog.get_slot("DepartureCity", intent)
    
    return continue_booking_flow(lex_request)

def check_account_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    # Same session attributes, different intent
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Access user info set by other intents
    if session_attrs.user_role == UserRole.GUEST:
        return prompt_for_account_creation(lex_request)
    
    # Update context for this intent
    session_attrs.current_intent_category = "account"
    
    return show_account_info(lex_request)
```

### Updating Session Attributes

Session attributes are automatically serialized and persisted across all intents:

```python
def update_preferences_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Update global user preferences
    session_attrs.preferred_language = "es"
    session_attrs.user_role = UserRole.PREMIUM
    
    # Update notification preferences (used by multiple intents)
    session_attrs.notification_preferences.update({
        "booking_confirmations": True,
        "promotional_offers": False,
        "service_updates": True
    })
    
    # Store temporary data for other intents to use
    session_attrs.temp_data["last_preference_update"] = datetime.now().isoformat()
    
    # The changes are automatically persisted and available to all intents
    return dialog.close(
        messages=[LexPlainText(content="Your preferences have been updated!")],
        lex_request=lex_request
    )

def greeting_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Use preferences set by other intents
    language = session_attrs.preferred_language
    user_name = session_attrs.user_name or "there"
    
    # Personalize greeting based on global session state
    if session_attrs.user_role == UserRole.PREMIUM:
        greeting = f"Welcome back, {user_name}! As a premium member, you have priority access."
    else:
        greeting = f"Hello {user_name}! How can I help you today?"
    
    return dialog.close(
        messages=[LexPlainText(content=greeting)],
        lex_request=lex_request
    )
```

## Validation and Error Handling

### Automatic Validation

Pydantic automatically validates data types and constraints:

```python
class ChatbotSessionAttributes(SessionAttributes):
    user_email: str = Field(default="", regex=r'^[^@]+@[^@]+\.[^@]+$')
    error_count: int = Field(default=0, ge=0, le=10)  # Track errors, max 10
    user_role: UserRole = UserRole.GUEST

# This will raise a ValidationError
try:
    attrs = ChatbotSessionAttributes(
        error_count=15,  # Invalid: > 10
        user_email="invalid-email"  # Invalid: not an email
    )
except ValidationError as e:
    print(e.errors())
```

### Custom Validators

Add custom validation logic with Pydantic validators:

```python
from pydantic import validator, root_validator

class ChatbotSessionAttributes(SessionAttributes):
    user_name: str = ""
    user_email: str = ""
    preferred_language: str = "en"
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if v and len(v) < 2:
            raise ValueError('User name must be at least 2 characters')
        if v and not v.replace(' ', '').replace('-', '').isalpha():
            raise ValueError('User name must contain only letters, spaces, and hyphens')
        return v.title() if v else v
    
    @validator('preferred_language')
    def validate_language_code(cls, v):
        valid_languages = ['en', 'es', 'fr', 'de', 'it']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v
    
    @root_validator
    def validate_user_consistency(cls, values):
        user_name = values.get('user_name')
        user_email = values.get('user_email')
        user_role = values.get('user_role')
        
        # If user has premium role, they must have both name and email
        if user_role == UserRole.PREMIUM and (not user_name or not user_email):
            raise ValueError('Premium users must have both name and email')
        
        return values
```

### Handling Validation Errors

Handle validation errors gracefully in your handlers:

```python
def update_profile_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    try:
        session_attrs = lex_request.sessionState.sessionAttributes
        intent = lex_request.sessionState.intent
        
        # This might raise ValidationError
        session_attrs.user_name = dialog.get_slot("UserName", intent)
        session_attrs.user_email = dialog.get_slot("UserEmail", intent)
        session_attrs.preferred_language = dialog.get_slot("Language", intent)
        
        return confirm_profile_update(lex_request)
        
    except ValidationError as e:
        # Convert validation errors to user-friendly messages
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            message = error['msg']
            
            # Customize messages for better UX
            if 'user_email' in field:
                error_messages.append("Please provide a valid email address.")
            elif 'user_name' in field:
                error_messages.append("Name must be at least 2 characters and contain only letters.")
            elif 'preferred_language' in field:
                error_messages.append("Please choose from: English, Spanish, French, German, or Italian.")
            else:
                error_messages.append(f"{field}: {message}")
        
        return dialog.elicit_intent(
            messages=[LexPlainText(content=f"I need to correct some information: {', '.join(error_messages)}")],
            lex_request=lex_request
        )
```

## Advanced Patterns

### Nested Session Attributes

Create complex nested structures for sophisticated state management across your entire chatbot:

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    address: str = ""
    date_of_birth: str = ""

class NotificationSettings(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    frequency: str = "daily"  # daily, weekly, monthly

class ConversationHistory(BaseModel):
    last_intent: str = ""
    intent_count: dict[str, int] = {}
    successful_completions: int = 0
    error_count: int = 0

class ChatbotSessionAttributes(SessionAttributes):
    # Nested user profile (used across all intents)
    user_profile: UserProfile = UserProfile()
    
    # Global notification settings
    notifications: NotificationSettings = NotificationSettings()
    
    # Conversation tracking
    conversation_history: ConversationHistory = ConversationHistory()
    
    # Dynamic data storage for any intent
    intent_data: dict[str, dict[str, str]] = {}  # intent_name -> data

# Usage across different intent handlers
def book_flight_handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Use global user profile
    if not session_attrs.user_profile.first_name:
        return collect_user_info(lex_request)
    
    # Store booking-specific data in global intent_data
    session_attrs.intent_data["booking"] = {
        "type": "flight",
        "departure": dialog.get_slot("DepartureCity", intent),
        "arrival": dialog.get_slot("ArrivalCity", intent)
    }
    
    # Update conversation history
    session_attrs.conversation_history.last_intent = "BookFlight"
    session_attrs.conversation_history.intent_count["BookFlight"] = (
        session_attrs.conversation_history.intent_count.get("BookFlight", 0) + 1
    )

def support_handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Access user profile set by other intents
    user_name = session_attrs.user_profile.first_name or "there"
    
    # Check if user has notification preferences
    if session_attrs.notifications.email_enabled:
        return offer_email_support(lex_request, user_name)
    
    # Access previous booking data if available
    booking_data = session_attrs.intent_data.get("booking", {})
    if booking_data:
        return provide_booking_support(lex_request, booking_data)
```

### Session Attribute Inheritance

Create hierarchical session attribute structures for different chatbot environments:

```python
class BaseChatbotSessionAttributes(SessionAttributes):
    """Base attributes shared across all chatbot deployments."""
    user_id: str = ""
    session_id: str = ""
    preferred_language: str = "en"
    session_start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_authenticated: bool = False

class CustomerServiceSessionAttributes(BaseChatbotSessionAttributes):
    """Attributes for customer service chatbot."""
    customer_tier: str = "standard"  # standard, premium, vip
    case_number: str = ""
    agent_escalation_requested: bool = False
    satisfaction_rating: int = 0

class EcommerceChatbotSessionAttributes(BaseChatbotSessionAttributes):
    """Attributes for e-commerce chatbot."""
    cart_items: list[str] = []
    total_cart_value: float = 0.0
    checkout_step: str = ""
    payment_method: str = ""
    shipping_address: str = ""

# Use the appropriate session attributes for your chatbot type
class MyChatbotSessionAttributes(CustomerServiceSessionAttributes):
    """My specific chatbot inherits customer service capabilities."""
    # Add any additional attributes specific to your use case
    custom_field: str = ""
```

### Dynamic Session Attributes

Handle dynamic attributes with Pydantic's `extra="allow"`:

```python
class FlexibleSessionAttributes(SessionAttributes):
    model_config = ConfigDict(extra="allow")
    
    # Core attributes
    user_id: str = ""
    
    # Dynamic attributes can be added at runtime
    # session_attrs.custom_field = "value"
    # session_attrs.another_field = 123

def handler(lex_request: LexRequest[FlexibleSessionAttributes]) -> LexResponse[FlexibleSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Add dynamic attributes
    session_attrs.__dict__["dynamic_field"] = "dynamic_value"
    
    # Access with getattr for safety
    custom_value = getattr(session_attrs, "custom_field", "default")
```

## Best Practices

### 1. Use Descriptive Field Names

```python
# Good: Clear, global attributes
class ChatbotSessionAttributes(SessionAttributes):
    user_authenticated: bool = False
    current_conversation_topic: str = ""
    user_satisfaction_score: int = 0

# Avoid: Unclear or overly specific names
class ChatbotSessionAttributes(SessionAttributes):
    flag1: bool = False  # What does this flag represent?
    data: str = ""       # What kind of data?
    booking_departure_city: str = ""  # Too specific to one intent
```

### 2. Provide Sensible Defaults

```python
class ChatbotSessionAttributes(SessionAttributes):
    # Always provide defaults for optional fields
    user_name: str = ""
    preferred_language: str = "en"
    conversation_count: int = 0
    user_preferences: dict[str, str] = {}
    
    # Use Field for complex defaults
    session_start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    notification_settings: dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "sms": False,
        "push": True
    })
```

### 3. Use Type Hints Consistently

```python
from typing import Optional, List, Dict

class ChatbotSessionAttributes(SessionAttributes):
    # Use specific types
    conversation_count: int = 0
    user_preferences: Dict[str, str] = {}
    conversation_history: List[str] = []
    
    # Use Optional for truly optional fields
    user_feedback: Optional[str] = None
    last_error_message: Optional[str] = None
```

### 4. Validate Critical Data

```python
class ChatbotSessionAttributes(SessionAttributes):
    user_email: str = Field(default="", regex=r'^[^@]+@[^@]+\.[^@]+$')
    error_count: int = Field(default=0, ge=0, le=10)
    user_satisfaction_score: int = Field(default=0, ge=0, le=10)
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if v and len(v) < 2:
            raise ValueError('User name must be at least 2 characters')
        return v
    
    @validator('preferred_language')
    def validate_language(cls, v):
        valid_languages = ['en', 'es', 'fr', 'de']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v
```

### 5. Document Your Attributes

```python
class ChatbotSessionAttributes(SessionAttributes):
    """Global session attributes for the entire chatbot.
    
    These attributes persist across all intents and provide shared state
    for user authentication, preferences, and conversation tracking.
    """
    
    user_id: str = Field(
        default="",
        description="Unique identifier for the user across sessions"
    )
    
    user_authenticated: bool = Field(
        default=False,
        description="Whether the user has been authenticated"
    )
    
    conversation_count: int = Field(
        default=0,
        ge=0,
        description="Number of conversations in this session"
    )
    
    temp_data: dict[str, str] = Field(
        default_factory=dict,
        description="Temporary storage for data that any intent might need"
    )
```

## Configuration with LexHelper

Configure your global session attributes with the LexHelper class:

```python
from lex_helper import LexHelper, Config

# Create configuration with your global chatbot session attributes
config = Config(
    session_attributes=ChatbotSessionAttributes(),
    package_name="my_chatbot",
    auto_handle_exceptions=True
)

# Initialize LexHelper - all intents will use the same session attributes
lex_helper = LexHelper(config)

def lambda_handler(event, context):
    return lex_helper.handler(event, context)

# Example: All intent handlers use the same session attributes type
def book_flight_handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    # Access global session state
    pass

def check_account_handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    # Same session attributes, different intent
    pass

def support_handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    # All handlers share the same global session state
    pass
```

## Debugging Session Attributes

### Logging Session State

```python
import logging

logger = logging.getLogger(__name__)

def handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    intent_name = lex_request.sessionState.intent.name
    
    # Log current global session state
    logger.info("Session state for %s: %s", intent_name, session_attrs.model_dump(exclude_none=True))
    
    # Log specific global fields
    logger.debug("User context - authenticated: %s, language: %s, conversation_count: %d", 
                session_attrs.user_authenticated, 
                session_attrs.preferred_language,
                session_attrs.conversation_count)
    
    # Log intent-specific data if available
    intent_data = session_attrs.temp_data.get(f"{intent_name}_data", {})
    if intent_data:
        logger.debug("Intent-specific data for %s: %s", intent_name, intent_data)
```

### Session Attribute Inspection

```python
def debug_session_handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes
    
    # Get all non-empty global attributes
    active_attrs = {
        k: v for k, v in session_attrs.model_dump().items() 
        if v not in [None, "", 0, False, [], {}]
    }
    
    # Create user-friendly debug message
    debug_info = []
    debug_info.append(f"User: {session_attrs.user_name or 'Anonymous'}")
    debug_info.append(f"Authenticated: {session_attrs.user_authenticated}")
    debug_info.append(f"Language: {session_attrs.preferred_language}")
    debug_info.append(f"Conversations: {session_attrs.conversation_count}")
    
    if session_attrs.temp_data:
        debug_info.append(f"Temp data: {len(session_attrs.temp_data)} items")
    
    debug_message = "Session Info: " + " | ".join(debug_info)
    
    return dialog.close(
        messages=[LexPlainText(content=debug_message)],
        lex_request=lex_request
    )
```

## Related Topics

- **[Core Concepts](core-concepts.md)** - Understanding lex-helper architecture
- **[Intent Handling](intent-handling.md)** - Using session attributes in intent handlers
- **[Error Handling](error-handling.md)** - Handling validation and session errors
- **[API Reference](../api/core.md)** - Complete SessionAttributes API documentation

---

**Next**: Learn about [Intent Handling](intent-handling.md) patterns and organization.
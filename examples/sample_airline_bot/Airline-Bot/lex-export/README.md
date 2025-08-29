# Lex Bot Export

This directory contains the Amazon Lex V2 bot configuration exported from the AWS console. These files define the bot's structure, intents, slots, and conversation flows that work with the Lambda fulfillment function.

## Overview

The Lex bot export provides the complete conversational AI configuration for the Airline-Bot, including:
- Bot definition and settings
- Intent definitions with sample utterances
- Slot configurations and validation
- Conversation flows and dialog management
- Locale-specific configurations (English US)

## Directory Structure

```
lex-export/
├── Manifest.json                      # Export metadata and version info
└── LexBot/                            # Bot configuration root
    ├── Bot.json                       # Main bot definition and settings
    └── BotLocales/                    # Locale-specific configurations
        └── en_US/                     # English (US) locale
            ├── BotLocale.json         # Locale settings and configuration
            ├── Intents/               # Intent definitions
            │   ├── AnythingElse/      # Additional assistance intent
            │   ├── Authenticate/      # User authentication intent
            │   │   └── Slots/         # Authentication slot definitions
            │   ├── BookFlight/        # Flight booking intent
            │   │   ├── Slots/         # Booking slot definitions
            │   │   │   ├── DepartureDate/
            │   │   │   ├── DestinationCity/
            │   │   │   ├── NumberOfPassengers/
            │   │   │   ├── OriginCity/
            │   │   │   ├── ReturnDate/
            │   │   │   └── TripType/
            │   │   └── ConversationFlow.json
            │   ├── CancelFlight/      # Flight cancellation intent
            │   ├── ChangeFlight/      # Flight modification intent
            │   ├── FallbackIntent/    # Fallback for unrecognized input
            │   ├── FlightDelayUpdate/ # Flight status inquiry intent
            │   ├── Goodbye/           # Farewell intent
            │   ├── Greeting/          # Welcome intent
            │   └── TrackBaggage/      # Baggage tracking intent
            └── SlotTypes/             # Custom slot type definitions
                └── TripType/          # Trip type slot (one-way/round-trip)
```

## Key Components

### Bot Configuration (`Bot.json`)
- Bot name, description, and settings
- IAM role configuration for Lex service
- Session timeout and idle settings
- Data privacy and compliance settings

### Locale Configuration (`BotLocale.json`)
- Language and locale settings (en_US)
- NLU confidence thresholds
- Voice interaction settings
- Slot resolution strategy

### Intent Definitions
Each intent directory contains:
- **`Intent.json`**: Intent configuration, sample utterances, and fulfillment settings
- **`Slots/`**: Individual slot definitions with validation rules
- **`ConversationFlow.json`**: Dialog flow configuration (where applicable)

### Slot Configurations
Each slot defines:
- Slot type (built-in or custom)
- Validation rules and constraints
- Prompts for elicitation
- Sample values and synonyms

## Intent Overview

### Core Airline Intents
- **BookFlight**: Complete flight booking with authentication
- **CancelFlight**: Flight cancellation with reservation lookup
- **ChangeFlight**: Flight modification and rebooking
- **FlightDelayUpdate**: Real-time flight status information
- **TrackBaggage**: Baggage tracking and status updates

### Conversation Management Intents
- **Greeting**: Welcome users and explain capabilities
- **Goodbye**: Polite conversation closure
- **AnythingElse**: Offer additional assistance
- **Authenticate**: User authentication flow
- **FallbackIntent**: Handle unrecognized inputs gracefully

## Slot Types

### Built-in Slot Types Used
- **AMAZON.City**: Origin and destination cities
- **AMAZON.Date**: Departure and return dates
- **AMAZON.Number**: Number of passengers
- **AMAZON.AlphaNumeric**: Flight numbers and reservation codes

### Custom Slot Types
- **TripType**: One-way or round-trip selection

## Usage in Deployment

The Lex export is used during deployment by:

1. **Packaging Script** (`package-lex-export.sh`):
   - Compresses the export into a deployment-ready ZIP file
   - Validates the export structure and required files

2. **CloudFormation Template**:
   - References the packaged export for bot creation
   - Configures the bot with the Lambda fulfillment function
   - Sets up proper IAM roles and permissions

3. **Deployment Process**:
   - Uploads the export package to S3
   - Creates or updates the Lex bot using the export
   - Links the bot to the Lambda fulfillment function

## Modifying the Bot Configuration

### Making Changes
1. **AWS Console**: Make changes in the Lex console
2. **Export**: Export the updated bot configuration
3. **Replace Files**: Replace the contents of this directory
4. **Redeploy**: Run the deployment script to apply changes

### Best Practices
- **Version Control**: Commit export changes to track bot evolution
- **Testing**: Test changes in a development environment first
- **Documentation**: Update intent documentation when adding new features
- **Validation**: Ensure all required files are included in exports

## Integration with Lambda

The bot configuration is designed to work seamlessly with the Lambda fulfillment function:

- **Code Hooks**: Intents are configured to use Lambda for dialog management
- **Slot Validation**: Lambda handles custom validation logic
- **Session Management**: Bot passes session data to Lambda handlers
- **Error Handling**: Fallback intents route to Lambda for graceful error handling

## Troubleshooting

### Common Issues
1. **Export Validation Errors**: Ensure all required files are present
2. **Intent Configuration**: Verify Lambda function ARN in intent settings
3. **Slot Type Mismatches**: Check slot type definitions match Lambda expectations
4. **Locale Settings**: Ensure locale configuration matches deployment region

### Validation
```bash
# Validate export structure
find lex-export/ -name "*.json" | wc -l  # Should show multiple JSON files

# Check for required files
ls lex-export/Manifest.json
ls lex-export/LexBot/Bot.json
```

## Version Information

This export is compatible with:
- **Amazon Lex V2** (not V1)
- **English (US)** locale
- **Lambda fulfillment** with lex_helper framework
- **CloudFormation** deployment automation

For deployment instructions, see the main [README.md](../README.md) and [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md).
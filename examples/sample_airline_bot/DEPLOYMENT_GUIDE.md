# Airline Bot Deployment Guide

This guide provides instructions for deploying the Airline Bot, including the Lambda function, Lambda layer, and Lex bot.

## Overview

The Airline Bot deployment consists of several components:

1. **Lambda Layer**: Contains the lex_helper module and its dependencies
2. **Lambda Function**: Handles the fulfillment logic for the Lex bot
3. **Lex Bot**: The conversational interface for airline-related tasks

## Prerequisites

- AWS CLI installed and configured with appropriate permissions
- Python 3.12 or later installed (to match the Lambda runtime)
- Docker installed (for building the Lambda layer with compatible dependencies)
- An S3 bucket for storing deployment artifacts
- IAM permissions to create and manage roles, Lambda functions, and Lex bots

## Deployment Options

### Option 1: All-in-One Deployment

The enhanced `deploy_airline_bot.sh` script handles the entire deployment process:

```bash
cd cloudformation
./deploy_airline_bot.sh [bot-alias-name]
```

This script will:
1. Package the Lambda layer with the lex_helper module and its dependencies
2. Package the Lambda function
3. Package the Lex bot export
4. Upload all artifacts to S3
5. Clean up any existing resources
6. Deploy the CloudFormation stack

### Option 2: Step-by-Step Deployment

If you prefer to deploy each component separately:

#### 1. Package the Lambda Layer

```bash
cd cloudformation/scripts
./package-lex-helper-layer.sh
```

This creates `zip/lex_helper_layer.zip` with the lex_helper module and its dependencies.

#### 2. Package the Lambda Function

```bash
cd cloudformation/scripts
./package-lambda-function.sh
```

This creates `zip/AirlineBotAPGLambda.zip` with the Lambda function code.

#### 3. Package the Lex Bot Export

```bash
cd cloudformation/scripts
./package-lex-export.sh
```

This creates `zip/AirlineBot.zip` with the Lex bot export.

#### 4. Deploy the CloudFormation Stack

```bash
cd cloudformation
./deploy_airline_bot.sh [bot-alias-name]
```

## Troubleshooting

### IAM Role Issues

If you encounter IAM role issues during deployment:

1. Check the IAM role permissions in the AWS Console and ensure the role has the necessary permissions for Lambda execution and CloudWatch Logs.

2. Wait a few minutes for IAM changes to propagate before trying again.

### Lambda Layer Issues

If you encounter issues with the Lambda layer:

1. Check the CloudWatch logs for the Lambda function to see any import errors.

2. If you see an error like `No module named 'pydantic_core._pydantic_core'`, this indicates an issue with the pydantic dependency. We've provided three solutions:

   **Solution 1: Integrated Dependencies Approach (Recommended)**

   The project uses an integrated approach where dependencies are included in the lex-helper layer:
   ```bash
   cd cloudformation/scripts
   ./package-lex-helper-layer.sh
   ```

   This creates a layer with the lex-helper module and all necessary dependencies in one place, avoiding conflicts.
   The CloudFormation template has been updated to use this comprehensive layer.

   **Solution 2: Updated lex-helper Layer**

   The `package-lex-helper-layer.sh` script includes the necessary versions of pydantic and its dependencies:
   ```bash
   cd cloudformation/scripts
   ./package-lex-helper-layer.sh
   ```

   This script:
   - Uses the versions from the lex-helper requirements
   - Installs dependencies in the correct Lambda layer structure
   - Creates a properly structured layer zip file

4. If issues persist, you can try manually installing the dependencies:
   ```bash
   # Create a temporary directory with the correct structure
   mkdir -p temp_layer/python

   # Install pydantic and its dependencies with specific versions
   pip install annotated-types==0.7.0 colorama==0.4.6 \
       pydantic-core==2.27.2 pydantic==2.10.6 typing-extensions==4.12.2 \
       -t temp_layer/python

   # Install the lex_helper package
   pip install layers/lex-helper-v0.0.11.zip -t temp_layer/python --no-deps

   # Create the zip file
   cd temp_layer && zip -r ../zip/lex_helper_layer.zip .

   # Clean up
   cd .. && rm -rf temp_layer
   ```

### Lex Bot Import Issues

If you encounter issues with importing the Lex bot:

1. If you see an error like `There was an error importing the bot. Make sure that the name of each folder containing Bot matches the Bot name within the definition`, this indicates an issue with the folder structure of the Lex bot export.

2. The folder structure for the Lex bot export should be:
   ```
   BotName/
     Manifest.json
     BotName/
       Bot.json
       en_US/
         ...
   ```

3. The updated `package-lex-export.sh` script should fix this by:
   - Extracting the bot name from Bot.json
   - Creating the correct folder structure with the bot name
   - Copying the files to the appropriate locations

4. If issues persist, you can try manually creating the correct folder structure:
   ```bash
   # Get the bot name
   BOT_NAME=$(grep -o '"name":"[^"]*"' "lex-export/LexBot/Bot.json" | cut -d'"' -f4)

   # Create the folder structure
   mkdir -p temp_export/$BOT_NAME/$BOT_NAME

   # Copy the files
   cp lex-export/Manifest.json temp_export/$BOT_NAME/
   cp -r lex-export/LexBot/* temp_export/$BOT_NAME/$BOT_NAME/

   # Create the zip file
   cd temp_export && zip -r ../zip/AirlineBot.zip .

   # Clean up
   cd .. && rm -rf temp_export
   ```

### Deployment Failures

If the CloudFormation stack deployment fails:

1. Check the CloudFormation events for detailed error messages:
   ```bash
   aws cloudformation describe-stack-events --stack-name AirlineBotAPGNative --region us-east-1
   ```

2. Make sure all required files are properly uploaded to S3.

## Testing the Deployment

After successful deployment, you can test the Lambda function:

```bash
aws lambda invoke --function-name AirlineBotAPGNative-AirlineBotFulfillment --payload file://test-event.json output.json
```

## Additional Resources

- `layers/README.md`: Detailed guide for setting up the Lambda layer
- `test-event.json`: Sample test event for the Lambda function
- `cloudformation/scripts/`: Directory containing all deployment scripts
- `cloudformation/airline-bot-native-template.yaml`: CloudFormation template for deployment

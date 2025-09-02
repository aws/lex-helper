#!/bin/bash

# Enhanced script to deploy the Airline Bot using native AWS::Lex::Bot resource
# This script ensures proper packaging and deployment of all components
#
# Prerequisites:
# 1. AWS CLI installed and configured
# 2. S3 bucket created for deployment artifacts
# 3. Python 3.13 installed for Lambda layer packaging

# Display usage information
usage() {
  echo "Usage: $0 [bot-alias-name]"
  echo "  bot-alias-name: Optional name for the bot alias (default: ProductionAlias)"
  echo ""
  echo "Example: $0 prod"
}

# Check if help is requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  usage
  exit 0
fi

# Set variables
STACK_NAME="AirlineBotAPG"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_FILE="$SCRIPT_DIR/airline-bot-native-template.yaml"
S3_BUCKET="airlinebot-apg"  # S3 bucket name
REGION=$(aws configure get region || echo "us-east-1")  # Use configured region or default to us-east-1
BOT_ALIAS_NAME=${1:-"ProductionAlias"}  # Default to ProductionAlias if not provided

echo "========================================================"
echo "=== Airline Bot Deployment Script ======================"
echo "========================================================"
echo "Using bot alias name: $BOT_ALIAS_NAME"
echo "Using AWS region: $REGION"
echo "Using S3 bucket: $S3_BUCKET"

# Check if S3 bucket exists
echo "Checking if S3 bucket exists..."
if ! aws s3 ls "s3://$S3_BUCKET" --region $REGION >/dev/null 2>&1; then
  echo "Error: S3 bucket $S3_BUCKET does not exist or you don't have access to it."
  echo "Please create the bucket or specify an existing bucket."
  exit 1
fi


# Step 1: Package the Lambda layer
echo ""
echo "=== Step 1: Packaging the Lambda Layer ==="
if [ -f "$SCRIPT_DIR/scripts/package-lex-helper-layer.sh" ]; then
  echo "Packaging Lambda layer..."
  cd "$PROJECT_ROOT" && bash "$SCRIPT_DIR/scripts/package-lex-helper-layer.sh"
else
  echo "Error: package-lex-helper-layer.sh not found"
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/zip/lex_helper_layer.zip" ]; then
  echo "Error: Failed to create lex_helper_layer.zip"
  exit 1
fi



# Step 2: Package the Lambda function
echo ""
echo "=== Step 2: Packaging the Lambda Function ==="
if [ -f "$SCRIPT_DIR/scripts/package-lambda-function.sh" ]; then
  echo "Packaging Lambda function..."
  cd "$PROJECT_ROOT" && bash "$SCRIPT_DIR/scripts/package-lambda-function.sh"
else
  echo "Error: package-lambda-function.sh not found"
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/zip/AirlineBotAPGLambda.zip" ]; then
  echo "Error: Failed to create AirlineBotAPGLambda.zip"
  exit 1
fi

# Step 3: Package the Lex bot export
echo ""
echo "=== Step 3: Packaging the Lex Bot Export ==="
if [ -f "$SCRIPT_DIR/scripts/package-lex-export.sh" ]; then
  echo "Packaging Lex bot export..."
  cd "$SCRIPT_DIR" && bash "scripts/package-lex-export.sh"
else
  echo "Error: package-lex-export.sh not found"
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/zip/AirlineBot.zip" ]; then
  echo "Error: AirlineBot.zip not found. Please create it using package-lex-export.sh"
  exit 1
fi

# Step 4: Upload the files to S3
echo ""
echo "=== Step 4: Uploading Files to S3 ==="
echo "Uploading Lambda function..."
aws s3 cp "$PROJECT_ROOT/zip/AirlineBotAPGLambda.zip" "s3://$S3_BUCKET/" --region $REGION

echo "Uploading Lambda layer..."
aws s3 cp "$PROJECT_ROOT/zip/lex_helper_layer.zip" "s3://$S3_BUCKET/" --region $REGION

echo "Uploading Lex bot export..."
aws s3 cp "$PROJECT_ROOT/zip/AirlineBot.zip" "s3://$S3_BUCKET/" --region $REGION

# Step 5: Clean up existing resources
echo ""
echo "=== Step 5: Cleaning Up Existing Resources ==="


# Check if stack exists and delete it if it does
echo "Checking if stack $STACK_NAME exists..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &>/dev/null; then
  echo "Stack $STACK_NAME exists, deleting first..."
  aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
  echo "Waiting for stack deletion to complete..."
  aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION

  # Add a delay after stack deletion to ensure resources are fully cleaned up
  echo "Adding a delay to ensure all resources are fully deleted..."
  sleep 30
fi

# Manually delete the Lambda function if it exists to avoid "function already exists" error
LAMBDA_FUNCTION_NAME="${STACK_NAME}-AirlineBotFulfillment"
echo "Checking if Lambda function $LAMBDA_FUNCTION_NAME exists..."
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION &>/dev/null; then
  echo "Lambda function $LAMBDA_FUNCTION_NAME exists, deleting it..."
  aws lambda delete-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION
  echo "Waiting for Lambda deletion to complete..."
  sleep 15  # Increased delay to ensure Lambda is fully deleted
fi

# Step 6: Deploy the CloudFormation stack
echo ""
echo "=== Step 6: Deploying CloudFormation Stack ==="


# Check if stack exists after cleanup
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &>/dev/null; then
  echo "Stack $STACK_NAME exists, updating..."
  UPDATE_OUTPUT=$(aws cloudformation update-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters \
          ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
          ParameterKey=LexHelperLayerKey,ParameterValue=lex_helper_layer.zip \
          ParameterKey=LambdaFunctionKey,ParameterValue=AirlineBotAPGLambda.zip \
          ParameterKey=BotImportKey,ParameterValue=AirlineBot.zip \
          ParameterKey=BotAliasName,ParameterValue=$BOT_ALIAS_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION 2>&1)
  UPDATE_RESULT=$?
  if echo "$UPDATE_OUTPUT" | grep -q "No updates are to be performed"; then
    echo "No updates needed - stack is already up to date."
    STACK_ACTION="none"
  else
    STACK_ACTION="update"
  fi
else
  echo "Stack $STACK_NAME does not exist, creating..."
  aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters \
          ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
          ParameterKey=LexHelperLayerKey,ParameterValue=lex_helper_layer.zip \
          ParameterKey=LambdaFunctionKey,ParameterValue=AirlineBotAPGLambda.zip \
          ParameterKey=BotImportKey,ParameterValue=AirlineBot.zip \
          ParameterKey=BotAliasName,ParameterValue=$BOT_ALIAS_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION
  STACK_ACTION="create"
fi


# Check the result
if [ "$STACK_ACTION" = "none" ]; then
    echo "Stack is up to date."

    # Get outputs
    LAMBDA_FUNCTION_ARN=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionArn'].OutputValue" --output text)
    LAMBDA_FUNCTION_NAME=$(echo $LAMBDA_FUNCTION_ARN | awk -F':' '{print $NF}')

    echo ""
    echo "========================================================"
    echo "=== Deployment Summary ================================="
    echo "========================================================"
    echo "Stack Name: $STACK_NAME"
    echo "Lambda Function: $LAMBDA_FUNCTION_NAME"
    echo "Bot Alias: $BOT_ALIAS_NAME"
elif [ "$STACK_ACTION" = "create" ] || [ "$STACK_ACTION" = "update" ]; then
    echo "Stack deployment initiated successfully."
    echo "Waiting for stack $STACK_ACTION to complete..."

    if [ "$STACK_ACTION" = "create" ]; then
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    else
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
    fi

    if [ $? -eq 0 ]; then
        echo "Stack deployment completed successfully."

        # Get the Lambda function name from the stack outputs
        LAMBDA_FUNCTION_ARN=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionArn'].OutputValue" --output text)
        LAMBDA_FUNCTION_NAME=$(echo $LAMBDA_FUNCTION_ARN | awk -F':' '{print $NF}')

        echo ""
        echo "========================================================"
        echo "=== Deployment Summary ================================="
        echo "========================================================"
        echo "Stack Name: $STACK_NAME"
        echo "Lambda Function: $LAMBDA_FUNCTION_NAME"
        echo "Bot Alias: $BOT_ALIAS_NAME"
        echo ""
        echo "To test the Lambda function, run:"
        echo "aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload file://$PROJECT_ROOT/test-event.json output.json --region $REGION"
        echo ""
        echo "To view the Lambda function logs, check CloudWatch Logs."
    else
        echo "Stack deployment failed or timed out."
        echo "Check the CloudFormation events for more details:"
        echo "aws cloudformation describe-stack-events --stack-name $STACK_NAME --region $REGION"
    fi

else
    echo "Stack deployment failed to initiate."
    echo "Please check your AWS credentials and permissions."
fi

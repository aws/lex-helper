#!/bin/bash

# Script to package the Lambda function in lambdas/fulfillment_function as a zip file

# Set variables
SOURCE_DIR="lambdas"
OUTPUT_ZIP="zip/AirlineBotAPGLambda.zip"

# Ensure zip directory exists
if [ ! -d "zip" ]; then
    echo "Creating zip directory..."
    mkdir -p zip
fi

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist"
    exit 1
fi

# Check if fulfillment_function directory exists
if [ ! -d "$SOURCE_DIR/fulfillment_function" ]; then
    echo "Error: fulfillment_function directory not found in $SOURCE_DIR"
    exit 1
fi

# Check for required files
if [ ! -f "$SOURCE_DIR/fulfillment_function/lambda_function.py" ]; then
    echo "Error: lambda_function.py not found in $SOURCE_DIR/fulfillment_function"
    exit 1
fi

if [ ! -f "$SOURCE_DIR/fulfillment_function/session_attributes.py" ]; then
    echo "Error: session_attributes.py not found in $SOURCE_DIR/fulfillment_function"
    exit 1
fi

if [ ! -d "$SOURCE_DIR/fulfillment_function/messages" ]; then
    echo "Warning: messages directory not found in $SOURCE_DIR/fulfillment_function"
fi

# Create zip file with the Lambda function
echo "Creating $OUTPUT_ZIP..."
# Change to the parent directory and include the fulfillment_function directory in the zip
cd "$SOURCE_DIR" && zip -r "../$OUTPUT_ZIP" fulfillment_function -x "**/__pycache__/*" "**/*.pyc"

# Verify the zip file was created and contains the expected files
if [ ! -f "../$OUTPUT_ZIP" ]; then
    echo "Error: Failed to create $OUTPUT_ZIP"
    exit 1
fi

echo "Verifying zip file contents..."
unzip -l "../$OUTPUT_ZIP" | grep -q "fulfillment_function/lambda_function.py" || { echo "Error: fulfillment_function/lambda_function.py not found in zip"; exit 1; }
unzip -l "../$OUTPUT_ZIP" | grep -q "fulfillment_function/session_attributes.py" || { echo "Error: fulfillment_function/session_attributes.py not found in zip"; exit 1; }
unzip -l "../$OUTPUT_ZIP" | grep -q "fulfillment_function/messages/" && echo "Messages directory included in zip" || echo "Warning: Messages directory not found in zip"

echo "Done! Created $OUTPUT_ZIP with Lambda function."
echo "The Lambda function is ready for deployment."

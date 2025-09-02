#!/bin/bash

# Script to build a Lambda layer from the lex-helper package
# This script:
# 1. Unzips the lex-helper zip file from layers/
# 2. Reads the dependencies from the pyproject.toml file
# 3. Creates a proper Lambda layer structure
# 4. Packages everything into a zip file

# Set variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LAYERS_DIR="$PROJECT_ROOT/layers"

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Layers directory: $LAYERS_DIR"
ZIP_DIR="$PROJECT_ROOT/zip"
TEMP_EXTRACT_DIR="$(mktemp -d)"
LAYER_DIR="$(mktemp -d)"
PYTHON_VERSION="3.13"  # Update this to match your Lambda runtime version

echo "=== Building Lambda Layer for lex-helper ==="

# Find the lex-helper zip file dynamically
LEX_HELPER_ZIP=$(find "$LAYERS_DIR" -name "lex-helper-v*.zip" | head -n 1)
if [ -z "$LEX_HELPER_ZIP" ]; then
    echo "Error: No lex-helper-v*.zip file found in $LAYERS_DIR"
    echo "Listing files in layers directory:"
    ls -la "$LAYERS_DIR"
    exit 1
fi

# Extract version from filename for logging
LEX_HELPER_VERSION=$(basename "$LEX_HELPER_ZIP" | sed 's/lex-helper-\(.*\)\.zip/\1/')
echo "Using lex-helper zip file: $LEX_HELPER_ZIP (version: $LEX_HELPER_VERSION)"

# Extract the zip file
echo "Extracting $LEX_HELPER_ZIP to $TEMP_EXTRACT_DIR"
unzip -q "$LEX_HELPER_ZIP" -d "$TEMP_EXTRACT_DIR"

# Find the extracted directory (should be something like lex-helper-v*)
EXTRACTED_DIR=$(find "$TEMP_EXTRACT_DIR" -type d -name "lex-helper*" | head -n 1)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "Error: No lex-helper directory found in the extracted zip"
    rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"
    exit 1
fi

echo "Found extracted directory: $EXTRACTED_DIR"

# Read the pyproject.toml file
TOML_PATH="$EXTRACTED_DIR/pyproject.toml"
if [ ! -f "$TOML_PATH" ]; then
    echo "Error: pyproject.toml not found at $TOML_PATH"
    rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"
    exit 1
fi

# Parse dependencies from the TOML file
echo "Parsing dependencies from pyproject.toml"
# Only extract lines between dependencies = [ and ] that contain quotes
DEPENDENCIES=$(awk '/dependencies = \[/,/\]/ { if ($0 ~ /"/) print }' "$TOML_PATH" |
              grep "\"" |
              sed 's/^[ \t]*//;s/[ \t]*$//' |
              sed 's/^"//' |
              sed 's/",$//' |
              sed 's/"$//' |  # Remove trailing quotes
              sed 's/ (//' |
              sed 's/)//')

# Filter out any non-dependency lines
DEPENDENCIES=$(echo "$DEPENDENCIES" | grep -v "license" | grep -v "name" | grep -v "version")

echo "Found dependencies:"
echo "$DEPENDENCIES"

# Create the layer directory structure
echo "Creating layer directory structure..."
mkdir -p "$LAYER_DIR/python"

# Copy the lex_helper package to the layer directory
LEX_HELPER_SRC="$EXTRACTED_DIR/lex_helper"
LEX_HELPER_DEST="$LAYER_DIR/python/lex_helper"
if [ -d "$LEX_HELPER_SRC" ]; then
    echo "Copying lex_helper package to $LEX_HELPER_DEST"
    cp -r "$LEX_HELPER_SRC" "$LEX_HELPER_DEST"
else
    echo "Error: lex_helper package not found at $LEX_HELPER_SRC"
    rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
REQUIREMENTS_PATH="$LAYER_DIR/requirements.txt"

# Create a requirements.txt file with dependencies from pyproject.toml
echo "# Dependencies from pyproject.toml" > "$REQUIREMENTS_PATH"

# Add each dependency to the requirements file
echo "$DEPENDENCIES" | while read -r dep; do
    # Extract the package name and version constraint
    if [[ "$dep" =~ ^([^\ ]+)\ (.+)$ ]]; then
        pkg="${BASH_REMATCH[1]}"
        ver="${BASH_REMATCH[2]}"
        echo "$pkg$ver" >> "$REQUIREMENTS_PATH"
    else
        # If no version constraint, just add the package name
        echo "$dep" >> "$REQUIREMENTS_PATH"
    fi
done

# Add additional dependencies needed for Lambda
echo "pydantic-core>=2.0.0" >> "$REQUIREMENTS_PATH"
echo "typing-extensions>=4.0.0" >> "$REQUIREMENTS_PATH"
echo "annotated-types>=0.6.0" >> "$REQUIREMENTS_PATH"

echo "Requirements file content:"
cat "$REQUIREMENTS_PATH"

# Install the dependencies with platform-specific options for Lambda
echo "Installing dependencies for Lambda environment..."
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.13 --only-binary=:all: --upgrade --target "$LAYER_DIR/python" -r "$REQUIREMENTS_PATH"

if [ $? -ne 0 ]; then
    echo "Error installing dependencies"
    rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"
    exit 1
fi

# Verify that pydantic_core is included
echo "Checking for pydantic_core..."
if [ -d "$LAYER_DIR/python/pydantic_core" ]; then
    echo "pydantic_core found!"
    ls -la "$LAYER_DIR/python/pydantic_core"
else
    echo "WARNING: pydantic_core not found in the dependencies!"
fi

echo "Successfully installed dependencies"

# Clean up unnecessary files to reduce layer size
echo "Cleaning up unnecessary files..."
find "$LAYER_DIR" -type d -name "__pycache__" -exec rm -rf {} +
find "$LAYER_DIR" -type f -name "*.pyc" -delete
find "$LAYER_DIR" -type f -name "*.pyo" -delete
find "$LAYER_DIR" -type d -name "tests" -exec rm -rf {} +
find "$LAYER_DIR" -type d -name ".pytest_cache" -exec rm -rf {} +

# Create the output directory if it doesn't exist
mkdir -p "$ZIP_DIR"

# Create the zip file
OUTPUT_ZIP="$PROJECT_ROOT/zip/lex_helper_layer.zip"
echo "Creating $OUTPUT_ZIP"

# Remove the existing zip file if it exists
if [ -f "$OUTPUT_ZIP" ]; then
    rm "$OUTPUT_ZIP"
fi

# Create the zip file
cd "$LAYER_DIR" && zip -r "$OUTPUT_ZIP" .

# Check if the zip file was created successfully
if [ -f "$OUTPUT_ZIP" ]; then
    echo "Successfully created Lambda layer at $OUTPUT_ZIP"
    ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)
    echo "Layer size: $ZIP_SIZE"
else
    echo "Error: Failed to create $OUTPUT_ZIP"
    rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"
    exit 1
fi

# Clean up
echo "Cleaning up temporary directories..."
rm -rf "$TEMP_EXTRACT_DIR" "$LAYER_DIR"

echo "=== Lambda Layer Creation Complete ==="

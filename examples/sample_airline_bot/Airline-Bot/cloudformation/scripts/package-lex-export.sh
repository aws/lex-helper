#!/bin/bash

# Script to package the Lex bot export files as a zip file for deployment

# Set variables
SOURCE_DIR="../lex-export"
OUTPUT_ZIP="../zip/AirlineBot.zip"

echo "=== Packaging Lex Bot Export ==="

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

# Check if required files exist
if [ ! -f "$SOURCE_DIR/Manifest.json" ]; then
    echo "Error: Manifest.json not found in $SOURCE_DIR"
    exit 1
fi

if [ ! -d "$SOURCE_DIR/LexBot" ]; then
    echo "Error: LexBot directory not found in $SOURCE_DIR"
    exit 1
fi

# Get the bot name from Bot.json
echo "Getting bot name from Bot.json..."
BOT_NAME=$(grep -o '"name":"[^"]*"' "$SOURCE_DIR/LexBot/Bot.json" | cut -d'"' -f4)

if [ -z "$BOT_NAME" ]; then
    echo "Error: Could not determine bot name from Bot.json"
    exit 1
fi

echo "Bot name is: $BOT_NAME"

# Create a temporary directory for the zip structure
TEMP_DIR="temp_lex_export"
echo "Creating temporary directory..."
mkdir -p "$TEMP_DIR/$BOT_NAME"

# Create the correct folder structure for Lex import
echo "Creating correct folder structure..."
mkdir -p "$TEMP_DIR"

# Copy files directly to temp directory root
echo "Copying Manifest.json..."
cp "$SOURCE_DIR/Manifest.json" "$TEMP_DIR/"

echo "Copying LexBot contents..."
cp -r "$SOURCE_DIR/LexBot/"* "$TEMP_DIR/$BOT_NAME/"

echo "Final structure:"
find "$TEMP_DIR" -type d | head -20

# Create zip file with the Lex bot export
echo "Creating $OUTPUT_ZIP..."
cd "$TEMP_DIR" && zip -r "../$OUTPUT_ZIP" Manifest.json "$BOT_NAME/"

# Clean up
echo "Cleaning up temporary directory..."
cd ..
rm -rf "$TEMP_DIR"

echo "Done! Created $OUTPUT_ZIP with Lex bot export."
echo "The Lex bot export is ready for deployment."

# List the contents of the zip file to verify the structure
echo ""
echo "Zip file contents (top-level directories only):"
unzip -l "$OUTPUT_ZIP" | grep -E "/$" | head -n 10
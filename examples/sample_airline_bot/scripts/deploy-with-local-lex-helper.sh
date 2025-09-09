#!/bin/bash

# Deploy Airline Bot with Local lex-helper Library
# This script builds the lex-helper library locally using uv and deploys the CDK stack

set -e

# Validate we're in the correct directory
if [[ ! -f "scripts/deploy-with-local-lex-helper.sh" ]]; then
    echo "❌ Error: This script must be run from the sample_airline_bot directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: scripts/deploy-with-local-lex-helper.sh"
    exit 1
fi

# Check if required tools are installed
command -v uv >/dev/null 2>&1 || { echo "❌ Error: uv is required but not installed. Please install uv first."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ Error: npm is required but not installed. Please install Node.js and npm first."; exit 1; }
command -v npx >/dev/null 2>&1 || { echo "❌ Error: npx is required but not installed. Please install Node.js and npm first."; exit 1; }

echo "🧹 Cleaning up old wheel files..."
cd ../../
# Remove old wheel files from both locations to prevent hash conflicts
rm -f dist/lex_helper-*.whl
rm -f examples/sample_airline_bot/lambdas/fulfillment_function/lex_helper-*.whl

echo "🔨 Building lex-helper library..."
uv build

echo "📦 Copying wheel to Lambda function..."
cp dist/lex_helper-*.whl examples/sample_airline_bot/lambdas/fulfillment_function/

echo "🔄 Updating uv dependencies..."
cd examples/sample_airline_bot/lambdas/fulfillment_function

# Update pyproject.toml to use the latest wheel
WHEEL_FILE=$(ls lex_helper-*.whl | head -1)
sed -i.bak "s/lex-helper = { path = \"lex_helper-.*\.whl\" }/lex-helper = { path = \"$WHEEL_FILE\" }/" pyproject.toml

# Remove lock file to force regeneration and avoid hash conflicts
echo "🗑️ Removing lock file to prevent hash conflicts..."
rm -f uv.lock

# Clear specific package cache and sync dependencies
echo "🔄 Syncing dependencies with fresh lock file..."
uv cache clean lex-helper
uv sync

echo "🏗️ Building CDK project..."
cd ../../
npm run build

echo "🚀 Deploying CDK stack..."
npx cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo "📝 Note: The Lambda function now includes your local lex-helper changes."
echo "🔧 Environment variables set:"
echo "   - MESSAGES_YAML_PATH: /var/task/fulfillment_function/messages"
echo "   - LOG_LEVEL: INFO"
echo ""
echo "🧪 To test your changes:"
echo "   - Use the Lex console to test the bot"
echo "   - Check CloudWatch logs for debugging"
echo "   - Run integration tests if available"

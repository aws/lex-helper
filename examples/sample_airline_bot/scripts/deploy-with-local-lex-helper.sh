#!/bin/bash

# Deploy Airline Bot with Local lex-helper Library
# This script builds the lex-helper library locally and deploys the CDK stack

set -e

echo "🔨 Building lex-helper library..."
cd ../../
uv build

echo "📦 Copying wheel to Lambda function..."
cp dist/lex_helper-*.whl examples/sample_airline_bot/lambdas/fulfillment_function/

echo "🔄 Updating Poetry dependencies..."
cd examples/sample_airline_bot/lambdas/fulfillment_function
# Update pyproject.toml to use the latest wheel
WHEEL_FILE=$(ls lex_helper-*.whl | head -1)
sed -i.bak "s/lex-helper = { path = \"lex_helper-.*\.whl\" }/lex-helper = { path = \"$WHEEL_FILE\" }/" pyproject.toml
poetry lock

echo "🏗️ Building CDK project..."
cd ../../
npm run build

echo "🚀 Deploying CDK stack..."
npx cdk deploy

echo "✅ Deployment complete!"
echo "📝 Note: The Lambda function now includes your local lex-helper changes."
echo "🔧 Environment variables set:"
echo "   - MESSAGES_YAML_PATH: /var/task/fulfillment_function/messages"
echo "   - LOG_LEVEL: INFO"

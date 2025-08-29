# Lambda Layers

This directory contains AWS Lambda layers used in the Airline-Bot project. Lambda layers provide a way to package and share code dependencies across multiple Lambda functions, reducing deployment package size and enabling code reuse.

## Overview

The Airline-Bot project uses Lambda layers to:
- Package the lex_helper framework separately from the main Lambda function
- Reduce deployment package size and deployment time
- Enable easy updates to shared dependencies
- Maintain clean separation between application code and dependencies

## Current Layers

### lex_helper Layer
- **Purpose**: Contains the lex_helper framework for Amazon Lex bot development
- **Version**: v0.0.14 (or latest available)
- **Source**: https://github.com/aws/lex-helper
- **Contents**: Complete lex_helper framework with all dependencies

## Directory Structure

```
layers/
├── lex_helper/                    # Local development layer structure
│   └── python/                    # Python packages directory
│       └── lex-helper-v*/         # Extracted lex_helper framework
├── lex-helper-v*.zip             # Downloaded layer package
└── README.md                      # This file
```

## Setting Up Layers for Local Development

### 1. Download the lex_helper Framework

```bash
# Download from the official repository
# Visit: https://github.com/aws/lex-helper
# Download the latest lex-helper-v*.zip file
```

### 2. Extract the Layer Package

```bash
# Create the layer directory structure
mkdir -p layers/lex_helper/python

# Extract the downloaded package
unzip layers/lex-helper-v*.zip -d layers/lex_helper/python

# Verify the structure
ls -la layers/lex_helper/python/
```

### 3. Automatic Layer Loading

The main Lambda function (`lambda_function.py`) automatically detects and loads the layer when running locally:

```python
# This code is already included in lambda_function.py
if not os.getenv('AWS_EXECUTION_ENV'):
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add layer to Python path
    layer_path = os.path.join(project_root, 'layers', 'lex_helper', 'python')
    sys.path.append(layer_path)
    
    # For versioned packages
    for item in os.listdir(layer_path):
        item_path = os.path.join(layer_path, item)
        if os.path.isdir(item_path) and item.startswith('lex_helper'):
            sys.path.append(item_path)
```

## Deployment

### Automated Deployment (Recommended)

The deployment scripts automatically handle layer packaging and deployment:

```bash
cd cloudformation
./deploy_airline_bot.sh
```

This script:
1. Packages the lex_helper layer from the local directory
2. Uploads the layer to AWS Lambda
3. Configures the Lambda function to use the layer

### Manual Layer Deployment

If you need to deploy the layer manually:

```bash
# Package the layer
cd layers/lex_helper
zip -r ../../lex-helper-layer.zip python/

# Deploy using AWS CLI
aws lambda publish-layer-version \
    --layer-name lex-helper \
    --description "lex_helper framework for Amazon Lex development" \
    --zip-file fileb://../../lex-helper-layer.zip \
    --compatible-runtimes python3.12

# Update Lambda function to use the layer
aws lambda update-function-configuration \
    --function-name AirlineBotFulfillment \
    --layers arn:aws:lambda:region:account:layer:lex-helper:version
```

## Layer Development Guidelines

### Adding New Layers

1. **Create Directory Structure**:
   ```bash
   mkdir -p layers/<layer_name>/python
   ```

2. **Add Dependencies**:
   ```bash
   # For Python packages
   pip install <package> -t layers/<layer_name>/python/
   
   # Or extract existing packages
   unzip <package>.zip -d layers/<layer_name>/python/
   ```

3. **Update Lambda Function**:
   - Add layer loading logic to `lambda_function.py`
   - Update deployment scripts to include the new layer

### Best Practices

- **Version Management**: Keep track of layer versions and update references
- **Size Optimization**: Only include necessary dependencies in layers
- **Testing**: Test layers both locally and in AWS environment
- **Documentation**: Document layer contents and usage

## Troubleshooting

### Common Issues

1. **Import Errors in Local Development**:
   ```bash
   # Verify layer structure
   ls -la layers/lex_helper/python/
   
   # Check if lex_helper is properly extracted
   find layers/ -name "*.py" | head -10
   ```

2. **Layer Not Found in AWS**:
   ```bash
   # List available layers
   aws lambda list-layers
   
   # Check layer versions
   aws lambda list-layer-versions --layer-name lex-helper
   ```

3. **Version Conflicts**:
   - Ensure local and deployed layer versions match
   - Check CloudFormation template for correct layer ARN
   - Verify layer compatibility with Python runtime

### Debugging Layer Loading

Add debug logging to verify layer loading:

```python
import sys
import os
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# Check if lex_helper is available
try:
    import lex_helper
    print(f"lex_helper loaded from: {lex_helper.__file__}")
except ImportError as e:
    print(f"Failed to import lex_helper: {e}")
```

## Layer Updates

### Updating the lex_helper Framework

1. **Download New Version**:
   ```bash
   # Download latest version from repository
   # Replace existing lex-helper-v*.zip file
   ```

2. **Update Local Layer**:
   ```bash
   # Remove old version
   rm -rf layers/lex_helper/python/*
   
   # Extract new version
   unzip layers/lex-helper-v*.zip -d layers/lex_helper/python/
   ```

3. **Test Locally**:
   ```bash
   cd lambdas/fulfillment_function
   python lambda_function.py
   ```

4. **Deploy Updated Layer**:
   ```bash
   cd cloudformation
   ./deploy_airline_bot.sh
   ```

## Performance Considerations

- **Layer Size**: Keep layers under 50MB unzipped for optimal performance
- **Loading Time**: Minimize the number of layers per function
- **Caching**: AWS caches layers, so updates may take time to propagate
- **Cold Starts**: Layers can impact Lambda cold start times

## Security

- **Access Control**: Use IAM policies to control layer access
- **Versioning**: Use specific layer versions in production
- **Scanning**: Regularly scan layer contents for vulnerabilities
- **Minimal Dependencies**: Only include necessary packages

## Additional Resources

- [AWS Lambda Layers Documentation](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [lex_helper Framework Documentation](https://github.com/aws/lex-helper)
- [Python Package Management Best Practices](https://packaging.python.org/guides/)


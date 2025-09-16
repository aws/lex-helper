# Lambda Layer Deployment Guide for Lex Helper Library

## Overview

This guide covers creating and deploying a Lambda layer containing the lex-helper library and its dependencies. Lambda layers allow you to share code across multiple Lambda functions and reduce deployment package sizes.

## Prerequisites

- Python 3.12+ installed locally
- AWS CLI configured with appropriate permissions
- lex-helper library (see [Installation Guide](getting-started/installation.md) for installation)
- Poetry installed (for Method 2): `pip install poetry`

## Method 1: Using pip install (Recommended)

### Step 1: Create Layer Directory Structure

```bash
mkdir -p lex-helper-layer/python/lib/python3.12/site-packages/
cd lex-helper-layer
```

### Step 2: Install lex-helper and Dependencies

```bash
# Install from PyPI
pip install lex-helper -t python/lib/python3.12/site-packages/

# Or install from local source
pip install /path/to/lex-helper -t python/lib/python3.12/site-packages/
```

### Step 3: Clean Up Unnecessary Files

Remove files that aren't needed in production to reduce layer size:

```bash
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove test files and directories
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Remove development files
find . -name "*.egg-info" -exec rm -rf {} +
find . -name ".git*" -delete
find . -name "*.md" -delete
find . -name "LICENSE*" -delete
```

## Method 2: Using Poetry

### Step 1: Create Poetry Project

```bash
mkdir lex-helper-layer-poetry
cd lex-helper-layer-poetry
poetry init --no-interaction
```

### Step 2: Add lex-helper Dependency

```bash
# Add lex-helper as dependency
poetry add lex-helper

# Or add from local source
poetry add /path/to/lex-helper
```

### Step 3: Export Dependencies and Install to Layer

```bash
# Export dependencies to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Create layer directory
mkdir -p ../lex-helper-layer/python/lib/python3.12/site-packages/

# Install dependencies to layer directory
pip install -r requirements.txt -t ../lex-helper-layer/python/lib/python3.12/site-packages/

# Clean up
cd ../lex-helper-layer
```

### Alternative: Using Poetry's Virtual Environment

```bash
# Create and activate poetry environment
poetry install
poetry shell

# Find the virtual environment path
poetry env info --path

# Copy site-packages from poetry venv to layer
cp -r $(poetry env info --path)/lib/python3.12/site-packages/* python/lib/python3.12/site-packages/

# Remove development dependencies manually
rm -rf python/lib/python3.12/site-packages/pytest*
rm -rf python/lib/python3.12/site-packages/ruff*
```

### Step 4: Clean Up (same as Method 1, Step 3)

## Verify Layer Contents and Size

### Check Layer Size

Lambda layers have a 250 MB unzipped size limit:

```bash
du -sh lex-helper-layer/
# Expected output: ~10-15MB for lex-helper with dependencies
```

### View Layer Contents

```bash
find lex-helper-layer -type f | head -20
```

Expected structure:
```
lex-helper-layer/
└── python/
    └── lib/
        └── python3.12/
            └── site-packages/
                ├── lex_helper/
                │   ├── __init__.py
                │   ├── core/
                │   └── utils/
                └── pydantic/
```

## Package the Layer

### Create ZIP Archive

```bash
cd lex-helper-layer
zip -r ../lex-helper-layer.zip .
cd ..
```

### Verify ZIP Contents

```bash
unzip -l lex-helper-layer.zip | head -10
```

## Deploy to AWS Lambda

### Using AWS CLI

```bash
# Create new layer version
aws lambda publish-layer-version \
    --layer-name lex-helper-layer \
    --description "Lex Helper Library with dependencies" \
    --zip-file fileb://lex-helper-layer.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures x86_64 arm64

# Note the LayerVersionArn from the response
```

### Using AWS Console

1. Open AWS Lambda Console
2. Navigate to "Layers" in the left sidebar
3. Click "Create layer"
4. Fill in:
   - Name: `lex-helper-layer`
   - Description: `Lex Helper Library with dependencies`
   - Upload ZIP file: `lex-helper-layer.zip`
   - Compatible runtimes: `Python 3.12`
   - Compatible architectures: `x86_64`, `arm64`
5. Click "Create"

## Using the Layer in Lambda Functions

### Add Layer to Function (AWS CLI)

```bash
aws lambda update-function-configuration \
    --function-name your-lex-bot-function \
    --layers arn:aws:lambda:region:account:layer:lex-helper-layer:1
```

### Add Layer to Function (Console)

1. Open your Lambda function
2. Scroll to "Layers" section
3. Click "Add a layer"
4. Select "Custom layers"
5. Choose your `lex-helper-layer`
6. Select the latest version
7. Click "Add"

### Using in Your Lambda Code

Once the layer is attached, import normally:

```python
from lex_helper import Config, LexHelper, dialog, LexPlainText
from lex_helper.core.types import LexRequest, LexResponse

def lambda_handler(event, context):
    # Your code here
    pass
```

### Environment Variables

Configure these environment variables in your Lambda function:

```bash
# Optional: Custom messages file path
MESSAGES_YAML_PATH=/opt/lambda/config/

# AWS region for Bedrock and other services
AWS_REGION=us-east-1

# Logging level
LOG_LEVEL=INFO
```

## Automation with Infrastructure as Code

### CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  LexHelperLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: lex-helper-layer
      Description: Lex Helper Library with dependencies
      Content:
        S3Bucket: your-deployment-bucket
        S3Key: layers/lex-helper-layer.zip
      CompatibleRuntimes:
        - python3.12
      CompatibleArchitectures:
        - x86_64
        - arm64

  YourLexBotFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: your-lex-bot-function
      Runtime: python3.12
      Handler: handler.lambda_handler
      Code:
        S3Bucket: your-deployment-bucket
        S3Key: functions/your-bot.zip
      Layers:
        - !Ref LexHelperLayer
      Environment:
        Variables:
          MESSAGES_YAML_PATH: /opt/lambda/config/
          AWS_REGION: us-east-1
          LOG_LEVEL: INFO
```

### Terraform Configuration

```hcl
resource "aws_lambda_layer_version" "lex_helper" {
  filename         = "lex-helper-layer.zip"
  layer_name       = "lex-helper-layer"
  description      = "Lex Helper Library with dependencies"

  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64", "arm64"]
}

resource "aws_lambda_function" "lex_bot" {
  filename         = "your-bot.zip"
  function_name    = "your-lex-bot-function"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.12"

  layers = [aws_lambda_layer_version.lex_helper.arn]

  environment {
    variables = {
      MESSAGES_YAML_PATH = "/opt/lambda/config/"
      AWS_REGION         = "us-east-1"
      LOG_LEVEL          = "INFO"
    }
  }
}
```

## Best Practices

### Layer Management
- **Version Control**: Tag layer versions for easy rollback
- **Size Optimization**: Regularly clean up unused dependencies
- **Regional Deployment**: Deploy layers in all regions where functions run
- **Permissions**: Set appropriate layer permissions for sharing

### Development Workflow
- **Local Testing**: Test with the same layer structure locally
- **CI/CD Integration**: Automate layer building and deployment
- **Dependency Updates**: Monitor for security updates in dependencies

### Troubleshooting

#### Common Issues

**Import Errors**:
```python
# Verify layer is attached and imports work
import sys
print(sys.path)  # Should include /opt/python/lib/python3.12/site-packages
```

**Size Limits**:
- Unzipped layer size: 250 MB maximum
- Total function + layers: 250 MB unzipped
- Deployment package: 50 MB zipped (direct upload)

**Python Version Mismatch**:
- Ensure layer Python version matches Lambda runtime
- Use correct site-packages path for Python version

#### Verification Script

```python
# Add to your Lambda function for debugging
def verify_layer():
    try:
        import lex_helper
        print(f"lex-helper version: {lex_helper.__version__}")
        print(f"lex-helper location: {lex_helper.__file__}")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

# Call in lambda_handler for testing
verify_layer()
```

## Layer Updates

### Updating the Layer

1. Modify dependencies or add new packages
2. Rebuild the layer following steps above
3. Create new layer version
4. Update Lambda functions to use new version
5. Test thoroughly before removing old versions

### Rollback Strategy

```bash
# List layer versions
aws lambda list-layer-versions --layer-name lex-helper-layer

# Rollback function to previous layer version
aws lambda update-function-configuration \
    --function-name your-lex-bot-function \
    --layers arn:aws:lambda:region:account:layer:lex-helper-layer:PREVIOUS_VERSION
```

This approach provides a clean, maintainable way to deploy and manage the lex-helper library across your Lambda functions.

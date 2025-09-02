# Deployment Scripts

This directory contains automated packaging scripts for the Airline-Bot deployment process. These scripts handle the preparation of all components required for AWS deployment including Lambda layers, function code, and Lex bot configuration.

## Overview

The deployment scripts automate the packaging process to ensure consistent and reliable deployments. They handle:
- Lambda layer packaging with proper directory structure
- Lambda function code packaging with dependency management
- Lex bot export preparation for CloudFormation deployment
- Artifact organization and cleanup

## Scripts

### `package-lex-helper-layer.sh`
**Purpose**: Packages the lex_helper framework into a Lambda layer
- Creates proper Python package structure for Lambda layers
- Includes the lex_helper framework and its dependencies
- Generates deployment-ready ZIP file for the layer
- Handles versioned package extraction and organization

### `package-lambda-function.sh`
**Purpose**: Packages the fulfillment Lambda function code
- Bundles all intent handlers and utility modules
- Excludes development files and unnecessary artifacts
- Creates optimized ZIP package for Lambda deployment
- Maintains proper file permissions and structure

### `package-lex-export.sh`
**Purpose**: Packages the Lex bot configuration for deployment
- Processes Lex bot export files for CloudFormation
- Organizes bot definition, intents, and slot types
- Creates deployment package for Lex bot resources
- Ensures proper formatting for AWS import

## Usage

### Automated Deployment (Recommended)
These scripts are automatically executed by the main deployment script:

```bash
cd cloudformation
./deploy_airline_bot.sh [bot-alias-name]
```

The main deployment script calls these packaging scripts in the correct order and handles all dependencies.

### Manual Execution
If you need to run individual packaging scripts for development or troubleshooting:

```bash
cd cloudformation/scripts

# Package the lex_helper layer
./package-lex-helper-layer.sh

# Package the Lambda function
./package-lambda-function.sh

# Package the Lex bot export
./package-lex-export.sh
```

**Note**: Manual execution requires that dependencies are properly set up in the project structure.

## Script Details

### Prerequisites
All scripts assume the following project structure:
```
Airline-Bot/
├── layers/lex_helper/python/          # lex_helper framework
├── lambdas/fulfillment_function/      # Lambda function code
├── lex-export/LexBot/                 # Lex bot export files
└── cloudformation/scripts/            # These scripts
```

### Output Artifacts
Scripts generate deployment packages in the `zip/` directory:
- `lex-helper-layer.zip`: Lambda layer package
- `fulfillment-function.zip`: Lambda function package
- `lex-export.zip`: Lex bot configuration package

### Error Handling
Each script includes:
- Prerequisite validation
- Error checking and reporting
- Cleanup on failure
- Success confirmation

## Development and Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   # Ensure lex_helper framework is extracted
   ls -la layers/lex_helper/python/
   ```

2. **Permission Issues**:
   ```bash
   # Make scripts executable
   chmod +x *.sh
   ```

3. **Path Issues**:
   ```bash
   # Run from correct directory
   cd cloudformation/scripts
   pwd  # Should end with /cloudformation/scripts
   ```

### Debugging
Enable debug output by setting environment variable:
```bash
export DEBUG=1
./package-lambda-function.sh
```

### Customization
To modify packaging behavior:
1. Edit the relevant script
2. Test with manual execution
3. Verify with full deployment

## Best Practices

- **Always use the main deployment script** for production deployments
- **Test individual scripts** only during development
- **Check output artifacts** in the `zip/` directory after packaging
- **Clean up artifacts** between deployments to avoid stale files
- **Verify file permissions** if deployment fails

## Integration with CloudFormation

These scripts integrate with the CloudFormation template by:
1. Creating properly formatted deployment packages
2. Placing artifacts in expected locations
3. Following AWS Lambda and Lex packaging requirements
4. Maintaining consistent naming conventions

The main deployment script uploads these packages to S3 and references them in the CloudFormation template.

## Maintenance

### Updating Scripts
When modifying scripts:
1. Test with local development environment
2. Verify with complete deployment
3. Update documentation if behavior changes
4. Consider backward compatibility

### Adding New Components
To add new packaging scripts:
1. Follow existing naming convention
2. Include proper error handling
3. Update main deployment script
4. Document in this README

## Security Considerations

- Scripts handle sensitive deployment artifacts
- Temporary files are cleaned up after execution
- No credentials are stored in scripts
- Artifacts should be treated as deployment secrets

## Performance

- Scripts are optimized for deployment speed
- Parallel execution where possible
- Minimal file operations
- Efficient compression algorithms

For more information about the overall deployment process, see the [main deployment guide](../DEPLOYMENT_GUIDE.md).

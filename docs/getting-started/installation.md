# Installation

Learn how to install lex-helper and set up your development environment for building Amazon Lex chatbots.

## Prerequisites

Before installing lex-helper, ensure you have:

- **Python 3.12 or higher** (Python 3.8+ supported, but 3.12+ recommended)
- **AWS account** with appropriate permissions
- **Basic familiarity** with AWS Lambda and Amazon Lex concepts

## Installation Methods

### Method 1: Using pip (Recommended)

Install the latest stable version from PyPI:

```bash
pip install lex-helper
```

### Method 2: Using uv (Modern Python Package Manager)

If you're using [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
uv add lex-helper
```

### Method 3: With Optional Dependencies

For enhanced features, install with optional dependencies:

```bash
# For Bedrock integration (AI-powered features)
pip install lex-helper[bedrock]

# For development tools
pip install lex-helper[dev]

# Install all optional dependencies
pip install lex-helper[bedrock,dev]
```

### Method 4: From Source (Development)

For the latest development version:

```bash
git clone https://github.com/aws/lex-helper.git
cd lex-helper
pip install -e .
```

## AWS Setup

### 1. AWS Credentials Configuration

Configure your AWS credentials using one of these methods:

**Option A: AWS CLI**
```bash
aws configure
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option C: IAM Roles (Recommended for Lambda)**
When deploying to Lambda, use IAM roles instead of hardcoded credentials.

### 2. Required AWS Permissions

Your AWS user or role needs these minimum permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lex:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "*"
        }
    ]
}
```

**For Bedrock features, add:**
```json
{
    "Effect": "Allow",
    "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
    ],
    "Resource": "*"
}
```

## Development Environment Setup

### 1. Create Project Structure

Create a new directory for your chatbot project:

```bash
mkdir my-chatbot
cd my-chatbot
```

### 2. Virtual Environment (Recommended)

Create and activate a virtual environment:

```bash
# Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Using uv (if installed)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install lex-helper

```bash
pip install lex-helper
```

### 4. Create Basic Project Structure

```bash
mkdir intents
touch handler.py
touch session_attributes.py
touch intents/__init__.py
```

Your project structure should look like:
```
my-chatbot/
├── .venv/
├── intents/
│   └── __init__.py
├── handler.py
└── session_attributes.py
```

## Verification

### 1. Test Installation

Create a simple test file to verify the installation:

```python
# test_installation.py
from lex_helper import LexHelper, Config, SessionAttributes

print("✅ lex-helper installed successfully!")
print(f"Version: {lex_helper.__version__}")
```

Run the test:
```bash
python test_installation.py
```

### 2. Check Dependencies

Verify all dependencies are installed correctly:

```bash
pip list | grep -E "(lex-helper|pydantic|boto3|PyYAML)"
```

You should see output similar to:
```
boto3                 1.34.0
botocore              1.34.0
lex-helper            0.1.0
pydantic              2.5.0
PyYAML                6.0.1
```

## IDE Setup

### VS Code Configuration

For the best development experience with VS Code:

1. **Install Python Extension**
   - Install the official Python extension by Microsoft

2. **Configure Python Interpreter**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose your virtual environment's Python interpreter

3. **Recommended Extensions**
   - Python (Microsoft)
   - Pylance (Microsoft) - for enhanced type checking
   - AWS Toolkit (Amazon Web Services)

### PyCharm Configuration

1. **Set Project Interpreter**
   - Go to File → Settings → Project → Python Interpreter
   - Select your virtual environment's Python interpreter

2. **Enable Type Checking**
   - Go to File → Settings → Editor → Inspections
   - Enable "Python → Type checker"

## Next Steps

Now that you have lex-helper installed and configured:

1. **[Quick Start Guide](quick-start.md)** - Build your first chatbot in 5 minutes
2. **[Your First Chatbot](first-chatbot.md)** - Comprehensive tutorial with explanations
3. **[Core Concepts](../guides/core-concepts.md)** - Understand lex-helper's architecture

## Troubleshooting

### Common Installation Issues

**Issue: `pip install lex-helper` fails with permission error**
```bash
# Solution: Use --user flag or virtual environment
pip install --user lex-helper

# Or create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install lex-helper
```

**Issue: Python version compatibility error**
```bash
# Check your Python version
python --version

# If you have an older version, upgrade Python
# Using pyenv (recommended)
pyenv install 3.12.0
pyenv global 3.12.0

# Using system package manager (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12

# Using Homebrew (macOS)
brew install python@3.12
```

**Issue: AWS credentials not found**
```bash
# Verify AWS configuration
aws sts get-caller-identity

# If this fails, configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, and region

# Alternative: Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Issue: Import errors after installation**
```bash
# Verify installation in correct environment
which python
pip show lex-helper

# Check if you're in the right virtual environment
echo $VIRTUAL_ENV

# Reinstall if needed
pip uninstall lex-helper
pip install lex-helper
```

**Issue: `ModuleNotFoundError: No module named 'lex_helper'`**
```bash
# Make sure you're using the correct Python interpreter
python -c "import sys; print(sys.path)"

# Verify lex-helper is installed
pip list | grep lex-helper

# If not found, install it
pip install lex-helper
```

**Issue: SSL certificate errors during installation**
```bash
# Upgrade pip and certificates
pip install --upgrade pip
pip install --upgrade certifi

# If still failing, use trusted hosts (temporary solution)
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org lex-helper
```

**Issue: Dependency conflicts**
```bash
# Check for conflicts
pip check

# Create a fresh virtual environment
deactivate  # if in a virtual environment
rm -rf .venv  # remove old environment
python -m venv .venv
source .venv/bin/activate
pip install lex-helper
```

### Platform-Specific Issues

**Windows-Specific Issues:**

```powershell
# PowerShell execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Path issues
where python
where pip

# Use py launcher if available
py -m pip install lex-helper
```

**macOS-Specific Issues:**

```bash
# Xcode command line tools required
xcode-select --install

# Multiple Python versions
which python3
python3 -m pip install lex-helper

# Homebrew Python issues
brew doctor
brew reinstall python@3.12
```

**Linux-Specific Issues:**

```bash
# Missing development headers
sudo apt-get install python3-dev python3-pip

# CentOS/RHEL
sudo yum install python3-devel python3-pip

# Permission issues with system Python
python3 -m pip install --user lex-helper
```

### AWS-Specific Issues

**Issue: Access denied errors**
```bash
# Check your AWS permissions
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Test basic Lex permissions
aws lex-models-v2 list-bots --region us-east-1
```

**Issue: Region configuration problems**
```bash
# Check current region
aws configure get region

# Set region explicitly
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

**Issue: Credential provider chain errors**
```bash
# Check credential sources in order:
# 1. Environment variables
echo $AWS_ACCESS_KEY_ID

# 2. AWS credentials file
cat ~/.aws/credentials

# 3. AWS config file
cat ~/.aws/config

# 4. IAM roles (if running on EC2)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### Development Environment Issues

**Issue: IDE not recognizing lex-helper**
```bash
# VS Code: Select correct Python interpreter
# Ctrl+Shift+P -> "Python: Select Interpreter"
# Choose the one from your virtual environment

# PyCharm: Configure project interpreter
# File -> Settings -> Project -> Python Interpreter
```

**Issue: Type hints not working**
```bash
# Install type checking tools
pip install mypy pylance

# For VS Code, install Pylance extension
# For PyCharm, enable type checking in settings
```

**Issue: Linting errors**
```bash
# Install development dependencies
pip install lex-helper[dev]

# Or install linting tools separately
pip install ruff black isort
```

### Performance Issues

**Issue: Slow import times**
```bash
# Check import time
python -X importtime -c "import lex_helper"

# Consider using lazy imports in production
# Or pre-warm Lambda containers
```

**Issue: Memory usage in Lambda**
```python
# Monitor memory usage
import psutil
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")

# Optimize Lambda configuration
# Increase memory allocation if needed
```

### Verification Steps

After resolving issues, verify your installation:

```bash
# 1. Check Python version
python --version

# 2. Verify lex-helper installation
pip show lex-helper

# 3. Test basic import
python -c "from lex_helper import LexHelper; print('✅ Import successful')"

# 4. Check AWS connectivity
python -c "import boto3; print('✅ AWS SDK available')"

# 5. Verify type hints work
python -c "from lex_helper import LexRequest, LexResponse; print('✅ Type hints available')"
```

### Getting Help

If you encounter issues not covered here:

1. **Check the [FAQ](../community/support.md#frequently-asked-questions)**
2. **Search [existing issues](https://github.com/aws/lex-helper/issues)**
3. **Create a new issue** with:
   - Operating system and version
   - Python version (`python --version`)
   - lex-helper version (`pip show lex-helper`)
   - Full error message and stack trace
   - Steps to reproduce the issue
   - Virtual environment details (`pip freeze`)

4. **For urgent issues:**
   - Check [Stack Overflow](https://stackoverflow.com/questions/tagged/lex-helper) for community solutions
   - Join our [Discord community](https://discord.gg/lex-helper) for real-time help

### Diagnostic Script

Run this diagnostic script to gather information for bug reports:

```python
# diagnostic.py
import sys
import platform
import subprocess
import importlib.util

def run_diagnostics():
    print("🔍 lex-helper Diagnostic Report")
    print("=" * 40)

    # System information
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Python executable: {sys.executable}")

    # Virtual environment
    venv = sys.prefix != sys.base_prefix
    print(f"Virtual environment: {'Yes' if venv else 'No'}")
    if venv:
        print(f"Virtual env path: {sys.prefix}")

    # Package information
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "lex-helper"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("\n📦 lex-helper Package Info:")
            print(result.stdout)
        else:
            print("\n❌ lex-helper not installed")
    except Exception as e:
        print(f"\n❌ Error checking package: {e}")

    # Import test
    try:
        import lex_helper
        print(f"\n✅ lex-helper import successful")
        print(f"Version: {getattr(lex_helper, '__version__', 'Unknown')}")
    except ImportError as e:
        print(f"\n❌ lex-helper import failed: {e}")

    # AWS SDK test
    try:
        import boto3
        print("✅ boto3 available")
    except ImportError:
        print("❌ boto3 not available")

    # Dependencies
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n📋 Installed packages:")
            relevant_packages = [line for line in result.stdout.split('\n')
                               if any(pkg in line.lower() for pkg in
                                     ['lex-helper', 'boto3', 'pydantic', 'pyyaml'])]
            for pkg in relevant_packages:
                if pkg.strip():
                    print(f"  {pkg}")
    except Exception as e:
        print(f"\n❌ Error listing packages: {e}")

if __name__ == "__main__":
    run_diagnostics()
```

Run the diagnostic:
```bash
python diagnostic.py
```

Include the output when reporting issues for faster resolution.

---

*Ready to build your first chatbot? Continue to the [Quick Start Guide](quick-start.md) →*

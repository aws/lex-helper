# Deployment Guide

## Prerequisites

- **uv**: `pip install uv`
- **Node.js and npm**: `brew install node`
- **TypeScript**: `npm install -g typescript`
- **Docker Desktop**: `brew install --cask docker` (must be running)
- **Poetry**: `pip install poetry`
- **AWS credentials**: `ada credentials update --account=<account> --role=<role>`

## Deployment Commands

### Initial Deployment
```bash
# IMPORTANT: Must be run from sample_airline_bot directory (not from scripts/)
cd sample_airline_bot
./scripts/deploy-with-local-lex-helper.sh
```

### Lambda Code Changes
```bash
npm run build && npx cdk deploy --require-approval never
```

### Infrastructure Changes
```bash
npm run build && npx cdk deploy
```

### lex-helper Library Changes
```bash
# From root lex-helper directory
./examples/sample_airline_bot/scripts/deploy-with-local-lex-helper.sh
```

## Troubleshooting

- **Script fails with "does not appear to be a Python project"**: Ensure you're running the script from `sample_airline_bot` directory, not from `scripts/`
- Ensure Docker Desktop is running
- Verify AWS credentials are valid
- Check all prerequisites are installed
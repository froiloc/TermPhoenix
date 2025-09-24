#!/bin/bash
# Automated environment setup for CI/CD

set -e

echo "Setting up TermPhoenix environment..."

# Check Python version
python --version

# Install dependencies
pip install -e ".[dev,analysis]"

# Run basic checks
python -c "import termphoenix; print('Import successful')"

echo "Environment setup complete!"

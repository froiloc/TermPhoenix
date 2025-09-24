#!/bin/bash
# Quick test script for development

set -e

source venv/bin/activate

echo "Running quick tests..."
python -m pytest tests/ -x -v --disable-warnings

echo "Quick lint check..."
flake8 src/ --count --exit-zero

echo "Quick tests completed!"

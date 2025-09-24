#!/bin/bash

# Clone the repository
git clone https://github.com/froiloc/TermPhoenix.git
cd TermPhoenix

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Or install only core dependencies
#pip install -e .

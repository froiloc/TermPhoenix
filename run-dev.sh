#!/bin/bash

# TermPhoenix Development Script
# Usage: ./run-dev.sh [command] [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
PYTHON_VERSION="3.12"
PROJECT_NAME="termphoenix"

print_status() {
    echo -e "${BLUE}[TERMPHOENIX]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

install_git_hooks() {
    print_status "Installing Git hooks..."
    
    if [ ! -d ".git" ]; then
        print_error "This is not a git repository."
        exit 1
    fi
    
    # Run the install script
    if [ -f ".githooks/install-hooks.sh" ]; then
        chmod +x .githooks/install-hooks.sh
        ./.githooks/install-hooks.sh
    else
        print_error "Hook installation script not found."
        exit 1
    fi
}

setup_environment() {
    print_status "Setting up Python virtual environment..."
    
    # Check if Python 3.12 is available
    if ! command -v python3.12 &> /dev/null; then
        print_error "Python 3.12 is required but not found. Please install it first."
        exit 1
    fi
    
    # Create virtual environment
    python3.12 -m venv $VENV_DIR
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install project in development mode
    pip install -e ".[dev]"
    
    print_success "Virtual environment setup complete!"
}

run_tests() {
    print_status "Running tests..."
    source $VENV_DIR/bin/activate
    python -m pytest tests/ -v --cov=src/termphoenix --cov-report=html
}

run_linting() {
    print_status "Running code formatting and linting..."
    source $VENV_DIR/bin/activate
    
    # Format code with black
    print_status "Formatting code with black..."
    black src/ tests/
    
    # Check code quality with flake8
    print_status "Checking code quality with flake8..."
    flake8 src/ tests/
    
    # Optional: type checking with mypy (if installed)
    if command -v mypy &> /dev/null; then
        print_status "Running type checks with mypy..."
        mypy src/
    fi
}

run_application() {
    print_status "Running TermPhoenix application..."
    source $VENV_DIR/bin/activate
    python -m termphoenix "$@"
}

clean_environment() {
    print_status "Cleaning up..."
    
    # Remove virtual environment
    if [ -d "$VENV_DIR" ]; then
        rm -rf $VENV_DIR
        print_success "Virtual environment removed"
    fi
    
    # Remove cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .coverage htmlcov
    
    print_success "Cleanup complete!"
}

show_help() {
    echo "TermPhoenix Development Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup       Set up the development environment"
    echo "  test        Run the test suite"
    echo "  lint        Format and lint the code"
    echo "  run         Run the application (pass arguments after 'run')"
    echo "  clean       Clean up the development environment"
    echo "  all         Run setup, lint, and test"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 test"
    echo "  $0 run --project-name test --url http://example.com"
    echo "  $0 all"
}

case "$1" in
    "setup")
        setup_environment
        ;;
    "test")
        run_tests
        ;;
    "lint")
        run_linting
        ;;
    "run")
        shift  # Remove 'run' from arguments
        run_application "$@"
        ;;
    "clean")
        clean_environment
        ;;
    "all")
        setup_environment
        run_linting
        run_tests
        ;;
     "git-hooks")
        install_git_hooks
        ;;
     "help"|"-h"|"--help")
        show_help
        ;;
    *)
        if [ $# -eq 0 ]; then
            show_help
        else
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
        fi
        ;;
esac

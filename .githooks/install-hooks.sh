#!/bin/bash

# Install Git hooks for TermPhoenix

set -e

echo "🔧 Installing TermPhoenix Git hooks..."

# Make sure we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: This is not a git repository."
    exit 1
fi

# Make hooks executable
chmod +x .githooks/*

# Configure git to use our hooks directory
git config core.hooksPath .githooks

# If using older git version, symlink individual hooks
if git --version | grep -q "2.9"; then
    echo "Git version < 2.9 detected, creating symlinks..."
    ln -sf ../../.githooks/pre-commit .git/hooks/pre-commit
    ln -sf ../../.githooks/pre-push .git/hooks/pre-push
fi

echo "✅ Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Runs before each commit"
echo "  - pre-push:   Runs before each push (includes tests)"
echo ""
echo "To skip hooks temporarily:"
echo "  git commit --no-verify"
echo "  git push --no-verify"

# Clone and setup
git clone https://github.com/froiloc/TermPhoenix.git
cd TermPhoenix

# One-time setup
./run-dev.sh setup
./run-dev.sh git-hooks

# Normal development workflow
git add .
git commit -m "Your message"  # Auto-formats code
git push                      # Runs tests first

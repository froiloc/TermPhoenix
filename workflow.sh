#!/bin/bash

# One-time setup
./run-dev.sh setup

# Run everything (setup, lint, test)
./run-dev.sh all

# Just run tests
./run-dev.sh test

# Just lint code
./run-dev.sh lint

# Run the application
./run-dev.sh run --project-name "Blindspot" --url "https://blindspot.fandom.com/wiki/Blindspot_Wiki"

# Clean up
./run-dev.sh clean

# Show help
./run-dev.sh help

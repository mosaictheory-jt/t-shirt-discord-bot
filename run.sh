#!/bin/bash

# Simple run script for local development

set -e

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your credentials."
    exit 1
fi

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Create necessary directories
mkdir -p generated_images
mkdir -p logs

# Run the bot
echo "Starting Discord T-Shirt Bot..."
python -m src.main

#!/bin/bash
set -e  # Exit on error

# Install system dependencies
apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Update pip and set up Python environment
python -m pip install --upgrade pip setuptools wheel

# Install git dependencies first
pip install --no-cache-dir git+https://github.com/agno-ai/agno-python.git@main

# Install other dependencies from requirements.txt
pip install --no-cache-dir -r requirements.txt

# Set up environment variables
export STREAMLIT_SERVER_PORT=10000
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

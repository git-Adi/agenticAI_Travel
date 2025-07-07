#!/bin/bash
# Update pip and set up Python environment
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install --no-cache-dir -r requirements.txt

# Install Streamlit explicitly
pip install --no-cache-dir streamlit

# Set up environment variables
export STREAMLIT_SERVER_PORT=10000
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

#!/bin/bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Set up environment variables
export STREAMLIT_SERVER_PORT=10000
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the Streamlit app
streamlit run run.py --server.port=10000 --server.address=0.0.0.0

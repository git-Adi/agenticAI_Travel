#!/bin/bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env <<EOL
# Environment Variables
SERPAPI_API_KEY=your_serpapi_api_key_here
# Add other environment variables here
EOL
    echo "Please update the .env file with your API keys and other configuration."
fi

echo "Setup complete!"

#!/bin/bash
set -e

echo "Setting up embedding application..."

# Initialize the database
python -m app.main setup

echo "Setup complete! You can now:"
echo "1. Embed documents: python -m app.main embed <json_file>"
echo "2. Start the web server: python -m app.main serve"
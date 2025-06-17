#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install dependencies using uv
uv pip install -r requirements.txt

echo "Setup complete! You can now run the script with:"
echo "source venv/bin/activate && python track_creator.py" 
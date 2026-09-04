#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Run the main application script
python src/main.py

# Deactivate the virtual environment
deactivate
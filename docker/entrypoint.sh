#!/bin/bash

# Run command to create secrets.toml file based on the secrets.example.toml file
python utils/generator.py
GENERATOR_EXIT_STATUS_CODE=$?

# Check the exit code
if [ $GENERATOR_EXIT_STATUS_CODE -ne 0 ]; then
  echo "Error: generate_secrets.py script encountered an error."
  # Add code to generate sns notification
fi

# Run the Goaling Report
streamlit run Local_Scorecard.py --server.address=0.0.0.0 --logger.level=debug
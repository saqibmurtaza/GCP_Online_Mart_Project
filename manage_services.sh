#!/bin/bash

# List of service directories
services=("fastapi_1" "fastapi_2" "user_service" "order_service" "inventory_service")

# Install dependencies and activate environment for each service
for service in "${services[@]}"; do
  echo "Processing $service"
  cd ~/kafka_project/$service || { echo "Directory $service not found"; continue; }
  
  # Install dependencies
  if [ -f "pyproject.toml" ]; then
    echo "Installing dependencies for $service"
    poetry install || { echo "Failed to install dependencies for $service"; }
  else
    echo "pyproject.toml not found for $service"
  fi
  
  # Activate virtual environment (if needed)
  if [ -d ".venv" ]; then
    echo "Activating environment for $service"
    source .venv/bin/activate || { echo "Failed to activate environment for $service"; }
    
    # Optionally, run additional commands here
    # e.g., python script.py
    
    # Deactivate environment (optional)
    deactivate || { echo "Failed to deactivate environment for $service"; }
  else
    echo ".venv not found for $service"
  fi
  
  cd ..
done

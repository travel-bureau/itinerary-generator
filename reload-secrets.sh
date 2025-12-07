#!/bin/bash
set -e  # Exit immediately if a command fails

echo "Deleting existing secrets..."
./delete-env-secrets.sh

echo "Loading new secrets..."
./upload-env-to-github.sh

echo "All scripts executed successfully."

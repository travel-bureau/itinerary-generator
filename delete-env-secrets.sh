#!/bin/bash

# Get current Git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Map branch to GitHub environment
ENV_NAME=$([[ "$CURRENT_BRANCH" == "master" ]] && echo "prod" || echo "$CURRENT_BRANCH")

# List all secrets in the environment
echo "🔍 Deleting secrets from environment: $ENV_NAME"
SECRETS=$(gh secret list --env "$ENV_NAME" --json name --jq '.[].name')

if [[ -z "$SECRETS" ]]; then
  echo "✅ No secrets found in environment: $ENV_NAME"
  exit 0
fi

# Convert secrets to array
readarray -t SECRET_ARRAY <<< "$SECRETS"
TOTAL=${#SECRET_ARRAY[@]}

# Loop through and delete each secret with progress
for ((i=0; i<TOTAL; i++)); do
  secret="${SECRET_ARRAY[$i]}"

  # 🌀 Show progress bar
  ./pretty_progress.sh "$((i + 1))" "$TOTAL"

  # 🗑️ Delete secret silently
  gh secret remove "$secret" --env "$ENV_NAME" &> /dev/null
done

echo -e "\n✅ All secrets deleted from environment: $ENV_NAME"

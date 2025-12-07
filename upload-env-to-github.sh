#!/bin/bash

# Repo and environment config
REPO=" travel-bureau/itinerary-generator"   # 🔁 Replace with your actual repo
ENV_NAME="prod"                  # Target GitHub environment
ENV_FILE_PATH=".env"

# Load token from .env
if [ -f "$ENV_FILE_PATH" ]; then
  export GH_TOKEN=$(grep CUSTOM_DEPLOY_TOKEN .env | cut -d '=' -f2 | xargs)
else
  echo "❌ .env file not found."
  exit 1
fi

# Ensure GitHub CLI is authenticated
gh auth status || exit 1

# Count total secrets excluding CUSTOM_DEPLOY_TOKEN, comments, and blank lines
total=$(grep -vE '^\s*#|^\s*$' "$ENV_FILE_PATH" | grep -v '^CUSTOM_DEPLOY_TOKEN=' | wc -l)
count=0

# Read and upload each line
while IFS="=" read -r key value; do
  [[ -z "$key" || "$key" =~ ^# || "$key" == "CUSTOM_DEPLOY_TOKEN" ]] && continue

  key=$(echo "$key" | xargs)
  value=$(echo "$value" | sed -e 's/^["'"'"']//' -e 's/["'"'"']$//' | xargs)

  # 🔐 Set secret silently
  gh secret set "$key" --env "$ENV_NAME" --body "$value" &> /dev/null

  # 🎯 Show progress bar
  count=$((count + 1))
  ./pretty_progress.sh "$count" "$total"
done < "$ENV_FILE_PATH"

echo -e "✅ All secrets uploaded to GitHub environment '$ENV_NAME'"

# 📁 Upload sa-key.json as GCP_SA_KEY
if [ -f "keys/sa-key.json" ]; then
  sa_key=$(<keys/sa-key.json)
  gh secret set GCP_SA_KEY --env "$ENV_NAME" --body "$sa_key" &> /dev/null
  echo "🔐 GCP_SA_KEY uploaded from keys/sa-key.json"
else
  echo "⚠️ keys/sa-key.json not found — skipping GCP_SA_KEY upload"
fi

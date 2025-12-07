#!/bin/bash

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Map branch to gcloud config name
case "$BRANCH" in
  master)
    CONFIG_NAME="lovelytrails"
    ;;
  *)
    echo "❌ No gcloud config mapped for branch: $BRANCH"
    exit 1
    ;;
esac

if ! gcloud config configurations list --format="value(name)" | grep -q "^$CONFIG_NAME$"; then
  echo "❌ Config '$CONFIG_NAME' not found"
  exit 1
fi

# Activate the config
echo "🔄 Activating gcloud config: $CONFIG_NAME"
gcloud config configurations activate "$CONFIG_NAME"

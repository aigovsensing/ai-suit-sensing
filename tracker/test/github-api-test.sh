#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$GH_TOKEN" ]; then
    echo "Error: GH_TOKEN is not set."
    exit 1
fi

echo "Testing GitHub API..."

curl -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user

#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "Error: SLACK_WEBHOOK_URL is not set."
    exit 1
fi

echo "Testing Slack Webhook API..."

curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"✅ AI Suit Tracker API Connection Test: Slack Webhook is working!"}' \
    "${SLACK_WEBHOOK_URL}"

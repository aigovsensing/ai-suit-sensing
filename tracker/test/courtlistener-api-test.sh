#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$COURTLISTENER_TOKEN" ]; then
    echo "Error: COURTLISTENER_TOKEN is not set."
    exit 1
fi

echo "Testing CourtListener API..."

curl -H "Authorization: Token ${COURTLISTENER_TOKEN}" \
    "https://www.courtlistener.com/api/rest/v3/search/?q=artificial+intelligence&type=r"

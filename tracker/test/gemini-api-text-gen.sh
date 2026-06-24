#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY is not set."
    exit 1
fi

echo "Testing Gemini Text Generation API (Gemini)..."

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
      "contents": [{
        "parts":[{"text": "Summarize the current status of AI copyright lawsuits in 3 bullet points."}]
      }]
    }'

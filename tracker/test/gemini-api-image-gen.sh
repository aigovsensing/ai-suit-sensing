#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY is not set."
    exit 1
fi

echo "Testing Gemini Image Generation API (Imagen 4)..."

# Note: Using imagen-4.0-generate-001 for Imagen 4 support in Gemini API
curl "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
        "instances": [
            { "prompt": "A futuristic courthouse with AI judges, digital art style, high resolution" }
        ]
    }'

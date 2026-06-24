#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$HF_TOKEN" ]; then
    echo "Error: HF_TOKEN is not set."
    exit 1
fi

echo "Testing Hugging Face Router API (Standard Inference)..."

# Using the confirmed 2026 Router endpoint with correct model ID case
curl https://router.huggingface.co/hf-inference/models/meta-llama/Llama-3.1-8B-Instruct \
    -X POST \
    -H "Authorization: Bearer ${HF_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"inputs": "Explain AI lawsuits in one sentence."}'

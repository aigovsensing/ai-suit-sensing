#!/bin/bash

# Load environment variables from /etc/environment
if [ -f /etc/environment ]; then
    export $(grep -v '^#' /etc/environment | xargs)
fi

if [ -z "$HF_TOKEN" ]; then
    echo "Error: HF_TOKEN is not set."
    exit 1
fi

echo "Testing Hugging Face Router API (FLUX.1-schnell Inference)..."
echo "⚠️  Note: You must accept terms at https://huggingface.co/black-forest-labs/FLUX.1-schnell"

# Using the confirmed 2026 Router hf-inference endpoint
curl -s -X POST https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell \
    -H "Authorization: Bearer ${HF_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"inputs": "A futuristic courthouse with AI judges, ghibli style, high resolution"}' \
    --output ./test/hf_test_image.png

if [ $? -eq 0 ] && [ -f ./test/hf_test_image.png ]; then
    # Check if the file is actually an image (standard inference returns binary)
    if file ./test/hf_test_image.png | grep -q "image"; then
        echo "✅ Image successfully generated and saved to ./test/hf_test_image.png"
    else
        echo "❌ Image generation failed. Response check:"
        head -c 200 ./test/hf_test_image.png
        echo -e "\n..."
    fi
else
    echo "❌ Curl command failed."
fi

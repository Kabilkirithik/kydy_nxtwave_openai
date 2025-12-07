#!/bin/bash
# Script to set up environment variables for the backend

echo "Kydy Backend API Key Setup"
echo "=========================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Get Gemini API Key
echo "Enter your Gemini API Key (or press Enter to skip):"
read -r GEMINI_KEY
if [ -n "$GEMINI_KEY" ]; then
    echo "GEMINI_API_KEY=$GEMINI_KEY" >> .env
    echo "✅ Gemini API Key saved"
else
    echo "⏭️  Skipping Gemini API Key (will use fallback)"
fi

echo ""

# Get Hugging Face API Token
echo "Enter your Hugging Face API Token (or press Enter to skip):"
read -r HF_TOKEN
if [ -n "$HF_TOKEN" ]; then
    echo "HF_API_TOKEN=$HF_TOKEN" >> .env
    echo "✅ Hugging Face API Token saved"
else
    echo "⏭️  Skipping Hugging Face API Token (will use fallback)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use these environment variables, run:"
echo "  source .env"
echo "  # or"
echo "  export \$(cat .env | xargs)"
echo ""
echo "Or use a tool like python-dotenv to load them automatically."


#!/bin/bash

# SafeGuard AI - GitHub Secrets Setup Script
# Automates the configuration of GitHub repository secrets

set -e

echo "🔐 SafeGuard AI - GitHub Secrets Setup"
echo "======================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged in to GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"
echo ""

# Load .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Create a .env file with your API keys first"
    exit 1
fi

echo "📥 Loading secrets from .env file..."
source .env

# Function to set secret
set_secret() {
    local name=$1
    local value=$2

    if [ -z "$value" ]; then
        echo "⏭️  Skipping $name (not set in .env)"
        return
    fi

    echo "Setting $name..."
    echo "$value" | gh secret set "$name" --repo="$REPO"
    echo "✅ $name set successfully"
}

echo ""
echo "🔑 Setting API Keys..."
set_secret "OPENAI_API_KEY" "$OPENAI_API_KEY"
set_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY"
set_secret "OPENWEATHER_API_KEY" "$OPENWEATHER_API_KEY"

echo ""
echo "📧 Setting Email Credentials..."
set_secret "EMAIL_FROM" "$EMAIL_FROM"
set_secret "EMAIL_PASSWORD" "$EMAIL_PASSWORD"
set_secret "EMAIL_TO" "$EMAIL_TO"
set_secret "SMTP_HOST" "${SMTP_HOST:-smtp.gmail.com}"
set_secret "SMTP_PORT" "${SMTP_PORT:-587}"

echo ""
echo "🤗 Setting Hugging Face Configuration..."
echo "Enter your Hugging Face username:"
read -r HF_USERNAME
set_secret "HF_USERNAME" "$HF_USERNAME"

echo "Enter your Hugging Face Space name (e.g., safeguard-ai-backend):"
read -r HF_SPACE_NAME
set_secret "HF_SPACE_NAME" "$HF_SPACE_NAME"

echo "Enter your Hugging Face API token (from https://huggingface.co/settings/tokens):"
read -rs HF_TOKEN
set_secret "HF_TOKEN" "$HF_TOKEN"

# Calculate Hugging Face backend URL
HF_BACKEND_URL="https://${HF_USERNAME}-${HF_SPACE_NAME}.hf.space"
echo "Hugging Face backend URL will be: $HF_BACKEND_URL"

echo ""
echo "▲ Setting Vercel Configuration..."
echo "Enter your Vercel authentication token (from https://vercel.com/account/tokens):"
read -rs VERCEL_TOKEN
set_secret "VERCEL_TOKEN" "$VERCEL_TOKEN"

set_secret "NEXT_PUBLIC_API_URL" "$HF_BACKEND_URL"
set_secret "NEXT_PUBLIC_WS_URL" "wss://${HF_USERNAME}-${HF_SPACE_NAME}.hf.space"

echo ""
echo "✅ All secrets configured successfully!"
echo ""
echo "📋 Summary:"
echo "  - OpenAI API Key: ✓"
echo "  - Hugging Face Space: $HF_USERNAME/$HF_SPACE_NAME"
echo "  - Backend URL: $HF_BACKEND_URL"
echo "  - Vercel Token: ✓"
echo ""
echo "🚀 You can now push to trigger CI/CD deployment!"

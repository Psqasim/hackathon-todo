#!/bin/bash
# Generate Kubernetes secrets.yaml from .env file
# WARNING: secrets.yaml contains sensitive data - never commit to git!

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
SECRETS_FILE="$PROJECT_ROOT/k8s/secrets.yaml"

echo "=== Kubernetes Secrets Generator ==="

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    echo "Please create .env with required secrets first"
    exit 1
fi

# Function to get value from .env file
get_env_value() {
    local key="$1"
    grep "^${key}=" "$ENV_FILE" | cut -d '=' -f 2- | tr -d '"' | tr -d "'"
}

# Function to base64 encode (compatible with both Linux and macOS)
b64encode() {
    echo -n "$1" | base64 | tr -d '\n'
}

# Load required variables
DATABASE_URL=$(get_env_value "DATABASE_URL")
JWT_SECRET_KEY=$(get_env_value "JWT_SECRET_KEY")
OPENAI_API_KEY=$(get_env_value "OPENAI_API_KEY")
GOOGLE_CLIENT_ID=$(get_env_value "GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=$(get_env_value "GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID=$(get_env_value "GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET=$(get_env_value "GITHUB_CLIENT_SECRET")

# Check required variables
REQUIRED_VARS=("DATABASE_URL" "JWT_SECRET_KEY" "OPENAI_API_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    eval "val=\$$var"
    if [ -z "$val" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "ERROR: Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

echo "✓ All required variables found in .env"
echo "✓ Generating secrets.yaml..."

# Generate secrets.yaml
cat > "$SECRETS_FILE" << EOF
# WARNING: This file contains base64-encoded secrets
# DO NOT commit this file to git!
# Generated from .env on $(date -u +"%Y-%m-%dT%H:%M:%SZ")

apiVersion: v1
kind: Secret
metadata:
  name: taskflow-secrets
  namespace: taskflow
  labels:
    app: taskflow
type: Opaque
data:
  # Database connection string
  DATABASE_URL: $(b64encode "$DATABASE_URL")

  # JWT secret for token signing
  JWT_SECRET_KEY: $(b64encode "$JWT_SECRET_KEY")

  # OpenAI API key for chatbot
  OPENAI_API_KEY: $(b64encode "$OPENAI_API_KEY")

  # OAuth credentials (if present)
EOF

# Add OAuth secrets if they exist
if [ -n "$GOOGLE_CLIENT_ID" ]; then
    echo "  GOOGLE_CLIENT_ID: $(b64encode "$GOOGLE_CLIENT_ID")" >> "$SECRETS_FILE"
fi

if [ -n "$GOOGLE_CLIENT_SECRET" ]; then
    echo "  GOOGLE_CLIENT_SECRET: $(b64encode "$GOOGLE_CLIENT_SECRET")" >> "$SECRETS_FILE"
fi

if [ -n "$GITHUB_CLIENT_ID" ]; then
    echo "  GITHUB_CLIENT_ID: $(b64encode "$GITHUB_CLIENT_ID")" >> "$SECRETS_FILE"
fi

if [ -n "$GITHUB_CLIENT_SECRET" ]; then
    echo "  GITHUB_CLIENT_SECRET: $(b64encode "$GITHUB_CLIENT_SECRET")" >> "$SECRETS_FILE"
fi

echo ""
echo "✅ Generated: $SECRETS_FILE"
echo ""
echo "⚠️  SECURITY REMINDER:"
echo "   - secrets.yaml is in .gitignore (DO NOT commit)"
echo "   - Base64 encoding is NOT encryption"
echo "   - Values are visible with: kubectl get secret -o yaml"
echo ""
echo "Next steps:"
echo "  1. Verify: cat $SECRETS_FILE"
echo "  2. Apply: kubectl apply -f $SECRETS_FILE"
echo ""

#!/usr/bin/env bash
# Deploy yt-scripter to AWS Lightsail Container Service.
# Prerequisites: AWS CLI configured, Docker running.
# Usage: ./deploy.sh [service-name]

set -euo pipefail

SERVICE="${1:-yt-scripter}"
REGION="us-east-1"          # change if needed
IMAGE_LABEL="app"

echo "==> Building Docker image..."
docker build -t "$SERVICE" .

echo "==> Creating Lightsail container service (skips if already exists)..."
aws lightsail create-container-service \
  --service-name "$SERVICE" \
  --power nano \
  --scale 1 \
  --region "$REGION" 2>/dev/null || echo "    (service already exists, continuing)"

echo "==> Waiting for service to be ready..."
aws lightsail wait container-service-is-stable \
  --service-name "$SERVICE" \
  --region "$REGION" || true

echo "==> Pushing image to Lightsail registry..."
aws lightsail push-container-image \
  --service-name "$SERVICE" \
  --label "$IMAGE_LABEL" \
  --image "$SERVICE:latest" \
  --region "$REGION"

# The pushed image is referenced as :service.label.N — grab the latest digest
IMAGE_REF=$(aws lightsail get-container-images \
  --service-name "$SERVICE" \
  --region "$REGION" \
  --query 'containerImages[0].image' \
  --output text)

echo "==> Deploying image: $IMAGE_REF"

# Prompt for API key if not set
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  read -rsp "Enter ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
  echo
fi

aws lightsail create-container-service-deployment \
  --service-name "$SERVICE" \
  --region "$REGION" \
  --containers "{
    \"app\": {
      \"image\": \"$IMAGE_REF\",
      \"environment\": {
        \"ANTHROPIC_API_KEY\": \"$ANTHROPIC_API_KEY\"
      },
      \"ports\": {\"5000\": \"HTTP\"}
    }
  }" \
  --public-endpoint "{
    \"containerName\": \"app\",
    \"containerPort\": 5000,
    \"healthCheck\": {
      \"path\": \"/\",
      \"intervalSeconds\": 30,
      \"timeoutSeconds\": 5,
      \"successCodes\": \"200\"
    }
  }"

echo "==> Waiting for deployment to stabilize..."
aws lightsail wait container-service-is-stable \
  --service-name "$SERVICE" \
  --region "$REGION"

URL=$(aws lightsail get-container-services \
  --service-name "$SERVICE" \
  --region "$REGION" \
  --query 'containerServices[0].url' \
  --output text)

echo ""
echo "============================================"
echo "  Deployed: $URL"
echo "============================================"

#!/bin/bash

# Deployment script for Google Cloud Platform

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="discord-tshirt-bot"

echo "Deploying Discord T-Shirt Bot to Google Cloud..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Check if required environment variables are set
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "Error: DISCORD_BOT_TOKEN is not set"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set"
    exit 1
fi

if [ -z "$PRINTFUL_API_KEY" ]; then
    echo "Error: PRINTFUL_API_KEY is not set"
    exit 1
fi

if [ -z "$PRINTFUL_STORE_ID" ]; then
    echo "Error: PRINTFUL_STORE_ID is not set"
    exit 1
fi

# Store secrets in Secret Manager
echo "Storing secrets in Secret Manager..."
echo -n "$DISCORD_BOT_TOKEN" | gcloud secrets create discord-bot-token \
    --replication-policy="automatic" \
    --data-file=- \
    --project="$PROJECT_ID" || \
    echo -n "$DISCORD_BOT_TOKEN" | gcloud secrets versions add discord-bot-token \
    --data-file=- \
    --project="$PROJECT_ID"

echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key \
    --replication-policy="automatic" \
    --data-file=- \
    --project="$PROJECT_ID" || \
    echo -n "$GOOGLE_API_KEY" | gcloud secrets versions add google-api-key \
    --data-file=- \
    --project="$PROJECT_ID"

echo -n "$PRINTFUL_API_KEY" | gcloud secrets create printful-api-key \
    --replication-policy="automatic" \
    --data-file=- \
    --project="$PROJECT_ID" || \
    echo -n "$PRINTFUL_API_KEY" | gcloud secrets versions add printful-api-key \
    --data-file=- \
    --project="$PROJECT_ID"

echo -n "$PRINTFUL_STORE_ID" | gcloud secrets create printful-store-id \
    --replication-policy="automatic" \
    --data-file=- \
    --project="$PROJECT_ID" || \
    echo -n "$PRINTFUL_STORE_ID" | gcloud secrets versions add printful-store-id \
    --data-file=- \
    --project="$PROJECT_ID"

# Build and deploy using Cloud Build
echo "Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml --project="$PROJECT_ID"

echo "Deployment complete!"
echo "Check status: gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"

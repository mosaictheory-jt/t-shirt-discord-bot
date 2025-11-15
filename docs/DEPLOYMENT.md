# Deployment Guide

This guide covers deploying the Discord T-Shirt Bot to Google Cloud Platform.

## Prerequisites

- Google Cloud account
- `gcloud` CLI installed and configured
- Docker installed (for local testing)
- All required API keys (Discord, Google, Printful)

## Deployment with Google Cloud Run

**Cloud Run is the recommended and supported deployment platform** for this bot because:
- **Automatic scaling**: Scales to zero when not in use, scales up automatically under load
- **Cost-effective**: Pay only for what you use (free tier available)
- **Easy deployment**: Simple one-command deployment
- **Managed infrastructure**: No server management required
- **Built-in logging**: Integrated with Cloud Logging
- **Fast updates**: Deploy new versions in seconds

#### Setup

1. **Install and Configure gcloud CLI**

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and authenticate
gcloud init
gcloud auth login
```

2. **Set Your Project**

```bash
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

3. **Enable Required APIs**

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

4. **Set Environment Variables**

```bash
export DISCORD_BOT_TOKEN="your-discord-bot-token"
export GOOGLE_API_KEY="your-google-api-key"
export PRINTFUL_API_KEY="your-printful-api-key"
export LANGCHAIN_API_KEY="your-langsmith-api-key"  # Optional
```

5. **Deploy Using the Script**

```bash
chmod +x deploy.sh
./deploy.sh
```

#### Manual Deployment

If you prefer manual deployment:

```bash
# Build the container
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot

# Deploy to Cloud Run
gcloud run deploy discord-tshirt-bot \
  --image gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --set-env-vars PRINTFUL_API_KEY=$PRINTFUL_API_KEY \
  --set-env-vars LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY \
  --memory 512Mi \
  --timeout 3600
```

#### Using Secret Manager (More Secure)

```bash
# Store secrets
echo -n "$DISCORD_BOT_TOKEN" | gcloud secrets create discord-bot-token \
  --replication-policy="automatic" \
  --data-file=-

echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key \
  --replication-policy="automatic" \
  --data-file=-

echo -n "$PRINTFUL_API_KEY" | gcloud secrets create printful-api-key \
  --replication-policy="automatic" \
  --data-file=-

# Deploy with secrets
gcloud run deploy discord-tshirt-bot \
  --image gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot \
  --region us-central1 \
  --platform managed \
  --set-secrets DISCORD_BOT_TOKEN=discord-bot-token:latest \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --set-secrets PRINTFUL_API_KEY=printful-api-key:latest
```

## Alternative: Local Deployment with Docker

For local testing or self-hosted deployment:

1. **Using Docker Compose**

```bash
# Create .env file with your credentials
cp .env.example .env
nano .env

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

2. **Direct Docker Run**

```bash
# Build the image
docker build -t discord-tshirt-bot .

# Run the container
docker run -d \
  --name discord-tshirt-bot \
  --env-file .env \
  -v $(pwd)/generated_images:/app/generated_images \
  -v $(pwd)/logs:/app/logs \
  discord-tshirt-bot

# View logs
docker logs -f discord-tshirt-bot

# Stop the container
docker stop discord-tshirt-bot
```

## Monitoring and Logs

### View Logs (Cloud Run)

```bash
gcloud run services logs read discord-tshirt-bot \
  --region us-central1 \
  --limit 50
```

### View Logs (Docker)

```bash
docker-compose logs -f
# or
docker logs -f discord-tshirt-bot
```

## Updating the Bot

### Cloud Run

```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot
gcloud run deploy discord-tshirt-bot \
  --image gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot \
  --region us-central1
```

### Local Docker

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Cost Optimization

### Cloud Run Pricing
- **Free tier**: 2 million requests/month, 360,000 GB-seconds memory/month
- **Pricing after free tier**:
  - CPU: $0.00002400 per vCPU-second
  - Memory: $0.00000250 per GiB-second
  - Requests: $0.40 per million requests
- **Typical costs**: $5-20/month for moderate usage
- **Idle cost**: $0 when not receiving requests (scales to zero)

### Cost Optimization Tips
- Use Secret Manager for credentials
- Enable Cloud Logging for debugging
- Set up budget alerts
- Use Cloud Monitoring for uptime checks

## Troubleshooting

### Bot not starting
```bash
# Check logs
gcloud run services logs read discord-tshirt-bot --region us-central1

# Check environment variables
gcloud run services describe discord-tshirt-bot --region us-central1
```

### Out of memory errors
```bash
# Increase memory allocation
gcloud run services update discord-tshirt-bot \
  --memory 1Gi \
  --region us-central1
```

### Timeout errors
```bash
# Increase timeout
gcloud run services update discord-tshirt-bot \
  --timeout 3600 \
  --region us-central1
```

# Deployment Guide

This guide covers deploying the Discord T-Shirt Bot to Google Cloud Platform.

## Prerequisites

- Google Cloud account
- `gcloud` CLI installed and configured
- Docker installed (for local testing)
- All required API keys (Discord, Google, Printful)

## Deployment Options

### Option 1: Google Cloud Run (Recommended)

Cloud Run is ideal for this bot because:
- Automatic scaling
- Pay only for what you use
- Easy deployment and updates
- Built-in logging and monitoring

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

### Option 2: Google Compute Engine

For more control and persistent storage:

1. **Create a VM Instance**

```bash
gcloud compute instances create discord-bot-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB
```

2. **SSH into the VM**

```bash
gcloud compute ssh discord-bot-vm --zone=us-central1-a
```

3. **Install Dependencies**

```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Log out and back in for group changes
exit
gcloud compute ssh discord-bot-vm --zone=us-central1-a
```

4. **Deploy the Bot**

```bash
# Clone repository
git clone <repository-url>
cd discord-tshirt-bot

# Create .env file with your credentials
nano .env

# Run with Docker Compose
docker-compose up -d
```

5. **Set Up Auto-Start**

```bash
# Create systemd service
sudo nano /etc/systemd/system/discord-bot.service
```

Add:

```ini
[Unit]
Description=Discord T-Shirt Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/<username>/discord-tshirt-bot
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=<username>

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

### Option 3: Google Kubernetes Engine (GKE)

For high availability and advanced orchestration:

1. **Create a GKE Cluster**

```bash
gcloud container clusters create discord-bot-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-small
```

2. **Create Kubernetes Secrets**

```bash
kubectl create secret generic bot-secrets \
  --from-literal=discord-bot-token=$DISCORD_BOT_TOKEN \
  --from-literal=google-api-key=$GOOGLE_API_KEY \
  --from-literal=printful-api-key=$PRINTFUL_API_KEY
```

3. **Create Deployment**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: discord-tshirt-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: discord-tshirt-bot
  template:
    metadata:
      labels:
        app: discord-tshirt-bot
    spec:
      containers:
      - name: bot
        image: gcr.io/PROJECT_ID/discord-tshirt-bot:latest
        env:
        - name: DISCORD_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: bot-secrets
              key: discord-bot-token
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: bot-secrets
              key: google-api-key
        - name: PRINTFUL_API_KEY
          valueFrom:
            secretKeyRef:
              name: bot-secrets
              key: printful-api-key
```

4. **Deploy**

```bash
kubectl apply -f deployment.yaml
```

## Monitoring and Logs

### View Logs (Cloud Run)

```bash
gcloud run services logs read discord-tshirt-bot \
  --region us-central1 \
  --limit 50
```

### View Logs (Compute Engine)

```bash
docker-compose logs -f
```

### View Logs (GKE)

```bash
kubectl logs -f deployment/discord-tshirt-bot
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

### Compute Engine

```bash
gcloud compute ssh discord-bot-vm --zone=us-central1-a
cd discord-tshirt-bot
git pull
docker-compose down
docker-compose up -d --build
```

### GKE

```bash
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/discord-tshirt-bot
kubectl rollout restart deployment/discord-tshirt-bot
```

## Cost Optimization

### Cloud Run
- Uses a pay-per-request model
- Free tier: 2 million requests/month
- Memory: 512Mi should be sufficient
- Timeout: Set to minimum needed (300-600s)

### Compute Engine
- Use preemptible VMs for cost savings
- e2-micro eligible for free tier
- Consider auto-shutdown during low usage

### Tips
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

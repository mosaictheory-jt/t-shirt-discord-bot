# Use official UV image which includes Python
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies using UV
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY src/ ./src/
COPY .env.example .env

# Create directory for generated images
RUN mkdir -p generated_images

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "-m", "src.main"]

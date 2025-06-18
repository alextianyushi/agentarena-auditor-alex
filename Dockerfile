# Builder stage for installing dependencies
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml .

# Install build tools and dependencies in a single layer
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && pip install --no-cache-dir fastapi>=0.95.0 uvicorn>=0.21.1 httpx>=0.24.0 \
    pydantic>=1.10.7 pydantic_settings>=2.0.0 python-dotenv>=1.0.0 \
    openai>=1.0.0 gitpython>=3.1.31 questionary>=2.0.1 \
    && rm -rf /var/lib/apt/lists/*

# Final stage for running the application
FROM python:3.11-slim

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Set working directory
WORKDIR /app

# Build arguments for configuration
ARG WEBHOOK_AUTH_TOKEN
ARG OPENAI_API_KEY
ARG AGENTARENA_API_KEY
ARG OPENAI_MODEL
ARG LOG_LEVEL
ARG LOG_FILE
ARG DATA_DIR
ARG PORT

# Set environment variables from build args
ENV WEBHOOK_AUTH_TOKEN=$WEBHOOK_AUTH_TOKEN \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    AGENTARENA_API_KEY=$AGENTARENA_API_KEY \
    OPENAI_MODEL=$OPENAI_MODEL \
    LOG_LEVEL=$LOG_LEVEL \
    LOG_FILE=$LOG_FILE \
    DATA_DIR=/app/data \
    PORT=$PORT

# Copy application code
COPY . .

# Create necessary directories for data and logs
RUN mkdir -p /app/data /app/logs

# Expose the application port
EXPOSE $PORT

# Start the FastAPI application
CMD ["python", "-c", "import logging; logging.basicConfig(level=logging.DEBUG); from agent.server import app, start_server; from agent.config import load_config; app.state.config = load_config(); import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')"] 
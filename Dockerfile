# Dockerfile for Hugging Face Spaces Deployment
# Runs FastAPI backend + MCP server in a single container

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt ./

# Install Python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/ ./src/

# Copy startup script
COPY start-services.sh ./
RUN chmod +x start-services.sh

# Copy environment configuration
COPY .env.example .env

# Create temp directory for logs and caches (Hugging Face write restriction)
RUN mkdir -p /tmp/logs

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start both services with proper orchestration
# Startup script ensures FastAPI is ready before starting MCP server
CMD ["./start-services.sh"]

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

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using UV
RUN uv sync --frozen --no-dev

# Copy backend source code
COPY src/ ./src/

# Copy environment configuration
COPY .env.example .env

# Create temp directory for logs and caches (Hugging Face write restriction)
RUN mkdir -p /tmp/logs

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start both services using a shell script
# FastAPI on internal port 8000, MCP server on 8001
# Nginx/proxy forwards external port 7860 to internal 8000
CMD ["sh", "-c", "\
    uv run python -m src.mcp_server.server & \
    uv run uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1 \
    "]

# Alternative using exec form (recommended for production)
# CMD ["sh", "-c", "uv run python -m src.mcp_server.server & exec uv run uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1"]

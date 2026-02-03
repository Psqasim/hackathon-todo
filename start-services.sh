#!/bin/bash
# Startup script for HF Spaces - ensures FastAPI is ready before starting MCP server

set -e

echo "Starting FastAPI backend on port 7860..."
uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1 &
FASTAPI_PID=$!

echo "Waiting for FastAPI to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:7860/health > /dev/null; then
    echo "FastAPI is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "FastAPI failed to start within 30 seconds"
    exit 1
  fi
  echo "Waiting for FastAPI... ($i/30)"
  sleep 1
done

echo "Starting MCP server on port 8001..."
python -m src.mcp_server.server &
MCP_PID=$!

echo "All services started successfully"
echo "FastAPI PID: $FASTAPI_PID"
echo "MCP Server PID: $MCP_PID"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

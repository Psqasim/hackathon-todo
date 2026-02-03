#!/bin/bash
# Startup script for HF Spaces - ensures FastAPI is ready before starting MCP server

set -e

echo "[Startup] ===== TaskFlow Services Starting ====="
echo "[Startup] Python version: $(python --version)"
echo "[Startup] Working directory: $(pwd)"

echo "[Startup] Starting FastAPI backend on port 7860..."
uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1 &
FASTAPI_PID=$!
echo "[Startup] FastAPI started with PID: $FASTAPI_PID"

echo "[Startup] Waiting for FastAPI health check..."
READY=false
for i in {1..45}; do
  if curl -f -s http://localhost:7860/health > /dev/null 2>&1; then
    echo "[Startup] ✓ FastAPI is healthy and ready!"
    READY=true
    break
  fi
  if [ $i -eq 45 ]; then
    echo "[Startup] ✗ FastAPI failed to start within 45 seconds"
    echo "[Startup] Checking if FastAPI process is still running..."
    if kill -0 $FASTAPI_PID 2>/dev/null; then
      echo "[Startup] FastAPI process is running but not responding"
    else
      echo "[Startup] FastAPI process has died"
    fi
    exit 1
  fi
  echo "[Startup] Waiting for FastAPI... (attempt $i/45)"
  sleep 1
done

if [ "$READY" = true ]; then
  echo "[Startup] Starting MCP server on port 8001..."
  python -m src.mcp_server.server &
  MCP_PID=$!
  echo "[Startup] MCP Server started with PID: $MCP_PID"

  # Give MCP server a moment to initialize
  sleep 2

  echo "[Startup] ===== All Services Running ====="
  echo "[Startup] FastAPI PID: $FASTAPI_PID (port 7860)"
  echo "[Startup] MCP Server PID: $MCP_PID (port 8001)"
  echo "[Startup] Container ready for requests"

  # Wait for any process to exit
  wait -n

  # Exit with status of process that exited first
  EXIT_CODE=$?
  echo "[Startup] Service exited with code: $EXIT_CODE"
  exit $EXIT_CODE
fi

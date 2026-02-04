#!/bin/sh
# Kubernetes-specific startup script for backend container
# Starts FastAPI + MCP server with proper orchestration and signal handling

set -e

echo "[K8s Startup] ===== TaskFlow Backend Starting ====="
echo "[K8s Startup] Python version: $(python --version)"
echo "[K8s Startup] Working directory: $(pwd)"
echo "[K8s Startup] User: $(id)"

# Handle SIGTERM for graceful shutdown
cleanup() {
    echo "[K8s Startup] Received SIGTERM, shutting down gracefully..."
    if [ ! -z "$FASTAPI_PID" ]; then
        echo "[K8s Startup] Stopping FastAPI (PID: $FASTAPI_PID)..."
        kill -TERM $FASTAPI_PID 2>/dev/null || true
    fi
    if [ ! -z "$MCP_PID" ]; then
        echo "[K8s Startup] Stopping MCP Server (PID: $MCP_PID)..."
        kill -TERM $MCP_PID 2>/dev/null || true
    fi
    wait
    echo "[K8s Startup] Graceful shutdown complete"
    exit 0
}

trap cleanup TERM INT

# Start FastAPI backend
echo "[K8s Startup] Starting FastAPI backend on port 7860..."
uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1 &
FASTAPI_PID=$!
echo "[K8s Startup] FastAPI started with PID: $FASTAPI_PID"

# Wait for FastAPI health check
echo "[K8s Startup] Waiting for FastAPI health check..."
READY=false
i=1
while [ $i -le 30 ]; do
  # Use wget instead of curl (more likely available in slim images)
  if wget -q -O /dev/null http://localhost:7860/health 2>/dev/null; then
    echo "[K8s Startup] ✓ FastAPI is healthy and ready!"
    READY=true
    break
  fi
  if [ $i -eq 30 ]; then
    echo "[K8s Startup] ✗ FastAPI failed to start within 30 seconds"
    echo "[K8s Startup] Checking if FastAPI process is still running..."
    if kill -0 $FASTAPI_PID 2>/dev/null; then
      echo "[K8s Startup] FastAPI process is running but not responding"
      echo "[K8s Startup] Container will continue but may fail readiness probe"
    else
      echo "[K8s Startup] FastAPI process has died"
      exit 1
    fi
  fi
  echo "[K8s Startup] Waiting for FastAPI... (attempt $i/30)"
  sleep 1
  i=$((i + 1))
done

if [ "$READY" = true ]; then
  # Start MCP server
  echo "[K8s Startup] Starting MCP server on port 8001..."
  python -m src.mcp_server.server &
  MCP_PID=$!
  echo "[K8s Startup] MCP Server started with PID: $MCP_PID"

  # Give MCP server a moment to initialize
  sleep 2

  echo "[K8s Startup] ===== All Services Running ====="
  echo "[K8s Startup] FastAPI PID: $FASTAPI_PID (port 7860)"
  echo "[K8s Startup] MCP Server PID: $MCP_PID (port 8001)"
  echo "[K8s Startup] Container ready for requests"
  echo "[K8s Startup] Health endpoint: http://localhost:7860/health"

  # Wait for any process to exit (POSIX-compliant)
  # Since 'wait -n' is not POSIX, we use a simple wait for all processes
  wait

  # If we reach here, a process has exited
  echo "[K8s Startup] A service has exited"

  # Clean up remaining processes
  kill $FASTAPI_PID $MCP_PID 2>/dev/null || true
  wait

  exit 1
fi

#!/bin/sh
# Kubernetes-specific startup script for backend container
# Uses Python launcher to run both FastAPI and MCP server

set -e

echo "[K8s Startup] ===== TaskFlow Backend Container Starting ====="
echo "[K8s Startup] Python version: $(python --version)"
echo "[K8s Startup] Working directory: $(pwd)"
echo "[K8s Startup] User: $(id)"

# Run Python launcher that manages both FastAPI and MCP server
exec python /app/scripts/start-both-servers.py

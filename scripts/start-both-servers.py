#!/usr/bin/env python
"""
Launcher script to run both FastAPI and MCP server in Kubernetes.
Properly handles output, signals, and graceful shutdown.
"""
import asyncio
import signal
import sys
from multiprocessing import Process

import uvicorn


def run_fastapi():
    """Run FastAPI server on port 7860."""
    print("[Launcher] Starting FastAPI on port 7860...")
    uvicorn.run(
        "src.interfaces.api:app",
        host="0.0.0.0",
        port=7860,
        log_level="info",
    )


def run_mcp():
    """Run MCP server on port 8001."""
    print("[Launcher] Starting MCP server on port 8001...")
    from src.mcp_server.server import run_server
    run_server()


def main():
    """Launch both servers and handle shutdown."""
    print("[Launcher] ===== TaskFlow Backend Starting =====")

    # Start both servers in separate processes
    fastapi_process = Process(target=run_fastapi, name="FastAPI")
    mcp_process = Process(target=run_mcp, name="MCP-Server")

    # Handle shutdown signals
    def shutdown_handler(signum, frame):
        print(f"\n[Launcher] Received signal {signum}, shutting down...")
        if fastapi_process.is_alive():
            print("[Launcher] Terminating FastAPI...")
            fastapi_process.terminate()
        if mcp_process.is_alive():
            print("[Launcher] Terminating MCP server...")
            mcp_process.terminate()

        # Wait for graceful shutdown
        fastapi_process.join(timeout=10)
        mcp_process.join(timeout=10)

        # Force kill if still alive
        if fastapi_process.is_alive():
            fastapi_process.kill()
        if mcp_process.is_alive():
            mcp_process.kill()

        print("[Launcher] Shutdown complete")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # Start processes
    fastapi_process.start()
    mcp_process.start()

    print(f"[Launcher] FastAPI PID: {fastapi_process.pid}")
    print(f"[Launcher] MCP Server PID: {mcp_process.pid}")
    print("[Launcher] Both servers started successfully")

    # Wait for either process to exit
    try:
        while fastapi_process.is_alive() and mcp_process.is_alive():
            fastapi_process.join(timeout=1)
            mcp_process.join(timeout=1)

        # If we reach here, one process died
        if not fastapi_process.is_alive():
            print(f"[Launcher] FastAPI exited with code {fastapi_process.exitcode}")
        if not mcp_process.is_alive():
            print(f"[Launcher] MCP server exited with code {mcp_process.exitcode}")

        # Terminate the other process
        shutdown_handler(None, None)

    except KeyboardInterrupt:
        shutdown_handler(None, None)


if __name__ == "__main__":
    main()

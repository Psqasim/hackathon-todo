"""
FastMCP server entry point with HTTP/SSE transport.

This module provides the main MCP server that exposes task management
tools via the Model Context Protocol, accessible by the OpenAI agent.

FR-001: System MUST expose an MCP server on port 8001 with task management tools
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

if TYPE_CHECKING:
    from starlette.requests import Request

# Load environment variables
load_dotenv()

# Configuration
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))
MCP_BACKEND_URL = os.getenv("MCP_BACKEND_URL", "http://localhost:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://hackathon-todo-orcin.vercel.app",
    "https://hackathon-todo.vercel.app",
]

# CORS middleware configuration for browser-based MCP clients
cors_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "Authorization",
            "Content-Type",
        ],
        expose_headers=["mcp-session-id"],
    )
]

# Create FastMCP server instance
mcp = FastMCP("TaskFlow MCP Server")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring.

    Returns status of the MCP server, OpenAI configuration,
    and backend connectivity.
    """
    from .backend_client import BackendClient

    # Check OpenAI configuration
    openai_configured = bool(OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"))

    # Check backend reachability
    backend_reachable = False
    try:
        client = BackendClient()
        backend_reachable = await client.health_check()
    except Exception:
        pass

    return JSONResponse({
        "status": "healthy",
        "openai_configured": openai_configured,
        "backend_reachable": backend_reachable,
        "mcp_server_port": MCP_SERVER_PORT,
        "backend_url": MCP_BACKEND_URL,
    })


def get_app():
    """Get the ASGI application with middleware.

    Returns the FastMCP HTTP app configured with CORS middleware
    for production deployment.
    """
    # Import tools to register them with the MCP server
    from src.mcp_server import tools  # noqa: F401

    return mcp.http_app(middleware=cors_middleware)


def run_server():
    """Run the MCP server.

    Starts the server on the configured port with HTTP transport.
    Used for local development.
    """
    import uvicorn

    app = get_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()

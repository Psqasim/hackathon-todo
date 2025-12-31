"""
MCP Server package for AI Chatbot integration.

This package provides the Model Context Protocol (MCP) server that exposes
task management tools to the OpenAI agent for natural language processing.

Modules:
    server: FastMCP server entry point with HTTP/SSE transport
    tools: 8 MCP tool definitions for task management
    agent: OpenAI gpt-4o-mini agent with function calling
    backend_client: HTTP client for FastAPI backend
    auth: JWT token validation
    nlp: Natural language date and priority parsing
    memory: Conversation history management
    prompts: System prompts for the agent
"""

__version__ = "1.0.0"

"""
Backends package for the Multi-Agent Todo Application.

Contains storage backend protocol and implementations.
Phase II: Added PostgreSQL backend for production persistence.
"""

from src.backends.base import StorageBackend
from src.backends.memory import InMemoryBackend
from src.backends.postgres import PostgresBackend

__all__ = ["StorageBackend", "InMemoryBackend", "PostgresBackend"]

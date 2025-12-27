"""
Backends package for the Multi-Agent Todo Application.

Contains storage backend protocol and implementations.
"""

from src.backends.base import StorageBackend
from src.backends.memory import InMemoryBackend

__all__ = ["StorageBackend", "InMemoryBackend"]

"""
TermPhoenix Database Module
Database management and operations for the web crawling system.
"""

from .manager import DatabaseManager, DatabaseError

__all__ = ["DatabaseManager", "DatabaseError"]

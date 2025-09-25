"""
Database manager for TermPhoenix
Handles database initialization, migrations, and core operations.
"""

import sqlite3
import json
import hashlib
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""

    pass


class DatabaseManager:
    """
    Manages TermPhoenix database operations including initialization,
    session management, and page storage.
    """

    def __init__(self, db_path: str, project_name: str):
        self.db_path = Path(db_path)
        self.project_name = project_name
        self.schema_path = Path(__file__).parent / "schemas"
        self.connection: Optional[sqlite3.Connection] = None

        logger.info(f"DatabaseManager initialized for project: {project_name}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.connection is None:
            raise DatabaseError(
                "Database not initialized. Call initialize_project() first."
            )
        return self.connection

    def initialize_project(
        self, recreate_if_exists: bool = False
    ) -> sqlite3.Connection:
        """
        Initialize a new project database or connect to existing one.

        Args:
            recreate_if_exists: If True, delete existing database and
            create new one

        Returns:
            SQLite connection object
        """
        try:
            # Handle existing database
            if self.db_path.exists():
                if recreate_if_exists:
                    logger.info(f"Recreating database: {self.db_path}")
                    self.db_path.unlink()
                else:
                    logger.info(
                        f"Connecting to existing database: {self.db_path}"
                    )
                    self.connection = sqlite3.connect(self.db_path)
                    self._configure_connection(self.connection)
                    return self.connection

            # Create new database
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Creating new database: {self.db_path}")

            self.connection = sqlite3.connect(self.db_path)
            self._configure_connection(self.connection)

            # Apply schema
            self._apply_schema()

            # Set project metadata
            self._set_project_metadata()

            logger.info(
                f"Project database initialized successfully: {self.db_path}"
            )
            return self.connection

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def _configure_connection(self, conn: sqlite3.Connection):
        """Configure SQLite connection for better performance."""
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -10000")  # 10MB cache
        conn.execute("PRAGMA temp_store = MEMORY")

        # Enable regex support if available
        try:
            conn.create_function(
                "regexp",
                2,
                lambda pattern, string: (
                    1
                    if string and pattern and re.search(pattern, string)
                    else 0
                ),
            )
        except Exception as e:
            logger.warning(f"Regex support not available in SQLite: {e}")

    def _apply_schema(self):
        """Apply the database schema from SQL file."""
        schema_file = self.schema_path / "initial.v1.sql"

        if not schema_file.exists():
            raise DatabaseError(f"Schema file not found: {schema_file}")

        try:
            schema_sql = schema_file.read_text(encoding="utf-8")
            self.connection.executescript(schema_sql)
            self.connection.commit()
            logger.info("Database schema applied successfully")
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to apply schema: {e}")

    def _set_project_metadata(self):
        """Set initial project metadata."""
        try:
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO project_metadata (key, value) VALUES (?, ?)",
                ("project_name", self.project_name),
            )
            cursor.execute(
                "INSERT INTO project_metadata (key, value) VALUES (?, ?)",
                ("created_at", datetime.now().isoformat()),
            )
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to set project metadata: {e}")

    def create_crawl_session(
        self, root_url: str, parameters: Dict[str, Any]
    ) -> int:
        """
        Create a new crawl session.

        Args:
            root_url: The starting URL for the crawl
            parameters: Dictionary of crawl parameters

        Returns:
            session_id of the newly created session
        """
        try:
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO crawl_sessions
                (root_url, parameters_json, started_at, status)
                VALUES (?, ?, datetime('now'), 'running')
            """,
                (root_url, json.dumps(parameters)),
            )

            session_id = cursor.lastrowid
            if session_id is None:
                raise DatabaseError("Failed to get session ID after insertion")

            self.connection.commit()
            logger.info(f"Created crawl session {session_id} for {root_url}")
            return session_id

        except Exception as e:
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            self.connection.rollback()
            raise DatabaseError(f"Failed to create crawl session: {e}")

    def get_or_create_website(self, domain: str, base_url: str = "") -> int:
        """
        Get existing website ID or create new one.

        Args:
            domain: The website domain
            base_url: The base URL of the website

        Returns:
            website_id
        """
        try:
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            cursor = self.connection.cursor()

            # Check if website exists
            cursor.execute(
                "SELECT website_id FROM websites WHERE domain = ?", (domain,)
            )
            result = cursor.fetchone()

            if result:
                website_id = result[0]
                # Update last_seen
                cursor.execute(
                    """
                    UPDATE websites SET last_seen = datetime('now')
                    WHERE website_id = ?
                    """,
                    (website_id,),
                )
                logger.debug(
                    f"Found existing website: {domain} (ID: {website_id})"
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO websites
                        (domain, base_url, first_seen, last_seen)
                    VALUES (?, ?, datetime('now'), datetime('now'))
                """,
                    (domain, base_url),
                )
                website_id = cursor.lastrowid
                logger.info(
                    f"Created new website: {domain} (ID: {website_id})"
                )

            self.connection.commit()
            return website_id

        except Exception as e:
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            self.connection.rollback()
            raise DatabaseError(f"Failed to get or create website: {e}")

    @staticmethod
    def url_to_hash(url: str) -> str:
        """
        Generate consistent URL hash for duplicate detection.

        Args:
            url: The URL to hash

        Returns:
            MD5 hash of the URL
        """
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def page_exists(self, url: str) -> bool:
        """
        Check if a page already exists in the database.

        Args:
            url: The URL to check

        Returns:
            True if page exists, False otherwise
        """
        try:
            url_hash = self.url_to_hash(url)
            if self.connection is None:
                raise RuntimeError("Database conneciton is not established")
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT page_id FROM pages WHERE url_hash = ?", (url_hash,)
            )
            return cursor.fetchone() is not None

        except Exception as e:
            raise DatabaseError(f"Failed to check if page exists: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Simple test
    db = DatabaseManager("test_project.db", "Test Project")
    conn = db.initialize_project()
    print("Database initialized successfully!")
    db.close()

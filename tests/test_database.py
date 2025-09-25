"""
Tests for TermPhoenix database functionality.
"""

import pytest
import tempfile
from pathlib import Path
from src.termphoenix.database.manager import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager."""

    def setup_method(self):
        """Set up temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_project.db"
        self.project_name = "Test Project"
        self.db_manager = DatabaseManager(self.db_path, self.project_name)

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "db_manager"):
            self.db_manager.close()
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_initialize_project(self):
        """Test database initialization."""
        conn = self.db_manager.initialize_project()
        assert conn is not None
        assert self.db_path.exists()

    def test_url_hashing(self):
        """Test URL hashing consistency."""
        url = "https://example.com/test"
        hash1 = DatabaseManager.url_to_hash(url)
        hash2 = DatabaseManager.url_to_hash(url)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length

    def test_create_crawl_session(self):
        """Test creating a crawl session."""
        conn = self.db_manager.initialize_project()
        session_id = self.db_manager.create_crawl_session(
            "https://example.com", {"depth": 2, "threads": 4}
        )

        assert session_id == 1  # First session should have ID 1

        # Verify session was created
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM crawl_sessions WHERE session_id = ?", (session_id,)
        )
        session = cursor.fetchone()
        assert session is not None
        assert session[1] == "https://example.com"  # root_url

    def test_get_or_create_website(self):
        """Test website creation and retrieval."""
        conn = self.db_manager.initialize_project()

        # Create new website
        website_id = self.db_manager.get_or_create_website(
            "example.com", "https://example.com"
        )
        assert website_id == 1

        # Get existing website
        same_website_id = self.db_manager.get_or_create_website("example.com")
        assert same_website_id == website_id

        # Verify website was created
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM websites WHERE website_id = ?", (website_id,)
        )
        website = cursor.fetchone()
        assert website is not None
        assert website[1] == "example.com"  # domain


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

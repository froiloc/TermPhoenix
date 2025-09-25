import pytest
import sqlite3
from unittest.mock import patch
from pathlib import Path

from src.termphoenix.database.manager import DatabaseManager, DatabaseError


@pytest.fixture
def db_manager(tmp_path):
    """Create a DatabaseManager instance for testing."""
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(db_path, "Test Project")
    manager.initialize_project()
    return manager


class TestDatabaseManagerComprehensive:
    """Comprehensive tests for DatabaseManager covering missing lines."""

    def test_initialize_project_connection_error(self, tmp_path):
        """Test database initialization when connection fails."""
        db_path = tmp_path / "test.db"

        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Connection failed")
            manager = DatabaseManager(db_path, "Test Project")

            with pytest.raises(
                DatabaseError, match="Database initialization failed"
            ):
                manager.initialize_project()

    def test_get_or_create_website_existing_domain(self, db_manager):
        """Test getting existing website by domain."""
        # First creation
        website_id_1 = db_manager.get_or_create_website(
            "example.com", "http://example.com"
        )

        # Getting the same domain should return same ID
        website_id_2 = db_manager.get_or_create_website("example.com")

        assert website_id_1 == website_id_2

    def test_get_or_create_website_different_domains(self, db_manager):
        """Test that different domains get different IDs."""
        website_id_1 = db_manager.get_or_create_website("example.com")
        website_id_2 = db_manager.get_or_create_website("example.org")

        assert website_id_1 != website_id_2

    def test_url_hashing_consistency(self):
        """Test that URL hashing is consistent."""
        manager = DatabaseManager(Path("test.db"), "Test")
        url = "http://example.com/page"

        hash1 = manager.url_to_hash(url)
        hash2 = manager.url_to_hash(url)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length

    def test_url_hashing_different_urls(self):
        """Test that different URLs get different hashes."""
        manager = DatabaseManager(Path("test.db"), "Test")

        hash1 = manager.url_to_hash("http://example.com/page1")
        hash2 = manager.url_to_hash("http://example.com/page2")

        assert hash1 != hash2

    def test_page_exists_basic(self, db_manager):
        """Test basic page existence checking."""
        # Test with non-existent page
        assert not db_manager.page_exists("http://example.com/new-page")

    def test_create_multiple_crawl_sessions(self, db_manager):
        """Test creating multiple crawl sessions."""
        session_id_1 = db_manager.create_crawl_session(
            "http://example.com", {"depth": 1}
        )
        session_id_2 = db_manager.create_crawl_session(
            "http://example.org", {"depth": 2}
        )

        assert session_id_1 != session_id_2
        assert isinstance(session_id_1, int)
        assert isinstance(session_id_2, int)

    def test_crawl_session_parameters_stored(self, db_manager):
        """Test that crawl session parameters are stored correctly."""
        test_params = {"depth": 3, "allow_leave_domain": True}
        session_id = db_manager.create_crawl_session(
            "http://example.com", test_params
        )

        # Verify the session was created (we can't easily retrieve parameters
        #  without a get method)
        assert session_id > 0

    def test_database_recreation(self, tmp_path):
        """Test database recreation with recreate_if_exists=True."""
        db_path = tmp_path / "test.db"

        # Create initial database
        manager = DatabaseManager(db_path, "Test Project")
        manager.initialize_project()

        # Recreate it
        manager.initialize_project(recreate_if_exists=True)

        # Should work without errors
        assert manager.connection is not None

    def test_connection_configuration(self, db_manager):
        """Test that database connection is properly configured."""
        # Test that foreign keys are enabled
        #  (this tests _configure_connection indirectly)
        cursor = db_manager.connection.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys should be enabled

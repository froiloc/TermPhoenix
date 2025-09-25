"""
Tests for HTML parser functionality.
"""

import pytest
from src.termphoenix.parser.html_parser import HTMLParser
from src.termphoenix.parser.models import EmphasisType


class TestHTMLParser:
    """Test cases for HTMLParser."""

    def setup_method(self):
        """Set up parser for each test."""
        self.parser = HTMLParser()

    def test_parse_simple_html(self):
        """Test parsing simple HTML with basic structure."""
        html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="A test page for parsing">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a <b>bold</b> and <i>italic</i> text.</p>
                <a href="/page2">Internal Link</a>
            </body>
        </html>
        """

        result = self.parser.parse_html(html, "https://example.com")

        assert result.title == "Test Page"
        assert result.meta_description == "A test page for parsing"
        assert len(result.tokens) > 0
        assert len(result.links) == 1
        assert result.links[0].url == "https://example.com/page2"

    def test_emphasis_detection(self):
        """Test detection of emphasis in HTML."""
        html = """
        <body>
            <h1>Header Text</h1>
            <p><b>Bold</b> and <i>Italic</i> and <strong>Strong</strong></p>
        </body>
        """

        result = self.parser.parse_html(html, "https://example.com")

        # Find tokens with specific emphasis
        header_tokens = [
            t for t in result.tokens if EmphasisType.HEADER in t.emphasis
        ]
        bold_tokens = [
            t for t in result.tokens if EmphasisType.BOLD in t.emphasis
        ]
        italic_tokens = [
            t for t in result.tokens if EmphasisType.ITALIC in t.emphasis
        ]

        assert len(header_tokens) > 0
        assert len(bold_tokens) > 0
        assert len(italic_tokens) > 0

    def test_link_extraction(self):
        """Test extraction of links from HTML."""
        html = """
        <body>
            <a href="/internal">Internal Link</a>
            <a href="https://external.com">External Link</a>
        </body>
        """

        result = self.parser.parse_html(html, "https://example.com")

        internal_links = [link for link in result.links if link.is_internal]
        external_links = [
            link for link in result.links if not link.is_internal
        ]

        assert len(internal_links) == 1
        assert len(external_links) == 1
        assert internal_links[0].url == "https://example.com/internal"
        assert external_links[0].url == "https://external.com"

    def test_image_alt_text_extraction(self):
        """Test extraction of image alt text."""
        html = """
        <body>
            <img src="image1.jpg" alt="First image">
            <img src="image2.jpg" alt="Second image">
            <img src="image3.jpg"> <!-- No alt text -->
        </body>
        """

        result = self.parser.parse_html(html, "https://example.com")

        assert len(result.image_alt_texts) == 2
        assert "First image" in result.image_alt_texts
        assert "Second image" in result.image_alt_texts

    def test_text_tokenization(self):
        """Test splitting text into proper tokens."""
        html = """
        <body>
            <p>Hello, world! This is a test.</p>
        </body>
        """

        result = self.parser.parse_html(html, "https://example.com")

        # Should split into words, removing punctuation but keeping words
        tokens_text = [t.text for t in result.tokens]
        expected_words = ["Hello", "world", "This", "is", "a", "test"]

        for word in expected_words:
            assert word in tokens_text

    def test_alphanumeric_patterns(self):
        """Test that alphanumeric patterns like 'NCC-1701' are preserved."""
        html = """
        <body>
            <p>Star Trek: NCC-1701 and BSG-75</p>
        </body>
        """

        result = self.parser.parse_html(html, "https://example.com")

        tokens_text = [t.text for t in result.tokens]

        assert "NCC-1701" in tokens_text
        assert "BSG-75" in tokens_text

    def test_meta_description_extraction(self):
        """Test that meta description is properly extracted."""
        html = """
        <html>
            <head>
                <meta name="description" content="This is a test description">
            </head>
            <body>
                <p>Some content</p>
            </body>
        </html>
        """

        result = self.parser.parse_html(html, "https://example.com")
        assert result.meta_description == "This is a test description"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

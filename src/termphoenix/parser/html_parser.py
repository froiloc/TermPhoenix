"""
HTML parser for TermPhoenix using BeautifulSoup4.
Extracts text, emphasis information, and links from web pages.
"""

import re
import logging
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag, Comment
from bs4.element import PageElement

from .models import ParsedPage, TextToken, LinkInfo, EmphasisType

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    Parses HTML content to extract text, emphasis information, and links.
    """

    # Tags that typically contain visible text
    TEXT_CONTAINER_TAGS = {
        "p",
        "div",
        "span",
        "article",
        "section",
        "main",
        "header",
        "footer",
        "li",
        "td",
        "th",
        "caption",
        "figcaption",
        "blockquote",
        "q",
        "cite",
    }

    # Tags that indicate emphasis
    EMPHASIS_TAGS = {
        "b": EmphasisType.BOLD,
        "strong": EmphasisType.STRONG,
        "i": EmphasisType.ITALIC,
        "em": EmphasisType.EMPHASIS,
        "u": EmphasisType.UNDERLINE,
        "code": EmphasisType.CODE,
        "h1": EmphasisType.HEADER,
        "h2": EmphasisType.HEADER,
        "h3": EmphasisType.HEADER,
        "h4": EmphasisType.HEADER,
        "h5": EmphasisType.HEADER,
        "h6": EmphasisType.HEADER,
        "a": EmphasisType.LINK_TEXT,
        "blockquote": EmphasisType.BLOCKQUOTE,
    }

    # Tags to completely remove (non-visible content)
    REMOVE_TAGS = {"script", "style", "noscript"}

    def __init__(self, parser: str = "lxml"):
        """
        Initialize the HTML parser.

        Args:
            parser: BeautifulSoup parser to use ('lxml', 'html.parser', etc.)
        """
        self.parser = parser
        logger.info(f"HTMLParser initialized with parser: {parser}")

    def parse_html(self, html_content: str, page_url: str) -> ParsedPage:
        """
        Parse HTML content and extract text, emphasis, and links.

        Args:
            html_content: Raw HTML content as string
            page_url: The URL of the page (for making links absolute)

        Returns:
            ParsedPage object containing all extracted information
        """
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, self.parser)

            # Remove non-visible content
            self._remove_non_content(soup)

            # Extract metadata
            title = self._extract_title(soup)
            meta_description = self._extract_meta_description(soup)

            # Extract image alt texts
            image_alt_texts = self._extract_image_alt_texts(soup)

            # Extract links
            links = self._extract_links(soup, page_url)

            # Extract text tokens with emphasis information
            tokens = self._extract_text_tokens(soup)

            # Combine all text for plain text version
            plain_text = self._extract_plain_text(soup)

            return ParsedPage(
                url=page_url,
                title=title,
                meta_description=meta_description,
                plain_text=plain_text,
                tokens=tokens,
                links=links,
                image_alt_texts=image_alt_texts,
                emphasis_stats={},  # Will be calculated in __post_init__
                word_count=0,  # Will be calculated in __post_init__
            )

        except Exception as e:
            logger.error(f"Failed to parse HTML from {page_url}: {e}")
            # Return empty parsed page on error
            return ParsedPage(
                url=page_url,
                title="",
                meta_description="",
                plain_text="",
                tokens=[],
                links=[],
                image_alt_texts=[],
                emphasis_stats={},
                word_count=0,
            )

    def _remove_non_content(self, soup: BeautifulSoup):
        """Remove scripts, styles, and other non-visible content."""
        for tag_name in self.REMOVE_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Remove comments
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        return title_tag.get_text().strip() if title_tag else ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description."""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        return None

    def _extract_image_alt_texts(self, soup: BeautifulSoup) -> List[str]:
        """Extract alt text from images."""
        alt_texts = []
        for img in soup.find_all("img"):
            alt = img.get("alt", "").strip()
            if alt:
                alt_texts.append(alt)
        return alt_texts

    def _extract_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[LinkInfo]:
        """Extract all links from the page."""
        links = []
        base_domain = urlparse(base_url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            link_text = a_tag.get_text().strip()

            # Make URL absolute
            absolute_url = urljoin(base_url, href)

            # Determine if internal link
            target_domain = urlparse(absolute_url).netloc
            is_internal = target_domain == base_domain

            # Extract emphasis from the link text
            emphasis = self._get_element_emphasis(a_tag)

            links.append(
                LinkInfo(
                    url=absolute_url,
                    text=link_text,
                    is_internal=is_internal,
                    emphasis=emphasis,
                )
            )

        return links

    def _extract_text_tokens(self, soup: BeautifulSoup) -> List[TextToken]:
        """
        Extract text tokens with emphasis information
        and proper positioning.
        """
        tokens = []
        absolute_position = 0
        text_group_id = 0

        # Find all text nodes in the document
        text_nodes = soup.find_all(string=True)

        for node in text_nodes:
            # Skip empty strings and strings with only whitespace
            text = node.string.strip()
            if not text:
                continue

            # Get emphasis and parent tags
            emphasis = self._get_node_emphasis(node)
            parent_tags = self._get_parent_tags(node)

            # Split into sentences first, then words
            sentences = self._split_into_sentences(text)

            for sentence_index, sentence in enumerate(sentences):
                words = self._split_text_into_words(sentence)

                for word_index, word in enumerate(words):
                    if not word:
                        continue

                    # Create both original and cleaned versions
                    cleaned_word = self._clean_word(word)

                    is_capitalized = (
                        cleaned_word[0].isupper() if cleaned_word else False
                    )
                    is_sentence_start = word_index == 0 and sentence_index == 0

                    token = TextToken(
                        text=word,  # Original word
                        cleaned_text=cleaned_word,  # Cleaned word
                        emphasis=emphasis.copy(),
                        position=absolute_position,
                        paragraph_position=word_index,
                        sentence_position=word_index,
                        is_capitalized=is_capitalized,
                        is_sentence_start=is_sentence_start,
                        parent_tags=parent_tags.copy(),
                        text_group_id=text_group_id,
                    )

                    tokens.append(token)
                    absolute_position += 1

            text_group_id += 1

        return tokens

    def _get_node_emphasis(self, node: PageElement) -> Set[EmphasisType]:
        """Get emphasis information for a text node by checking parent tags."""
        emphasis = set()
        current = node.parent

        while current and current.name:
            if current.name in self.EMPHASIS_TAGS:
                emphasis.add(self.EMPHASIS_TAGS[current.name])
            # Special case for title tag
            elif current.name == "title":
                emphasis.add(
                    EmphasisType.HEADER
                )  # Treat title as highest-level header
            current = current.parent

        return emphasis

    def _get_element_emphasis(self, element: Tag) -> Set[EmphasisType]:
        """Get emphasis information for an HTML element."""
        emphasis = set()
        current = element

        while current and current.name:
            if current.name in self.EMPHASIS_TAGS:
                emphasis.add(self.EMPHASIS_TAGS[current.name])
            current = current.parent

        return emphasis

    def _get_parent_tags(self, node: PageElement) -> List[str]:
        """Get the hierarchy of parent tags for a node."""
        parents = []
        current = node.parent

        while current and current.name:
            parents.append(current.name)
            current = current.parent

        return parents

    def _split_text_into_words(self, text: str) -> List[str]:
        """
        Split text into words, handling punctuation and special characters.
        Preserves alphanumeric patterns like 'NCC-1701'.
        """
        # Split on whitespace, then clean each word
        words = []
        for word in text.split():
            # Remove leading/trailing punctuation but
            #  keep internal hyphens, apostrophes
            cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", word)
            if cleaned:
                words.append(cleaned)

        return words

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using punctuation."""
        # Simple sentence splitting - can be enhanced later
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    # ENHANCE: Word cleaning
    def _clean_word(self, word: str) -> str:
        """Clean a word by removing surrounding punctuation."""
        return re.sub(r"^[^\w]+|[^\w]+$", "", word)

    def _is_sentence_start(self, node: PageElement, word: str) -> bool:
        """
        Determine if a word is likely the start of a sentence.
        This is a heuristic approach.
        """
        # Check if the previous sibling ends with sentence-ending punctuation
        prev_sibling = node.previous_sibling
        if prev_sibling and isinstance(prev_sibling, str):
            if re.search(r"[.!?]\s*$", prev_sibling):
                return True

        # Check if this is the first text in a block-level element
        parent = node.parent
        if parent and parent.name in [
            "p",
            "div",
            "li",
            "td",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]:
            # Check if this is the first text content in the parent
            for child in parent.children:
                if child is node:
                    return True
                if isinstance(child, str) and child.strip():
                    break

        return False

    def _extract_plain_text(self, soup: BeautifulSoup) -> str:
        """Extract clean plain text from the HTML."""
        # Get text with proper spacing
        text = soup.get_text(separator=" ", strip=True)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

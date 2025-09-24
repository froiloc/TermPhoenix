"""
Data models for HTML parsing results.
"""

from dataclasses import dataclass
from typing import List, Set, Optional, Dict
from enum import Enum

class EmphasisType(Enum):
    """Types of text emphasis."""
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    HEADER = "header"
    LINK_TEXT = "link_text"
    STRONG = "strong"
    EMPHASIS = "emphasis"
    CODE = "code"
    BLOCKQUOTE = "blockquote"

@dataclass
class TextToken:
    """A single token of text with emphasis information."""
    text: str
    cleaned_text: str  # store both original and cleaned
    emphasis: Set[EmphasisType]
    position: int  # Position in the document
    paragraph_position: int  # Position within paragraph
    sentence_position: int  # Position within sentence
    is_capitalized: bool
    is_sentence_start: bool
    parent_tags: List[str]  # HTML tags this token is contained within
    text_group_id: int  # Groups words from the same original text node

@dataclass
class LinkInfo:
    """Information about a link found on the page."""
    url: str
    text: str  # The link text
    is_internal: bool
    emphasis: Set[EmphasisType]

@dataclass
class ParsedPage:
    """Complete parsing results for a single HTML page."""
    url: str
    title: str
    meta_description: Optional[str]
    plain_text: str  # Cleaned text without HTML
    tokens: List[TextToken]
    links: List[LinkInfo]
    emphasis_stats: Dict[EmphasisType, int]  # Count of each emphasis type
    word_count: int
    image_alt_texts: List[str]  # Alt text from images
    
    def __post_init__(self):
        """Calculate derived statistics."""
        self.emphasis_stats = {
            emp_type: sum(1 for token in self.tokens if emp_type in token.emphasis)
            for emp_type in EmphasisType
        }
        self.word_count = len(self.tokens)

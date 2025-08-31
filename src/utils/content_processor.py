#!/usr/bin/env python3
"""
Advanced content processing for LLMs.txt generation.
Provides intelligent HTML cleaning, content extraction, and formatting.
"""

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Advanced content processing for documentation sites."""

    def __init__(self):
        self.html_cleaners = [
            self._remove_scripts_and_styles,
            self._remove_navigation_elements,
            self._remove_boilerplate,
            self._clean_formatting,
            self._extract_main_content,
        ]

    def process_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Process HTML content and extract clean, structured information.

        Args:
            html_content: Raw HTML content
            url: Source URL for context

        Returns:
            Dictionary with processed content
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Apply all cleaning steps
            for cleaner in self.html_cleaners:
                soup = cleaner(soup, url)

            # Extract structured content
            processed = {
                "url": url,
                "title": self._extract_title(soup, url),
                "description": self._extract_description(soup),
                "main_content": self._extract_main_content_text(soup),
                "headings": self._extract_headings(soup),
                "code_blocks": self._extract_code_blocks(soup),
                "links": self._extract_relevant_links(soup, url),
                "metadata": self._extract_metadata(soup),
            }

            return processed

        except Exception as e:
            logger.error(f"Content processing failed for {url}: {e}")
            return {
                "url": url,
                "title": "Error Processing Content",
                "description": "Failed to process content",
                "main_content": "",
                "headings": [],
                "code_blocks": [],
                "links": [],
                "metadata": {},
            }

    def _remove_scripts_and_styles(
        self, soup: BeautifulSoup, url: str
    ) -> BeautifulSoup:
        """Remove script and style elements."""
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        return soup

    def _remove_navigation_elements(
        self, soup: BeautifulSoup, url: str
    ) -> BeautifulSoup:
        """Remove navigation and header/footer elements."""
        for element in soup(["nav", "header", "footer", "aside", "menu"]):
            element.decompose()
        return soup

    def _remove_boilerplate(self, soup: BeautifulSoup, url: str) -> BeautifulSoup:
        """Remove common boilerplate elements."""
        # Remove common boilerplate classes and IDs
        boilerplate_selectors = [
            ".sidebar",
            ".navigation",
            ".menu",
            ".breadcrumb",
            ".footer",
            ".header",
            ".advertisement",
            ".ad",
            ".social",
            ".share",
            ".comment",
            ".related",
        ]

        for selector in boilerplate_selectors:
            for element in soup.select(selector):
                element.decompose()

        return soup

    def _clean_formatting(self, soup: BeautifulSoup, url: str) -> BeautifulSoup:
        """Clean up formatting and preserve structure."""
        # Convert common elements to markdown-like format
        for element in soup.find_all(["strong", "b"]):
            element.replace_with(f"**{element.get_text()}**")

        for element in soup.find_all(["em", "i"]):
            element.replace_with(f"*{element.get_text()}*")

        # Clean up whitespace
        for element in soup.find_all(text=True):
            if element.parent.name not in ["pre", "code"]:
                element.replace_with(element.strip())

        return soup

    def _extract_main_content(self, soup: BeautifulSoup, url: str) -> BeautifulSoup:
        """Extract main content area."""
        # Try to find main content container
        main_selectors = [
            "main",
            "article",
            ".content",
            ".main-content",
            ".post-content",
            ".entry-content",
            ".documentation",
        ]

        for selector in main_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                # Replace the entire soup with just the main content
                new_soup = BeautifulSoup(str(main_element), "html.parser")
                return new_soup

        return soup

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title with intelligent fallbacks."""
        # Try title tag first
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # Clean common suffixes
            for suffix in [" | ", " - ", " — ", " :: "]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title and len(title) > 3:
                return title

        # Try h1 tags
        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            title = h1.get_text().strip()
            if title and len(title) > 3:
                return title

        # Try meta title
        meta_title = soup.find("meta", attrs={"name": "title"})
        if meta_title and meta_title.get("content"):
            return meta_title["content"].strip()

        # Fallback to URL path
        from urllib.parse import urlparse

        path = urlparse(url).path
        if path and path != "/":
            title = path.strip("/").replace("-", " ").replace("_", " ").title()
            if title:
                return title

        return "Untitled"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        # Try meta description first
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        # Try og:description
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        # Extract from first paragraph
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50 and len(text) < 300:
                return text

        return ""

    def _extract_main_content_text(self, soup: BeautifulSoup) -> str:
        """Extract main content as clean text."""
        # Remove remaining unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        # Get text and clean it up
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings with their levels."""
        headings = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = int(tag.name[1])
            text = tag.get_text().strip()
            if text:
                headings.append({"level": level, "text": text, "id": tag.get("id", "")})
        return headings

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks with language detection."""
        code_blocks = []

        # Extract pre and code blocks
        for code_element in soup.find_all(["pre", "code"]):
            if code_element.name == "pre":
                # Pre blocks often contain code
                code_text = code_element.get_text()
                language = self._detect_language(code_element)
                code_blocks.append(
                    {"type": "block", "language": language, "content": code_text}
                )
            elif code_element.name == "code" and not code_element.parent.name == "pre":
                # Inline code
                code_text = code_element.get_text()
                if len(code_text) > 10:  # Only include substantial inline code
                    language = self._detect_language(code_element)
                    code_blocks.append(
                        {"type": "inline", "language": language, "content": code_text}
                    )

        return code_blocks

    def _detect_language(self, element: BeautifulSoup) -> str:
        """Detect programming language from code element."""
        # Check for language classes
        classes = element.get("class", [])
        for cls in classes:
            if cls.startswith("language-"):
                return cls.replace("language-", "")
            elif cls in ["python", "javascript", "js", "html", "css", "json", "xml"]:
                return cls

        # Check for data attributes
        data_lang = element.get("data-language")
        if data_lang:
            return data_lang

        return "text"

    def _extract_relevant_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        """Extract relevant links with context."""
        links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text().strip()

            if text and href:
                # Determine if it's an internal or external link
                from urllib.parse import urljoin, urlparse

                full_url = urljoin(base_url, href)

                link_info = {
                    "url": full_url,
                    "text": text,
                    "type": (
                        "external"
                        if urlparse(full_url).netloc != urlparse(base_url).netloc
                        else "internal"
                    ),
                }

                links.append(link_info)

        return links

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page."""
        metadata = {}

        # Extract meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")

            if name and content:
                metadata[name] = content

        # Extract structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json

                data = json.loads(script.string)
                metadata["structured_data"] = data
            except (ValueError, TypeError):
                pass

        return metadata

    def clean_html_to_markdown(self, html_content: str, url: str) -> str:
        """
        Convert HTML content to clean markdown-like text.

        Args:
            html_content: Raw HTML content
            url: Source URL for context

        Returns:
            Clean markdown-like text
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted elements
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside"]
            ):
                element.decompose()

            # Convert headings
            for i in range(1, 7):
                for heading in soup.find_all(f"h{i}"):
                    heading.replace_with(f"\n{'#' * i} {heading.get_text()}\n")

            # Convert links
            for link in soup.find_all("a", href=True):
                text = link.get_text().strip()
                href = link["href"]
                if text and href:
                    link.replace_with(f"[{text}]({href})")

            # Convert lists
            for ul in soup.find_all("ul"):
                for li in ul.find_all("li"):
                    li.replace_with(f"\n- {li.get_text()}\n")

            for ol in soup.find_all("ol"):
                for i, li in enumerate(ol.find_all("li"), 1):
                    li.replace_with(f"\n{i}. {li.get_text()}\n")

            # Convert code blocks
            for pre in soup.find_all("pre"):
                code = pre.get_text()
                pre.replace_with(f"\n```\n{code}\n```\n")

            # Convert inline code
            for code in soup.find_all("code"):
                if code.parent.name != "pre":
                    code.replace_with(f"`{code.get_text()}`")

            # Get clean text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error(f"HTML to markdown conversion failed for {url}: {e}")
            return html_content

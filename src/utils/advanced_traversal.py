#!/usr/bin/env python3
"""
Advanced website traversal with specialized modes for documentation sites.
Provides intelligent crawling with different strategies for different content types.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedWebsiteTraverser:
    """Advanced website traverser with specialized modes."""

    def __init__(self, rate_limit: float = 0.5, max_concurrent: int = 5):
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.visited_urls = set()
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "LLMs.txt Generator/1.0"},
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def traverse_website(
        self, base_url: str, mode: str = "docs", max_pages: int = 30, max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Traverse website with specialized modes.

        Args:
            base_url: Starting URL
            mode: Traversal mode - "docs", "research", "map"
            max_pages: Maximum pages to visit
            max_depth: Maximum traversal depth
        """
        logger.info(f"Starting {mode} traversal of {base_url}")

        if mode == "docs":
            return await self._traverse_documentation(base_url, max_pages, max_depth)
        elif mode == "research":
            return await self._traverse_research(base_url, max_pages, max_depth)
        elif mode == "map":
            return await self._traverse_structure(base_url, max_pages, max_depth)
        else:
            logger.warning(f"Unknown mode: {mode}, using docs mode")
            return await self._traverse_documentation(base_url, max_pages, max_depth)

    async def _traverse_documentation(
        self, docs_url: str, max_pages: int, max_depth: int
    ) -> List[Dict[str, Any]]:
        """Specialized traversal for documentation sites."""
        pages = []
        queue = [(docs_url, 0)]  # (url, depth)

        while queue and len(pages) < max_pages:
            url, depth = queue.pop(0)

            if depth > max_depth or url in self.visited_urls:
                continue

            self.visited_urls.add(url)

            try:
                page_data = await self._fetch_page(url)
                if page_data:
                    page_data["depth"] = depth
                    page_data["traversal_mode"] = "documentation"
                    pages.append(page_data)

                    # Find documentation-specific links
                    if depth < max_depth:
                        doc_links = self._extract_documentation_links(
                            page_data["html"], url
                        )
                        for link in doc_links[:10]:  # Limit links per page
                            if link not in self.visited_urls:
                                queue.append((link, depth + 1))

                await asyncio.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")

        return pages

    async def _traverse_research(
        self, topic_url: str, max_pages: int, max_depth: int
    ) -> List[Dict[str, Any]]:
        """Specialized traversal for research topics."""
        pages = []
        queue = [(topic_url, 0)]

        while queue and len(pages) < max_pages:
            url, depth = queue.pop(0)

            if depth > max_depth or url in self.visited_urls:
                continue

            self.visited_urls.add(url)

            try:
                page_data = await self._fetch_page(url)
                if page_data:
                    page_data["depth"] = depth
                    page_data["traversal_mode"] = "research"
                    pages.append(page_data)

                    # Find research-relevant links
                    if depth < max_depth:
                        research_links = self._extract_research_links(
                            page_data["html"], url
                        )
                        for link in research_links[:8]:
                            if link not in self.visited_urls:
                                queue.append((link, depth + 1))

                await asyncio.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")

        return pages

    async def _traverse_structure(
        self, website_url: str, max_pages: int, max_depth: int
    ) -> List[Dict[str, Any]]:
        """Specialized traversal for website structure mapping."""
        pages = []
        queue = [(website_url, 0)]

        while queue and len(pages) < max_pages:
            url, depth = queue.pop(0)

            if depth > max_depth or url in self.visited_urls:
                continue

            self.visited_urls.add(url)

            try:
                page_data = await self._fetch_page(url)
                if page_data:
                    page_data["depth"] = depth
                    page_data["traversal_mode"] = "structure"

                    # Add structure analysis
                    page_data["structure_info"] = self._analyze_page_structure(
                        page_data["html"], url
                    )
                    pages.append(page_data)

                    # Find structural links
                    if depth < max_depth:
                        structure_links = self._extract_structure_links(
                            page_data["html"], url
                        )
                        for link in structure_links[:12]:
                            if link not in self.visited_urls:
                                queue.append((link, depth + 1))

                await asyncio.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")

        return pages

    async def _fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a single page with error handling."""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    return {
                        "url": url,
                        "title": self._extract_title(soup, url),
                        "html": html,
                        "content": self._extract_main_content(soup),
                        "links": self._extract_all_links(soup, url),
                    }
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title with fallbacks."""
        # Try title tag first
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # Clean common suffixes
            for suffix in [" | ", " - ", " — "]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                return title

        # Try h1 tags
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()

        # Fallback to URL path
        path = urlparse(url).path
        if path and path != "/":
            return path.strip("/").replace("-", " ").replace("_", " ").title()

        return "Unknown Title"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content area."""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        # Try to find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
        )
        if main_content:
            return main_content.get_text()

        # Fallback to body
        body = soup.find("body")
        if body:
            return body.get_text()

        return soup.get_text()

    def _extract_all_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page."""
        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            # Only include HTTP/HTTPS links
            if full_url.startswith(("http://", "https://")):
                links.append(full_url)

        return links

    def _extract_documentation_links(self, html: str, base_url: str) -> List[str]:
        """Extract documentation-specific links."""
        soup = BeautifulSoup(html, "html.parser")
        doc_links = []

        # Look for documentation-specific patterns
        doc_patterns = [
            "/docs/",
            "/documentation/",
            "/guide/",
            "/tutorial/",
            "/api/",
            "/reference/",
        ]

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            if any(pattern in full_url.lower() for pattern in doc_patterns):
                doc_links.append(full_url)

        return doc_links

    def _extract_research_links(self, html: str, base_url: str) -> List[str]:
        """Extract research-relevant links."""
        soup = BeautifulSoup(html, "html.parser")
        research_links = []

        # Look for research-relevant patterns
        research_patterns = ["/wiki/", "/article/", "/study/", "/research/", "/paper/"]

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            if any(pattern in full_url.lower() for pattern in research_patterns):
                research_links.append(full_url)

        return research_links

    def _extract_structure_links(self, html: str, base_url: str) -> List[str]:
        """Extract structural navigation links."""
        soup = BeautifulSoup(html, "html.parser")
        structure_links = []

        # Look for navigation and structural links
        nav_patterns = [
            "/about/",
            "/contact/",
            "/services/",
            "/products/",
            "/blog/",
            "/news/",
        ]

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            if any(pattern in full_url.lower() for pattern in nav_patterns):
                structure_links.append(full_url)

        return structure_links

    def _analyze_page_structure(self, html: str, url: str) -> Dict[str, Any]:
        """Analyze page structure for mapping mode."""
        soup = BeautifulSoup(html, "html.parser")

        return {
            "depth": url.count("/") - 2,  # Rough depth calculation
            "is_homepage": url.rstrip("/") == urlparse(url).netloc,
            "has_navigation": bool(soup.find("nav")),
            "has_sidebar": bool(soup.find("aside")),
            "has_footer": bool(soup.find("footer")),
            "heading_count": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
            "link_count": len(soup.find_all("a", href=True)),
        }

#!/usr/bin/env python3
"""
Sitemap Extractor for LLMs.txt Generator

Extracts URLs from various sitemap formats:
- XML sitemaps (sitemap.xml, sitemap_index.xml)
- HTML sitemaps
- Robots.txt sitemap references
- Common sitemap locations
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SitemapExtractor:
    """Extract URLs from various sitemap formats."""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": "LLMs.txt Generator/1.0"})
        self.discovered_urls: Set[str] = set()

    def extract_urls_from_sitemap(self, base_url: str) -> List[str]:
        """
        Extract URLs from sitemap using multiple strategies.

        Args:
            base_url: Base URL of the website

        Returns:
            List of discovered URLs
        """
        logger.info(f"Extracting URLs from sitemap for: {base_url}")

        # Try different sitemap discovery methods
        sitemap_urls = []

        # 1. Check robots.txt for sitemap references
        robots_sitemaps = self._extract_from_robots_txt(base_url)
        sitemap_urls.extend(robots_sitemaps)

        # 2. Try common sitemap locations
        common_sitemaps = self._try_common_sitemap_locations(base_url)
        sitemap_urls.extend(common_sitemaps)

        # 3. Extract URLs from all discovered sitemaps
        all_urls = []
        for sitemap_url in sitemap_urls:
            urls = self._extract_urls_from_sitemap_url(sitemap_url)
            all_urls.extend(urls)

        # 4. Try to find HTML sitemap
        html_sitemap_urls = self._find_html_sitemap(base_url)
        all_urls.extend(html_sitemap_urls)

        # Remove duplicates and filter
        unique_urls = list(set(all_urls))
        filtered_urls = [
            url for url in unique_urls if self._is_valid_url(url, base_url)
        ]

        logger.info(f"Discovered {len(filtered_urls)} URLs from sitemaps")
        return filtered_urls

    def _extract_from_robots_txt(self, base_url: str) -> List[str]:
        """Extract sitemap URLs from robots.txt file."""
        robots_url = urljoin(base_url, "/robots.txt")
        sitemap_urls = []

        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                content = response.text

                # Look for sitemap directives
                for line in content.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        if sitemap_url:
                            sitemap_urls.append(sitemap_url)

                logger.info(
                    f"Found {len(sitemap_urls)} sitemap references in robots.txt"
                )

        except Exception as e:
            logger.warning(f"Could not fetch robots.txt from {robots_url}: {e}")

        return sitemap_urls

    def _try_common_sitemap_locations(self, base_url: str) -> List[str]:
        """Try common sitemap locations."""
        common_paths = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap/sitemap.xml",
            "/sitemaps/sitemap.xml",
            "/sitemap1.xml",
            "/sitemap_news.xml",
            "/sitemap_products.xml",
        ]

        sitemap_urls = []

        for path in common_paths:
            sitemap_url = urljoin(base_url, path)
            try:
                response = self.session.head(sitemap_url, timeout=5)
                if response.status_code == 200:
                    sitemap_urls.append(sitemap_url)
                    logger.info(f"Found sitemap at: {sitemap_url}")
            except Exception:
                continue

        return sitemap_urls

    def _extract_urls_from_sitemap_url(self, sitemap_url: str) -> List[str]:
        """Extract URLs from a specific sitemap URL."""
        try:
            response = self.session.get(sitemap_url, timeout=15)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if "xml" in content_type:
                return self._parse_xml_sitemap(response.text, sitemap_url)
            elif "html" in content_type:
                return self._parse_html_sitemap(response.text, sitemap_url)
            else:
                # Try to detect format
                if response.text.strip().startswith("<?xml"):
                    return self._parse_xml_sitemap(response.text, sitemap_url)
                else:
                    return self._parse_html_sitemap(response.text, sitemap_url)

        except Exception as e:
            logger.error(f"Error extracting URLs from {sitemap_url}: {e}")
            return []

    def _parse_xml_sitemap(self, xml_content: str, sitemap_url: str) -> List[str]:
        """Parse XML sitemap and extract URLs."""
        urls = []

        try:
            # Handle XML namespaces
            namespaces = {
                "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                "xhtml": "http://www.w3.org/1999/xhtml",
            }

            root = ET.fromstring(xml_content)

            # Check if this is a sitemap index
            if "sitemapindex" in root.tag:
                logger.info(f"Found sitemap index: {sitemap_url}")
                # Extract sitemap URLs from index
                for sitemap in root.findall(".//sm:sitemap/sm:loc", namespaces):
                    sub_sitemap_url = sitemap.text
                    if sub_sitemap_url:
                        sub_urls = self._extract_urls_from_sitemap_url(sub_sitemap_url)
                        urls.extend(sub_urls)
            else:
                # Regular sitemap
                for url_elem in root.findall(".//sm:url/sm:loc", namespaces):
                    url = url_elem.text
                    if url:
                        urls.append(url)

            logger.info(f"Extracted {len(urls)} URLs from XML sitemap: {sitemap_url}")

        except ET.ParseError as e:
            logger.error(f"XML parsing error for {sitemap_url}: {e}")
        except Exception as e:
            logger.error(f"Error parsing XML sitemap {sitemap_url}: {e}")

        return urls

    def _parse_html_sitemap(self, html_content: str, sitemap_url: str) -> List[str]:
        """Parse HTML sitemap and extract URLs."""
        urls = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Find all links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(sitemap_url, href)

                # Only include HTTP/HTTPS URLs
                if full_url.startswith(("http://", "https://")):
                    urls.append(full_url)

            logger.info(f"Extracted {len(urls)} URLs from HTML sitemap: {sitemap_url}")

        except Exception as e:
            logger.error(f"Error parsing HTML sitemap {sitemap_url}: {e}")

        return urls

    def _find_html_sitemap(self, base_url: str) -> List[str]:
        """Find and extract URLs from HTML sitemap pages."""
        html_sitemap_paths = [
            "/sitemap",
            "/sitemap.html",
            "/sitemap.htm",
            "/site-map",
            "/site-map.html",
            "/links",
            "/all-pages",
            "/directory",
        ]

        all_urls = []

        for path in html_sitemap_paths:
            sitemap_url = urljoin(base_url, path)
            try:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    urls = self._parse_html_sitemap(response.text, sitemap_url)
                    all_urls.extend(urls)
                    logger.info(f"Found HTML sitemap at: {sitemap_url}")
            except Exception:
                continue

        return all_urls

    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid and should be included."""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            # Must be HTTP/HTTPS
            if parsed_url.scheme not in ["http", "https"]:
                return False

            # Should be from the same domain (optional, but usually desired)
            if parsed_url.netloc != parsed_base.netloc:
                return False

            # Exclude common non-content URLs
            exclude_patterns = [
                "#",
                "mailto:",
                "javascript:",
                "tel:",
                "ftp:",
                ".pdf",
                ".zip",
                ".exe",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".css",
                ".js",
                ".xml",
                ".json",
            ]

            for pattern in exclude_patterns:
                if pattern in url.lower():
                    return False

            return True

        except Exception:
            return False

    def extract_sitemap_info(self, base_url: str) -> Dict[str, Any]:
        """
        Extract comprehensive sitemap information.

        Args:
            base_url: Base URL of the website

        Returns:
            Dictionary with sitemap information
        """
        info = {
            "base_url": base_url,
            "sitemap_urls": [],
            "robots_txt_sitemaps": [],
            "html_sitemaps": [],
            "total_urls": 0,
            "urls_by_type": {},
        }

        # Extract from robots.txt
        robots_sitemaps = self._extract_from_robots_txt(base_url)
        info["robots_txt_sitemaps"] = robots_sitemaps
        info["sitemap_urls"].extend(robots_sitemaps)

        # Try common locations
        common_sitemaps = self._try_common_sitemap_locations(base_url)
        info["sitemap_urls"].extend(common_sitemaps)

        # Find HTML sitemaps
        html_sitemap_paths = [
            "/sitemap",
            "/sitemap.html",
            "/site-map",
            "/links",
            "/all-pages",
        ]
        for path in html_sitemap_paths:
            sitemap_url = urljoin(base_url, path)
            try:
                response = self.session.head(sitemap_url, timeout=5)
                if response.status_code == 200:
                    info["html_sitemaps"].append(sitemap_url)
            except Exception:
                continue

        # Extract URLs from all sitemaps
        all_urls = []
        for sitemap_url in info["sitemap_urls"]:
            urls = self._extract_urls_from_sitemap_url(sitemap_url)
            all_urls.extend(urls)

        # Add HTML sitemap URLs
        for sitemap_url in info["html_sitemaps"]:
            urls = self._extract_urls_from_sitemap_url(sitemap_url)
            all_urls.extend(urls)

        # Remove duplicates and filter
        unique_urls = list(set(all_urls))
        filtered_urls = [
            url for url in unique_urls if self._is_valid_url(url, base_url)
        ]

        info["total_urls"] = len(filtered_urls)

        # Categorize URLs
        info["urls_by_type"] = self._categorize_urls(filtered_urls)

        return info

    def _categorize_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """Categorize URLs by type."""
        categories = {
            "documentation": [],
            "api": [],
            "guides": [],
            "tutorials": [],
            "blog": [],
            "other": [],
        }

        for url in urls:
            url_lower = url.lower()

            if any(
                pattern in url_lower
                for pattern in ["/docs/", "/documentation/", "/guide/"]
            ):
                categories["documentation"].append(url)
            elif any(pattern in url_lower for pattern in ["/api/", "/reference/"]):
                categories["api"].append(url)
            elif any(pattern in url_lower for pattern in ["/guides/", "/how-to/"]):
                categories["guides"].append(url)
            elif any(pattern in url_lower for pattern in ["/tutorial/", "/tutorials/"]):
                categories["tutorials"].append(url)
            elif any(
                pattern in url_lower for pattern in ["/blog/", "/news/", "/articles/"]
            ):
                categories["blog"].append(url)
            else:
                categories["other"].append(url)

        return categories

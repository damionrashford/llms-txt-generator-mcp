#!/usr/bin/env python3
"""
Core LLMs.txt Generator Framework

The main generator class that orchestrates the entire LLMs.txt generation process.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Import utility modules
try:
    from ..utils.content_processor import ContentProcessor
except ImportError:
    from utils.content_processor import ContentProcessor

# Configure logging
logger = logging.getLogger(__name__)


class LLMsTxtGenerator:
    """
    Generic LLMs.txt generator that can work with any documentation website.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the generator with a configuration.

        Args:
            config: Configuration dictionary containing:
                - name: Project name
                - description: Project description
                - base_urls: List of URLs to start crawling from
                - content_selectors: CSS selectors for content extraction
                - title_selectors: CSS selectors for title extraction
                - category_rules: Rules for categorizing pages
                - rate_limit: Delay between requests (seconds)
                - max_pages: Maximum number of pages to process
                - user_agent: User agent string
                - traversal_mode: Traversal mode - "docs", "research", "map"
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": config.get("user_agent", "LLMs.txt Generator/1.0")}
        )
        self.visited_urls = set()
        self.pages_data = []

        # Initialize advanced components
        self.content_processor = ContentProcessor()

    def discover_pages(self) -> List[Dict[str, str]]:
        """Discover pages using simple link discovery."""
        discovered_pages = []
        base_urls = self.config.get("urls", [])  # Use 'urls' instead of 'base_urls'
        max_pages = self.config.get("max_pages", 100)

        logger.info("Using simple page discovery")
        logger.info(f"Base URLs: {base_urls}")

        for base_url in base_urls:
            logger.info(f"Processing base URL: {base_url}")

            # Use simple link discovery to find pages
            discovered_urls = self._simple_link_discovery(base_url, max_pages)
            
            # Add the base URL itself if not already found
            if base_url not in discovered_urls:
                discovered_urls.insert(0, base_url)
            
            for url in discovered_urls:
                if len(discovered_pages) >= max_pages:
                    break
                if url not in [page["url"] for page in discovered_pages]:
                    discovered_pages.append({"url": url, "source": "link_discovery"})

        logger.info(f"Discovered {len(discovered_pages)} pages using simple discovery")
        
        # Ensure we return a list, not None
        if discovered_pages is None:
            discovered_pages = []
            
        return discovered_pages

    def _simple_link_discovery(self, base_url: str, max_pages: int) -> List[str]:
        """Simple link discovery as fallback."""
        discovered_urls = []

        try:
            html_content = self.get_page_content(base_url)
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                links = soup.find_all("a", href=True)

                for link in links:
                    if len(discovered_urls) >= max_pages:
                        break

                    href = link["href"]
                    full_url = urljoin(base_url, href)

                    if self._is_valid_url(full_url, base_url):
                        discovered_urls.append(full_url)

        except Exception as e:
            logger.warning(f"Simple link discovery failed: {e}")

        # If no links found, at least return the base URL
        if not discovered_urls:
            discovered_urls = [base_url]

        return discovered_urls

    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid and from the same domain."""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            # Must be HTTP/HTTPS
            if parsed_url.scheme not in ["http", "https"]:
                return False

            # Must be from same domain
            if parsed_url.netloc != parsed_base.netloc:
                return False

            # Skip common non-content URLs
            skip_patterns = [
                "#", "javascript:", "mailto:", "tel:", "ftp://", 
                ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
                ".css", ".js", ".xml", ".zip", ".tar", ".gz"
            ]
            
            for pattern in skip_patterns:
                if pattern in url.lower():
                    return False

            # Check include/exclude patterns
            include_patterns = self.config.get("include_patterns", [])
            exclude_patterns = self.config.get("exclude_patterns", [])

            for pattern in exclude_patterns:
                if pattern in url:
                    return False

            if include_patterns:
                return any(pattern in url for pattern in include_patterns)

            return True

        except Exception:
            return False

    def get_page_content(self, url: str) -> Optional[str]:
        """Get HTML content from a URL."""
        try:
            # Use the existing session for now
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            logger.info(f"Successfully fetched {url}, content length: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""

    def process_pages(self, discovered_pages: List[Dict[str, str]]):
        """Process discovered pages and extract content."""
        logger.info(f"\nProcessing {len(discovered_pages)} pages with simple method...")

        # Ensure discovered_pages is not None
        if discovered_pages is None:
            discovered_pages = []

        for i, page_info in enumerate(discovered_pages, 1):
            url = page_info["url"]
            logger.info(f"Processing {i}/{len(discovered_pages)}: {url}")

            html_content = self.get_page_content(url)
            logger.info(f"HTML content length: {len(html_content) if html_content else 0}")
            
            if html_content:
                # Process content using the content processor
                processed = self.content_processor.process_content(html_content, url)
                logger.info(f"Processed content keys: {list(processed.keys()) if processed else 'None'}")

                # Categorize the page
                category = self._categorize_page(processed)

                # Add to pages data
                self.pages_data.append(
                    {
                        "url": url,
                        "title": processed["title"],
                        "description": processed["description"],
                        "content": processed["main_content"],
                        "category": category,
                        "source": page_info["source"],
                    }
                )
                logger.info(f"Added page: {processed['title']} to category: {category}")

            # Rate limiting - removed for debugging
            # time.sleep(self.config.get("rate_limit", 0.5))
        
        logger.info(f"Total pages processed: {len(self.pages_data)}")

    def _categorize_page(self, processed: Dict[str, Any]) -> str:
        """Categorize a page based on URL and title patterns."""
        url = processed["url"]
        title = processed["title"].lower()

        category_rules = self.config.get("category_rules", {})

        for category, rules in category_rules.items():
            # Check URL patterns
            url_patterns = rules.get("url_patterns", [])
            for pattern in url_patterns:
                if pattern in url:
                    return category

            # Check title patterns
            title_patterns = rules.get("title_patterns", [])
            for pattern in title_patterns:
                if pattern in title:
                    return category

        return "Other"

    def generate_llms_txt(self, output_file: str = "llms.txt"):
        """Generate the llms.txt file following the official llmstxt.org spec."""
        logger.info(f"\nGenerating {output_file}...")
        logger.info(f"Pages data length: {len(self.pages_data)}")

        # Group pages by category
        categories = {}
        for page in self.pages_data:
            category = page["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(page)

        logger.info(f"Categories: {list(categories.keys())}")

        with open(output_file, "w", encoding="utf-8") as f:
            # Write H1 title (required)
            f.write(f"# {self.config['name']}\n\n")

            # Write blockquote summary (required)
            f.write(f"> {self.config['description']}\n\n")

            # Write additional information (optional)
            if self.config.get("additional_info"):
                f.write(f"{self.config['additional_info']}\n\n")

            # Write sections with H2 headers
            for category in sorted(categories.keys()):
                if category == "Other":
                    # Use "Optional" for the "Other" category as per spec
                    f.write("## Optional\n\n")
                else:
                    f.write(f"## {category}\n\n")

                for page in sorted(categories[category], key=lambda x: x["title"]):
                    # Format: - [title](url): description
                    description = page["description"] if page["description"] else ""
                    f.write(f"- [{page['title']}]({page['url']})")
                    if description:
                        f.write(f": {description}")
                    f.write("\n")

                f.write("\n")

        logger.info(
            f"Generated {output_file} with {len(self.pages_data)} pages "
            f"following llmstxt.org specification"
        )

    def generate_llms_full_txt(self, output_file: str = "llms-full.txt"):
        """Generate the llms-full.txt file with full content."""
        logger.info(f"\nGenerating {output_file}...")

        # Group pages by category
        categories = {}
        for page in self.pages_data:
            category = page["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(page)

        with open(output_file, "w", encoding="utf-8") as f:
            # Write H1 title (required)
            f.write(f"# {self.config['name']}\n\n")

            # Write blockquote summary (required)
            f.write(f"> {self.config['description']}\n\n")

            # Write additional information (optional)
            if self.config.get("additional_info"):
                f.write(f"{self.config['additional_info']}\n\n")

            # Write sections with H2 headers and full content
            for category in sorted(categories.keys()):
                if category == "Other":
                    # Use "Optional" for the "Other" category as per spec
                    f.write("## Optional\n\n")
                else:
                    f.write(f"## {category}\n\n")

                for page in sorted(categories[category], key=lambda x: x["title"]):
                    # Write the link first (following llmstxt.org format)
                    description = page["description"] if page["description"] else ""
                    f.write(f"- [{page['title']}]({page['url']})")
                    if description:
                        f.write(f": {description}")
                    f.write("\n\n")

                    # Write the full content
                    f.write(page["content"])
                    f.write("\n\n---\n\n")

        logger.info(
            f"Generated {output_file} with full content from "
            f"{len(self.pages_data)} pages"
        )

    def generate_llms_ctx_files(self):
        """Generate llms-ctx.txt and llms-ctx-full.txt files following the spec."""
        logger.info("\nGenerating llms-ctx.txt and llms-ctx-full.txt...")

        # Generate llms-ctx.txt (without Optional section)
        self._generate_ctx_file("llms-ctx.txt", include_optional=False)

        # Generate llms-ctx-full.txt (with Optional section)
        self._generate_ctx_file("llms-ctx-full.txt", include_optional=True)

        logger.info("Generated llms-ctx.txt and llms-ctx-full.txt files")

    def _generate_ctx_file(self, output_file: str, include_optional: bool = False):
        """Generate a context file with expanded content."""
        # Group pages by category
        categories = {}
        for page in self.pages_data:
            category = page["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(page)

        with open(output_file, "w", encoding="utf-8") as f:
            # Write XML-style header
            f.write(
                f'<project title="{self.config["name"]}" summary="{self.config["description"]}">\n'
            )

            # Write sections
            for category in sorted(categories.keys()):
                if category == "Other" and not include_optional:
                    continue

                f.write(f'<section name="{category}">\n')

                for page in sorted(categories[category], key=lambda x: x["title"]):
                    f.write(f'<page title="{page["title"]}" url="{page["url"]}">\n')
                    f.write(f'<content>{page["content"]}</content>\n')
                    f.write("</page>\n")

                f.write("</section>\n")

            f.write("</project>")

        logger.info(f"Generated {output_file}")

    def save_data(self, output_file: str = "documentation_data.json"):
        """Save raw data for debugging."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.pages_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw data to {output_file}")

    def run(self):
        """Main execution method."""
        logger.info(f"LLMs.txt Generator for {self.config['name']}")
        logger.info("=" * 50)

        # Discover pages
        logger.info("Starting page discovery...")
        discovered_pages = self.discover_pages()
        logger.info(f"\nDiscovered {len(discovered_pages)} pages")

        # Process pages
        logger.info("Starting page processing...")
        self.process_pages(discovered_pages)

        # Generate output files following llmstxt.org specification
        logger.info("Starting file generation...")
        output_dir = self.config.get("output_dir", ".")
        
        # Generate files in the specified output directory
        self.generate_llms_txt(Path(output_dir) / "llms.txt")
        self.generate_llms_full_txt(Path(output_dir) / "llms-full.txt")
        self.save_data(Path(output_dir) / "documentation_data.json")

        logger.info("\nGeneration complete!")
        logger.info(f"Processed {len(self.pages_data)} pages")
        logger.info("Generated files:")
        logger.info("- llms.txt (standard llmstxt.org format)")
        logger.info("- llms-full.txt (full content with expanded links)")
        logger.info("- documentation_data.json (raw data)")

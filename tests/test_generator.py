"""
Tests for the LLMsTxtGenerator class.
"""

from unittest.mock import Mock, patch

import pytest

from llms_txt_generator.config.config import create_default_config
from llms_txt_generator.core.generator import LLMsTxtGenerator


class TestLLMsTxtGenerator:
    """Test cases for LLMsTxtGenerator."""

    def test_init(self):
        """Test generator initialization."""
        config = create_default_config()
        generator = LLMsTxtGenerator(config)

        assert generator.config == config
        assert generator.visited_urls == set()
        assert generator.pages_data == []
        assert generator.session.headers["User-Agent"] == "LLMs.txt Generator/1.0"

    def test_is_valid_url(self):
        """Test URL validation."""
        config = create_default_config()
        generator = LLMsTxtGenerator(config)

        # Valid URL
        assert generator._is_valid_url(
            "https://example.com/docs", "https://example.com"
        )

        # Invalid scheme
        assert not generator._is_valid_url(
            "ftp://example.com/docs", "https://example.com"
        )

        # Different domain
        assert not generator._is_valid_url(
            "https://other.com/docs", "https://example.com"
        )

        # Excluded pattern
        config["exclude_patterns"] = ["#"]
        generator = LLMsTxtGenerator(config)
        assert not generator._is_valid_url(
            "https://example.com/docs#section", "https://example.com"
        )

    def test_categorize_page(self):
        """Test page categorization."""
        config = create_default_config()
        generator = LLMsTxtGenerator(config)

        # Test URL pattern matching
        processed = {
            "url": "https://example.com/docs/api/reference",
            "title": "API Reference",
        }
        category = generator._categorize_page(processed)
        assert category == "API"

        # Test title pattern matching
        processed = {
            "url": "https://example.com/some-page",
            "title": "API Documentation",
        }
        category = generator._categorize_page(processed)
        assert category == "API"

        # Test fallback to "Other"
        processed = {"url": "https://example.com/random-page", "title": "Random Page"}
        category = generator._categorize_page(processed)
        assert category == "Other"

    @patch("llms_txt_generator.core.generator.requests.Session")
    def test_get_page_content(self, mock_session):
        """Test page content retrieval."""
        config = create_default_config()
        generator = LLMsTxtGenerator(config)

        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        content = generator.get_page_content("https://example.com")
        assert content == "<html><body>Test content</body></html>"

        # Mock failed response
        mock_session.return_value.get.side_effect = Exception("Connection error")
        content = generator.get_page_content("https://example.com")
        assert content is None


class TestConfig:
    """Test cases for configuration."""

    def test_create_default_config(self):
        """Test default configuration creation."""
        from llms_txt_generator.config.config import (
            create_default_config,
            validate_config,
        )

        config = create_default_config()

        # Check required fields
        assert "name" in config
        assert "description" in config
        assert "base_urls" in config
        assert len(config["base_urls"]) > 0

        # Validate configuration
        assert validate_config(config) is True

    def test_validate_config_missing_fields(self):
        """Test configuration validation with missing fields."""
        from llms_txt_generator.config.config import validate_config

        # Missing required field
        config = {"name": "Test"}
        with pytest.raises(ValueError, match="Missing required configuration key"):
            validate_config(config)

        # Empty base_urls
        config = {"name": "Test", "description": "Test description", "base_urls": []}
        with pytest.raises(ValueError, match="base_urls must be a non-empty list"):
            validate_config(config)

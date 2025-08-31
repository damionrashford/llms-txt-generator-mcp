"""
Configuration module for LLMs.txt Generator Framework.

Contains default configuration for generating LLMs.txt files.
"""

from typing import Any, Dict


def create_default_config() -> Dict[str, Any]:
    """Create a default configuration template."""
    return {
        "name": "Website Documentation",
        "description": "Documentation generated from website",
        "urls": ["https://example.com"],
        "output_dir": "./output",
        "max_pages": 100,
        "max_depth": 3,
        "traversal_mode": "docs",
        "rate_limit": 1.0,
        "user_agent": "LLMs.txt Generator/1.0",
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate a configuration dictionary."""
    required_keys = ["name", "description", "urls"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    if not isinstance(config["urls"], list) or len(config["urls"]) == 0:
        raise ValueError("urls must be a non-empty list")

    return True

#!/usr/bin/env python3
"""
Command-line interface for LLMs.txt Generator Framework.
"""

import argparse
import json
import logging
import os
from typing import Any, Dict

from ..config.config import create_default_config, validate_config
from ..core.generator import LLMsTxtGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate LLMs.txt files for documentation websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for a website
  python -m llms_txt_generator --urls https://example.com

  # Generate with custom options
  python -m llms_txt_generator --name "My Docs" --description "My documentation" \
    --urls https://example.com/docs --max-pages 200 --max-depth 4

  # Use configuration file
  python -m llms_txt_generator --config my_config.json
        """,
    )

    parser.add_argument("--config", "-c", help="Path to configuration JSON file")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--urls", nargs="+", help="Base URLs to crawl")
    parser.add_argument(
        "--output-dir", "-o", default=".", help="Output directory (default: current)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum number of pages to crawl (default: 100)",
    )
    parser.add_argument(
        "--max-depth", type=int, default=3, help="Maximum traversal depth (default: 3)"
    )
    parser.add_argument(
        "--traversal-mode",
        choices=["docs", "research", "map"],
        default="docs",
        help="Traversal mode: docs, research, or map (default: docs)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = _load_configuration(args)

    # Validate configuration
    try:
        validate_config(config)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate LLMs.txt files
    generator = LLMsTxtGenerator(config)

    try:
        generator.run()

        # Move files to output directory
        _move_files_to_output(args.output_dir)

        logger.info(f"\nFiles saved to: {os.path.abspath(args.output_dir)}")
        return 0

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return 1


def _load_configuration(args) -> Dict[str, Any]:
    """Load configuration from file or command line arguments."""
    # Load from config file if provided
    if args.config and os.path.exists(args.config):
        logger.info(f"Loading configuration from {args.config}")
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        # Use default configuration
        logger.info("Using default configuration")
        config = create_default_config()

    # Override with command line arguments
    if args.name:
        config["name"] = args.name
    if args.description:
        config["description"] = args.description
    if args.urls:
        config["urls"] = args.urls
    if args.max_pages:
        config["max_pages"] = args.max_pages
    if args.max_depth:
        config["max_depth"] = args.max_depth
    if args.traversal_mode:
        config["traversal_mode"] = args.traversal_mode
    if args.rate_limit:
        config["rate_limit"] = args.rate_limit

    return config


def _move_files_to_output(output_dir: str):
    """Move generated files to output directory."""
    files_to_move = ["llms.txt", "llms-full.txt", "documentation_data.json"]

    for filename in files_to_move:
        if os.path.exists(filename):
            source_path = filename
            dest_path = os.path.join(output_dir, filename)
            os.rename(source_path, dest_path)
            logger.debug(f"Moved {filename} to {dest_path}")


if __name__ == "__main__":
    exit(main())

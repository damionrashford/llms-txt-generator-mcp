#!/usr/bin/env python3
"""
LLMs.txt Generator - Command Line Interface

A standalone CLI tool for generating LLMs.txt files for any website.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generator import LLMsTxtGenerator
from src.config.config import create_default_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LLMs.txt files for any website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s @https://example.com
  %(prog)s example.com
  %(prog)s /path/to/local/file.html
  %(prog)s https://example.com ./output
        """
    )
    
    parser.add_argument(
        "url",
        help="Website URL or local file path to generate documentation for"
    )
    
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum number of pages to process (default: 100)"
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum crawl depth (default: 3)"
    )
    
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Rate limit in seconds between requests (default: 1.0)"
    )
    
    parser.add_argument(
        "--traversal-mode",
        choices=["docs", "links", "sitemap"],
        default="docs",
        help="Page discovery mode (default: docs)"
    )
    
    args = parser.parse_args()
    
    # Normalize URL
    url = args.url
    if url.startswith('@'):
        url = url[1:]
    if not url.startswith(('http://', 'https://', 'file://')):
        if os.path.exists(url):
            url = f"file://{os.path.abspath(url)}"
        else:
            url = f"https://{url}"
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create configuration
    config = create_default_config()
    config.update({
        "name": "Website Documentation",
        "description": f"Documentation generated from {url}",
        "urls": [url],
        "output_dir": str(output_dir),
        "max_pages": args.max_pages,
        "max_depth": args.max_depth,
        "traversal_mode": args.traversal_mode,
        "rate_limit": args.rate_limit,
    })
    
    print(f"🚀 LLMs.txt Generator")
    print(f"📄 URL: {url}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️  Max Pages: {args.max_pages}")
    print(f"🔍 Max Depth: {args.max_depth}")
    print(f"🔄 Traversal: {args.traversal_mode}")
    print("-" * 50)
    
    try:
        # Initialize and run generator
        generator = LLMsTxtGenerator(config)
        generator.run()
        
        # List generated files
        txt_files = list(output_dir.glob("*.txt"))
        json_files = list(output_dir.glob("*.json"))
        all_files = txt_files + json_files
        
        print(f"✅ Successfully generated {len(all_files)} files:")
        for file in all_files:
            print(f"   📄 {file.name}")
        
        print(f"\n📊 Statistics:")
        print(f"   📄 Pages processed: {len(generator.pages_data)}")
        print(f"   📁 Output directory: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

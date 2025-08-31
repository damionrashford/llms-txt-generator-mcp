#!/usr/bin/env python3
"""
Low-level MCP Server for LLMs.txt Generator

This server uses the official MCP Python SDK for full protocol control.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from core.generator import LLMsTxtGenerator
from config.config import create_default_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("llms-txt-generator")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_llms_txt",
            description="Generate LLMs.txt files for a website following the llmstxt.org specification",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string", 
                        "description": "Website URL to generate LLMs.txt for (supports various formats: https://example.com, example.com, @https://example.com, local file paths)"
                    }
                },
                "required": ["url"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "description": "Whether generation was successful"},
                    "pages_processed": {"type": "number", "description": "Number of pages processed"},
                    "files_generated": {"type": "array", "items": {"type": "string"}, "description": "List of generated files"},
                    "output_directory": {"type": "string", "description": "Directory where files were saved"},
                    "files_content": {"type": "object", "description": "Content of generated files"}
                },
                "required": ["success", "pages_processed", "files_generated", "output_directory"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool calls with proper error handling and logging."""
    if name != "generate_llms_txt":
        raise ValueError(f"Unknown tool: {name}")
    
    url = arguments.get("url", "")
    if not url or not url.strip():
        logger.error("URL is required and cannot be empty")
        return {
            "success": False,
            "error": "URL is required and cannot be empty",
            "pages_processed": 0,
            "files_generated": [],
            "output_directory": "",
            "files_content": {}
        }
    
    try:
        # Normalize URL
        if url.startswith('@'):
            url = url[1:]
        if not url.startswith(('http://', 'https://', 'file://')):
            if os.path.exists(url):
                url = f"file://{os.path.abspath(url)}"
            else:
                url = f"https://{url}"
        
        logger.info(f"Generating LLMs.txt for: {url}")
        
        # Create temporary output directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create configuration
            config = create_default_config()
            config.update({
                "name": "Website Documentation",
                "description": f"Documentation generated from {url}",
                "urls": [url],
                "output_dir": temp_dir,
                "max_pages": 100,
                "max_depth": 3,
                "traversal_mode": "docs",
                "rate_limit": 1.0,
            })
            
            # Initialize and run generator
            generator = LLMsTxtGenerator(config)
            generator.run()
            
            # Get generated files
            output_path = Path(temp_dir)
            txt_files = list(output_path.glob("*.txt"))
            json_files = list(output_path.glob("*.json"))
            all_files = txt_files + json_files
            
            # Read file contents for response
            files_data = {}
            for file in all_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        files_data[file.name] = f.read()
                except Exception as e:
                    logger.warning(f"Could not read {file.name}: {e}")
            
            # Copy files to current directory for user access
            import shutil
            for file in all_files:
                shutil.copy2(file, ".")
            
            logger.info(f"Successfully generated {len(all_files)} files")
            
            return {
                "success": True,
                "pages_processed": len(generator.pages_data),
                "files_generated": [f.name for f in all_files],
                "output_directory": os.getcwd(),
                "files_content": files_data
            }
            
    except Exception as e:
        logger.error(f"Error generating LLMs.txt: {e}")
        return {
            "success": False,
            "error": str(e),
            "pages_processed": 0,
            "files_generated": [],
            "output_directory": "",
            "files_content": {}
        }


async def run():
    """Run the low-level MCP server with proper initialization."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="llms-txt-generator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Main entry point for the MCP server."""
    print("Starting LLMs.txt Generator MCP Server...")
    print("Server: llms-txt-generator")
    print("Transport: STDIO")
    print("Tool: generate_llms_txt")
    print("-" * 50)
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

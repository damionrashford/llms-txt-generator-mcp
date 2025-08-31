#!/usr/bin/env python3
"""
Generate Cursor Deeplink for LLMs.txt Generator

This script helps users create a Cursor deeplink for installing the LLMs.txt Generator MCP server.
"""

import json
import base64
import os
import sys
from pathlib import Path

def generate_deeplink():
    """Generate a Cursor deeplink for the LLMs.txt Generator."""
    
    # Get the current directory (should be the project root)
    project_path = Path.cwd().absolute()
    server_path = project_path / "server.py"
    
    # Check if server.py exists
    if not server_path.exists():
        print("❌ Error: server.py not found in current directory")
        print("Please run this script from the llms-txt-generator project root")
        sys.exit(1)
    
    # Create the MCP configuration
    config = {
        "llms-txt-generator": {
            "command": "python3",
            "args": [str(server_path)],
            "env": {
                "PYTHONPATH": str(project_path),
                "LOG_LEVEL": "INFO"
            },
            "timeout": 60000,
            "initTimeout": 15000,
            "stderr": "inherit"
        }
    }
    
    # Convert to JSON and base64 encode
    config_json = json.dumps(config, separators=(',', ':'))
    config_b64 = base64.b64encode(config_json.encode()).decode()
    
    # Create the deeplink
    deeplink = f"cursor://anysphere.cursor-deeplink/mcp/install?name=llms-txt-generator&config={config_b64}"
    
    # Display results
    print("🚀 LLMs.txt Generator - Cursor Deeplink Generator")
    print("=" * 50)
    print()
    print(f"📁 Project Path: {project_path}")
    print(f"🔧 Server Path: {server_path}")
    print()
    print("📋 MCP Configuration:")
    print(json.dumps(config, indent=2))
    print()
    print("🔗 Your Cursor Deeplink:")
    print("-" * 50)
    print(deeplink)
    print("-" * 50)
    print()
    print("📝 Instructions:")
    print("1. Copy the deeplink above")
    print("2. Paste it into your browser or click it")
    print("3. Cursor will prompt you to install the MCP server")
    print("4. Restart Cursor to activate the server")
    print()
    print("✅ The generate_llms_txt tool will then be available in Cursor!")
    print()
    print("💡 Alternative: You can also manually add the configuration to ~/.cursor/mcp.json")

if __name__ == "__main__":
    generate_deeplink()

# LLMs.txt Generator

A powerful MCP (Model Context Protocol) server that automatically generates `llms.txt` and `llms-full.txt` files for any website, following the [llmstxt.org specification](https://llmstxt.org/).

## 🚀 Quick Start - Install in Cursor

### Option 1: One-Click Installation (Recommended)

**Note**: The one-click installation requires you to have the repository cloned locally. After cloning, you can create your own deeplink.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/damionrashford/llms-txt-generator.git
   cd llms-txt-generator
   ```

2. **Create your deeplink:**
   
   Replace `/path/to/your/llms-txt-generator` with your actual path in this configuration:
   ```json
   {
     "llms-txt-generator": {
       "command": "python3",
       "args": ["/path/to/your/llms-txt-generator/server.py"],
       "env": {
         "PYTHONPATH": "/path/to/your/llms-txt-generator",
         "LOG_LEVEL": "INFO"
       },
       "timeout": 60000,
       "initTimeout": 15000,
       "stderr": "inherit"
     }
   }
   ```

3. **Generate the deeplink:**
   - Copy the JSON configuration above
   - Replace `/path/to/your/llms-txt-generator` with your actual path
   - Base64 encode the JSON
   - Create the deeplink: `cursor://anysphere.cursor-deeplink/mcp/install?name=llms-txt-generator&config=YOUR_BASE64_CONFIG`

4. **Click the deeplink** to install in Cursor

### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/damionrashford/llms-txt-generator.git
   cd llms-txt-generator
   ```

2. **Set up the environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Add to Cursor's MCP configuration:**
   
   Open `~/.cursor/mcp.json` (create if it doesn't exist) and add:
   ```json
   {
     "mcpServers": {
       "llms-txt-generator": {
         "command": "python3",
         "args": ["/path/to/your/llms-txt-generator/server.py"],
         "env": {
           "PYTHONPATH": "/path/to/your/llms-txt-generator",
           "LOG_LEVEL": "INFO"
         },
         "timeout": 60000,
         "initTimeout": 15000,
         "stderr": "inherit"
       }
     }
   }
   ```

4. **Restart Cursor** to load the new MCP server.

## 🛠️ Usage

Once installed, you can use the `generate_llms_txt` tool in Cursor:

### Supported URL Formats:
- `https://example.com`
- `@https://example.com` (with @ prefix)
- `example.com` (auto-adds https://)
- Local file paths

### Example Usage:
```
Generate LLMs.txt for https://gofastmcp.com/clients/roots
```

The tool will generate:
- **`llms.txt`**: Clean, structured documentation
- **`llms-full.txt`**: Full content with HTML
- **`documentation_data.json`**: Structured data for programmatic use

## 📋 Features

- ✅ **Automatic Page Discovery**: Crawls websites to find relevant pages
- ✅ **Flexible URL Support**: Handles various URL formats and local files
- ✅ **Structured Output**: Generates both human-readable and machine-readable formats
- ✅ **MCP Integration**: Seamless integration with Cursor and other MCP clients
- ✅ **Error Handling**: Robust error handling with detailed feedback
- ✅ **Rate Limiting**: Built-in rate limiting to be respectful to servers

## 🏗️ Architecture

### Core Components

- **`server.py`**: Main MCP server using the official MCP Python SDK
- **`src/core/generator.py`**: Core LLMs.txt generation logic
- **`src/config/config.py`**: Configuration management
- **`src/utils/`**: Utility modules for content processing and sitemap extraction

### MCP Server Features

- **Single Tool**: `generate_llms_txt` - generates documentation for any website
- **Structured Output**: Returns success status, page count, file contents, and output location
- **Flexible Input**: Accepts URLs in various formats with automatic normalization
- **Temporary Processing**: Uses temporary directories for clean file generation

## 🔧 Development

### Prerequisites

- Python 3.8+
- pip or uv

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/damionrashford/llms-txt-generator.git
   cd llms-txt-generator
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Run the server:**
   ```bash
   python server.py
   ```

3. **Test with CLI:**
   ```bash
   python generate_llms_txt.py https://example.com
   ```

### Project Structure

```
llms-txt-generator/
├── server.py                 # Main MCP server
├── generate_llms_txt.py      # Standalone CLI tool
├── generate_deeplink.py      # Helper script for creating deeplinks
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
├── src/
│   ├── core/
│   │   └── generator.py     # Core generation logic
│   ├── config/
│   │   └── config.py        # Configuration management
│   └── utils/               # Utility modules
└── README.md
```

## 📦 Distribution

### For Other Users

To make this available to other users, they can:

1. **Use the one-click installation link** (recommended)
2. **Clone and setup manually** following the installation instructions above
3. **Create their own deeplink** using the MCP configuration format

### MCP Configuration Format

```json
{
  "llms-txt-generator": {
    "command": "python3",
    "args": ["/path/to/server.py"],
    "env": {
      "PYTHONPATH": "/path/to/project",
      "LOG_LEVEL": "INFO"
    },
    "timeout": 60000,
    "initTimeout": 15000,
    "stderr": "inherit"
  }
}
```

### Creating a Deeplink

1. **Prepare the configuration:**
   ```bash
   # Create the JSON config (replace with your path)
   echo '{"llms-txt-generator":{"command":"python3","args":["/path/to/your/llms-txt-generator/server.py"],"env":{"PYTHONPATH":"/path/to/your/llms-txt-generator","LOG_LEVEL":"INFO"},"timeout":60000,"initTimeout":15000,"stderr":"inherit"}}' > config.json
   ```

2. **Base64 encode:**
   ```bash
   cat config.json | base64
   ```

3. **Create the deeplink:**
   ```
   cursor://anysphere.cursor-deeplink/mcp/install?name=llms-txt-generator&config=YOUR_BASE64_OUTPUT
   ```

## 🙏 Acknowledgments

- [llmstxt.org](https://llmstxt.org/) for the specification
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) for the protocol implementation
- [Cursor](https://cursor.sh/) for MCP client integration

---

**Ready to generate LLMs.txt files for any website? Install the MCP server and start documenting!** 🚀

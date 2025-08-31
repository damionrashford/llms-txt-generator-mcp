"""
LLMs.txt Generator Framework

A standalone Python framework for automatically generating LLMs.txt files
from any documentation website, following the llmstxt.org specification.

This framework can be configured to work with any documentation site by
providing the appropriate configuration.
"""

__version__ = "1.0.0"
__author__ = "LLMs.txt Generator Team"
__description__ = "Generate LLMs.txt files from documentation websites"

from .core.generator import LLMsTxtGenerator

__all__ = [
    "LLMsTxtGenerator",
]

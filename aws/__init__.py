"""
AWS Integration Module for OmniMCP Virtual Assistant.

Provides:
- Amazon Bedrock client for high-reasoning LLM inference & tool calling
- Amazon S3 sync for cloud backup of everyday state, notes, and memories
- Serverless architecture blueprints for hack day scaling
"""
from .bedrock_client import BedrockLLMClient
from .s3_sync import S3CloudSync

__all__ = ["BedrockLLMClient", "S3CloudSync"]

"""
Amazon Bedrock Client for OmniMCP Virtual Assistant.

Allows the assistant to run on AWS-hosted foundation models:
- Claude 3.5 Sonnet / Claude 3 Haiku (anthropic.claude-3-5-sonnet-20241022-v2:0)
- Amazon Titan Text Express (amazon.titan-text-express-v1)
- Meta Llama 3 70B Instruct (meta.llama3-70b-instruct-v1:0)

Supports standard Bedrock Converse API with native tool-use mapping for MCP tools.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OmniMCP.AWS.Bedrock")


class BedrockLLMClient:
    """Client for invoking models on Amazon Bedrock with MCP tool calling support."""

    DEFAULT_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    def __init__(self, region_name: Optional[str] = None, model_id: Optional[str] = None):
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        self.model_id = model_id or os.environ.get("BEDROCK_MODEL_ID", self.DEFAULT_MODEL)
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            self._client = boto3.client("bedrock-runtime", region_name=self.region_name)
            logger.info("Initialized AWS Bedrock client in region %s", self.region_name)
        except ImportError:
            logger.info("boto3 not installed. Install with `pip install boto3` to enable AWS Bedrock.")
            self._client = None
        except Exception as e:
            logger.warning("AWS Bedrock initialization deferred: %s", e)
            self._client = None

    def is_available(self) -> bool:
        return self._client is not None

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        mcp_tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Invokes model via Bedrock Converse API with MCP tool definitions.
        """
        if not self.is_available():
            return {
                "status": "error",
                "message": "AWS Bedrock client is not configured or boto3 is missing.",
            }

        # Convert MCP tools to Bedrock toolConfig format
        tool_config = None
        if mcp_tools:
            tool_list = []
            for t in mcp_tools:
                tool_list.append({
                    "toolSpec": {
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "inputSchema": {
                            "json": t.get("parameters", {"type": "object", "properties": {}})
                        },
                    }
                })
            tool_config = {"tools": tool_list}

        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
        }

        # Format system prompt
        system_list = [{"text": system_prompt}] if system_prompt else []

        try:
            kwargs = {
                "modelId": self.model_id,
                "messages": messages,
                "inferenceConfig": inference_config,
            }
            if system_list:
                kwargs["system"] = system_list
            if tool_config:
                kwargs["toolConfig"] = tool_config

            response = self._client.converse(**kwargs)
            output_msg = response.get("output", {}).get("message", {})
            return {
                "status": "success",
                "message": output_msg,
                "usage": response.get("usage", {}),
                "stopReason": response.get("stopReason"),
            }
        except Exception as e:
            logger.error("AWS Bedrock converse failed: %s", e)
            return {"status": "error", "message": str(e)}

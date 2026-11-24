"""
Model Context Protocol (MCP) data models and schema definitions.
Conforms to the standard MCP specification (v2024-11-05).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# ── Standard JSON-RPC 2.0 Types ──────────────────────────────────────────────

@dataclass
class JSONRPCRequest:
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            d["params"] = self.params
        if self.id is not None:
            d["id"] = self.id
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class JSONRPCResponse:
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCResponse":
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            result=data.get("result"),
            error=data.get("error"),
        )


# ── MCP Tool & Resource Schemas ──────────────────────────────────────────────

@dataclass
class MCPToolParameterSchema:
    type: str = "object"
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
    server_name: str = "local"
    requires_confirmation: bool = False

    def to_gemini_declaration(self) -> Dict[str, Any]:
        """Convert MCP tool definition into Gemini / OpenAI compatible function declaration."""
        props = self.input_schema.get("properties", {})
        converted_props = {}
        for prop_name, prop_def in props.items():
            p_type = prop_def.get("type", "string").upper()
            if p_type == "OBJECT":
                p_type = "OBJECT"
            elif p_type == "ARRAY":
                p_type = "ARRAY"
            elif p_type in ("NUMBER", "FLOAT"):
                p_type = "NUMBER"
            elif p_type == "INTEGER":
                p_type = "INTEGER"
            elif p_type == "BOOLEAN":
                p_type = "BOOLEAN"
            else:
                p_type = "STRING"

            converted_props[prop_name] = {
                "type": p_type,
                "description": prop_def.get("description", f"Parameter {prop_name}"),
            }

        return {
            "name": f"mcp_{self.server_name}_{self.name}" if not self.name.startswith("mcp_") else self.name,
            "description": f"[{self.server_name.upper()} MCP] {self.description}",
            "parameters": {
                "type": "OBJECT",
                "properties": converted_props,
                "required": self.input_schema.get("required", []),
            },
        }


@dataclass
class MCPResource:
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None

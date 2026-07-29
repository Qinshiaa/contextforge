"""Tool'ları gölgele, schema'ları minimize et."""
import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ShadowTool:
    name: str
    description: str
    original_schema: Dict[str, Any]
    minified_schema: Dict[str, Any]
    server_name: str


def minify_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return {"type": "object"}

    minified = {}
    if "type" in schema:
        minified["type"] = schema["type"]
    if "required" in schema:
        minified["required"] = schema["required"]

    if "properties" in schema and isinstance(schema["properties"], dict):
        minified["properties"] = {}
        for key, prop in schema["properties"].items():
            min_prop = {}
            if isinstance(prop, dict):
                if "type" in prop:
                    min_prop["type"] = prop["type"]
                if "enum" in prop:
                    min_prop["enum"] = prop["enum"]
                if "description" in prop:
                    desc = prop["description"]
                    min_prop["description"] = desc[:77] + "..." if len(desc) > 80 else desc
            minified["properties"][key] = min_prop

    if "items" in schema:
        minified["items"] = minify_schema(schema["items"]) if isinstance(schema["items"], dict) else schema["items"]

    return minified


class ShadowRegistry:
    def __init__(self):
        self.tools: Dict[str, ShadowTool] = {}

    def register(self, tool: ShadowTool):
        self.tools[tool.name] = tool

    def get_minified_tools(self) -> List[Dict[str, Any]]:
        return [{
            "name": name,
            "description": t.description,
            "inputSchema": t.minified_schema
        } for name, t in self.tools.items()]

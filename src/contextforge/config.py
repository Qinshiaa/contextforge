"""Claude Desktop config'ini oku, ContextForge hariç tüm sunucuları listele."""
import json
import os
from pathlib import Path
from typing import Dict, List, Any


def get_claude_config_path() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif os.uname().sysname == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def load_mcp_servers() -> List[Dict[str, Any]]:
    config_path = get_claude_config_path()
    if not config_path.exists():
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    servers = []
    for name, server_def in config.get("mcpServers", {}).items():
        if name.lower() in ("contextforge", "context-forge", "context_forge"):
            continue
        servers.append({
            "name": name,
            "command": server_def.get("command", ""),
            "args": server_def.get("args", []),
            "env": {**os.environ, **server_def.get("env", {})}
        })
    return servers

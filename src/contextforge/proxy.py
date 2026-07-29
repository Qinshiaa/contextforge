"""Diğer MCP sunucularını başlat, tool'larını proxy'le."""
import asyncio
import json
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from contextforge.config import load_mcp_servers
from contextforge.registry import ShadowRegistry, ShadowTool, minify_schema
from contextforge.compressor import ResultCompressor
from contextforge.archive import ArchiveDB


class ProxyManager:
    def __init__(self):
        self.registry = ShadowRegistry()
        self.sessions: Dict[str, ClientSession] = {}
        self._transports = []
        self.compressor = ResultCompressor()
        self.archive = ArchiveDB()
    
    async def bootstrap(self):
        servers = load_mcp_servers()
        if not servers:
            print("⚠️  Proxy'lenecek sunucu bulunamadı.")
            return
        
        print(f"🔧 {len(servers)} sunucu bulundu.")
        for server_def in servers:
            await self._connect(server_def)
        
        print(f"✅ {len(self.registry.tools)} tool proxy'leniyor.")
    
    async def _connect(self, server_def: Dict[str, Any]):
        name = server_def["name"]
        try:
            params = StdioServerParameters(
                command=server_def["command"],
                args=server_def["args"],
                env=server_def["env"]
            )
            
            # Yeni MCP: stdio_client direkt tuple döndürür
            read, write = await stdio_client(params)
            self._transports.append((read, write))
            
            session = ClientSession(read, write)
            await session.initialize()
            self.sessions[name] = session
            
            result = await session.list_tools()
            for tool in result.tools:
                tool_name = tool.name
                if tool_name in self.registry.tools:
                    tool_name = f"{name}_{tool_name}"
                
                schema = tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                self.registry.register(ShadowTool(
                    name=tool_name,
                    description=tool.description or f"Tool from {name}",
                    original_schema=schema,
                    minified_schema=minify_schema(schema),
                    server_name=name
                ))
            print(f"   ✅ {name}: {len(result.tools)} tool")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        tool = self.registry.tools.get(tool_name)
        if not tool:
            return f"❌ Tool '{tool_name}' bulunamadı."
        
        session = self.sessions.get(tool.server_name)
        if not session:
            return f"❌ Sunucu '{tool.server_name}' bağlı değil."
        
        try:
            original_name = tool_name
            if original_name.startswith(f"{tool.server_name}_"):
                original_name = original_name[len(tool.server_name)+1:]
            
            result = await session.call_tool(original_name, arguments)
            texts = []
            for c in result.content:
                if hasattr(c, 'text'):
                    texts.append(c.text)
                else:
                    texts.append(str(c))
            raw_text = "\n".join(texts)
            
            try:
                raw_data = json.loads(raw_text)
            except:
                raw_data = raw_text
            
            summary, ratio = self.compressor.compress(tool_name, raw_data)
            archive_id = self.archive.store(tool_name, raw_data, summary)
            
            return (
                f"📦 {summary}\n\n"
                f"[Archive: {archive_id} | "
                f"Compressed {len(raw_text)//4}→{len(summary)//4} tokens "
                f"({ratio:.1f}x)]"
            )
        except Exception as e:
            return f"❌ Hata: {e}"
    
    async def cleanup(self):
        for session in self.sessions.values():
            try:
                await session.aclose()
            except:
                pass
        for read, write in self._transports:
            try:
                await read.aclose()
                await write.aclose()
            except:
                pass
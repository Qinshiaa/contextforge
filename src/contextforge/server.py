"""ContextForge MCP Server — FastMCP stabil versiyon."""
import asyncio
import json
import sys
from mcp.server.fastmcp import FastMCP

from contextforge.proxy import ProxyManager
from contextforge.archive import ArchiveDB

mcp = FastMCP("ContextForge")
archive = ArchiveDB()
proxy = ProxyManager()

def _log(msg):
    """Log stderr'e yazılır, stdout MCP için ayrılmıştır."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

@mcp.tool()
async def cf_context_status() -> str:
    stats = archive.stats()
    proxy_count = len(proxy.registry.tools)
    return (
        f"📊 ContextForge Durumu\n"
        f"{'='*40}\n"
        f"Proxy'lenen tool: {proxy_count}\n"
        f"Arşiv kayıt: {stats['count']}\n"
        f"Arşiv boyut: {stats['size_kb']} KB\n"
        f"Tahmini tasarruf: ~{proxy_count * 300} token/tur\n\n"
        f"🙏 Token'ları koruyoruz."
    )

@mcp.tool()
async def cf_search_archive(query: str, limit: int = 5) -> str:
    results = archive.search(query, limit)
    if not results:
        return f"'{query}' için arşivde sonuç yok."
    lines = [f"📦 '{query}' için {len(results)} sonuç:"]
    for r in results:
        lines.append(f"- [{r['tool_name']}] {r['summary'][:100]}... (ID: {r['id']})")
    return "\n".join(lines)

@mcp.tool()
async def cf_retrieve_archive(archive_id: str) -> str:
    result = archive.retrieve(archive_id)
    if result:
        return f"📦 Arşiv: {archive_id}\n\n{json.dumps(result['content'], indent=2, ensure_ascii=False)[:4000]}"
    return f"Arşiv '{archive_id}' bulunamadı."

async def add_proxy_tools():
    _log("🔧 ContextForge: Proxy sunucular başlatılıyor...")
    await proxy.bootstrap()
    for name, tool in proxy.registry.tools.items():
        async def make_handler(tn=name):
            async def handler(**kwargs):
                return await proxy.call_tool(tn, kwargs)
            return handler
        mcp.add_tool(await make_handler(), name=name)
    _log(f"✅ Toplam {len(proxy.registry.tools)} proxy tool aktif.")

def main():
    asyncio.run(add_proxy_tools())
    mcp.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _log("\n👋 ContextForge kapatıldı. Token'lar güvende. 🙏")
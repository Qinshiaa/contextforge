"""ContextForge MCP Server — Ana giriş noktası."""
import asyncio
import json
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ListToolsResult

from contextforge.proxy import ProxyManager
from contextforge.archive import ArchiveDB


archive = ArchiveDB()
proxy = ProxyManager()
server = Server("ContextForge")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    tools = proxy.get_all_tools()

    # Native ContextForge tools
    tools.append(Tool(
        name="cf_context_status",
        description="ContextForge durumunu ve token tasarruf istatistiklerini göster",
        inputSchema={"type": "object", "properties": {}}
    ))
    tools.append(Tool(
        name="cf_search_archive",
        description="Arşivlenmiş tool sonuçlarını doğal dil ile ara",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Arama sorgusu"},
                "limit": {"type": "integer", "description": "Max sonuç", "default": 5}
            },
            "required": ["query"]
        }
    ))
    tools.append(Tool(
        name="cf_retrieve_archive",
        description="Arşiv ID'si ile ham sonucu geri getir",
        inputSchema={
            "type": "object",
            "properties": {
                "archive_id": {"type": "string", "description": "Arşiv ID"}
            },
            "required": ["archive_id"]
        }
    ))

    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "cf_context_status":
        stats = archive.stats()
        proxy_count = len(proxy.registry.tools)
        text = (
            f"📊 ContextForge Durumu\n"
            f"{'='*40}\n"
            f"Proxy'lenen tool: {proxy_count}\n"
            f"Arşiv kayıt: {stats['count']}\n"
            f"Arşiv boyut: {stats['size_kb']} KB\n"
            f"Tahmini tasarruf: ~{proxy_count * 300} token/tur (schema)\n"
            f"                    + ~%90 (sonuç sıkıştırma)\n\n"
            f"🙏 Token'ları koruyoruz."
        )
        return [TextContent(type="text", text=text)]

    if name == "cf_search_archive":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)
        results = archive.search(query, limit)
        if not results:
            return [TextContent(type="text", text=f"'{query}' için arşivde sonuç yok.")]
        lines = [f"📦 '{query}' için {len(results)} sonuç:"]
        for r in results:
            lines.append(f"- [{r['tool_name']}] {r['summary'][:100]}... (ID: {r['id']})")
        return [TextContent(type="text", text="\n".join(lines))]

    if name == "cf_retrieve_archive":
        archive_id = arguments.get("archive_id", "")
        result = archive.retrieve(archive_id)
        if result:
            text = f"📦 Arşiv: {archive_id}\n\n{json.dumps(result['content'], indent=2, ensure_ascii=False)[:4000]}"
            return [TextContent(type="text", text=text)]
        return [TextContent(type="text", text=f"Arşiv '{archive_id}' bulunamadı.")]

    # Proxy'lenen tool
    result = await proxy.call_tool(name, arguments)
    return [TextContent(type="text", text=result)]


async def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    ContextForge Başlatılıyor...                  ║
║                    Token'ları koruyoruz 🙏                       ║
╚══════════════════════════════════════════════════════════════════╝
""")
    await proxy.bootstrap()

    if not proxy.registry.tools:
        print("⚠️  Proxy tool yok, sadece native tool'lar aktif.")

    print("🚀 MCP Server çalışıyor... (stdio)")
    try:
        async with stdio_server(server) as (read, write):
            await server.run(read, write)
    finally:
        await proxy.cleanup()


def main_sync():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ContextForge kapatıldı. Token'lar güvende. 🙏")


if __name__ == "__main__":
    main_sync()

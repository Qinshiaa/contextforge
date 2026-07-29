# 🏗️ ContextForge

> "Claude Desktop token'larına elit ball knowledge uygula.  
>  Context exhaustion? son im crine😭 — Artık değil." 🙏

## 🚀 15 Saniyede Kurulum (npx)

### Adım 1: Tek satırda kur
```bash
npx -y github:Qinshiaa/contextforge
```

İlk çalıştırmada Python paketini otomatik kurar. Sonraki çalıştırmalarda anında açılır.

### Adım 2: Claude Desktop'a ekle
`claude_desktop_config.json`'e şunu yapıştır:

```json
{
  "mcpServers": {
    "contextforge": {
      "command": "npx",
      "args": ["-y", "github:Qinshiaa/contextforge"]
    }
  }
}
```

> 💡 **Not:** `npx` Node.js ile gelir. Zaten kurulu değilse:  
> `npm install -g npx` veya direkt Node.js kur: https://nodejs.org

### Adım 3: Restart at
Claude Desktop'ı tamamen kapatıp aç. Hepsi bu. cornball değiliz. 😭

---

## 🎯 Ne Yapar?

| Özellik | Açıklama |
|---------|----------|
| **🔦 Auto-Discovery** | Diğer TÜM MCP sunucularını otomatik bulur ve proxy'ler |
| **✂️ Schema Minify** | Tool tanımlarını ~%40 daha az token ile sunar |
| **🗜️ Result Compress** | Ham JSON sonuçlarını ~%90 sıkıştırır |
| **📦 Smart Archive** | Her sonucu SQLite'e kaydeder, sonra arayıp geri getirebilirsin |
| **📊 Context Status** | Token tasarruf istatistiklerini raporlar |

---

## 🎮 Kullanım

ContextForge **arka planda** çalışır. Sen fark etmezsin ama token'lar fark eder.

Ama istersen Claude'a şunları sorabilirsin:

- `"Context durumum ne?"` → `cf_context_status`
- `"Geçen haftaki arşivlerimi göster"` → `cf_search_archive`
- `"archive_abc123 detaylarını getir"` → `cf_retrieve_archive`

---

## 📊 Token Tasarrufu

| Senaryo | Önce | Sonra | Tasarruf |
|---------|------|-------|----------|
| 20 MCP aracı, ilk tur | ~12,000 token | ~7,000 token | **%42** |
| GitHub API sonucu (47 repo) | ~8,000 token | ~400 token | **%95** |
| 30 tur sonrası history | ~180,000 token | ~45,000 token | **%75** |

---

## 🛠️ Manuel Kurulum (Alternatif)

Eğer `npx` kullanmak istemiyorsan:

```bash
# 1. Repoyu klonla
git clone https://github.com/Qinshiaa/contextforge.git
cd contextforge

# 2. Python paketini kur
pip install .

# 3. Claude config'ine ekle
# "command": "contextforge"
```

---

## 📝 Lisans

MIT — Token'ları özgür bırak! 🙏

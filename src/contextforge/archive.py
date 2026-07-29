"""FTS5 destekli SQLite arşiv. Doğal dil sorgusuyla geri çağrılabilir."""
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class ArchiveDB:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".contextforge" / "archive.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archives (
                    id TEXT PRIMARY KEY,
                    tool_name TEXT,
                    content TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS archives_fts USING fts5(
                    summary, tool_name, content=archives, content_rowid=rowid
                )
            """)
            conn.commit()

    def store(self, tool_name: str, content: Any, summary: str) -> str:
        archive_id = f"{tool_name}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
        content_json = json.dumps(content, ensure_ascii=False)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO archives (id, tool_name, content, summary) VALUES (?, ?, ?, ?)",
                (archive_id, tool_name, content_json, summary)
            )
            conn.commit()
        return archive_id

    def retrieve(self, archive_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM archives WHERE id = ?", (archive_id,)).fetchone()
            if row:
                return {"id": row[0], "tool_name": row[1], "content": json.loads(row[2]), "summary": row[3], "created_at": row[4]}
            return None

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT a.id, a.tool_name, a.summary, a.created_at 
                FROM archives_fts fts
                JOIN archives a ON a.rowid = fts.rowid
                WHERE archives_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit)).fetchall()
            return [{"id": r[0], "tool_name": r[1], "summary": r[2], "created_at": r[3]} for r in rows]

    def stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM archives").fetchone()[0]
        size = self.db_path.stat().st_size if self.db_path.exists() else 0
        return {"count": count, "size_kb": round(size / 1024, 1)}

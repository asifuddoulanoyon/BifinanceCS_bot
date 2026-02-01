import aiosqlite
import datetime

DB_FILE = "support.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                added_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE,
                user_id INTEGER,
                user_name TEXT,
                bif_uid TEXT,
                email TEXT,
                problem TEXT,
                status TEXT DEFAULT 'OPEN',  -- OPEN, IN_PROGRESS, CLOSED, TRANSFERRED
                assigned_agent INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                from_id INTEGER,
                is_agent BOOLEAN,
                content_type TEXT,
                content TEXT,
                caption TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()

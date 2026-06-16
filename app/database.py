import sqlite3

from app.path_utils import get_database_path


def get_connection():
    """创建数据库连接，并让查询结果可以通过字段名读取。"""
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    return connection


def get_table_columns(conn, table_name):
    """读取指定数据表当前已经存在的字段名。"""
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def ensure_column(conn, table_name, column_name, ddl):
    """字段不存在时追加字段，已经存在时直接跳过。"""
    columns = get_table_columns(conn, table_name)
    if column_name in columns:
        return False

    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")
    return True


def init_database():
    """初始化数据库，并在 books 表不存在时创建它。"""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nfc_id TEXT UNIQUE,
                title TEXT NOT NULL,
                author TEXT,
                category TEXT,
                location TEXT,
                status TEXT DEFAULT '未借出',
                created_at TEXT
            )
            """
        )
        ensure_column(
            connection,
            "books",
            "reading_status",
            "reading_status TEXT DEFAULT '未读'",
        )
        ensure_column(
            connection,
            "books",
            "rating",
            "rating INTEGER DEFAULT 0",
        )

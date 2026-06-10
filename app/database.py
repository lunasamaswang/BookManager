import sqlite3

from app.path_utils import get_database_path


def get_connection():
    """创建数据库连接，并让查询结果可以通过字段名读取。"""
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    return connection


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

import sqlite3
from datetime import datetime

from app.database import get_connection


class DuplicateNfcError(Exception):
    """当 NFC 编号已经存在时抛出的业务异常。"""


def add_book(nfc_id, title, author, category, location, status="未借出"):
    """添加一本图书，并返回新记录的编号。"""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("书名不能为空")

    clean_nfc_id = nfc_id.strip() or None
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO books
                    (nfc_id, title, author, category, location, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clean_nfc_id,
                    clean_title,
                    author.strip(),
                    category.strip(),
                    location.strip(),
                    status.strip() or "未借出",
                    created_at,
                ),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as error:
        if "books.nfc_id" in str(error):
            raise DuplicateNfcError("该 NFC 编号已存在，请更换后重试") from error
        raise


def get_books(keyword=""):
    """查询图书；有关键词时按书名、作者或 NFC 编号模糊搜索。"""
    clean_keyword = keyword.strip()

    with get_connection() as connection:
        if clean_keyword:
            search_value = f"%{clean_keyword}%"
            rows = connection.execute(
                """
                SELECT id, nfc_id, title, author, category, location, status, created_at
                FROM books
                WHERE title LIKE ? OR author LIKE ? OR nfc_id LIKE ?
                ORDER BY id DESC
                """,
                (search_value, search_value, search_value),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, nfc_id, title, author, category, location, status, created_at
                FROM books
                ORDER BY id DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def get_book_statistics():
    """返回首页需要的基础统计数据。"""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = '已借出' THEN 1 ELSE 0 END) AS borrowed
            FROM books
            """
        ).fetchone()

    return {
        "total": row["total"] or 0,
        "borrowed": row["borrowed"] or 0,
    }


def get_recent_books(limit=5):
    """按添加顺序返回最近的图书，默认取 5 本。"""
    safe_limit = max(0, int(limit))
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, nfc_id, title, author, category, location, status, created_at
            FROM books
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_book(book_id):
    """根据图书编号查询单本图书，不存在时返回 None。"""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, nfc_id, title, author, category, location, status, created_at
            FROM books
            WHERE id = ?
            """,
            (book_id,),
        ).fetchone()

    return dict(row) if row else None


def update_book(book_id, nfc_id, title, author, category, location, status):
    """更新一本图书的信息，并返回是否更新成功。"""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("书名不能为空")

    clean_nfc_id = nfc_id.strip() or None

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE books
                SET nfc_id = ?, title = ?, author = ?, category = ?,
                    location = ?, status = ?
                WHERE id = ?
                """,
                (
                    clean_nfc_id,
                    clean_title,
                    author.strip(),
                    category.strip(),
                    location.strip(),
                    status.strip() or "未借出",
                    book_id,
                ),
            )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError as error:
        if "books.nfc_id" in str(error):
            raise DuplicateNfcError("该 NFC 编号已存在，请更换后重试") from error
        raise


def delete_book(book_id):
    """根据图书编号删除记录，并返回是否删除成功。"""
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return cursor.rowcount > 0

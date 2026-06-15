import sqlite3
from datetime import datetime

from app.database import get_connection


class DuplicateNfcError(Exception):
    """当 NFC 编号已经存在时抛出的业务异常。"""


def validate_category_and_location(category, location):
    """校验分类和位置不能使用筛选下拉框的保留词。"""
    clean_category = category.strip()
    clean_location = location.strip()

    if clean_category == "全部分类":
        raise ValueError(
            "分类不能使用“全部分类”，请填写具体分类或保留“未分类”"
        )
    if clean_location == "全部位置":
        raise ValueError(
            "位置不能使用“全部位置”，请填写具体位置或保留“未设置”"
        )

    return clean_category, clean_location


def add_book(nfc_id, title, author, category, location, status="未借出"):
    """添加一本图书，并返回新记录的编号。"""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("书名不能为空")

    clean_nfc_id = nfc_id.strip() or None
    clean_category, clean_location = validate_category_and_location(
        category,
        location,
    )
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
                    clean_category,
                    clean_location,
                    status.strip() or "未借出",
                    created_at,
                ),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as error:
        if "books.nfc_id" in str(error):
            raise DuplicateNfcError("该 NFC 编号已存在，请更换后重试") from error
        raise


def get_books(keyword="", category="", location=""):
    """按关键词、分类和存放位置组合查询图书。"""
    clean_keyword = keyword.strip()
    clean_category = category.strip()
    clean_location = location.strip()

    conditions = []
    parameters = []

    if clean_keyword:
        search_value = f"%{clean_keyword}%"
        conditions.append("(title LIKE ? OR author LIKE ? OR nfc_id LIKE ?)")
        parameters.extend([search_value, search_value, search_value])

    if clean_category and clean_category != "全部分类":
        conditions.append("TRIM(category) = ?")
        parameters.append(clean_category)

    if clean_location and clean_location != "全部位置":
        conditions.append("TRIM(location) = ?")
        parameters.append(clean_location)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT id, nfc_id, title, author, category, location, status, created_at
            FROM books
            {where_clause}
            ORDER BY id DESC
            """,
            parameters,
        ).fetchall()

    return [dict(row) for row in rows]


def get_categories():
    """返回已使用且非空的分类列表。"""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT TRIM(category) AS value
            FROM books
            WHERE category IS NOT NULL
                AND TRIM(category) <> ''
                AND TRIM(category) <> '全部分类'
            ORDER BY value COLLATE NOCASE
            """
        ).fetchall()

    return [row["value"] for row in rows]


def get_locations():
    """返回已使用且非空的存放位置列表。"""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT TRIM(location) AS value
            FROM books
            WHERE location IS NOT NULL
                AND TRIM(location) <> ''
                AND TRIM(location) <> '全部位置'
            ORDER BY value COLLATE NOCASE
            """
        ).fetchall()

    return [row["value"] for row in rows]


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
    clean_category, clean_location = validate_category_and_location(
        category,
        location,
    )

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
                    clean_category,
                    clean_location,
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

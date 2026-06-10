import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent


def get_data_dir():
    """根据运行方式返回当前应使用的数据目录。"""
    if not getattr(sys, "frozen", False):
        return PROJECT_DIR / "data"

    exe_dir = Path(sys.executable).resolve().parent
    portable_data_dir = exe_dir / "data"
    if portable_data_dir.is_dir():
        return portable_data_dir

    local_app_data = os.environ.get(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local"),
    )
    return Path(local_app_data) / "BookManager"


def get_database_path():
    """返回当前运行模式对应的 SQLite 数据库路径。"""
    return get_data_dir() / "books.db"

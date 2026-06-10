import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.database import init_database
from app.ui.main_window import MainWindow


def load_styles(app):
    """读取 QSS 文件并应用到整个程序。"""
    style_path = Path(__file__).resolve().parent / "app" / "assets" / "styles.qss"
    app.setStyleSheet(style_path.read_text(encoding="utf-8"))


def main():
    """初始化数据库并启动桌面应用。"""
    init_database()

    app = QApplication(sys.argv)
    app.setApplicationName("个人图书管理系统")
    load_styles(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

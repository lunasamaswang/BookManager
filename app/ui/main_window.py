from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.bookbot_panel import BookBotPanel
from app.ui.dashboard_page import DashboardPage
from app.ui.library_page import LibraryPage


class MainWindow(QMainWindow):
    """应用主窗口，负责三栏布局和页面切换。"""

    NAV_ITEMS = [
        ("home", "首页"),
        ("library", "图书库"),
        ("reading", "阅读"),
        ("borrowing", "借阅"),
        ("find", "找书"),
        ("inventory", "盘点"),
        ("ai", "AI 助手"),
        ("smart_shelf", "智能书架"),
        ("settings", "设置"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BookManager 智能书房")
        self.resize(1440, 820)
        self.setMinimumSize(1180, 680)
        self.current_page_key = "home"
        self.nav_buttons = {}
        self.setup_ui()
        self.show_page("home")

    def setup_ui(self):
        """创建左侧导航、中间页面和右侧助手栏。"""
        root_widget = QWidget()
        root_widget.setObjectName("appRoot")
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.create_sidebar())

        self.page_stack = QStackedWidget()
        self.page_stack.setObjectName("pageStack")

        self.dashboard_page = DashboardPage()
        self.library_page = LibraryPage()
        self.page_stack.addWidget(self.dashboard_page)
        self.page_stack.addWidget(self.library_page)

        self.dashboard_page.search_requested.connect(self.open_library_search)
        self.library_page.books_changed.connect(self.dashboard_page.refresh_data)
        self.library_page.success_message.connect(self.show_success_message)

        root_layout.addWidget(self.page_stack, 1)
        root_layout.addWidget(BookBotPanel())
        self.setCentralWidget(root_widget)

        self.statusBar().setObjectName("appStatusBar")
        self.statusBar().setSizeGripEnabled(False)

    def create_sidebar(self):
        """创建应用品牌和九个导航入口。"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(208)

        brand_mark = QLabel("BM")
        brand_mark.setObjectName("brandMark")

        title = QLabel("BookManager")
        title.setObjectName("appTitle")

        subtitle = QLabel("你的智能书房")
        subtitle.setObjectName("appSubtitle")

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        brand_text_layout.addWidget(title)
        brand_text_layout.addWidget(subtitle)

        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.addWidget(brand_mark)
        brand_layout.addLayout(brand_text_layout)

        nav_label = QLabel("空间导航")
        nav_label.setObjectName("navSectionTitle")

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(5)
        for key, label in self.NAV_ITEMS:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, page_key=key: self.handle_navigation(page_key)
            )
            self.nav_group.addButton(button)
            self.nav_buttons[key] = button
            nav_layout.addWidget(button)

        footer = QLabel("BookManager v1.1.0\n本地数据 · 安心收藏")
        footer.setObjectName("sidebarFooter")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 22)
        layout.setSpacing(18)
        layout.addLayout(brand_layout)
        layout.addSpacing(10)
        layout.addWidget(nav_label)
        layout.addLayout(nav_layout)
        layout.addStretch()
        layout.addWidget(footer)
        return sidebar

    def handle_navigation(self, page_key):
        """切换可用页面，其他入口显示后续版本提示。"""
        if page_key in {"home", "library"}:
            self.show_page(page_key)
            return

        QMessageBox.information(
            self,
            "功能预告",
            "该功能将在后续版本开放。",
        )
        self.nav_buttons[self.current_page_key].setChecked(True)

    def show_page(self, page_key):
        """显示首页或图书库，并同步导航选中状态。"""
        self.current_page_key = page_key
        if page_key == "home":
            self.dashboard_page.refresh_data()
            self.page_stack.setCurrentWidget(self.dashboard_page)
        else:
            self.library_page.load_books()
            self.page_stack.setCurrentWidget(self.library_page)

        self.nav_buttons[page_key].setChecked(True)

    def open_library_search(self, keyword):
        """从首页快速搜索跳转到图书库。"""
        self.show_page("library")
        self.library_page.set_search_keyword(keyword)

    def show_success_message(self, message):
        """在窗口底部短暂显示操作成功提示。"""
        self.statusBar().showMessage(message, 3500)

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.quotes import get_daily_quote
from app.services.book_service import get_book_statistics, get_recent_books


class DashboardPage(QWidget):
    """首页仪表盘，展示藏书概览和常用入口。"""

    search_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardPage")
        self.stat_values = {}
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """创建首页仪表盘布局。"""
        scroll_area = QScrollArea()
        scroll_area.setObjectName("dashboardScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("dashboardContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(18)

        welcome = QLabel("欢迎回来，今天想读点什么？")
        welcome.setObjectName("dashboardWelcome")
        welcome_subtitle = QLabel("这里是你的智能书房，一眼掌握藏书与最近动态。")
        welcome_subtitle.setObjectName("pageSubtitle")

        layout.addWidget(welcome)
        layout.addWidget(welcome_subtitle)
        layout.addWidget(self.create_statistics_section())
        layout.addWidget(self.create_quick_search_card())

        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(18)
        lower_layout.addWidget(self.create_recent_books_card(), 3)
        lower_layout.addWidget(self.create_side_cards(), 2)
        layout.addLayout(lower_layout)
        layout.addStretch()

        scroll_area.setWidget(content)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll_area)

    def create_statistics_section(self):
        """创建藏书统计卡片区域。"""
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        cards = [
            ("total", "总藏书", "真实藏书数量"),
            ("reading", "在读", "后续版本开放"),
            ("finished", "已读", "后续版本开放"),
            ("borrowed", "已借出", "当前借出状态"),
            ("pending", "待确认", "后续版本开放"),
        ]
        for index, (key, title, description) in enumerate(cards):
            card = QFrame()
            card.setObjectName("statCard")

            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
            value_label = QLabel("0")
            value_label.setObjectName("statValue")
            description_label = QLabel(description)
            description_label.setObjectName("statDescription")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 15, 16, 15)
            card_layout.setSpacing(5)
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(description_label)

            self.stat_values[key] = value_label
            grid.addWidget(card, 0, index)

        return container

    def create_quick_search_card(self):
        """创建可以跳转到图书库的快速找书卡片。"""
        card = QFrame()
        card.setObjectName("dashboardCard")

        title = QLabel("快速找书")
        title.setObjectName("cardTitle")
        description = QLabel("输入书名、作者或 NFC 编号，直接前往图书库查看。")
        description.setObjectName("cardDescription")

        self.quick_search_input = QLineEdit()
        self.quick_search_input.setObjectName("dashboardSearchInput")
        self.quick_search_input.setPlaceholderText("今天想找哪一本书？")
        self.quick_search_input.returnPressed.connect(self.submit_search)

        search_button = QPushButton("开始查找")
        search_button.setObjectName("primaryButton")
        search_button.clicked.connect(self.submit_search)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.addWidget(self.quick_search_input, 1)
        search_layout.addWidget(search_button)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(9)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(search_layout)
        return card

    def create_recent_books_card(self):
        """创建最近添加图书列表。"""
        card = QFrame()
        card.setObjectName("dashboardCard")

        title = QLabel("最近添加")
        title.setObjectName("cardTitle")
        description = QLabel("按添加顺序展示最近 5 本图书。")
        description.setObjectName("cardDescription")

        self.recent_books_layout = QVBoxLayout()
        self.recent_books_layout.setSpacing(0)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(self.recent_books_layout)
        layout.addStretch()
        return card

    def create_side_cards(self):
        """创建今日待处理和每日名言卡片。"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        pending_card = QFrame()
        pending_card.setObjectName("dashboardCard")
        pending_title = QLabel("今日待处理")
        pending_title.setObjectName("cardTitle")
        pending_text = QLabel("今天没有待处理事项。\n借阅与盘点提醒将在后续版本开放。")
        pending_text.setObjectName("cardDescription")
        pending_text.setWordWrap(True)
        pending_layout = QVBoxLayout(pending_card)
        pending_layout.setContentsMargins(20, 18, 20, 20)
        pending_layout.setSpacing(10)
        pending_layout.addWidget(pending_title)
        pending_layout.addWidget(pending_text)
        pending_layout.addStretch()

        quote_card = QFrame()
        quote_card.setObjectName("quoteCard")
        quote_title = QLabel("每日书中名言")
        quote_title.setObjectName("quoteTitle")
        quote, author = get_daily_quote()
        quote_text = QLabel(f"“{quote}”")
        quote_text.setObjectName("quoteText")
        quote_text.setWordWrap(True)
        quote_author = QLabel(f"— {author}")
        quote_author.setObjectName("quoteAuthor")
        quote_author.setAlignment(Qt.AlignmentFlag.AlignRight)
        quote_layout = QVBoxLayout(quote_card)
        quote_layout.setContentsMargins(20, 18, 20, 20)
        quote_layout.setSpacing(12)
        quote_layout.addWidget(quote_title)
        quote_layout.addWidget(quote_text)
        quote_layout.addWidget(quote_author)
        quote_layout.addStretch()

        layout.addWidget(pending_card, 1)
        layout.addWidget(quote_card, 1)
        return container

    def submit_search(self):
        """提交快速搜索并交由主窗口切换页面。"""
        self.search_requested.emit(self.quick_search_input.text().strip())

    def refresh_data(self):
        """刷新统计数字和最近添加列表。"""
        statistics = get_book_statistics()
        self.stat_values["total"].setText(str(statistics["total"]))
        self.stat_values["borrowed"].setText(str(statistics["borrowed"]))
        self.stat_values["reading"].setText("0")
        self.stat_values["finished"].setText("0")
        self.stat_values["pending"].setText("0")
        self.refresh_recent_books(get_recent_books(5))

    def refresh_recent_books(self, books):
        """重新生成最近添加图书列表。"""
        while self.recent_books_layout.count():
            item = self.recent_books_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not books:
            empty_label = QLabel("还没有图书，去图书库添加第一本吧。")
            empty_label.setObjectName("recentEmpty")
            self.recent_books_layout.addWidget(empty_label)
            return

        for book in books:
            row = QFrame()
            row.setObjectName("recentBookRow")

            full_title = book.get("title") or "未命名图书"
            full_author = book.get("author") or "未知作者"

            title = QLabel(self.shorten_text(full_title, 26))
            title.setObjectName("recentBookTitle")
            title.setMinimumWidth(0)
            title.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Preferred,
            )
            title.setToolTip(full_title)
            author = QLabel(self.shorten_text(full_author, 20))
            author.setObjectName("recentBookMeta")
            author.setMinimumWidth(0)
            author.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Preferred,
            )
            author.setToolTip(full_author)
            status = QLabel(book.get("status") or "未借出")
            status.setObjectName(
                "recentAvailableStatus"
                if (book.get("status") or "未借出") == "未借出"
                else "recentBorrowedStatus"
            )

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            text_layout.addWidget(title)
            text_layout.addWidget(author)

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 10, 0, 10)
            row_layout.addLayout(text_layout, 1)
            row_layout.addWidget(status)
            self.recent_books_layout.addWidget(row)

    @staticmethod
    def shorten_text(text, max_length):
        """截短列表中的长文本，完整内容仍可通过提示查看。"""
        clean_text = str(text)
        if len(clean_text) <= max_length:
            return clean_text
        return clean_text[: max_length - 1] + "…"

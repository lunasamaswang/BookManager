import sys
from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
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

from app.path_utils import get_data_dir
from app.services.book_service import get_book_statistics, get_recent_books


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


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
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(14)

        layout.addWidget(self.create_welcome_banner())
        layout.addWidget(self.create_statistics_section())
        layout.addWidget(self.create_quick_search_card())

        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(14)

        side_cards_layout = QVBoxLayout()
        side_cards_layout.setSpacing(14)
        side_cards_layout.addWidget(self.create_task_card())
        side_cards_layout.addWidget(self.create_room_status_card())

        lower_layout.addWidget(self.create_recent_books_card(), 5)
        lower_layout.addLayout(side_cards_layout, 4)

        layout.addLayout(lower_layout)
        layout.addStretch()

        scroll_area.setWidget(content)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll_area)

    def create_welcome_banner(self):
        """创建带有书房氛围装饰的欢迎横幅。"""
        banner = QFrame()
        banner.setObjectName("welcomeSection")

        welcome = QLabel("欢迎回到你的书房")
        welcome.setObjectName("dashboardWelcome")
        welcome.setWordWrap(True)
        welcome.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        welcome_subtitle = QLabel("让藏书各归其位，也让每一次阅读都有温度。")
        welcome_subtitle.setObjectName("dashboardSubtitle")
        welcome_subtitle.setWordWrap(True)
        welcome_subtitle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        welcome_hint = QLabel("BOOKMANAGER · YOUR READING SPACE")
        welcome_hint.setObjectName("welcomeHint")
        welcome_hint.setMinimumWidth(0)
        welcome_hint.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        text_layout.addStretch()
        text_layout.addWidget(welcome_hint)
        text_layout.addWidget(welcome)
        text_layout.addWidget(welcome_subtitle)
        text_layout.addStretch()

        illustration = QLabel()
        illustration.setObjectName("studyBannerImage")
        illustration.setFixedSize(320, 136)
        illustration.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        pixmap = QPixmap(str(ASSETS_DIR / "study_banner.png"))
        illustration.setPixmap(
            pixmap.scaled(
                illustration.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(24, 12, 16, 12)
        layout.setSpacing(18)
        layout.addLayout(text_layout, 1)
        layout.addWidget(illustration)
        return banner

    def create_statistics_section(self):
        """创建一张总藏书主卡和四张辅助统计卡。"""
        container = QWidget()

        total_card = QFrame()
        total_card.setObjectName("statCardTotal")
        total_icon = QLabel("藏")
        total_icon.setObjectName("statIconTotal")
        total_title = QLabel("总藏书")
        total_title.setObjectName("totalStatTitle")
        total_value = QLabel("0")
        total_value.setObjectName("totalStatValue")
        total_description = QLabel("你的私人书房正在慢慢丰盛起来")
        total_description.setObjectName("totalStatDescription")
        total_description.setWordWrap(True)
        total_badge = QLabel("实时统计")
        total_badge.setObjectName("totalStatBadge")

        total_header = QHBoxLayout()
        total_header.addWidget(total_icon)
        total_header.addStretch()
        total_header.addWidget(total_badge)

        total_layout = QVBoxLayout(total_card)
        total_layout.setContentsMargins(22, 20, 22, 20)
        total_layout.setSpacing(7)
        total_layout.addLayout(total_header)
        total_layout.addWidget(total_title)
        total_layout.addWidget(total_value)
        total_layout.addWidget(total_description)
        self.stat_values["total"] = total_value

        small_grid = QGridLayout()
        small_grid.setContentsMargins(0, 0, 0, 0)
        small_grid.setHorizontalSpacing(12)
        small_grid.setVerticalSpacing(12)

        cards = [
            ("reading", "读", "在读", "后续版本开放", "statCardReading", "statIconReading"),
            ("finished", "阅", "已读", "后续版本开放", "statCardFinished", "statIconFinished"),
            ("borrowed", "借", "已借出", "当前借出状态", "statCardBorrowed", "statIconBorrowed"),
            ("pending", "待", "待确认", "后续版本开放", "statCardPending", "statIconPending"),
        ]
        for index, (key, icon_text, title, description, card_name, icon_name) in enumerate(cards):
            card = self.create_small_stat_card(
                key,
                icon_text,
                title,
                description,
                card_name,
                icon_name,
            )
            small_grid.addWidget(card, index // 2, index % 2)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(total_card, 5)
        layout.addLayout(small_grid, 6)

        return container

    def create_small_stat_card(
        self,
        key,
        icon_text,
        title,
        description,
        card_name,
        icon_name,
    ):
        """创建统计区中的辅助小卡片。"""
        card = QFrame()
        card.setObjectName(card_name)

        icon_label = QLabel(icon_text)
        icon_label.setObjectName(icon_name)
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        value_label = QLabel("0")
        value_label.setObjectName("statValue")
        description_label = QLabel(description)
        description_label.setObjectName("statDescription")
        description_label.setWordWrap(True)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addWidget(description_label)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(11)
        card_layout.addWidget(icon_label)
        card_layout.addLayout(text_layout, 1)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.stat_values[key] = value_label
        return card

    def create_quick_search_card(self):
        """创建可以跳转到图书库的快速找书卡片。"""
        card = QFrame()
        card.setObjectName("quickSearchCard")

        title = QLabel("今天想找哪本书？")
        title.setObjectName("searchHeroTitle")
        title.setWordWrap(True)
        description = QLabel("在你的私人书房中快速定位藏书")
        description.setObjectName("searchHeroDescription")
        description.setWordWrap(True)

        self.quick_search_input = QLineEdit()
        self.quick_search_input.setObjectName("dashboardSearchInput")
        self.quick_search_input.setPlaceholderText("今天想找哪一本书？")
        self.quick_search_input.returnPressed.connect(self.submit_search)

        search_button = QPushButton("开始查找")
        search_button.setObjectName("dashboardSearchButton")
        search_button.setMinimumWidth(108)
        search_button.clicked.connect(self.submit_search)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.addWidget(self.quick_search_input, 1)
        search_layout.addWidget(search_button)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(7)
        filters_label = QLabel("快捷筛选")
        filters_label.setObjectName("quickFilterLabel")
        filters_layout.addWidget(filters_label)
        for label, placeholder in [
            ("按书名", "输入书名进行查找"),
            ("按作者", "输入作者姓名进行查找"),
            ("按 NFC", "输入 NFC 编号进行查找"),
        ]:
            button = QPushButton(label)
            button.setObjectName("quickFilterButton")
            button.setMinimumWidth(68)
            button.clicked.connect(
                lambda checked=False, text=placeholder: self.focus_quick_search(text)
            )
            filters_layout.addWidget(button)
        filters_layout.addStretch()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 15, 18, 16)
        layout.setSpacing(7)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(search_layout)
        layout.addLayout(filters_layout)
        return card

    def create_recent_books_card(self):
        """创建最近添加图书列表。"""
        card = QFrame()
        card.setObjectName("recentBooksCard")

        title = QLabel("最近添加")
        title.setObjectName("cardTitle")
        description = QLabel("按添加顺序展示最近 5 本图书。")
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        self.recent_books_layout = QVBoxLayout()
        self.recent_books_layout.setSpacing(0)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 15, 16, 16)
        layout.setSpacing(7)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(self.recent_books_layout)
        layout.addStretch()
        return card

    def create_task_card(self):
        """创建由多条任务项组成的今日待处理卡片。"""
        pending_card = QFrame()
        pending_card.setObjectName("taskCard")
        pending_title = QLabel("今日待处理")
        pending_title.setObjectName("cardTitle")
        pending_label = QLabel("TODAY")
        pending_label.setObjectName("taskBadge")

        title_layout = QHBoxLayout()
        title_layout.addWidget(pending_title)
        title_layout.addStretch()
        title_layout.addWidget(pending_label)

        pending_layout = QVBoxLayout(pending_card)
        pending_layout.setContentsMargins(15, 15, 15, 15)
        pending_layout.setSpacing(5)
        pending_layout.addLayout(title_layout)
        pending_layout.addWidget(
            self.create_task_item(
                "taskMarkerGold",
                "确认新入库图书",
                "待确认功能将在后续版本开放",
            )
        )
        pending_layout.addWidget(
            self.create_task_item(
                "taskMarkerGreen",
                "整理阅读计划",
                "阅读计划功能将在后续版本开放",
            )
        )
        pending_layout.addWidget(
            self.create_task_item(
                "taskMarkerPurple",
                "检查书架空间",
                "位置盘点功能将在后续版本开放",
            )
        )
        return pending_card

    def create_task_item(self, marker_name, title_text, description_text):
        """创建一条带颜色标识和占位按钮的任务项。"""
        item = QFrame()
        item.setObjectName("taskItem")

        marker = QFrame()
        marker.setObjectName(marker_name)
        marker.setFixedWidth(4)

        title = QLabel(title_text)
        title.setObjectName("taskItemTitle")
        title.setWordWrap(True)
        description = QLabel(description_text)
        description.setObjectName("taskItemDescription")
        description.setWordWrap(True)
        description.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(title)
        text_layout.addWidget(description)

        action = QPushButton("查看")
        action.setObjectName("taskActionButton")
        action.setMinimumWidth(52)
        action.clicked.connect(self.show_placeholder)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(8)
        layout.addWidget(marker)
        layout.addLayout(text_layout, 1)
        layout.addWidget(action)
        return item

    def create_room_status_card(self):
        """创建书房运行状态和占位信息卡片。"""
        card = QFrame()
        card.setObjectName("roomStatusCard")

        title = QLabel("书房状态")
        title.setObjectName("cardTitle")
        status_badge = QLabel("●  本地数据正常")
        status_badge.setObjectName("roomOnlineStatus")
        status_badge.setWordWrap(True)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        layout.addLayout(header_layout)
        layout.addWidget(self.create_status_row("运行模式", self.get_runtime_mode_label()))
        layout.addWidget(self.create_status_row("书架空间", "占位 · 后续版本开放"))
        layout.addWidget(self.create_status_row("分类数量", "占位 · 未统计"))
        layout.addWidget(self.create_status_row("标签数量", "占位 · 未统计"))
        return card

    @staticmethod
    def create_status_row(label_text, value_text):
        """创建一条书房状态信息。"""
        row = QFrame()
        row.setObjectName("roomStatusRow")
        label = QLabel(label_text)
        label.setObjectName("roomStatusLabel")
        value = QLabel(value_text)
        value.setObjectName("roomStatusValue")
        value.setWordWrap(True)
        value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        value.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.addWidget(label)
        layout.addWidget(value, 1)
        return row

    @staticmethod
    def get_runtime_mode_label():
        """根据现有路径规则显示当前运行模式，不改变路径逻辑。"""
        if not getattr(sys, "frozen", False):
            return "源码模式"

        exe_data_dir = Path(sys.executable).resolve().parent / "data"
        if get_data_dir() == exe_data_dir:
            return "便携模式"
        return "默认 AppData 模式"

    def focus_quick_search(self, placeholder):
        """切换搜索提示并聚焦输入框，不改变原有搜索逻辑。"""
        self.quick_search_input.setPlaceholderText(placeholder)
        self.quick_search_input.setFocus()

    def show_placeholder(self):
        """显示尚未开放功能的统一提示。"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "功能预告",
            "该功能将在后续版本开放。",
        )

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
            row_layout.setContentsMargins(0, 7, 0, 7)
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

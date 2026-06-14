from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from app.quotes import get_daily_quote


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class BookBotPanel(QFrame):
    """右侧 BookBot 助手占位栏。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bookbotPanel")
        self.setFixedWidth(296)
        self.setup_ui()

    def setup_ui(self):
        """创建助手标题、欢迎信息和占位入口。"""
        avatar = QLabel()
        avatar.setObjectName("bookbotAvatar")
        avatar.setFixedSize(64, 64)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_pixmap = QPixmap(str(ASSETS_DIR / "bookbot_avatar.png"))
        avatar.setPixmap(
            avatar_pixmap.scaled(
                avatar.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        online_dot = QLabel("●")
        online_dot.setObjectName("bookbotOnlineDot")
        online_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("BookBot")
        title.setObjectName("bookbotTitle")
        title.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        subtitle = QLabel("智能书库助手 · 在线")
        subtitle.setObjectName("bookbotSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        header = QFrame()
        header.setObjectName("bookbotHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(11)
        header_layout.addWidget(avatar)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout, 1)
        header_layout.addWidget(online_dot)

        welcome_card = QFrame()
        welcome_card.setObjectName("bookbotSpeechBubble")
        welcome_card.setMinimumHeight(82)
        welcome_title = QLabel("你好呀")
        welcome_title.setObjectName("bookbotBubbleTitle")
        welcome_text = QLabel(
            "我会陪你照看每一本书。今天也一起整理书房吧。"
        )
        welcome_text.setObjectName("bookbotBubbleText")
        welcome_text.setWordWrap(True)
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(16, 13, 16, 14)
        welcome_layout.setSpacing(5)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_text)

        reminder_card = QFrame()
        reminder_card.setObjectName("bookbotReminderCard")
        reminder_card.setMinimumHeight(92)
        reminder_title = QLabel("今日提醒")
        reminder_title.setObjectName("bookbotCardTitle")
        reminder_text = QLabel("暂无提醒\n更多智能提醒将在后续版本开放。")
        reminder_text.setObjectName("bookbotText")
        reminder_text.setWordWrap(True)
        reminder_layout = QVBoxLayout(reminder_card)
        reminder_layout.setContentsMargins(16, 16, 16, 16)
        reminder_layout.setSpacing(8)
        reminder_layout.addWidget(reminder_title)
        reminder_layout.addWidget(reminder_text)

        action_label = QLabel("我可以帮助你")
        action_label.setObjectName("bookbotSectionTitle")

        actions_card = QFrame()
        actions_card.setObjectName("bookbotActions")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        for button_text in ["今日推荐", "AI 锐评", "问问 BookBot"]:
            button = QPushButton(button_text)
            button.setObjectName("bookbotActionButton")
            button.setMinimumHeight(42)
            button.clicked.connect(self.show_placeholder)
            actions_layout.addWidget(button)

        quote, author = get_daily_quote()
        quote_card = QFrame()
        quote_card.setObjectName("bookbotQuoteCard")
        quote_card.setMinimumHeight(150)

        bookmark_ribbon = QLabel("今日书签")
        bookmark_ribbon.setObjectName("bookmarkRibbon")
        quote_mark = QLabel("“")
        quote_mark.setObjectName("bookbotQuoteMark")
        quote_text = QLabel(quote)
        quote_text.setObjectName("bookbotQuoteText")
        quote_text.setWordWrap(True)
        quote_author = QLabel(f"— {author}")
        quote_author.setObjectName("bookbotQuoteAuthor")
        quote_author.setWordWrap(True)
        quote_author.setAlignment(Qt.AlignmentFlag.AlignRight)

        quote_layout = QVBoxLayout(quote_card)
        quote_layout.setContentsMargins(16, 13, 16, 15)
        quote_layout.setSpacing(5)
        quote_layout.addWidget(bookmark_ribbon)
        quote_layout.addWidget(quote_mark)
        quote_layout.addWidget(quote_text)
        quote_layout.addWidget(quote_author)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 24)
        layout.setSpacing(14)
        layout.addWidget(header)
        layout.addSpacing(4)
        layout.addWidget(welcome_card)
        layout.addWidget(reminder_card)
        layout.addSpacing(4)
        layout.addWidget(action_label)
        layout.addWidget(actions_card)
        layout.addStretch()
        layout.addWidget(quote_card)

    def show_placeholder(self):
        """提示用户当前助手功能仍处于占位阶段。"""
        QMessageBox.information(
            self,
            "功能预告",
            "该功能将在后续版本开放。",
        )

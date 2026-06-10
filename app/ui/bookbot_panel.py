from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class BookBotPanel(QFrame):
    """右侧 BookBot 助手占位栏。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bookbotPanel")
        self.setFixedWidth(280)
        self.setup_ui()

    def setup_ui(self):
        """创建助手标题、欢迎信息和占位入口。"""
        badge = QLabel("BOOKBOT")
        badge.setObjectName("bookbotBadge")

        title = QLabel("智能书库助手")
        title.setObjectName("bookbotTitle")

        welcome_card = QFrame()
        welcome_card.setObjectName("bookbotWelcomeCard")
        welcome_title = QLabel("你好，我是 BookBot")
        welcome_title.setObjectName("bookbotCardTitle")
        welcome_text = QLabel(
            "我会逐步帮你发现藏书、整理阅读计划，并提供更聪明的书库建议。"
        )
        welcome_text.setObjectName("bookbotText")
        welcome_text.setWordWrap(True)
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(16, 16, 16, 16)
        welcome_layout.setSpacing(8)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_text)

        reminder_card = QFrame()
        reminder_card.setObjectName("bookbotReminderCard")
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 24)
        layout.setSpacing(14)
        layout.addWidget(badge)
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(welcome_card)
        layout.addWidget(reminder_card)
        layout.addSpacing(4)

        for button_text in ["今日推荐", "AI 锐评", "问问 BookBot"]:
            button = QPushButton(button_text)
            button.setObjectName("bookbotActionButton")
            button.clicked.connect(self.show_placeholder)
            layout.addWidget(button)

        layout.addStretch()

    def show_placeholder(self):
        """提示用户当前助手功能仍处于占位阶段。"""
        QMessageBox.information(
            self,
            "功能预告",
            "该功能将在后续版本开放。",
        )

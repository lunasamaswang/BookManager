from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.viewmodels.book_view_model import BookViewModel


class BookDetailDialog(QDialog):
    """按结构化区块只读展示单本图书信息。"""

    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.view_model = BookViewModel.from_book(book)
        self.edit_requested = False
        self.setObjectName("bookDetailDialog")
        self.setWindowTitle("图书详情")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setup_ui()

    def setup_ui(self):
        """创建结构化详情区块和底部操作按钮。"""
        title = QLabel(self.view_model.title)
        title.setObjectName("detailBookTitle")
        title.setWordWrap(True)

        subtitle = QLabel("图书详情")
        subtitle.setObjectName("detailSubtitle")

        status = QLabel(self.view_model.status_text)
        status.setObjectName(self.view_model.status_style)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)

        title_text_layout = QVBoxLayout()
        title_text_layout.setContentsMargins(0, 0, 0, 0)
        title_text_layout.setSpacing(4)
        title_text_layout.addWidget(subtitle)
        title_text_layout.addWidget(title)

        title_layout.addLayout(title_text_layout, 1)
        title_layout.addWidget(status, 0, Qt.AlignmentFlag.AlignTop)

        separator = QFrame()
        separator.setObjectName("dialogSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)

        edit_button = QPushButton("编辑图书")
        edit_button.setObjectName("primaryButton")
        edit_button.clicked.connect(self.request_edit)

        close_button = QPushButton("关闭")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.reject)
        close_button.setDefault(True)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addWidget(edit_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(20)
        layout.addLayout(title_layout)
        self.render_sections(layout)
        layout.addWidget(separator)
        layout.addLayout(button_layout)

    def render_sections(self, parent_layout):
        """按照 ViewModel 提供的顺序渲染全部详情区块。"""
        for section in self.view_model.sections:
            parent_layout.addWidget(self.render_section(section))

    def render_section(self, section_data):
        """渲染一个详情区块。"""
        section = QFrame()
        section.setObjectName("detailSection")

        title = QLabel(section_data.title)
        title.setObjectName("detailSectionTitle")

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)

        for row, field in enumerate(section_data.fields):
            label, value = self.render_field(field)
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            grid.setColumnStretch(1, 1)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(grid)
        return section

    def render_field(self, field):
        """渲染一个标签和值组成的详情字段。"""
        label = QLabel(field.label)
        label.setObjectName("detailFieldLabel")
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        value = QLabel(field.value)
        value.setObjectName("detailFieldValue")
        value.setWordWrap(True)
        value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        return label, value

    def request_edit(self):
        """关闭详情弹窗，并记录用户希望继续编辑。"""
        self.edit_requested = True
        self.accept()

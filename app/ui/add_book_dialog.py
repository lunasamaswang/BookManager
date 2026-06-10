from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.services.book_service import DuplicateNfcError, add_book, update_book


class AddBookDialog(QDialog):
    """用于添加或编辑图书信息的弹窗。"""

    def __init__(self, parent=None, book=None):
        super().__init__(parent)
        self.book = book
        self.setObjectName("bookDialog")
        self.setWindowTitle("编辑图书" if book else "添加图书")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setup_ui()
        if self.book:
            self.fill_form()

    def setup_ui(self):
        """创建清晰、紧凑的图书信息表单。"""
        dialog_title = QLabel("编辑图书" if self.book else "添加图书")
        dialog_title.setObjectName("dialogTitle")

        dialog_description = QLabel(
            "修改图书的基本信息。" if self.book else "填写图书的基本信息。"
        )
        dialog_description.setObjectName("dialogDescription")

        self.nfc_input = QLineEdit()
        self.nfc_input.setPlaceholderText("例如：NFC-0001")

        nfc_helper = QLabel("可留空；填写后不能与其他图书重复。")
        nfc_helper.setObjectName("fieldHelper")

        nfc_container = QWidget()
        nfc_layout = QVBoxLayout(nfc_container)
        nfc_layout.setContentsMargins(0, 0, 0, 0)
        nfc_layout.setSpacing(5)
        nfc_layout.addWidget(self.nfc_input)
        nfc_layout.addWidget(nfc_helper)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入书名")

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("请输入作者")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("例如：文学、计算机")

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("例如：书房 A1")

        self.status_input = QComboBox()
        self.status_input.addItems(["未借出", "已借出"])

        form_layout = QFormLayout()
        form_layout.setObjectName("bookForm")
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(14)
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.addRow("NFC 编号", nfc_container)
        form_layout.addRow(self.create_required_label("书名"), self.title_input)
        form_layout.addRow("作者", self.author_input)
        form_layout.addRow("分类", self.category_input)
        form_layout.addRow("存放位置", self.location_input)
        form_layout.addRow("状态", self.status_input)

        separator = QFrame()
        separator.setObjectName("dialogSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        save_button.setText("保存")
        save_button.setObjectName("primaryButton")
        cancel_button.setText("取消")
        cancel_button.setObjectName("secondaryButton")
        buttons.accepted.connect(self.save_book)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(18)
        layout.addWidget(dialog_title)
        layout.addWidget(dialog_description)
        layout.addSpacing(2)
        layout.addLayout(form_layout)
        layout.addWidget(separator)
        layout.addWidget(buttons)

        self.setTabOrder(self.nfc_input, self.title_input)
        self.setTabOrder(self.title_input, self.author_input)
        self.setTabOrder(self.author_input, self.category_input)
        self.setTabOrder(self.category_input, self.location_input)
        self.setTabOrder(self.location_input, self.status_input)
        self.title_input.setFocus()

    def create_required_label(self, text):
        """创建带红色星号的必填字段标签。"""
        label = QLabel(f"{text} <span style='color:#D92D20'>*</span>")
        label.setTextFormat(Qt.TextFormat.RichText)
        return label

    def fill_form(self):
        """把已有图书信息填入表单，供用户编辑。"""
        self.nfc_input.setText(self.book.get("nfc_id") or "")
        self.title_input.setText(self.book.get("title") or "")
        self.author_input.setText(self.book.get("author") or "")
        self.category_input.setText(self.book.get("category") or "")
        self.location_input.setText(self.book.get("location") or "")

        status = self.book.get("status") or "未借出"
        status_index = self.status_input.findText(status)
        if status_index >= 0:
            self.status_input.setCurrentIndex(status_index)

    def save_book(self):
        """校验表单并把图书保存到数据库。"""
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "无法保存", "书名不能为空，请填写后再保存。")
            self.title_input.setFocus()
            return

        try:
            book_data = {
                "nfc_id": self.nfc_input.text(),
                "title": self.title_input.text(),
                "author": self.author_input.text(),
                "category": self.category_input.text(),
                "location": self.location_input.text(),
                "status": self.status_input.currentText(),
            }

            if self.book:
                updated = update_book(self.book["id"], **book_data)
                if not updated:
                    QMessageBox.warning(self, "无法保存", "这本图书已不存在。")
                    self.reject()
                    return
            else:
                add_book(**book_data)
        except DuplicateNfcError as error:
            QMessageBox.warning(self, "无法保存", str(error))
            self.nfc_input.setFocus()
            self.nfc_input.selectAll()
            return
        except Exception as error:
            QMessageBox.critical(self, "保存失败", f"保存图书时发生错误：\n{error}")
            return

        self.accept()

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

from app.services.book_service import (
    DuplicateNfcError,
    add_book,
    get_categories,
    get_locations,
    update_book,
)


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

        self.category_input = self.create_editable_combo(
            get_categories(),
            "例如：文学、计算机",
        )

        self.location_input = self.create_editable_combo(
            get_locations(),
            "例如：书房 A1",
        )

        if not self.book:
            self.set_combo_value(self.category_input, "未分类")
            self.set_combo_value(self.location_input, "未设置")

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

    def create_editable_combo(self, values, placeholder):
        """创建可选择已有值、也可以输入新值的下拉框。"""
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.addItems(values)
        combo.lineEdit().setPlaceholderText(placeholder)
        return combo

    def set_combo_value(self, combo, value):
        """设置下拉框当前值，并保留不在选项中的历史值。"""
        if value and combo.findText(value) < 0:
            combo.addItem(value)
        combo.setCurrentText(value)

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
        self.set_combo_value(
            self.category_input,
            self.book.get("category") or "",
        )
        self.set_combo_value(
            self.location_input,
            self.book.get("location") or "",
        )

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

        category = self.category_input.currentText().strip()
        if category == "全部分类":
            QMessageBox.warning(
                self,
                "无法保存",
                "分类不能使用“全部分类”，请填写具体分类或保留“未分类”。",
            )
            self.category_input.setFocus()
            self.category_input.lineEdit().selectAll()
            return

        location = self.location_input.currentText().strip()
        if location == "全部位置":
            QMessageBox.warning(
                self,
                "无法保存",
                "位置不能使用“全部位置”，请填写具体位置或保留“未设置”。",
            )
            self.location_input.setFocus()
            self.location_input.lineEdit().selectAll()
            return

        try:
            book_data = {
                "nfc_id": self.nfc_input.text(),
                "title": self.title_input.text(),
                "author": self.author_input.text(),
                "category": category,
                "location": location,
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

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.book_service import delete_book, get_book, get_books
from app.services.import_service import ExcelImportError, import_books_from_excel
from app.ui.add_book_dialog import AddBookDialog


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class MainWindow(QMainWindow):
    """应用主窗口，显示导航栏、搜索区和图书列表。"""

    TABLE_COLUMNS = [
        ("id", "编号"),
        ("nfc_id", "NFC 编号"),
        ("title", "书名"),
        ("author", "作者"),
        ("category", "分类"),
        ("location", "存放位置"),
        ("status", "状态"),
        ("created_at", "添加时间"),
        ("actions", "操作"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("个人图书管理系统")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        """创建主窗口中的导航栏、工具栏和表格。"""
        root_widget = QWidget()
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.create_sidebar())
        root_layout.addWidget(self.create_content_area(), 1)
        self.setCentralWidget(root_widget)

        self.statusBar().setObjectName("appStatusBar")
        self.statusBar().setSizeGripEnabled(False)

    def create_sidebar(self):
        """创建左侧导航栏。"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(208)

        title = QLabel("我的书库")
        title.setObjectName("appTitle")

        subtitle = QLabel("个人藏书管理")
        subtitle.setObjectName("appSubtitle")

        nav_button = QPushButton("  图书管理")
        nav_button.setObjectName("navButton")
        nav_button.setIcon(QIcon(str(ASSETS_DIR / "book.svg")))
        nav_button.setIconSize(QSize(18, 18))
        nav_button.setCheckable(True)
        nav_button.setChecked(True)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 28, 20, 24)
        layout.setSpacing(28)
        layout.addLayout(brand_layout)
        layout.addWidget(nav_button)
        layout.addStretch()
        return sidebar

    def create_content_area(self):
        """创建右侧图书管理页面。"""
        content = QFrame()
        content.setObjectName("contentArea")

        page_title = QLabel("图书管理")
        page_title.setObjectName("pageTitle")

        self.book_count_label = QLabel("共 0 本图书")
        self.book_count_label.setObjectName("pageSubtitle")

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(3)
        title_text_layout.addWidget(page_title)
        title_text_layout.addWidget(self.book_count_label)

        add_button = QPushButton("添加图书")
        add_button.setObjectName("primaryButton")
        add_button.setToolTip("添加一本新图书")
        add_button.clicked.connect(self.open_add_dialog)

        self.import_button = QPushButton("导入 Excel")
        self.import_button.setObjectName("secondaryButton")
        self.import_button.setToolTip("从 Excel 文件批量导入图书")
        self.import_button.clicked.connect(self.open_excel_import)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()
        title_layout.addWidget(self.import_button)
        title_layout.addWidget(add_button)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("搜索书名、作者或 NFC 编号")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(320)
        self.search_input.setMaximumWidth(420)
        self.search_input.addAction(
            QIcon(str(ASSETS_DIR / "search.svg")),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_input.textChanged.connect(self.load_books)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        card_layout = QVBoxLayout(table_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.table_stack = QStackedLayout()
        self.table_stack.setContentsMargins(0, 0, 0, 0)
        self.book_table = self.create_book_table()
        self.empty_state = self.create_empty_state()
        self.table_stack.addWidget(self.book_table)
        self.table_stack.addWidget(self.empty_state)
        card_layout.addLayout(self.table_stack)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(16)
        layout.addLayout(title_layout)
        layout.addLayout(search_layout)
        layout.addWidget(table_card, 1)
        return content

    def create_book_table(self):
        """创建并配置图书表格。"""
        table = QTableWidget()
        table.setObjectName("bookTable")
        table.setColumnCount(len(self.TABLE_COLUMNS))
        table.setHorizontalHeaderLabels(
            [column_title for _, column_title in self.TABLE_COLUMNS]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(48)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setMinimumSectionSize(48)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        table.setColumnWidth(0, 52)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(3, 90)
        table.setColumnWidth(4, 76)
        table.setColumnWidth(5, 90)
        table.setColumnWidth(6, 82)
        table.setColumnWidth(7, 120)
        table.setColumnWidth(8, 128)
        return table

    def create_empty_state(self):
        """创建无数据和无搜索结果时显示的提示区域。"""
        widget = QWidget()
        widget.setObjectName("emptyState")

        self.empty_title = QLabel("还没有图书")
        self.empty_title.setObjectName("emptyTitle")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.empty_description = QLabel("点击“添加图书”，开始整理你的个人藏书。")
        self.empty_description.setObjectName("emptyDescription")
        self.empty_description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(8)
        layout.addStretch()
        layout.addWidget(self.empty_title)
        layout.addWidget(self.empty_description)
        layout.addStretch()
        return widget

    def load_books(self, keyword=None):
        """读取数据库中的图书，并刷新表格内容。"""
        if keyword is None:
            keyword = self.search_input.text()

        books = get_books(keyword)
        self.book_count_label.setText(f"共 {len(books)} 本图书")
        self.book_table.setRowCount(len(books))

        for row_index, book in enumerate(books):
            for column_index, (field_name, _) in enumerate(self.TABLE_COLUMNS):
                if field_name == "actions":
                    self.book_table.setCellWidget(
                        row_index,
                        column_index,
                        self.create_action_buttons(book["id"]),
                    )
                    continue

                if field_name == "status":
                    self.book_table.setCellWidget(
                        row_index,
                        column_index,
                        self.create_status_badge(book.get("status") or "未借出"),
                    )
                    continue

                value = book.get(field_name)
                text = "" if value is None else str(value)
                item = QTableWidgetItem(text)
                item.setToolTip(text)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                    if field_name == "id"
                    else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self.book_table.setItem(row_index, column_index, item)

        if books:
            self.table_stack.setCurrentWidget(self.book_table)
        else:
            has_keyword = bool(str(keyword).strip())
            self.empty_title.setText("没有找到相关图书" if has_keyword else "还没有图书")
            self.empty_description.setText(
                "请尝试其他书名、作者或 NFC 编号。"
                if has_keyword
                else "点击“添加图书”，开始整理你的个人藏书。"
            )
            self.table_stack.setCurrentWidget(self.empty_state)

    def create_status_badge(self, status):
        """创建带文字的状态徽标。"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        label = QLabel(status)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName(
            "availableBadge" if status == "未借出" else "borrowedBadge"
        )

        layout.addWidget(label)
        return widget

    def create_action_buttons(self, book_id):
        """为每一行创建编辑和删除按钮。"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        edit_button = QPushButton("编辑")
        edit_button.setObjectName("tableActionButton")
        edit_button.setToolTip("编辑这本图书")
        edit_button.clicked.connect(
            lambda checked=False, current_id=book_id: self.open_edit_dialog(current_id)
        )

        delete_button = QPushButton("删除")
        delete_button.setObjectName("dangerButton")
        delete_button.setToolTip("永久删除这本图书")
        delete_button.clicked.connect(
            lambda checked=False, current_id=book_id: self.confirm_delete(current_id)
        )

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        return widget

    def show_success_message(self, message):
        """在窗口底部短暂显示成功提示，不打断连续操作。"""
        self.statusBar().showMessage(message, 3500)

    def open_add_dialog(self):
        """打开添加图书弹窗，保存成功后刷新列表。"""
        dialog = AddBookDialog(self)
        if dialog.exec():
            self.load_books()
            self.show_success_message("图书已成功添加")

    def open_excel_import(self):
        """选择 Excel 文件，完成导入后显示统计结果。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要导入的 Excel 文件",
            "",
            "Excel 文件 (*.xlsx)",
        )
        if not file_path:
            return

        try:
            result = import_books_from_excel(file_path)
        except ExcelImportError as error:
            QMessageBox.warning(self, "导入失败", str(error))
            return

        self.load_books()

        message_lines = [
            f"成功导入：{result['imported']} 本",
            f"跳过空行：{result['empty_rows']} 行",
            f"跳过重复书名：{result['duplicate_titles']} 本",
            f"失败记录：{result['failed']} 条",
        ]

        if result["errors"]:
            message_lines.append("")
            message_lines.append("部分失败记录：")
            for error in result["errors"][:5]:
                message_lines.append(
                    f"第 {error['row']} 行《{error['title']}》：{error['reason']}"
                )
            if len(result["errors"]) > 5:
                message_lines.append(f"另有 {len(result['errors']) - 5} 条失败记录。")

        QMessageBox.information(self, "Excel 导入完成", "\n".join(message_lines))
        self.show_success_message(f"Excel 导入完成，新增 {result['imported']} 本图书")

    def open_edit_dialog(self, book_id):
        """打开编辑弹窗，修改成功后刷新当前列表。"""
        book = get_book(book_id)
        if not book:
            QMessageBox.warning(self, "无法编辑", "这本图书已不存在。")
            self.load_books()
            return

        dialog = AddBookDialog(self, book=book)
        if dialog.exec():
            self.load_books()
            self.show_success_message("图书信息已成功修改")

    def confirm_delete(self, book_id):
        """确认后永久删除图书，并刷新当前列表。"""
        book = get_book(book_id)
        if not book:
            QMessageBox.warning(self, "无法删除", "这本图书已不存在。")
            self.load_books()
            return

        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除《{book['title']}》吗？\n删除后无法恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        if delete_book(book_id):
            self.load_books()
            self.show_success_message("图书已删除")
        else:
            QMessageBox.warning(self, "删除失败", "这本图书已不存在。")
            self.load_books()

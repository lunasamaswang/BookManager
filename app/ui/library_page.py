from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
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


class LibraryPage(QWidget):
    """图书库页面，保留原有图书管理功能。"""

    books_changed = Signal()
    success_message = Signal(str)

    # 常见窗口宽度下优先保证操作列完整，其余列按可用空间伸缩。
    MIN_COLUMN_WIDTHS = [48, 74, 84, 48, 52, 58, 68, 72, 152]
    COLUMN_GROWTH_LIMITS = [
        (2, 80),  # 书名优先获得空间
        (5, 34),  # 存放位置
        (7, 48),  # 添加时间
        (1, 24),  # NFC 编号
        (3, 28),  # 作者
        (4, 16),  # 分类
        (6, 12),  # 状态
    ]

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("libraryPage")
        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        """创建图书库标题、搜索栏和表格。"""
        page_title = QLabel("图书库")
        page_title.setObjectName("pageTitle")

        self.book_count_label = QLabel("共 0 本图书")
        self.book_count_label.setObjectName("pageSubtitle")

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(3)
        title_text_layout.addWidget(page_title)
        title_text_layout.addWidget(self.book_count_label)

        add_button = QPushButton("添加图书")
        add_button.setObjectName("primaryButton")
        add_button.setMinimumWidth(104)
        add_button.setToolTip("添加一本新图书")
        add_button.clicked.connect(self.open_add_dialog)

        self.import_button = QPushButton("导入 Excel")
        self.import_button.setObjectName("secondaryButton")
        self.import_button.setMinimumWidth(112)
        self.import_button.setToolTip("从 Excel 文件批量导入图书")
        self.import_button.clicked.connect(self.open_excel_import)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.addLayout(title_text_layout, 1)
        title_layout.addStretch()
        title_layout.addWidget(self.import_button)
        title_layout.addWidget(add_button)

        header = QFrame()
        header.setObjectName("libraryHeader")
        header.setLayout(title_layout)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("搜索书名、作者或 NFC 编号")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(300)
        self.search_input.setMaximumWidth(420)
        self.search_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.search_input.addAction(
            QIcon(str(ASSETS_DIR / "search.svg")),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_input.textChanged.connect(self.load_books)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(16, 12, 16, 12)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        search_panel = QFrame()
        search_panel.setObjectName("librarySearchPanel")
        search_panel.setLayout(search_layout)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        card_layout = QVBoxLayout(table_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.table_stack = QStackedLayout()
        self.table_stack.setContentsMargins(0, 0, 0, 0)
        self.book_table = self.create_book_table()
        self.book_table.viewport().installEventFilter(self)
        self.empty_state = self.create_empty_state()
        self.table_stack.addWidget(self.book_table)
        self.table_stack.addWidget(self.empty_state)
        card_layout.addLayout(self.table_stack)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(16)
        layout.addWidget(header)
        layout.addWidget(search_panel)
        layout.addWidget(table_card, 1)

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
        table.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        table.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        table.setTextElideMode(Qt.TextElideMode.ElideRight)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(52)

        header = table.horizontalHeader()
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header.setMinimumSectionSize(48)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        for column, width in enumerate(self.MIN_COLUMN_WIDTHS):
            table.setColumnWidth(column, width)
        return table

    def eventFilter(self, watched, event):
        """表格可视区域变化后重新计算列宽，避免最右侧操作列被裁切。"""
        if (
            hasattr(self, "book_table")
            and watched is self.book_table.viewport()
            and event.type() == QEvent.Type.Resize
        ):
            QTimer.singleShot(0, self.update_table_column_widths)
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        """窗口尺寸变化时同步调整表格列宽。"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_table_column_widths)

    def update_table_column_widths(self):
        """按表格可视宽度分配列宽，并始终保留完整操作列。"""
        viewport_width = self.book_table.viewport().width()
        if viewport_width <= 0:
            return

        widths = self.MIN_COLUMN_WIDTHS.copy()
        minimum_total = sum(widths)
        target_width = max(viewport_width, minimum_total)
        remaining = target_width - minimum_total

        for column, growth_limit in self.COLUMN_GROWTH_LIMITS:
            growth = min(remaining, growth_limit)
            widths[column] += growth
            remaining -= growth
            if remaining == 0:
                break

        # 更宽的窗口把剩余空间继续交给书名列。
        if remaining > 0:
            widths[2] += remaining

        for column, width in enumerate(widths):
            self.book_table.setColumnWidth(column, width)

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

    def set_search_keyword(self, keyword):
        """设置搜索词并刷新图书列表。"""
        keyword_changed = self.search_input.text() != keyword
        self.search_input.setText(keyword)
        self.search_input.setFocus()
        if not keyword_changed:
            self.load_books(keyword)

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

        QTimer.singleShot(0, self.update_table_column_widths)

    def create_status_badge(self, status):
        """创建带文字的状态徽标。"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 8, 6, 8)

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
        layout.setContentsMargins(5, 6, 5, 6)
        layout.setSpacing(6)

        edit_button = QPushButton("编辑")
        edit_button.setObjectName("tableActionButton")
        edit_button.setMinimumWidth(52)
        edit_button.setToolTip("编辑这本图书")
        edit_button.clicked.connect(
            lambda checked=False, current_id=book_id: self.open_edit_dialog(current_id)
        )

        delete_button = QPushButton("删除")
        delete_button.setObjectName("dangerButton")
        delete_button.setMinimumWidth(52)
        delete_button.setToolTip("永久删除这本图书")
        delete_button.clicked.connect(
            lambda checked=False, current_id=book_id: self.confirm_delete(current_id)
        )

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        return widget

    def notify_books_changed(self, message):
        """刷新页面，并通知主窗口更新首页和状态栏。"""
        self.load_books()
        self.books_changed.emit()
        self.success_message.emit(message)

    def open_add_dialog(self):
        """打开添加图书弹窗，保存成功后刷新列表。"""
        dialog = AddBookDialog(self)
        if dialog.exec():
            self.notify_books_changed("图书已成功添加")

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
        self.books_changed.emit()

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
        self.success_message.emit(
            f"Excel 导入完成，新增 {result['imported']} 本图书"
        )

    def open_edit_dialog(self, book_id):
        """打开编辑弹窗，修改成功后刷新当前列表。"""
        book = get_book(book_id)
        if not book:
            QMessageBox.warning(self, "无法编辑", "这本图书已不存在。")
            self.load_books()
            return

        dialog = AddBookDialog(self, book=book)
        if dialog.exec():
            self.notify_books_changed("图书信息已成功修改")

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
            self.notify_books_changed("图书已删除")
        else:
            QMessageBox.warning(self, "删除失败", "这本图书已不存在。")
            self.load_books()

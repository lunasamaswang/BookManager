from pathlib import Path

from PySide6.QtCore import QEvent, QSignalBlocker, QTimer, Signal, Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QStyle,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.book_service import (
    delete_book,
    get_book,
    get_books,
    get_categories,
    get_locations,
)
from app.services.import_service import ExcelImportError, import_books_from_excel
from app.ui.add_book_dialog import AddBookDialog
from app.ui.book_detail_dialog import BookDetailDialog


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class BookTableDelegate(QStyledItemDelegate):
    """为图书表格绘制整行悬停背景。"""

    def paint(self, painter, option, index):
        styled_option = option
        table = self.parent()
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)

        if table and index.row() == table.property("hoveredRow") and not is_selected:
            painter.save()
            painter.fillRect(option.rect, QColor("#F6F9FF"))
            painter.restore()

            styled_option = option.__class__(option)
            styled_option.state &= ~QStyle.StateFlag.State_MouseOver

        super().paint(painter, styled_option, index)


class LibraryPage(QWidget):
    """图书库页面，保留原有图书管理功能。"""

    books_changed = Signal()
    success_message = Signal(str)

    # 各列按权重分配可用空间，并保留保证文字可读的最小宽度。
    COLUMN_WEIGHTS = [0.6, 1.2, 3.5, 1.2, 1.0, 1.6, 1.0, 1.8, 2.2]
    MIN_COLUMN_WIDTHS = [40, 65, 80, 50, 50, 65, 55, 85, 180]

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
        self.refresh_filter_options()
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

        self.category_filter = QComboBox()
        self.category_filter.setObjectName("libraryFilter")
        self.category_filter.setMinimumWidth(120)
        self.category_filter.setMaximumWidth(160)
        self.category_filter.currentTextChanged.connect(
            lambda _text: self.load_books()
        )

        self.location_filter = QComboBox()
        self.location_filter.setObjectName("libraryFilter")
        self.location_filter.setMinimumWidth(120)
        self.location_filter.setMaximumWidth(160)
        self.location_filter.currentTextChanged.connect(
            lambda _text: self.load_books()
        )

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(16, 12, 16, 12)
        search_layout.setSpacing(12)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.location_filter)
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
        table.itemDoubleClicked.connect(self.open_book_detail)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.setMouseTracking(True)
        table.setProperty("hoveredRow", -1)
        table.setItemDelegate(BookTableDelegate(table))
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
        vertical_header = table.verticalHeader()
        vertical_header.setVisible(False)
        vertical_header.setMinimumSectionSize(52)
        vertical_header.setDefaultSectionSize(52)
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        header = table.horizontalHeader()
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header.setMinimumSectionSize(40)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        for column, width in enumerate(self.MIN_COLUMN_WIDTHS):
            table.setColumnWidth(column, width)
        return table

    def eventFilter(self, watched, event):
        """处理表格尺寸变化和整行悬停反馈。"""
        if hasattr(self, "book_table") and watched is self.book_table.viewport():
            if event.type() == QEvent.Type.Resize:
                QTimer.singleShot(0, self.update_table_column_widths)
            elif event.type() == QEvent.Type.MouseMove:
                hovered_row = self.book_table.indexAt(event.position().toPoint()).row()
                if hovered_row != self.book_table.property("hoveredRow"):
                    self.book_table.setProperty("hoveredRow", hovered_row)
                    self.book_table.viewport().update()
            elif event.type() == QEvent.Type.Leave:
                self.book_table.setProperty("hoveredRow", -1)
                self.book_table.viewport().update()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        """窗口尺寸变化时同步调整表格列宽。"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_table_column_widths)

    def update_table_column_widths(self):
        """根据表格可视宽度和列权重动态分配列宽。"""
        viewport_width = self.book_table.viewport().width()
        if viewport_width <= 0:
            return

        minimum_total = sum(self.MIN_COLUMN_WIDTHS)
        available_width = max(viewport_width, minimum_total)
        extra_width = available_width - minimum_total
        total_weight = sum(self.COLUMN_WEIGHTS)

        raw_growth = [
            extra_width * weight / total_weight
            for weight in self.COLUMN_WEIGHTS
        ]
        growth = [int(value) for value in raw_growth]

        # 把取整后的剩余像素交给小数部分最大的列，保证总宽度稳定。
        remaining_pixels = extra_width - sum(growth)
        growth_order = sorted(
            range(len(raw_growth)),
            key=lambda column: raw_growth[column] - growth[column],
            reverse=True,
        )
        for column in growth_order[:remaining_pixels]:
            growth[column] += 1

        widths = [
            minimum_width + column_growth
            for minimum_width, column_growth in zip(
                self.MIN_COLUMN_WIDTHS,
                growth,
            )
        ]
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

    def refresh_filter_options(self):
        """刷新分类和位置选项，并尽量保留当前筛选条件。"""
        self.refresh_filter_combo(
            self.category_filter,
            "全部分类",
            get_categories(),
        )
        self.refresh_filter_combo(
            self.location_filter,
            "全部位置",
            get_locations(),
        )

    def refresh_filter_combo(self, combo, default_text, values):
        """在不触发重复查询的情况下更新一个筛选下拉框。"""
        current_text = combo.currentText() or default_text
        blocker = QSignalBlocker(combo)
        combo.clear()
        combo.addItem(default_text)
        combo.addItems(values)

        current_index = combo.findText(current_text)
        combo.setCurrentIndex(current_index if current_index >= 0 else 0)
        del blocker

    def load_books(self, keyword=None):
        """读取数据库中的图书，并刷新表格内容。"""
        if keyword is None:
            keyword = self.search_input.text()

        books = get_books(
            keyword,
            self.category_filter.currentText(),
            self.location_filter.currentText(),
        )
        books = sorted(books, key=lambda book: book["id"])
        self.book_count_label.setText(f"共 {len(books)} 本图书")
        self.book_table.setRowCount(len(books))

        for row_index, book in enumerate(books, start=1):
            table_row = row_index - 1
            for column_index, (field_name, _) in enumerate(self.TABLE_COLUMNS):
                if field_name == "actions":
                    self.book_table.setCellWidget(
                        table_row,
                        column_index,
                        self.create_action_buttons(book["id"]),
                    )
                    continue

                if field_name == "status":
                    self.book_table.setCellWidget(
                        table_row,
                        column_index,
                        self.create_status_badge(book.get("status") or "未借出"),
                    )
                    continue

                value = row_index if field_name == "id" else book.get(field_name)
                text = "" if value is None else str(value)
                item = QTableWidgetItem(text)
                item.setToolTip(text)
                item.setData(Qt.ItemDataRole.UserRole, book["id"])
                if field_name in {"id", "nfc_id", "created_at"}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft
                        | Qt.AlignmentFlag.AlignVCenter
                    )
                if field_name == "title":
                    title_font = item.font()
                    title_font.setBold(True)
                    item.setFont(title_font)
                self.book_table.setItem(table_row, column_index, item)

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
        layout.setContentsMargins(6, 0, 6, 0)

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
        layout.setContentsMargins(5, 0, 5, 0)
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

    def open_book_detail(self, item):
        """双击普通数据列时打开只读图书详情。"""
        if item.column() in {6, 8}:
            return

        book_id = item.data(Qt.ItemDataRole.UserRole)
        if book_id is None:
            return

        book = get_book(book_id)
        if not book:
            QMessageBox.warning(self, "无法查看", "这本图书已不存在。")
            self.load_books()
            return

        dialog = BookDetailDialog(book, self)
        dialog.exec()
        if dialog.edit_requested:
            self.open_edit_dialog(book_id)

    def notify_books_changed(self, message):
        """刷新页面，并通知主窗口更新首页和状态栏。"""
        self.refresh_filter_options()
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

        self.refresh_filter_options()
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

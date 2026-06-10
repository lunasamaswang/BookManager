# 个人图书管理系统 v1.0.1

这是一个使用 Python、PySide6 和 SQLite 编写的基础桌面图书管理软件。当前版本支持添加、编辑、删除、搜索和从 Excel 批量导入图书。

NFC 编号目前只是预留字段，不连接真实 NFC 硬件。

## 环境要求

- Python 3.10 或更高版本
- Windows、macOS 或 Linux

## 项目结构

```text
book_manager/
├── main.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── BookManager.spec
├── app/
│   ├── database.py
│   ├── path_utils.py
│   ├── services/book_service.py
│   ├── services/import_service.py
│   ├── ui/main_window.py
│   ├── ui/add_book_dialog.py
│   └── assets/styles.qss
└── data/
    ├── .gitkeep
    └── books.db
```

## 安装依赖

进入项目目录后，建议先创建虚拟环境：

```powershell
cd E:\library\book_manager
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS 或 Linux 激活虚拟环境时使用：

```bash
source .venv/bin/activate
```

## 运行程序

```powershell
py -3.13 main.py
```

源码运行时，程序会使用项目根目录的 `data/books.db`。

如果已经激活由 Python 3.10+ 创建的虚拟环境，也可以使用 `python main.py`。

## 打包 Windows exe

项目已经提供 `BookManager.spec`。先安装依赖，然后在项目根目录执行：

```powershell
py -3.13 -m PyInstaller --noconfirm --clean BookManager.spec
```

打包完成后的程序位于：

```text
dist\BookManager\BookManager.exe
```

打包版不会显示命令行窗口。QSS 和 SVG 图标会包含在程序目录中。

`BookManager.spec` 会排除当前开发环境中可能存在的旧版 Anaconda ICU DLL，避免它与 PySide6 使用的 Windows 系统 ICU 冲突。

## 数据存储位置

程序会根据运行方式选择数据库路径：

1. **源码模式**：使用项目根目录下的 `data\books.db`。
2. **便携版模式**：打包 exe 同级存在 `data` 文件夹时，使用 `data\books.db`。
3. **默认打包模式**：exe 同级不存在 `data` 文件夹时，使用：

```text
%LOCALAPPDATA%\BookManager\books.db
```

如需启用便携版模式，请在 `BookManager.exe` 同级目录手动创建 `data` 文件夹，再启动程序。

便携版数据库和 `%LOCALAPPDATA%` 数据库彼此独立，程序不会自动迁移、复制或覆盖数据。如需切换并保留原数据，请先关闭程序，再手工复制对应的 `books.db`。

数据库不存在时会自动创建。重新打包或替换 `dist` 文件夹不会删除 `%LOCALAPPDATA%` 中的图书数据。

## 从 Excel 导入图书

1. 新建一个 `.xlsx` 文件。
2. 在第一个工作表的 `A1` 单元格填写 `书名` 或 `title`。
3. 从 `A2` 开始，每一行填写一本书的名称。
4. 启动程序，点击右上角的“导入 Excel”按钮并选择文件。
5. 导入结束后，程序会显示成功、空行、重复书名和失败记录数量。

示例：

| 书名 |
| --- |
| 活着 |
| Python 编程：从入门到实践 |
| 小王子 |

导入的图书会自动生成 `BOOK000001` 格式的 NFC 编号。作者默认为空，分类默认为“未分类”，位置默认为“未设置”，状态默认为“未借出”。

## 功能测试

1. 运行程序，确认可以看到左侧导航栏和右侧图书表格。
2. 点击“添加图书”，填写书名等信息并保存。
3. 确认新图书立即出现在表格中。
4. 在搜索框输入书名、作者或 NFC 编号，确认列表能够筛选。
5. 再次添加相同的非空 NFC 编号，确认程序提示“NFC 编号已存在”。
6. 不填写书名直接保存，确认程序提示“书名不能为空”。
7. 关闭并重新启动程序，确认已经添加的图书仍然存在。
8. 点击表格中的“编辑”，修改图书信息并保存，确认列表自动刷新。
9. 点击“删除”，选择“否”确认数据仍保留；再次删除并选择“是”，确认记录消失。

## 第一版范围

当前版本不包含借阅流程、统计和真实 NFC 硬件接入功能。

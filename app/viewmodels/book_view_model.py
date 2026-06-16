from dataclasses import dataclass

from app.viewmodels.book_status_model import BookStatusModel
from app.viewmodels.rating_view_model import RatingViewModel
from app.viewmodels.reading_status_model import ReadingStatusModel


def format_text(value, empty_text="未填写"):
    """清理展示文本，并为缺失值提供统一占位。"""
    if value is None:
        return empty_text

    text = str(value).strip()
    return text or empty_text


@dataclass(frozen=True)
class DetailField:
    """描述详情区块中的一行字段。"""

    key: str
    label: str
    value: str


@dataclass(frozen=True)
class DetailSection:
    """描述一个可由详情弹窗统一渲染的区块。"""

    key: str
    title: str
    fields: tuple[DetailField, ...]


@dataclass(frozen=True)
class BookViewModel:
    """统一图书详情弹窗使用的只读展示数据。"""

    book_id: int | None
    title: str
    author: str
    category: str
    location: str
    status: BookStatusModel
    reading_status: ReadingStatusModel
    rating: RatingViewModel
    nfc_id: str
    created_at: str
    basic_info: DetailSection
    location_info: DetailSection
    status_info: DetailSection
    reading_info: DetailSection
    meta_info: DetailSection
    sections: tuple[DetailSection, ...]

    @classmethod
    def from_book(cls, book):
        """将服务层返回的图书字典转换为详情展示模型。"""
        title = format_text(book.get("title"))
        author = format_text(book.get("author"))
        category = format_text(book.get("category"))
        location = format_text(book.get("location"))
        status = BookStatusModel.from_value(book.get("status"))
        reading_status = ReadingStatusModel.from_value(book.get("reading_status"))
        rating = RatingViewModel.from_value(book.get("rating"))
        nfc_id = format_text(book.get("nfc_id"), "未绑定")
        created_at = format_text(book.get("created_at"))

        basic_info = DetailSection(
            key="basic_info",
            title="基本信息",
            fields=(
                DetailField("author", "作者", author),
                DetailField("category", "分类", category),
            ),
        )
        location_info = DetailSection(
            key="location_info",
            title="位置信息",
            fields=(
                DetailField("location", "存放位置", location),
            ),
        )
        status_info = DetailSection(
            key="status_info",
            title="状态",
            fields=(
                DetailField("status", "当前状态", status.label),
            ),
        )
        reading_info = DetailSection(
            key="reading_info",
            title="阅读信息",
            fields=(
                DetailField("reading_status", "阅读状态", reading_status.label),
                DetailField("rating", "我的评分", rating.label),
            ),
        )
        meta_info = DetailSection(
            key="meta_info",
            title="NFC 信息",
            fields=(
                DetailField("nfc_id", "NFC 编号", nfc_id),
                DetailField("created_at", "添加时间", created_at),
            ),
        )

        return cls(
            book_id=book.get("id"),
            title=title,
            author=author,
            category=category,
            location=location,
            status=status,
            reading_status=reading_status,
            rating=rating,
            nfc_id=nfc_id,
            created_at=created_at,
            basic_info=basic_info,
            location_info=location_info,
            status_info=status_info,
            reading_info=reading_info,
            meta_info=meta_info,
            sections=(
                basic_info,
                location_info,
                status_info,
                reading_info,
                meta_info,
            ),
        )

    @property
    def status_text(self):
        """兼容详情界面使用的状态文字属性。"""
        return self.status.label

    @property
    def status_style(self):
        """兼容详情界面使用的状态样式属性。"""
        return self.status.style_name

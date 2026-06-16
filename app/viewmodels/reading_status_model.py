from dataclasses import dataclass


@dataclass(frozen=True)
class ReadingStatusModel:
    """统一描述图书的个人阅读状态展示信息。"""

    value: str
    label: str
    style_name: str
    category: str

    @classmethod
    def from_value(cls, value):
        """把数据库中的阅读状态转换为详情页可展示的模型。"""
        clean_value = str(value or "").strip()
        if not clean_value:
            clean_value = "未读"

        mapping = {
            "未读": ("未读", "neutral", "neutral"),
            "想读": ("想读", "wish", "wish"),
            "在读": ("在读", "reading", "reading"),
            "已读": ("已读", "finished", "finished"),
            "暂停": ("暂停", "paused", "paused"),
            "弃读": ("弃读", "dropped", "dropped"),
        }
        label, style_name, category = mapping.get(
            clean_value,
            (clean_value, "neutral", "neutral"),
        )
        return cls(
            value=clean_value,
            label=label,
            style_name=style_name,
            category=category,
        )

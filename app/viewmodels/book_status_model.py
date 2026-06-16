from dataclasses import dataclass


@dataclass(frozen=True)
class BookStatusModel:
    """描述详情页使用的轻量图书状态。"""

    value: str
    label: str
    style_name: str
    category: str

    @classmethod
    def from_value(cls, value, empty_text="未填写"):
        """根据当前数据库状态生成展示模型。"""
        clean_value = "" if value is None else str(value).strip()
        label = clean_value or empty_text

        if clean_value == "未借出":
            return cls(
                value=clean_value,
                label=label,
                style_name="availableBadge",
                category="available",
            )

        if clean_value == "已借出":
            return cls(
                value=clean_value,
                label=label,
                style_name="borrowedBadge",
                category="borrowed",
            )

        return cls(
            value=clean_value,
            label=label,
            style_name="borrowedBadge",
            category="neutral",
        )


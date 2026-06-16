from dataclasses import dataclass


@dataclass(frozen=True)
class RatingViewModel:
    """统一描述图书评分的展示文本。"""

    value: int
    label: str

    @classmethod
    def from_value(cls, value):
        """把数据库评分转换为 0 到 5 分的展示模型。"""
        try:
            rating = int(value)
        except (TypeError, ValueError):
            rating = 0

        if rating < 0 or rating > 5:
            rating = 0

        label = "未评分" if rating == 0 else f"{rating} 分"
        return cls(value=rating, label=label)

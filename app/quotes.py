from datetime import date


QUOTES = [
    ("书籍是人类进步的阶梯。", "高尔基"),
    ("读一本好书，就是和许多高尚的人谈话。", "歌德"),
    ("生活里没有书籍，就好像没有阳光。", "莎士比亚"),
    ("阅读使人充实，会谈使人敏捷，写作使人精确。", "培根"),
    ("书卷多情似故人，晨昏忧乐每相亲。", "于谦"),
    ("立身以立学为先，立学以读书为本。", "欧阳修"),
    ("纸上得来终觉浅，绝知此事要躬行。", "陆游"),
]


def get_daily_quote(current_date=None):
    """根据日期稳定返回当天的名言和作者。"""
    selected_date = current_date or date.today()
    return QUOTES[selected_date.toordinal() % len(QUOTES)]

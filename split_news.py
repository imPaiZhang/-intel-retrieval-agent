"""把 AIHOT 每天一个的大 JSON，拆成每天一个 Markdown 文件，每条以 ## 标题开头，方便 grep 和分页读。"""
import json, pathlib
SRC = pathlib.Path("raw")
DST = pathlib.Path("news")
DST.mkdir(exist_ok=True)
total = 0
for f in sorted(SRC.glob("2026-10-*.json")):
    if f.stem.endswith("-pm"):
        continue
    items = json.load(open(f))["items"]
    lines = [f"# AIHOT {f.stem}（{len(items)} 条）", ""]
    for it in items:
        lines += [
            f"## {it['title']}",
            f"分类:{it.get('category')} | 评分:{it.get('score')} | 来源:{it['source']['name']} | 时间:{it.get('publishedAt')}",
            f"摘要:{it.get('summary') or ''}",
            f"链接:{it['links'].get('original') or it['links'].get('aihot')}",
            "",
        ]
    (DST / f"{f.stem}.md").write_text("\n".join(lines), encoding="utf-8")
    total += len(items)
print("拆完", total, "条，", len(list(DST.glob('*.md'))), "个文件")

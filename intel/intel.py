#!/usr/bin/env python3
"""排长 AI 情报库检索（全项目共用）。

  python3 intel.py sync                       # 把 raw/*.json 增量拆成 news/*.md（search/ask 会自动先跑）
  python3 intel.py search 可灵 API [--days 7] [--cat ai-models] [--min-score 40] [--limit 20]
                                              # 零成本：别名扩展 + 元数据预筛，直接列命中条目
  python3 intel.py ask "这周可灵开放了哪些能力？" [--days 7] [--save 可灵-api] [--fresh]
                                              # 调模型：Agent 检索+子智能体读，带缓存与记账；--save 回写答案卡
  python3 intel.py cost                       # 看累计花费
"""
import argparse, datetime as dt, hashlib, json, os, pathlib, re, sys, time

KB = pathlib.Path(__file__).resolve().parent.parent          # /workspace/knowledge/ai-intel
HERE = pathlib.Path(__file__).resolve().parent
RAW, NEWS = KB / "raw", HERE / "news"
CACHE, ANSWERS, LOGS = HERE / "cache", HERE / "answers", HERE / "logs"
for d in (NEWS, CACHE, ANSWERS, LOGS):
    d.mkdir(exist_ok=True)
# MiniMax-M3.1-Flash 估价（元/百万 token），只用于记账提醒，按官网价调整
PRICE_IN, PRICE_OUT = float(os.environ.get("PRICE_IN", 1.0)), float(os.environ.get("PRICE_OUT", 4.0))
BUDGET_PER_ASK = float(os.environ.get("BUDGET_PER_ASK", 1.0))   # 单次超过这个数就提醒


# ---------- 1. 同步：raw JSON → 每天一个 Markdown ----------
def _items(f):
    d = json.load(open(f, encoding="utf-8"))
    return d["items"] if isinstance(d, dict) else d

def sync(quiet=False):
    made = 0
    for f in sorted(RAW.glob("*.json")):
        out = NEWS / f"{f.stem}.md"
        if out.exists() and out.stat().st_mtime >= f.stat().st_mtime:
            continue
        items = _items(f)
        lines = [f"# AIHOT {f.stem}（{len(items)} 条）", ""]
        for it in items:
            src = (it.get("source") or {}).get("name", "")
            link = (it.get("links") or {}).get("original") or (it.get("links") or {}).get("aihot", "")
            lines += [f"## {it.get('title','')}",
                      f"分类:{it.get('category')} | 评分:{it.get('score')} | 来源:{src} | 时间:{it.get('publishedAt')}",
                      f"摘要:{it.get('summary') or ''}", f"链接:{link}", ""]
        out.write_text("\n".join(lines), encoding="utf-8")
        made += 1
    if made and not quiet:
        print(f"[sync] 新拆 {made} 天", file=sys.stderr)
    return made


# ---------- 2. 零成本检索：别名扩展 + 元数据预筛 ----------
def load_aliases():
    groups = json.load(open(HERE / "aliases.json", encoding="utf-8"))["groups"]
    idx = {}
    for g in groups:
        for w in g:
            idx.setdefault(w.lower(), set()).update(x.lower() for x in g)
    return idx

def expand(words):
    idx = load_aliases()
    return [sorted(idx.get(w.lower(), {w.lower()})) for w in words]

def _day_ok(stem, days):
    if not days:
        return True
    try:
        d = dt.date.fromisoformat(stem[:10])
    except ValueError:
        return True
    return (dt.date.today() - d).days < days

def find(keywords, days=None, cat=None, min_score=None):
    """每个关键词展开成别名组；条目要命中每一组里的至少一个词。返回按 评分↓、日期↓ 排的命中（同标题去重）。"""
    groups = expand(keywords.split())
    hits, seen = [], set()
    for f in sorted(NEWS.glob("*.md"), reverse=True):
        if not _day_ok(f.stem, days):
            continue
        for block in f.read_text(encoding="utf-8").split("\n## ")[1:]:
            low = block.lower()
            if not all(any(w in low for w in g) for g in groups):
                continue
            meta = re.search(r"分类:(\S*) \| 评分:(\S*)", block)
            c, s = (meta.group(1), meta.group(2)) if meta else ("", "")
            if cat and c != cat:
                continue
            score = int(s) if s.isdigit() else 0
            if min_score and score < min_score:
                continue
            title = block.splitlines()[0].strip()
            if title in seen:
                continue
            seen.add(title)
            hits.append({"day": f.stem, "score": score, "cat": c, "title": title, "block": "## " + block.strip()})
    hits.sort(key=lambda h: (h["score"], h["day"]), reverse=True)
    return hits, groups


# ---------- 3. 调模型问答：缓存 + 记账 + 回写 ----------
def _data_version():
    return max((f.stat().st_mtime for f in NEWS.glob("*.md")), default=0)

def _slug(s):
    return re.sub(r"[^\w\u4e00-\u9fff]+", "-", s).strip("-")[:40] or "q"

def find_answer_card(q):
    """先查已回写的答案卡：问题完全相同直接复用。"""
    for p in sorted(ANSWERS.glob("*.md"), reverse=True):
        head = p.read_text(encoding="utf-8").split("\n", 6)
        if any(l.strip() == f"question: {q}" for l in head):
            return p
    return None

def ask(q, days=None, save=None, fresh=False, max_hits=6):
    key = hashlib.sha1(f"{q}|{days}".encode()).hexdigest()[:16]
    cf = CACHE / f"{key}.json"
    if not fresh:
        card = find_answer_card(q)
        if card:
            print(f"[命中答案卡 {card.name}，0 成本]\n" + card.read_text(encoding="utf-8"))
            return
        if cf.exists():
            c = json.load(open(cf, encoding="utf-8"))
            if c["data_version"] >= _data_version():
                print("[命中缓存，0 成本]\n" + c["answer"])
                if save: write_card(q, c["answer"], save, c["usage"])
                return
    sys.path.insert(0, str(HERE))
    import agent_core as A
    A.NEWS_DAYS, A.MAX_HITS = days, max_hits
    t = time.time()
    usage = {"in": 0, "out": 0, "calls": 0}
    answer = ""
    for ns, upd in A.build().stream({"messages": [{"role": "user", "content": q}]}, stream_mode="updates", subgraphs=True):
        for val in (upd or {}).values():
            if not isinstance(val, dict):
                continue
            for m in val.get("messages", []) or []:
                if m.type == "ai":
                    u = getattr(m, "usage_metadata", None) or {}
                    usage["in"] += u.get("input_tokens", 0); usage["out"] += u.get("output_tokens", 0); usage["calls"] += 1
                    if not ns and not m.tool_calls:
                        answer = str(m.content)
    usage["seconds"] = round(time.time() - t)
    usage["yuan"] = round(usage["in"] / 1e6 * PRICE_IN + usage["out"] / 1e6 * PRICE_OUT, 3)
    with open(LOGS / "cost.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": dt.datetime.now().isoformat(timespec="seconds"), "q": q, "days": days,
                            "model": os.environ.get("LLM_MODEL"), **usage}, ensure_ascii=False) + "\n")
    json.dump({"q": q, "answer": answer, "usage": usage, "data_version": _data_version()},
              open(cf, "w", encoding="utf-8"), ensure_ascii=False)
    print(answer)
    print(f"\n[用时 {usage['seconds']} 秒｜{usage['calls']} 次调用｜输入 {usage['in']:,}｜输出 {usage['out']:,}｜约 ¥{usage['yuan']}]")
    if usage["yuan"] > BUDGET_PER_ASK:
        print(f"[提醒] 本次超过单次预算 ¥{BUDGET_PER_ASK}，考虑加 --days 或换更具体的问题。")
    if save:
        write_card(q, answer, save, usage)

def write_card(q, answer, slug, usage):
    p = ANSWERS / f"{dt.date.today()}-{_slug(slug)}.md"
    p.write_text(f"---\nquestion: {q}\ndate: {dt.date.today()}\nstatus: auto-answer\ncost_yuan: {usage.get('yuan')}\n---\n"
                 f"# {q}\n\n{answer}\n", encoding="utf-8")
    with open(HERE / "ANSWERS.md", "a", encoding="utf-8") as f:
        f.write(f"| {dt.date.today()} | {q} | answers/{p.name} |\n")
    print(f"[已回写答案卡 answers/{p.name}；值得深挖的再升级成 entries/ 知识卡]")


def cost():
    rows = [json.loads(l) for l in open(LOGS / "cost.jsonl", encoding="utf-8")] if (LOGS / "cost.jsonl").exists() else []
    tot = sum(r.get("yuan", 0) for r in rows)
    print(f"共 {len(rows)} 次问答，累计约 ¥{tot:.2f}")
    for r in rows[-10:]:
        print(f"{r['time']} ¥{r.get('yuan')} 输入{r['in']:,} {r['q'][:40]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync"); sub.add_parser("cost")
    s = sub.add_parser("search"); s.add_argument("keywords", nargs="+")
    s.add_argument("--days", type=int); s.add_argument("--cat"); s.add_argument("--min-score", type=int)
    s.add_argument("--limit", type=int, default=20); s.add_argument("--full", action="store_true")
    a = sub.add_parser("ask"); a.add_argument("question"); a.add_argument("--days", type=int)
    a.add_argument("--save"); a.add_argument("--fresh", action="store_true"); a.add_argument("--max-hits", type=int, default=6)
    o = ap.parse_args()
    if o.cmd == "sync":
        print(f"新拆 {sync(quiet=True)} 天，共 {len(list(NEWS.glob('*.md')))} 天")
    elif o.cmd == "cost":
        cost()
    elif o.cmd == "search":
        sync()
        hits, groups = find(" ".join(o.keywords), o.days, o.cat, o.min_score)
        print(f"展开后：{' AND '.join('(' + '|'.join(g) + ')' for g in groups)}｜命中 {len(hits)} 条")
        for h in hits[:o.limit]:
            if o.full:
                print(f"\n[{h['day']}] {h['block']}")
            else:
                link = re.search(r"链接:(\S+)", h["block"])
                print(f"[{h['day']}｜{h['cat']}｜{h['score']}] {h['title']}  {link.group(1) if link else ''}")
    elif o.cmd == "ask":
        sync()
        ask(o.question, o.days, o.save, o.fresh, o.max_hits)

if __name__ == "__main__":
    main()

import tiktoken, pathlib, subprocess, json
enc = tiktoken.get_encoding("o200k_base")
T = lambda s: len(enc.encode(s))
raw = "".join(open(f).read() for f in sorted(pathlib.Path("raw").glob("2026-10-??.json")))
md = "".join(p.read_text() for p in sorted(pathlib.Path("news").glob("*.md")))
today_json = open("raw/2026-10-24.json").read()
print("8 天原始 JSON 全塞:", T(raw))
print("8 天 Markdown 全塞:", T(md))
print("今天 1 天 JSON:", T(today_json))
g = subprocess.run(["grep","-rn","可灵","news/"],capture_output=True,text=True).stdout
print("grep 可灵 命中行数:", g.count("\n"), "token:", T(g))
gl = subprocess.run(["grep","-rl","可灵","news/"],capture_output=True,text=True).stdout
print("grep -l 只要文件名 token:", T(gl), gl.split())
gc = subprocess.run(["grep","-rc","可灵","news/"],capture_output=True,text=True).stdout
print("grep -c 计数 token:", T(gc))
page = "\n".join(pathlib.Path("news/2026-10-24.md").read_text().splitlines()[:100])
print("read_file 默认 100 行一页 token:", T(page))

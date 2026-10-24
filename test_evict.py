"""验证：自定义工具返回大段中文时，什么情况下会被存成文件。"""
import pathlib, tiktoken
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from deepagents import create_deep_agent
from deepagents.middleware import FilesystemMiddleware
from test_offline import Fake
import agent as A
enc = tiktoken.get_encoding("o200k_base")
day = (A.ROOT / "news/2026-10-24.md").read_text()

@tool
def dump_today() -> str:
    """把今天的情报整份返回（反面教材）。"""
    return day[:60000]

def run(middleware=()):
    m = Fake(responses=[AIMessage("", tool_calls=[{"name": "dump_today", "args": {}, "id": "d1"}]), AIMessage("x")])
    ag = create_deep_agent(model=m, tools=[dump_today], backend=A.backend, middleware=list(middleware))
    t = [x for x in ag.invoke({"messages": [{"role": "user", "content": "x"}]})["messages"] if x.type == "tool"][0]
    c = str(t.content)
    print(f"进上下文 {len(c)} 字符 / {len(enc.encode(c))} token；开头：{c[:160]!r}\n")

print("工具原样返回 60000 字符 =", len(enc.encode(day[:60000])), "token")
print("【默认设置】"); run()
print("【阈值调到 8000】"); run([FilesystemMiddleware(backend=A.backend, tool_token_limit_before_evict=8000)])

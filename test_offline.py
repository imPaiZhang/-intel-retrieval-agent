"""不花一分钱的接线测试：用写好剧本的假模型，验证工具、文件、子智能体、权限都接通了。"""
import shutil, tiktoken
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
import agent as A

class Fake(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kw):
        return self

shutil.rmtree(A.ROOT / "retrieved", ignore_errors=True)
main = Fake(responses=[
    AIMessage("", tool_calls=[{"name": "grep", "args": {"pattern": "Kling 4.0", "path": "/news", "output_mode": "count"}, "id": "c1"}]),
    AIMessage("", tool_calls=[{"name": "search_news", "args": {"keywords": "可灵 API", "max_hits": 3}, "id": "c2"}]),
    AIMessage("", tool_calls=[{"name": "task", "args": {"subagent_type": "news-reader", "description": "问题：可灵4.0 API 最长多少秒？文件：/retrieved/可灵-API/2026-10-22-0.md"}, "id": "c3"}]),
    AIMessage("", tool_calls=[{"name": "write_file", "args": {"file_path": "/news/hack.md", "content": "x"}, "id": "c4"}]),
    AIMessage("（剧本结束）"),
])
reader = Fake(responses=[
    AIMessage("", tool_calls=[{"name": "read_file", "args": {"file_path": "/retrieved/可灵-API/2026-10-22-0.md", "offset": 0, "limit": 20}, "id": "r1"}]),
    AIMessage("相关；（假模型占位结论）；链接见文件"),
])
ag = A.build(model=main, reader_model=reader)
out = ag.invoke({"messages": [{"role": "user", "content": "可灵 4.0 API 最长多少秒？"}]})
enc = tiktoken.get_encoding("o200k_base")
for m in out["messages"]:
    if m.type == "tool":
        print(f"--- 工具 {m.name} 返回（{len(enc.encode(str(m.content)))} token）:\n{str(m.content)[:500]}\n")
print("retrieved 下的文件：", sorted(str(p.relative_to(A.ROOT)) for p in (A.ROOT/'retrieved').rglob('*.md')))
print("hack.md 写进去了吗：", (A.ROOT/'news'/'hack.md').exists())

# intel-retrieval-agent

用 LangChain Deep Agents 搭一个本地资料库检索 Agent：先找再读、检索结果存文件只返回路径、读的活交给子智能体。配套公众号文章《我每天 300 条 AI 情报，怎么让 Agent 只读该读的那几条》（排长 · 技术专栏）。

## 文件

| 文件 | 作用 |
|---|---|
| `split_news.py` | 把每天一个的 JSON 情报拆成 `news/日期.md`，每条以 `## 标题` 开头 |
| `agent.py` | 检索 Agent：`search_news` 工具 + `news-reader` 子智能体 + 情报库只读权限 + 中文转存阈值 |
| `agent_v2.py` | 改法：`MainToolAllowlist` 中间件，主 Agent 只看得到 `search_news` 和 `task` |
| `run_real.py` | 接真实模型跑一次，打印调用链、耗时和 token 用量 |
| `test_offline.py` | 用剧本化假模型离线验证工具、文件、子智能体、权限是否接通（不花钱） |
| `test_evict.py` | 验证大结果转存阈值对中文资料的影响 |
| `measure.py` | 用 tiktoken 估算各种做法的 token 数 |
| `article/` | 文章 Markdown 与 LangChain 原文截图 |
| `wechat-layout/` | 公众号排版预览（`preview.html`）和生成脚本 |

## 快速开始

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 && uv pip install -r requirements.txt

# 1. 把原始 JSON 放进 raw/，或者直接把 "## 标题 + 几行正文" 的 Markdown 放进 news/
uv run python split_news.py

# 2. 任意兼容 OpenAI 接口的模型
export LLM_MODEL="模型名"
export LLM_BASE_URL="厂商的 OpenAI 兼容地址"
export LLM_API_KEY="你的 Key"

# 3. 提问
uv run python agent.py "这周可灵 4.0 开放了哪些能力？API 最长能生成多少秒？"
# 改法对比
AGENT_MOD=agent_v2 uv run python run_real.py "这周可灵 4.0 开放了哪些能力？API 最长能生成多少秒？"
```

## 实测（MiniMax-M3.1-Flash，同一问题各跑一次，仅作量级参考）

| | agent.py | agent_v2.py |
|---|---|---|
| 用时 | 303 秒 | 228 秒 |
| 模型调用（含子智能体） | 47 次 | 63 次 |
| 累计输入 token | 约 169 万 | 约 27 万 |
| 费用（无缓存） | 约 1.8 元 | 约 0.4 元 |

环境：Python 3.12，deepagents 0.7.32，langchain 1.4.7，langgraph 1.2.17。

## 参考

- LangChain，《Context Engineering Starts with Retrieval》：https://www.langchain.com/blog/context-engineering-starts-with-retrieval
- Deep Agents 文档：https://docs.langchain.com/oss/python/deepagents/overview

文章中的 LangChain 截图版权归原作者所有，仅作引用说明。

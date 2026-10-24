# intel/：v3 日常版

文章里的 v1/v2 是教学版；这里是我每天真在用的版本，在 v2 白名单基础上加了：

- 中英文别名自动扩展（aliases.json，可灵/Kling、Kimi/月之暗面……）
- 时间窗、分类、评分预筛，命中按评分排序、同标题去重，只派评分最高的几条给子智能体
- 零成本 `search` 模式：不调模型，直接列条目和原文链接
- `ask` 模式：问答结果缓存（数据没更新就复用）、每次记账到 logs/cost.jsonl、`--save` 回写答案卡

```bash
python3 intel.py search 可灵 API --days 7
python3 intel.py ask "这周可灵 4.0 开放了哪些能力？" --days 7 --save kling-api
python3 intel.py cost
```
需要 `raw/` 目录（每天一个情报 JSON，结构见 split_news.py），以及 LLM_BASE_URL / LLM_MODEL / LLM_API_KEY 三个环境变量。

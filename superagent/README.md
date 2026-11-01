# superagent

复算 DeepSeek Harness 团队《Super-agent 设计探索：迈向更自主的 Agent 系统》（2026-10-31）第 7 节公开数字：

- 去掉直通后的 token 增幅与每个决定的 token 变化
- Router 批处理：单次耗时/batch 与原文“分摊推理时间”的差距
- 40 条/分 时 Router 占用率（两种读法）
- 用两点拟合 L(b)=a+c*b 的批处理排队仿真（泊松到达）
- 消融实验样本量与 p95

只用标准库：`python3 superagent_math.py`，输出见 output.txt。

原文转载：https://finance.eastmoney.com/a/202610313917654063.html
原型仓库：https://github.com/deepseek-ai/dsh-superagent-prototype

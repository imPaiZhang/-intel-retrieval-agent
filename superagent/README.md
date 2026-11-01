# DeepSeek Super-agent 实验数字复算

复算 DeepSeek Harness 团队《Super-agent 设计探索：迈向更自主的 Agent 系统》（2026-10-31）第 7 节公开数字：去直通的 token 账、Router 批处理分摊口径、40 条/分时的占用率，以及用两点拟合做的 Router 排队仿真。

只用 python 标准库：`python3 superagent_math.py`，输出见 output.txt。

排队仿真是粗糙模型（泊松到达、单次耗时随 batch 线性增长、每轮合并全部积压），只用来看量级和拐点，不代表 DeepSeek 实测。

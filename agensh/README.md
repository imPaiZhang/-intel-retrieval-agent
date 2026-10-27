# Agensh 数字复算

排长技术专栏《去掉编排器后，Agent 越多越强吗？Agensh 数据拆解》配套脚本。

只用论文 Agensh: Scaling Organizational Intelligence to 1,024 Agents（arXiv:2609.26781v1）公开的数字，复算：

1. 五题均值每个区间的边际收益
2. 拿掉 pandoc 后其余四题的均值（五题均值 ×5 − pandoc，再 ÷4 反推）
3. pandoc 1→1024 的边际收益
4. 按附录 C 错峰启动规则算的累计 Agent·小时
5. 每多 1 个点要多烧的 Agent·小时
6. 1024 个 Agent 单题 token 成本的量级区间（输入 token 速率和单价均为假设，论文未披露成本）

运行：

    python3 agensh_math.py

不依赖第三方库，Python 3.8+ 即可。输出见 output.txt。

注意：论文没有披露重复运行数据，部分差值可能含随机波动；第 6 项只看量级，不是实际账单。

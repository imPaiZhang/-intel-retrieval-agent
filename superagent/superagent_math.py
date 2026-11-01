"""复算 DeepSeek《Super-agent 设计探索》(2026-10-31) 第 7 节公开数字。
只用标准库：python3 superagent_math.py
"""
import random
import statistics

print("== 1. 去掉直通后的 token 账（7.1 节）==")
tok_full, tok_nopass = 2323e4, 3177e4          # 总读缓存 token：2323 万 -> 3177 万
dec_ratio = 1.30                               # Router 决定数 +约 30%
inc = tok_nopass / tok_full - 1
print(f"读缓存 token 增幅 {inc:.1%}（原文：约 37%）")
print(f"按决定数 +30% 摊开，每个决定的 token 变化 {(1+inc)/dec_ratio-1:+.1%}")

print("\n== 2. Router 批处理（7.2 节）==")
pts = {1: (1.0, 2.5, 6.4), 40: (2.8, 3.9, 1.6)}   # 到达速率/分 -> (平均 batch, 单次请求秒, 单个决定分摊秒)
for r, (b, lat, amort) in pts.items():
    naive = lat / b
    print(f"{r:>2} 条/分：单次 {lat}s / batch {b} = {naive:.2f}s；原文分摊 {amort}s；"
          f"差 {amort/naive:.2f} 倍（推断：每个决定不止一次模型请求）")
print(f"原文分摊时间改善 {6.4/1.6:.1f} 倍；只按 单次耗时/batch 算是 {(2.5/1.0)/(3.9/2.8):.2f} 倍")
lat_growth, batch_growth = 3.9 / 2.5, 2.8 / 1.0
print(f"batch 涨 {batch_growth:.1f} 倍，单次耗时涨 {lat_growth:.2f} 倍")

print("\n== 3. 40 条/分 时 Router 有多忙 ==")
rate = 40 / 60                                 # 条/秒
# 读法 A：每个 batch 只发一次请求
req_per_s = rate / 2.8
print(f"读法 A（一个 batch 一次请求）：每分钟 {req_per_s*60:.1f} 次请求 x 3.9s = "
      f"{req_per_s*3.9*60:.0f}s 推理 / 60s，占用率 {req_per_s*3.9:.0%}")
# 读法 B：每个决定分摊 1.6s
print(f"读法 B（按分摊 1.6s/决定）：40 x 1.6 = {40*1.6:.0f}s 推理 / 60s，占用率 {40*1.6/60:.0%}")

print("\n== 4. 用两点拟合 L(b)=a+c*b 做排队仿真（假设：一个 batch 一次请求，泊松到达）==")
c = (3.9 - 2.5) / (2.8 - 1.0)
a = 2.5 - c * 1.0
print(f"拟合：L(b) = {a:.2f} + {c:.2f}*b 秒；理论吞吐上限 1/c = {60/c:.0f} 条/分（b 无穷大时）")

def simulate(per_min, n=20000, seed=7):
    rnd = random.Random(seed)
    lam = per_min / 60
    t, arrivals = 0.0, []
    for _ in range(n):
        t += rnd.expovariate(lam)
        arrivals.append(t)
    i, clock, batches, waits = 0, 0.0, [], []
    while i < n:
        clock = max(clock, arrivals[i])
        j = i
        while j < n and arrivals[j] <= clock:
            j += 1
        b = j - i
        clock += a + c * b
        batches.append(b)
        waits += [clock - x for x in arrivals[i:j]]
        i = j
    return statistics.mean(batches), statistics.mean(waits), sorted(waits)[int(0.95 * len(waits))]

for r in (1, 10, 20, 40, 60, 75):
    mb, mw, p95 = simulate(r)
    print(f"{r:>2} 条/分：平均 batch {mb:.2f}，事件到决定平均 {mw:.1f}s，p95 {p95:.1f}s")

print("\n== 5. 消融实验的样本量（7.1 节）==")
runs, req = 5, 20
n = runs * req
print(f"每种方案约 {n} 个任务完成时间；p95 落在最慢的约 {n - int(0.95*n)} 个上")
print(f"提示优先委派：5 次里 1 次没委派，那一次约占 {req/n:.0%} 的样本，p95 大概率由这一次决定")
print(f"中性提示 p95 / Super-agent p95 = {29.5/15.7:.2f}")

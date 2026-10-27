"""复算 Agensh 论文（arXiv:2609.26781v1）公开数字：边际收益、其余四题均值、错峰启动下的 Agent·小时、每个点的算力账。"""
import math

N = [1, 8, 32, 128]
mean5 = {1: 19.31, 8: 20.68, 32: 26.52, 128: 28.78}          # 论文 3.1 节，五题均值
pandoc = {1: 33.89, 8: 41.75, 32: 43.11, 128: 50.94, 1024: 55.06}  # 论文 3.1 节 / 图 1

print("== 1. 五题均值的边际收益 ==")
for a, b in zip(N, N[1:]):
    d = mean5[b] - mean5[a]
    print(f"{a:>4} -> {b:<4} 人数 x{b//a:<3} 提升 {d:+.2f} 点，每翻一倍 {d/math.log2(b/a):+.2f} 点")
print(f"1 -> 128 共 {mean5[128]-mean5[1]:.2f} 点，相对 {100*(mean5[128]/mean5[1]-1):.1f}%")

print("\n== 2. 拿掉 pandoc，其余四题均值（由 五题均值x5 - pandoc 再 /4 反推）==")
rest = {n: (mean5[n]*5 - pandoc[n]) / 4 for n in N}
for n in N:
    print(f"{n:>4} 个 Agent：其余四题均值 {rest[n]:.2f}%")
print(f"其余四题 1 -> 8：{rest[8]-rest[1]:+.2f} 点；1 -> 128：{rest[128]-rest[1]:+.2f} 点")
print(f"pandoc 1 -> 8：{pandoc[8]-pandoc[1]:+.2f} 点，占五题均值提升 {(pandoc[8]-pandoc[1])/5:.2f}/{mean5[8]-mean5[1]:.2f}")

print("\n== 3. pandoc 的边际收益 ==")
P = [1, 8, 32, 128, 1024]
for a, b in zip(P, P[1:]):
    d = pandoc[b] - pandoc[a]
    print(f"{a:>4} -> {b:<4} 提升 {d:+.2f} 点，每翻一倍 {d/math.log2(b/a):+.2f} 点")

print("\n== 4. 错峰启动下的 Agent·小时 ==")
# 附录 C：第一小时每 30 秒起一个，之后每 3 秒起一个；6 小时到点全部终止
def start(k):  # 第 k 个（从 1 数）的启动秒
    return (k-1)*30 if k <= 120 else 3600 + (k-121)*3
def agent_hours(n):
    return sum(max(0, 6*3600 - start(k)) for k in range(1, n+1)) / 3600
AH = {n: agent_hours(n) for n in P}
for n in P:
    print(f"{n:>4} 个：最后一个在第 {start(n)/60:.1f} 分钟起跑，合计 {AH[n]:.0f} Agent·小时（单 Agent 的 {AH[n]/AH[1]:.0f} 倍）")

print("\n== 5. 每多拿 1 个点，要多烧多少 Agent·小时 ==")
for a, b in zip(N, N[1:]):
    print(f"五题均值 {a:>4} -> {b:<4}：{(AH[b]-AH[a])/(mean5[b]-mean5[a]):7.1f} Agent·小时/点")
for a, b in zip(P, P[1:]):
    print(f"pandoc   {a:>4} -> {b:<4}：{(AH[b]-AH[a])/(pandoc[b]-pandoc[a]):7.1f} Agent·小时/点")

print("\n== 6. token 区间（论文没披露，下面全是假设，只用来看量级）==")
# 每个 Agent 每小时吃多少输入 token：低档 2M、中档 6M、高档 15M（假设：上下文上限 27.2 万，
# 平均上下文 10 万左右，1~2.5 分钟一轮）。单价按每百万输入 token 1/3/5 美元三档（假设）。
for tph in (2e6, 6e6, 15e6):
    row = []
    for n in (1, 128, 1024):
        tok = AH[n]*tph
        row.append(f"{n}个 {tok/1e9:.2f}B")
    print(f"每 Agent 每小时 {tph/1e6:.0f}M：" + "，".join(row))
for price in (1, 3, 5):
    lo, mid, hi = (AH[1024]*t/1e6*price for t in (2e6, 6e6, 15e6))
    print(f"单价 ${price}/M：1024 个跑一题 ≈ ${lo:,.0f} ~ ${hi:,.0f}（中档 ${mid:,.0f}）")

print("\n== 7. 换模型 vs 加人（pandoc）==")
print(f"GPT-5.6-sol 1024 个 Agent：55.06%；GPT-6.1-sol 1 个 Agent：56.19%（README）；GPT-6.1-sol 32 个：79.59%")
print(f"同样 1 个 Agent，换模型提升 {56.19-33.89:.2f} 点；同一模型 1->1024 提升 {55.06-33.89:.2f} 点")

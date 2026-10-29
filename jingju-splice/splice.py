"""把一段真人京剧插进 Suno 纯音乐：找插入点 → 对齐拍点 → 响度对齐 → 交叉淡化插入。
用法：python3 splice.py inst.mp3 opera.mp3 out.wav [--near 秒数]
依赖：pip install librosa soundfile pyloudnorm（另需系统装 ffmpeg 读 mp3）"""
import sys, argparse, numpy as np, librosa, soundfile as sf, pyloudnorm as pyln

p = argparse.ArgumentParser()
p.add_argument("inst"); p.add_argument("opera"); p.add_argument("out")
p.add_argument("--near", type=float, default=None, help="大概想插在第几秒，不填就自动找")
p.add_argument("--fade", type=float, default=0.3, help="交叉淡化秒数")
p.add_argument("--bar-align", action="store_true", help="把京剧补齐到整小节，让后段鼓点回到原来的拍子相位")
a = p.parse_args()

# 1. 读音频，统一采样率和声道（本例 Suno 导出 48k，京剧那段是 24k）
inst, sr = librosa.load(a.inst, sr=None, mono=False)
opera, _ = librosa.load(a.opera, sr=sr, mono=False)          # 重采样到伴奏的采样率
if inst.ndim == 1: inst = np.stack([inst, inst])
if opera.ndim == 1: opera = np.stack([opera, opera])
mono = inst.mean(axis=0)
print(f"伴奏 {inst.shape[1]/sr:.2f}s，京剧 {opera.shape[1]/sr:.2f}s，采样率 {sr}")

# 2. 拍点和段落边界
tempo, beats = librosa.beat.beat_track(y=mono, sr=sr, units="time")
tempo = float(np.atleast_1d(tempo)[0])
chroma = librosa.feature.chroma_stft(y=mono, sr=sr)
bounds = librosa.frames_to_time(librosa.segment.agglomerative(chroma, 10), sr=sr)
print(f"BPM {tempo:.1f}，一拍 {60/tempo:.3f}s，一小节(4拍) {240/tempo:.2f}s")
print("段落边界:", np.round(bounds, 1))

# 3. 选插入点：指定了 --near 就找离它最近的段落边界；否则找能量最低的那个边界
def rms_db(t, w=2.0):
    s = mono[int(t*sr):int((t+w)*sr)]
    return 20*np.log10(np.sqrt(np.mean(s**2)) + 1e-9)
cands = [b for b in bounds if 10 < b < inst.shape[1]/sr - 10]
if a.near is not None:
    seg = min(cands, key=lambda b: abs(b - a.near))
else:
    seg = min(cands, key=rms_db)
cut = beats[np.argmin(np.abs(beats - seg))]                   # 吸附到最近的拍点
print(f"段落边界 {seg:.2f}s → 吸附拍点 {cut:.3f}s（该处能量 {rms_db(cut):.1f} dB）")

# 4. 响度对齐：让京剧和插入点前 8 秒的伴奏一样响（按 LUFS）
meter = pyln.Meter(sr)
ref = inst[:, int((cut-8)*sr):int(cut*sr)].T
l_ref, l_op = meter.integrated_loudness(ref), meter.integrated_loudness(opera.T)
gain = l_ref - l_op
opera = opera * (10 ** (gain/20))
print(f"伴奏局部 {l_ref:.1f} LUFS，京剧 {l_op:.1f} LUFS，京剧增益 {gain:+.1f} dB")

# 4.5 可选：补齐整小节。插入长度 = 京剧长度 - 2×淡化，补到小节长度的整数倍
if a.bar_align:
    bar = 240 / tempo
    ins = opera.shape[1]/sr - 2*a.fade
    target = np.ceil(ins / bar) * bar
    pad = int(round((target - ins) * sr))
    opera = np.concatenate([opera, np.zeros((2, pad))], axis=1)   # 末尾补一点空白，让京剧尾音自然收
    print(f"插入 {ins:.2f}s = {ins/bar:.2f} 小节 → 补到 {target/bar:.0f} 小节，尾部补 {pad/sr:.2f}s")

# 5. 插入（不是覆盖）：前段 + 京剧 + 后段，两个接口各做等功率交叉淡化
f = int(a.fade * sr); c = int(cut * sr)
th = np.linspace(0, np.pi/2, f)
fin, fout = np.sin(th), np.cos(th)                          # 等功率曲线：sin²+cos²=1，接口处总能量不塌
head, tail = inst[:, :c], inst[:, c:]
j1 = head[:, -f:]*fout + opera[:, :f]*fin
j2 = opera[:, -f:]*fout + tail[:, :f]*fin
out = np.concatenate([head[:, :-f], j1, opera[:, f:-f], j2, tail[:, f:]], axis=1)

peak = np.max(np.abs(out))
if peak > 0.99: out = out * 0.99 / peak; print(f"峰值 {peak:.2f} 超了，整体压到 0.99")
sf.write(a.out, out.T, sr)
print(f"输出 {a.out}：{out.shape[1]/sr:.2f}s（= 伴奏 + 京剧 - 2×淡化），京剧位于 {cut:.2f}s – {cut+opera.shape[1]/sr-2*a.fade:.2f}s")

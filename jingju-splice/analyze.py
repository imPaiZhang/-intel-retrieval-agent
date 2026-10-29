import librosa, numpy as np, pyloudnorm as pyln, soundfile as sf
y, sr = librosa.load("inst.mp3", sr=None, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
print("时长 %.2fs  sr %d  BPM %.1f  拍点数 %d" % (len(y)/sr, sr, float(np.atleast_1d(tempo)[0]), len(beats)))
# 每 2 秒 RMS 能量曲线，找"留白"
hop=sr*2
rms=[20*np.log10(np.sqrt(np.mean(y[i:i+hop]**2))+1e-9) for i in range(0,len(y),hop)]
for i,r in enumerate(rms): print(f"{i*2:4d}s {r:6.1f} dB " + "#"*int(max(0,r+40)))
# 鼓还在吗：onset 强度
oenv=librosa.onset.onset_strength(y=y,sr=sr)
t=librosa.times_like(oenv,sr=sr)
for a in range(0,int(len(y)/sr),4):
    m=(t>=a)&(t<a+4); print(f"onset {a:3d}-{a+4:3d}s 均值 {oenv[m].mean():.2f}")
meter=pyln.Meter(sr)
for f in ["inst.mp3","opera.mp3"]:
    x,s=sf.read(f) if f.endswith('wav') else librosa.load(f,sr=None,mono=False)
    x=x.T if x.ndim>1 else x
    print(f, "LUFS %.1f" % pyln.Meter(s).integrated_loudness(x))
yo,so=librosa.load("opera.mp3",sr=None)
to,bo=librosa.beat.beat_track(y=yo,sr=so,units="time")
print("京剧 时长 %.2f sr %d 估计BPM %.1f"%(len(yo)/so,so,float(np.atleast_1d(to)[0])))
# 段落边界
S=np.abs(librosa.stft(y)); chroma=librosa.feature.chroma_stft(S=S,sr=sr)
bounds=librosa.segment.agglomerative(chroma,10); print("段落边界(s):",np.round(librosa.frames_to_time(bounds,sr=sr),1))
np.save("beats.npy",beats)

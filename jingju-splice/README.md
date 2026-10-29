# jingju-splice：把真人京剧唱段插进 Suno 纯音乐

配套文章：《Suno 唱不像京剧，我把真唱段拼进去》（排长技术专栏）。

## 安装
```bash
pip install librosa soundfile pyloudnorm   # 读 mp3 还需要系统装 ffmpeg
```

## 用法
```bash
python3 analyze.py                      # 先看：BPM、能量曲线、段落边界（默认读 inst.mp3 / opera.mp3）
python3 splice.py inst.mp3 opera.mp3 out.wav --near 112 --bar-align
```
- `--near`：大概想插在第几秒，脚本会吸到最近的段落边界和拍点；不填就选能量最低的边界（往往不是你想要的位置，建议填）。
- `--bar-align`：把京剧补齐到整小节，后段鼓点回到原来的拍子相位。
- `--fade`：交叉淡化秒数，默认 0.3。

做法：插入不是覆盖；京剧响度按插入点前 8 秒伴奏的 LUFS 对齐；两个接口等功率交叉淡化。

音频文件不在仓库里，请用自己有权使用的录音。

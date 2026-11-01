### Phase 0ag: Clip Assembly（多源视频安全拼接）

片头、主片、生成片和片尾来自不同画布、方向、帧率、SAR、时间戳、采样率或声道数时，用 `clip_assembly.py` 代替 concat copy。按最终播放顺序传入每条唯一源片；同一片重复使用 `loop_fill.py`。

```bash
python3 scripts/clip_assembly.py plan \
  origin/intro.mp4 origin/main.mov origin/outro.mp4 \
  --width 1080 --height 1920 --fps 30 \
  --fit contain --audio-mode fill-silence \
  --delivery output/assembled.mp4 \
  --boundary-proof verify/clip-assembly-boundaries.mp4 \
  --project-dir . \
  --output work/clip_assembly_plan.json \
  --markdown work/clip_assembly_plan.md
python3 scripts/clip_assembly.py apply work/clip_assembly_plan.json
```

脚本在一条 FFmpeg filter graph 内统一 PTS、画布、rotation、CFR、SAR 1:1、`yuv420p` 和 48 kHz stereo，再 hard cut 输出 H.264/AAC。至少一段有音频时，无音轨片段用等长静音保持 A/V coverage；完全不需要声音时用 `--audio-mode drop`。已有音轨与视频首尾失配或 HDR/BT.2020/>8-bit 会在 plan 阶段停止。

apply 通过总时长、尺寸、帧率、decoded cadence、SAR、音画首尾和完整解码后才原子提升，并从确切交付件生成覆盖所有接缝的正常速度 proof。完整播放 delivery 和 proof 后，对 clip order、visual seams、frame continuity、audio seams、complete coverage 全部做出可观察结论，再 `confirm` 和 `verify --strict`。本工具不发明转场或语义连续性；需要 J-cut/L-cut 时走独立 audio transition 计划。详见 [Clip Assembly](./docs/prompts/118-clip-assembly.md)。

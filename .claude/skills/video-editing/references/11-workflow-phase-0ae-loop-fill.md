### Phase 0ae: Loop Fill（短背景 / 环境片填满固定时长）

需要把短视频重复到指定次数或固定 slot 时，用 `loop_fill.py plan` 绑定 progressive CFR 源片、目标、交付件和首个真实接缝 proof。它保留或显式丢弃源音频，重复时音画一起推进；不自动加 crossfade，也不会把任意首尾包装成无缝循环。

```bash
python3 scripts/loop_fill.py plan origin/ambient.mp4 \
  --duration 00:30 \
  --audio-mode drop \
  --delivery work/ambient-30s.mp4 \
  --seam-proof verify/ambient-loop-seam.mp4 \
  --project-dir . \
  --output work/loop_fill_plan.json \
  --markdown work/loop_fill_plan.md
python3 scripts/loop_fill.py apply work/loop_fill_plan.json
```

正常速度看完 seam proof 与完整 delivery；确认画面接缝、运动连续性、重复闪帧、声音接缝和 slot 覆盖后运行 `confirm`，再用 `verify --strict` 或 `pipeline_manifest.py --require loop_fill_plan --strict` 放行。VFR 先跑 `frame_rate_conform.py`，HDR/BT.2020/>8-bit 先确定 `hdr_sdr.py` 色彩路径。详见 [Loop Fill](./docs/prompts/117-loop-fill.md)。

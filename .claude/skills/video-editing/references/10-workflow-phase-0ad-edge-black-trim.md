### Phase 0ad: Edge-black Trim（片头 / 片尾黑场可选）

采集卡、相机预录或转码文件的首尾出现黑场时，用 `black_edge_trim.py plan` 运行 FFmpeg `blackdetect`；默认还会用 `silencedetect` 核对确切移除范围至少 95% 为静音，只考虑接触时间线头尾的区间，中间黑场保持不变。

```bash
python3 scripts/black_edge_trim.py plan origin/capture.mp4 \
  --delivery work/capture-edge-trimmed.mp4 \
  --edge-proof verify/capture-edge-proof.mp4 \
  --audio-policy silent_only \
  --project-dir . \
  --output work/black_edge_trim_plan.json \
  --markdown work/black_edge_trim_plan.md
python3 scripts/black_edge_trim.py apply work/black_edge_trim_plan.json
```

脚本保留默认 0.08 秒视觉 padding，对音画执行相同 source-time trim，输出 H.264/yuv420p CFR 与可选 48 kHz AAC；媒体合同和完整解码通过后才原子提升。edge proof 来自原片，包含拟议删除区与紧邻内容。完整 1× 看完 proof 和 delivery，确认首尾帧、内容覆盖与声音连续后运行 `confirm`，再执行 `verify --strict`。确知黑画面里的声音也应删除时可显式使用 `--audio-policy allow_audible`，该 override 保留 warning。详见 [Edge-black Trim](./docs/prompts/119-black-edge-trim.md)。

长节目或录制母版需要找内部段落边界时，运行 `program_breaks.py analyze <video> --output work/program_breaks.json`；它只标出内部 `blackdetect` 与**每条音轨** `silencedetect` 同时成立的重叠区间，默认取重叠中点作复核时间。用 `verify <report.json>` 重扫源片并核对 JSON/Markdown。候选不是已批准的切点；逐处正常速度看听后再决定分段，尤其要检查淡入淡出、黑底字幕和有声过场。无音轨素材无法证明静音，会明确拒绝。

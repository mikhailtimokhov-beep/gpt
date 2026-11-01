### Phase 2.6b: Multimodal Dead-Air（静音 + 静帧保守去死区，可选）

如果纯音频 `jump_cut.py` 可能误删仍有表情、手势、产品展示或屏幕操作的停顿，改用音频静音与画面静帧的 AND gate：

```bash
python3 scripts/multimodal_dead_air.py plan origin/talking.mp4 \
  --delivery work/talking-dead-air-tight.mp4 \
  --output work/multimodal_dead_air_plan.json \
  --markdown work/multimodal_dead_air_plan.md \
  --strict
python3 scripts/multimodal_dead_air.py verify work/multimodal_dead_air_plan.json --strict
DEAD_AIR_CUT_COUNT="$(python3 -c 'import json; print(len(json.load(open("work/multimodal_dead_air_plan.json"))["removed_segments"]))')"
python3 scripts/timeline_view.py origin/talking.mp4 \
  --cut-list work/multimodal_dead_air_plan.json \
  --output-dir verify/dead-air-cuts \
  --limit "$DEAD_AIR_CUT_COUNT"
python3 scripts/multimodal_dead_air.py apply work/multimodal_dead_air_plan.json \
  --markdown work/multimodal_dead_air_plan.md
```

默认只有静帧覆盖静音至少 60% 才入选，并且只删除二者交集；80ms padding、30ms 音频 fade 和 20% 删除预算继续生效。计划绑定源 SHA-256 和媒体契约，apply 使用临时 MP4，并在 H.264/AAC、`yuv420p`、尺寸、帧率、采样率、声道、时长和完整解码全部通过后原子提升。`timeline_view.py` 默认只看 20 个切点，因此必须像上面一样把本计划的实际删除段数传给 `--limit`；若计数为 0，停止并保留原片。它不理解表演、语义或有意留白；所有源切点仍须先看，输出仍须 1× 带声音完整复核。详见 [docs/prompts/88-multimodal-dead-air.md](docs/prompts/88-multimodal-dead-air.md)。

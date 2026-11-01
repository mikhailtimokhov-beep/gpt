### Phase 2a: Adaptive Scene Boundaries（自适应视觉场景边界）

长视频拆条、抽样理解或成片节奏分析前，优先为运动镜头生成自适应场景边界：

```bash
python3 scripts/scene_boundaries.py video.mp4 \
  --method adaptive \
  --adaptive-threshold 3.0 \
  --min-scene-score 0.15 \
  --min-scene-duration 1.0 \
  --output work/scene_boundaries.json \
  --markdown work/scene_boundaries.md
```

`adaptive` 把每帧 FFmpeg scene score 与前后邻域均值比较，可减少持续摇镜、运动或闪烁造成的密集误切；`boundary_evidence[]` 保留 score、adaptive ratio 和邻域均值，必须先看 Markdown 再交给 `highlight_picker.py --scene-boundaries`。需要复现旧流程或固定机位素材时，用 `--method fixed --threshold 0.35`。

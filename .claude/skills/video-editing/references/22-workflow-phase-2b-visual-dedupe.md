### Phase 2b: Visual Dedupe（跨素材重复镜头复核）

多机位、多 take、重复转码或 B-roll 候选进入时间线前，用 `visual_dedupe.py` 对多个 source 的场景做三点感知哈希复核：

```bash
python3 scripts/visual_dedupe.py \
  --manifest work/visual_dedupe_sources.json \
  --output work/visual_dedupe.json \
  --markdown work/visual_dedupe.md \
  --strict
```

manifest 的 `sources[]` 为每个来源提供 `id`、`video`、可选 `scene_boundaries` 和 `quality_score`；相对路径以 manifest 目录为基准。脚本默认只比较不同来源，要求 10%/50%/90% 至少两个采样点匹配，并把 `quality_score`、分辨率和文件大小用于保留建议。它只输出 review artifact，绝不删除或移动源素材。发现重复组时，先人工查看 source range，再从下游 edit plan 排除确认重复的候选。

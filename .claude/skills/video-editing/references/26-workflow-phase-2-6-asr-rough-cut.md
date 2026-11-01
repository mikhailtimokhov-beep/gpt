### Phase 2.6: ASR Rough Cut（口头禅/重复句粗剪，可选）

如果 transcript 中纯口头禅、卡壳重说或相邻重复句较多，先用 [rough_cut.py](./scripts/rough_cut.py) 生成可审计粗剪计划：

```bash
python3 scripts/rough_cut.py --transcript work/transcript.json --cut-list work/rough_cut.json
```

确认计划后可直接渲染粗剪版：

```bash
python3 scripts/rough_cut.py \
  --transcript work/transcript.json \
  --input origin/talking.mp4 \
  --output output/talking.roughcut.mp4 \
  --cut-list work/rough_cut.json
```

`rough_cut.py` 会输出 `decisions` / `removed_segments` / `keep_segments` / `speedup_ratio`。它不调用 LLM，不提交任何付费任务；只用 `transcribe.py --detect-fillers` 的 filler metadata 和相邻文本相似度做保守粗剪。渲染前用 `timeline_view.py --cut-list work/rough_cut.json` 看源素材删除段；渲染后用 `--rendered-cut-list work/rough_cut.json` 看成片实际拼接点。

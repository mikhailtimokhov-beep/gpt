### Phase 5c: NLE Handoff EDL / FCPXML / OTIO（交给 Premiere / FCP / Resolve）

如果用户不需要剪映草稿，而是要把自动剪辑方案交给专业剪辑软件做调色、混音、精剪或协作复核，可导出单轨 EDL、单 spine FCPXML 或 OpenTimelineIO `.otio`：

```bash
python3 scripts/export_edl.py --config render_config.json --output work/edit.edl --fps 30
python3 scripts/export_edl.py --cut-list work/rough_cut.json --output work/rough_cut.edl --fps 30
python3 scripts/export_fcpxml.py --config render_config.json --output work/edit.fcpxml --fps 30 --width 1080 --height 1920
python3 scripts/export_fcpxml.py --cut-list work/rough_cut.json --output work/rough_cut.fcpxml --fps 30
python3 scripts/export_otio.py --config render_config.json --output work/edit.otio --fps 30
python3 scripts/export_otio.py --cut-list work/rough_cut.json --output work/rough_cut.otio --fps 30
```

`export_edl.py` / `export_fcpxml.py` / `export_otio.py` 都会同时写 `<output>.json` manifest，保留绝对源路径、精确秒数、record/source timecode 和事件清单。`export_otio.py` 默认写 V1 + A1 两条 track，可用 `--no-audio-track` 只交接视频；复杂字幕、overlay、章节卡、B-roll 仍以 `render_final.py` / `export_capcut.py` 为准；NLE handoff 只负责轻量选段时间线。

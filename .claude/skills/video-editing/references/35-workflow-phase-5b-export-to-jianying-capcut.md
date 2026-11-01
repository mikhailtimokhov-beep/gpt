### Phase 5b: Export to JianYing / CapCut（导出剪映工程）

如果用户希望在剪映中继续编辑（添加特效、调色、精修转场等），可以将剪辑方案**直接导出为剪映工程文件**，无需 ffmpeg 渲染：

```bash
python3 scripts/export_capcut.py --config render_config.json --output ./my_draft
```

**导出内容**：
- **视频轨道**：所有选定的片段按顺序排列在主视频轨道上，包含片头封面（冻结首帧或自定义封面图）
- **字幕轨道**：每个片段的转录文字作为独立字幕段落，位于画面下方
- **文字轨道**：封面标题、副标题、结尾卡片文字（与字幕分离，便于单独编辑）
- **音频轨道**：背景音乐（BGM），自动设置音量
- **转场**：片段之间自动添加淡入淡出转场（300ms）
- **B-roll**：支持 B-roll 替换画面（使用 broll 路径作为视频源）

参数说明：
- `--config`：渲染配置 JSON 路径（与 render_final.py 共用同一个 render_config.json）
- `--output`：输出文件夹路径（会创建 draft_content.json 和 draft_meta_info.json）
- `--name`：项目名称（默认使用配置中的标题）

**使用方式**：
1. 将导出的文件夹复制到剪映草稿目录：
   - macOS: `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/`
   - Windows: `%APPDATA%/JianyingPro/User Data/Projects/com.lveditor.draft/`
2. 打开剪映，在"草稿"列表中即可看到该项目
3. 在剪映中可继续添加特效、调整转场、调色、导出等

**注意**：
- 导出的工程文件使用**绝对路径**引用视频/音频素材，确保素材文件不要移动位置
- 支持剪映专业版（JianyingPro）；剪映 6+ 版本均可打开生成的草稿
- 此功能与 Phase 5（ffmpeg 渲染）**二选一**：如果用户只需要最终视频，用 render_final.py；如果需要进一步在剪映中编辑，用 export_capcut.py

如果字幕已经在剪映/CapCut 里用 Auto Captions 生成并人工校对过，可以反向导入为本项目 transcript：

```bash
python3 scripts/import_capcut_subtitles.py \
  --draft ~/Movies/JianyingPro/User\ Data/Projects/com.lveditor.draft/day58 \
  --transcript work/capcut_transcript.json \
  --cut-list work/capcut_gap_cut.json \
  --markdown work/capcut_subtitles.md \
  --source-media origin/talking.mp4
```

也可以导入剪映导出的 SRT：

```bash
python3 scripts/import_capcut_subtitles.py \
  --srt exports/capcut_auto_captions.srt \
  --transcript work/capcut_transcript.json \
  --srt-output output/subtitles/capcut_clean.srt
```

`--cut-list` 用字幕间隙生成 `keep_segments`，适合先用 `timeline_view.py --cut-list` 复核，再交给 `export_edl.py` 或后续粗剪流程。默认只读取 subtitle 材料；如果草稿把自动字幕存为普通文字轨，再加 `--include-overlays`。

如果已经有 SRT 和人工/agent 写好的字幕编号编辑意见，用 `srt_edit_plan.py` 直接生成可复核剪辑方案：

`work/edit_guide.md` 示例：

```md
title: 发布会高光
platform: xhs
keep 3-5: 先用产品发布和用户反应
drop 1-2: 铺垫太慢
keep 8: 补一句核心结论
```

```bash
python3 scripts/srt_edit_plan.py \
  --srt exports/capcut_auto_captions.srt \
  --guide work/edit_guide.md \
  --source-media origin/talking.mp4 \
  --output work/srt_edit_plan.json \
  --render-config work/render_config.json \
  --cut-list work/srt_edit_cut.json \
  --markdown work/srt_edit_plan.md \
  --strict
```

`keep/include/use/select` 行按出现顺序生成最终输出顺序；`drop/skip/exclude/remove` 行写入 review。`--cut-list` 输出按原素材时间排序，适合 `timeline_view.py --cut-list` 看切点；真正的重排序输出看 `--render-config`。需要强制每个字幕编号都被审过时，加 `--require-all-reviewed --strict`。

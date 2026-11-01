### Phase 2a: Video Keyframe Extraction（视频关键帧提取）

对于口播类视频（尤其是在户外行走中拍摄的、带有环境音的素材），仅靠音频转录无法了解视频的视觉内容。使用 [extract_keyframes.py](./scripts/extract_keyframes.py) 提取视频关键帧并生成时序图，以便全面理解视频内容：

拿到场景检测、字幕或审片时间码时，先运行 `frame_grid.py locate origin/clip.mp4 --at-seconds 20.4`，读取 `nearest.decoded_frame` 和相邻两帧的真实 PTS。再以该帧附近为 `--start-frame` 运行 `frame_grid.py grid origin/clip.mp4 --start-frame 240 --step 2 --count 16 --output verify/grid.png --receipt verify/grid.json`。PNG 中的 `CELL 1` 等标记与 JSON 的 `cell` 对应；找到目标后运行 `frame_grid.py frame origin/clip.mp4 --start-frame 250 --output verify/frame.png --receipt verify/frame.json` 导出确切帧。交接前用 `verify <receipt>` 核对源片、PNG 和映射收据。定位和抽帧都从头顺序解码，长片深处查询会耗时；网格最多 36 格，格图不能代替正常速度播放。

```bash
python3 scripts/extract_keyframes.py "<video_path>"
```

参数说明：
- `--max-frames 16`：最大关键帧数量（默认 16）
- `--threshold 0.4`：场景变化检测灵敏度（0.0-1.0，越低提取越多关键帧，默认 0.4）
- `--cols 4`：时序图网格列数（默认 4）
- `--thumb-width 320`：缩略图宽度（默认 320px）
- `--output-dir`：关键帧输出目录（默认 `<video_name>_keyframes/`）
- `--no-storyboard`：仅提取关键帧，不合成时序图

输出：
- `<video_name>_keyframes/` — 各关键帧 PNG 图片（带时间戳命名）
- `<video_name>_storyboard.png` — 合成的时序图（网格布局 + 时间戳标注）
- `<video_name>_keyframes.json` — 关键帧元数据（时间戳、帧号、文件路径）

**为什么需要关键帧提取**：
- 口播视频经常在走路中拍摄，画面中的场景变化（街道→公园→咖啡店）是重要的叙事线索
- 时序图让 AI 可以同时看到音频内容（transcript）和视觉内容（keyframes），做出更好的选片判断
- 可以发现纯音频分析无法捕捉的信息：肢体语言、表情变化、环境切换、产品展示等

**典型工作流**：
```bash
# 1. 提取音频并转录
python3 scripts/extract_audio.py video.mp4
python3 scripts/transcribe.py video_audio.wav --model auto --language zh --detect-fillers

# 2. 提取关键帧生成时序图
python3 scripts/extract_keyframes.py video.mp4

# 3. 把每帧与前后 3 秒内的原话对齐，查看索引并核验来源
python3 scripts/visual_transcript_index.py build video_keyframes.json video_transcript.json \
  --output work/visual_transcript_index.json --markdown work/visual_transcript_index.md
python3 scripts/visual_transcript_index.py verify work/visual_transcript_index.json
```

索引每帧最多展示 8 段原话，并标明截断；`--radius` 可设 0.1–30 秒，`--max-segments` 可设 1–12。画面是抽样帧，原话是附近时间窗口，不能据此断言画面中出现了某件事，也不能代替原片完整播放。源视频、关键帧元数据、图片、转写或 Markdown 改动后需重新构建索引。

教程成片需要图文伴读稿时，先人工核对 `chapter_markers.py` 导出的章节标题、边界和说明，再运行 `tutorial_companion.py build output/master.mp4 output/chapters/chapters.json work/transcript.json --title "教程标题" --output output/companion`。每章默认在中点截取一张图；若中点为过场，用 `--at ch01=12.5` 指定该章内更合适的时间。`verify output/companion/receipt.json` 检查源片、章节、转写、截图和 Markdown 字节；生成状态只表示草稿已建立。逐章看图、听原片，确认截图确实展示该步骤、说明没有超出证据后再对外交付。伴读稿最多 24 章、每章列出 6 段原话，超出会标明遗漏数。

**AI Agent 综合分析要点**：
- 将关键帧时序图与转录文本对照，标注每个时间段的「说了什么 + 画面是什么」
- 找出画面与语音最匹配的高质量片段（如：讲到"这家店"时画面正好对着店铺）
- 识别画面模糊、遮挡、光线不佳的片段，建议跳过
- 户外拍摄时，注意画面抖动严重的片段，在选片时降低优先级

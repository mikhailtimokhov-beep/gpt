### Phase 0: Media Library Setup（素材库初始化）

首次使用时，帮助用户建立素材目录结构：

```bash
python3 scripts/media_library.py init [project_dir]
```

这会创建以下目录结构：
```
media/
├── raw/      — 原始素材（摄像机/手机直出的视频）
├── broll/    — B-roll 素材（城市街景、产品特写等）
├── bgm/      — 背景音乐（MP3/WAV/M4A）
├── assets/   — 叠加素材（水印 PNG、Logo 等）
└── output/   — 输出目录
```

**询问素材来源**：
1. 询问用户的视频文件位置（本地路径、外部设备或云端）
2. 建议将原始素材复制/移动到 `media/raw/` 目录
3. 询问是否有 B-roll、BGM 等辅助素材
4. 如果用户视频散落在多个目录，建议先集中到 `media/raw/`

**扫描并建立索引**：
```bash
python3 scripts/media_library.py scan [project_dir]
```

索引系统会自动：
- 扫描所有视频/音频/图片文件
- 提取时长、分辨率、帧率等元数据
- 关联已有的 transcript 文件
- 小型项目（< 200 文件）使用 JSON 索引（`media_index.json`）
- 大型项目自动升级为 SQLite 索引（`media_index.db`）
- 手动升级：`python3 scripts/media_library.py upgrade`

**查看素材库状态**：
```bash
python3 scripts/media_library.py status
```

**搜索素材**：
```bash
python3 scripts/media_library.py search "关键词"
```

**推荐 B-roll 候选**：
```bash
python3 scripts/media_library.py recommend "AI workflow dashboard" \
  --project-dir . \
  --category broll \
  --target-duration 3 \
  --target-aspect 9:16 \
  --json
```

推荐结果包含 `score`、`reasons`、`absolute_path`，用于人工/agent 先确认再写入 `render_config` 或 `enrich_plan`。默认过滤已经不存在的索引文件；需要清理 stale index 时可加 `--include-missing`。

**本地素材不足时规划 stock 查询**：
```bash
python3 scripts/stock_material_plan.py \
  --subject "AI workflow automation" \
  --script work/transcript.json \
  --provider pexels \
  --provider pixabay \
  --provider coverr \
  --media-library . \
  --output work/stock_material_plan.json \
  --markdown work/stock_material_plan.md
```

`stock_material_plan.py` 只生成 `stock_material_plan.v1` 和 Markdown review，不联网、不下载、不消耗额度。它借鉴 MoneyPrinterTurbo 的 `video_terms` / Pexels / Pixabay / Coverr / `video_count` 素材规划方式，但保持本 skill 的 artifact-first 风格。

**下载或客户给的素材确认授权后登记**：
```bash
python3 scripts/media_library.py import /path/to/downloaded.mp4 \
  --project-dir . \
  --category broll \
  --copy \
  --provider pexels \
  --source-url "https://www.pexels.com/video/demo-123/" \
  --creator "Demo Creator" \
  --license "Pexels License" \
  --tag "workflow,dashboard"

python3 scripts/media_library.py annotate media/broll/downloaded.mp4 \
  --project-dir . \
  --source-url "https://example.com/source" \
  --license "owned" \
  --tag "client-approved"
```

登记后的 `provider`、`source_url`、`creator`、`license` 会进入 `media_index.json/db`，后续由 `asset_provenance.py` 做发布门禁。

---
name: video-editing
description: "Short-form video editing workflow (talking-head, voice-over, tutorials, interviews, screen recordings): ingest, transcription, rough cut, B-roll, captions, audio mix, render, QA and platform exports (Xiaohongshu/Douyin-tuned). Use for multi-step edits of real footage."
metadata: { "openclaw": { "emoji": "🎬", "os": ["darwin", "linux", "win32"], "requires": { "bins": ["ffmpeg", "python3"] }, "install": [{ "id": "ffmpeg-brew", "kind": "brew", "formula": "ffmpeg", "bins": ["ffmpeg"], "label": "Install FFmpeg (brew)" }] } }
---

# Video Editing Skill — 视频剪辑技能（V3）

适配 **小红书 / 抖音 / 微信视频号** 三大主流平台。一条 **从素材导入 → 口播 → 重组故事 → 平台守门 → 自动丰富 → 渲染 → 三平台导出 → 标题文案** 的端到端流水线，按各平台的算法、比例、时长、审核规则调过参——不只是剪辑工具。

## V3 完整流水线（一图看懂）

```
口播音频 + 无声素材
   │
   ├─→ project_bootstrap.py     原始素材目录 → source inventory / project.md
   ├─→ edit_brief_plan.py       用户一句话需求 → 本地脚本 runbook / gates
   ├─→ runtime_preflight.py     workflow profile → FFmpeg/Node 命令、编码器、filters / live gate
   ├─→ interlace_conform.py     交错/telecine 采样 → progressive 工作副本 / 全长 A/B gate
   ├─→ frame_rate_conform.py    手机/录屏 VFR → 全量 PTS 检测 / CFR 工作副本 / live gate
   ├─→ black_edge_trim.py       首尾黑场 + 静音覆盖 → CFR 工作副本 / 原片边界 proof + live gate
   ├─→ program_breaks.py        内部黑场与全音轨静音重叠 → 只读分段候选 / 复核时间点
   ├─→ border_crop.py           画面内持续黑边 → 逐时点 cropdetect 证据 / 保守裁切建议
   ├─→ motion_center.py         局部像素运动中心 → 只读构图复核时间点
   ├─→ loop_fill.py             短片 → 次数/固定时长 hard repeat / 真实接缝 proof + 完整审片 gate
   ├─→ ping_pong_loop.py        短动作 → 端帧去重正放/倒放 / 折返+循环双 proof / live gate
   ├─→ clip_assembly.py         多源片段 → 单次画布/CFR/SAR/音频归一 / 全接缝 proof + live gate
   ├─→ edit_style_profile.py    个人/品牌创意方向、节奏与渲染/文案默认值 → 可移植 profile
   ├─→ production_authorization.py
   │                            确切素材/动作/provider/权利依据 → 显式授权 + live gate
   ├─→ transcribe.py            转写 + 词级时间戳 + 口误标记
   ├─→ transcript_silence_qa.py 原始转写 vs 实测静音 → 幻觉疑点供回听
   ├─→ transcript_lookup.py     原话检索 / 时间窗口读取 → 少量带源时间码的结果
   ├─→ visual_transcript_index.py
   │                            现有关键帧 + 附近原话 → 带源哈希的 JSON/Markdown 复核索引
   ├─→ semantic_transcript_review.py
   │                            全篇前后文审校包 / 最小补丁验证 / 人工 choices gate
   ├─→ transcript_review.py     本地同步媒体 HTML 校稿 / CPS 提示 / review.txt 回写
   ├─→ takes_pack.py            多 take / Scribe transcript → phrase-level 阅读视图
   │                            speaker / audio_event 编辑节拍
   ├─→ script_alignment.py      已审目标稿 → 多 take 原话候选 / choices / render_config
   │                            词/段边界 / 透明分数 / 歧义与缺素材 gate
   ├─→ audio_sync.py            外录音轨自动对齐 / 替换音轨计划
   ├─→ multicam_sync.py         多机位 → 参考时间线 / 时钟漂移证据 / 对齐预览 gate
   ├─→ multicam_switch.py       已同步机位 → 归一化说话者音频 / 自动导播草稿 / 完整审片 gate
   ├─→ scene_boundaries.py      fixed/adaptive 视觉切点 + 逐切点 evidence
   ├─→ visual_dedupe.py         多来源场景 → 感知哈希重复组 / 保留建议 / review gate
   ├─→ video_understanding.py   抽样帧 + 可选 YOLO 检测 / tracks / scene_tags
   ├─→ video_stabilization.py   手持素材 → source-bound 后端计划 / 工作副本 / 全长 A/B gate
   ├─→ chroma_key.py            绿幕/蓝幕 → composite + matte 代表帧 / 人工 review / 完整渲染 gate
   ├─→ highlight_picker.py      长视频精华候选 / brief-query 定向找片段
   ├─→ audio_boundary_snap.py   已选片段 → 词/句末/静音边界校正
   ├─→ shorts_batch.py          精华候选 → per-short render_config / render + QA job sheet
   ├─→ rough_cut.py             ASR 粗剪：去纯口头禅 / 相邻重复句
   ├─→ hook_variants.py         前三秒 hook 批量角度 / 推荐排序 / 风险检查
   ├─→ rewrite_script.py        LLM 重组 5 段式（hook/pain/turn/value/cta）
   ├─→ content_guard.py         80+ 条平台雷区 lint
   ├─→ source_receipts.py       事实 claim → URL/截图 source deck + publish gate
   ├─→ beat_sync.py             BGM beat-grid → 可审计剪辑骨架，或吸附已有切点
   ├─→ speed_ramp.py            impact ranges → source-bound 局部变速计划 / 验证 / apply
   ├─→ freeze_punch.py          impact frame → 定格替换窗口 / punch crop / unchanged audio timeline gate
   ├─→ auto_enrich.py           B-roll / 章节卡 / 贴纸 / 强调点 / BGM 卡点 / imagegen 提示词
   │       └─→ Codex imagegen   gpt-image-2 自动生图（抽象概念配图）
   ├─→ audio_cue_sheet.py       BGM / SFX 音频设计清单 / 生成审批 gate
   ├─→ audio_cue_mix.py         cue sheet + 最终旁白 → 本地/程序化 SFX 单轨 / 1× review gate
   ├─→ storyboard_plan.py       分镜 shot cards / 生成路由 / 连续性锚点
   ├─→ storyboard_animatic.py   每镜静帧 + 可选旁白 → timed MP4 / 1× review / live gate
   ├─→ photo_montage.py         有序照片 → 轻微缩放/叠化/可选配乐 MP4 + 源绑定收据
   ├─→ sequence_handoff.py      相邻镜头 receive/handoff / edit type / 轴线方向 / live gate
   ├─→ reference_story_formula.py
   │                            参考片时间码情绪机制 → 目标分镜 content anchors / live gate
   ├─→ provider_capability.py   provider/surface/model 能力合同 / 核验日期 / live gate
   ├─→ video_prompt_pack.py     Dreamina/Veo/LTX/Wan/Sora 提示词包 / 审批 + capability gate
   ├─→ reference_frame_preflight.py
   │                            首帧/style key 尺寸/方向/透明背景/画幅 gate
   ├─→ generation_task_log.py   异步生成任务台账 / submit_id / 下载 gate
   ├─→ generated_clip_review.py 生成片段 contact sheet / 常识物理 / 连续性 / 重生 gate
   ├─→ generation_chain_handoff.py
   │                            已审上一镜末帧 → 下一镜精确首帧 / 顺序生成 live gate
   ├─→ generated_motion_window.py
   │                            短生成片 0.25s freeze → active intervals / 人工裁切 / live gate
   ├─→ scoped_video_edit_review.py
   │                            原片 vs 局部 AI 编辑结果 / change-only + preserve invariants / A-B gate
   ├─→ generated_sequence_review.py
   │                            已审片段相邻尾帧/首帧/预览 / 跨镜头连续性 gate
   ├─→ final_audio_storyboard.py
   │                            锁定视觉 EDL + 原 storyboard → 最终声音分镜 / voice ledger / live gate
   ├─→ narration_loudness_qa.py 最终独立旁白 + 精确短语范围 → LUFS/spread/dBTP/LRA live gate
   ├─→ caption_speech_qa.py    subtitle_pack + 独立人声轨 → 孤立/错位/越界字幕 live gate
   ├─→ subtitle_glyph_qa.py   subtitle_pack + 显式字体 → 逐字符 cmap 覆盖 / 缺字 live gate
   ├─→ generation_lessons.py    已审片段 → provider/model scoped 提示词经验库
   ├─→ storyboard_assets.py     素材任务清单 / ready 预检 / paid 额度提醒
   │                            可选 media_library.py recommend 排名 B-roll 候选
   ├─→ stock_material_plan.py   远程 stock 搜索规划
   │                            Pexels / Pixabay / Coverr 查询计划 + 素材登记提示
   ├─→ screen_focus.py          录屏点击/热点 → 自动聚焦计划
   ├─→ pip_overlay.py           录屏 + facecam → PIP 小窗计划
   ├─→ color_grade.py           bounded 调色 plan / render_final 单次编码接入
   ├─→ lut_grade.py             外部 .cube LUT 校验 / SHA-256 绑定 / 单次编码接入
   ├─→ jump_cut.py              自适应去停顿 + 20% 删除预算 + 可审计 cut list + 30ms 防爆音 fade
   ├─→ multimodal_dead_air.py   静音 AND 静帧 → source-bound 保守删段 / 单次编码 / live gate
   ├─→ audio_transition.py      显式 J-cut/L-cut → source handle / hash / 1× 试听 gate
   ├─→ edit_revision.py         文本剪辑 artifact → source-bound 审批 / 成组 apply / undo / redo
   ├─→ edit_recipe.py           已审 render_config → typed-slot 可移植配方 / 新素材绑定回放
   ├─→ edit_preflight.py        render_config/enrich_plan/cut list 渲染前预检 gate
   ├─→ platform_safe_area_qa.py 字幕/PIP/CTA/marker → 平台 UI 安全区 gate + SVG guide
   ├─→ subtitle_style_preview.py 真实源帧 → 最终 ASS 预设对比 JPEG / 选择 / live gate
   ├─→ render_final.py          单次编码渲染（可选口播降噪 + enrich_plan/focus_events/pip_overlays + Heavy 字幕 + 响度规范化 + BGM ducking）
   │                            可选 --versioned-output 防覆盖旧成片
   ├─→ subtitle_render_review.py 最终 MP4 + subtitle_pack → 高风险字幕 1× clips / 原尺寸帧 / 完整审片 live gate
   ├─→ render_qa.py             渲染后黑屏/静帧/静音/尺寸质检 + review packet
   ├─→ stream_coverage_qa.py    最终 MP4 → decoded 音视频首尾 PTS / 帧数 / 容器覆盖 live gate
   ├─→ encode_quality_qa.py     同时间线 master vs 重编码件 → SSIM/PSNR / 最差帧 / live gate
   ├─→ audio_channel_qa.py      成片声道活动/起始/平衡/相位/mono fold-down live gate
   ├─→ audio_dropout_qa.py      最终人声/混音短促近静音候选 / 1× WAV 听审 live gate
   ├─→ flash_safety_qa.py       成片亮度/饱和红 flash → 1s/5s 风险窗口 / live gate
   ├─→ temporal_artifact_qa.py  单帧/少数帧 return-to-state spike → 三帧证据 / 人工 audit / live gate
   ├─→ shot_color_qa.py         成片镜头亮度/对比/色度/饱和度/broadcast-range + 切点跳变 gate
   ├─→ retention_rhythm_qa.py   成片 hook 活动 / 长镜头 / 注意力空窗 / 节奏 gate
   ├─→ reference_edit_rhythm.py 参考片 vs 成片 hard-cut 结构 / contact sheets / live gate
   ├─→ speech_continuity_qa.py  成片二次 ASR → 切点复读 / 近重复 take / 句内口吃 gate
   ├─→ lip_sync_review.py       最终 master → 1×/0.25× 口型证据 / 人工 audit / live gate
   ├─→ review_proxy.py          低码率完整审片 MP4 / 可见时间码 / faststart
   ├─→ timeline_view.py         源素材删除段 / 成片输出切点 filmstrip + waveform 复盘图
   ├─→ edit_compare.py          原片连续时钟 vs 最终像素 / 删段置黑 / 映射验证
   ├─→ subtitle_pack.py         SRT/VTT/ASS/JSON 字幕交付包（speed/offset 对齐）
   ├─→ soft_subtitles.py        已审 SRT → MP4 可开关字幕轨 / 无损复制音视频 / live 收据
   ├─→ chapter_mux.py           已审章节 JSON → MP4 可跳转章节 / 无损复制音视频 / live 收据
   ├─→ metadata_scrub.py       分享前清除 MP4 容器标签/章节/额外轨，保留音视频流
   ├─→ hls_vod.py               已审 SDR MP4 → 单码率 HLS 点播目录 / 分片+收据 live verify
   ├─→ subtitle_readability_qa.py
   │                            最终字幕 CPS / 时长 / 行长 / 重叠 / 媒体越界 gate
   ├─→ import_capcut_subtitles.py
   │                            剪映/CapCut 自动字幕 → transcript / gap cut list
   ├─→ srt_edit_plan.py         SRT + keep/drop 编辑指令 → render_config / cut list
   ├─→ project_resume.py        续跑上下文包 / agent handoff / 可选 CLAUDE.md
   ├─→ review_dashboard.py      静态 HTML/JSON 人工复核面板 / gate review queue
   ├─→ export_edl.py            render_config / cut list → EDL + manifest
   ├─→ export_fcpxml.py         render_config / cut list → FCPXML + manifest
   ├─→ export_otio.py           render_config / cut list → OTIO + manifest
   ├─→ framing_preview.py       master → 各平台 cover/contain/blur 真实帧 / 选择 / live gate
   ├─→ multi_export.py          已审画幅策略 → 小红书 3:4 / 抖音 9:16 / 视频号 ≤60s
   ├─→ hdr_sdr.py               PQ/HLG HDR → source-bound Rec.709 SDR / 完整解码 gate
   ├─→ video_enhancement.py     Lanczos 放大 + 可选运动补帧 / 全长 A-B + 带声复核 gate
   ├─→ delivery_encode.py       source-bound 两遍 H.264/AAC / 硬大小上限 / 完整解码 gate
   ├─→ gif_preview.py           视频短摘录 → 调色板 GIF / 源绑定收据 / 完整解码
   ├─→ logo_overlay.py          已审 MP4 + PNG Logo → 四角叠加 / 源绑定收据 / 完整解码
   ├─→ generate_caption.py      标题 + 200-500 字正文 + 3-6 tags + 发布时段
   ├─→ cover_variants.py        2-4 套封面 / feed-size 预览 / 最终选择 gate
   ├─→ approval_receipt.py      已复核交付件 → SHA-256 收据 / stale approval gate
   └─→ publish_package.py       平台视频/封面/字幕/章节/文案上传包 + gate 状态
```

**每天做一条短视频的完整提示词模板**：[docs/prompts/15-xhs-daily-tech-video.md](docs/prompts/15-xhs-daily-tech-video.md)（推荐入口）。

生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。

## Reference index

The full workflow is split by phase. Read only the file for the step you are on; paths inside reference files (`scripts/…`, `docs/…`) are relative to this skill folder.

| File | Section | Lines |
|---|---|---|
| `references/01-v3.md` | V3 新增脚本一览（按调用顺序） | 135 |
| `references/02-v3-render-final-py.md` | V3 新增 render_final.py 标志位 | 16 |
| `references/03-v3-day58-production.md` | V3 Day58 production 教训（已编码进默认行为） | 17 |
| `references/04-prerequisites.md` | Prerequisites（前置要求） | 10 |
| `references/05-prerequisites.md` | Prerequisites（前置要求） | 179 |
| `references/06-workflow-phase-0a-project-bootstrap.md` | Workflow（工作流程） — Phase 0a: Project Bootstrap（项目启动 / 原始素材导入） | 34 |
| `references/07-workflow-phase-0aa-runtime-preflight.md` | Workflow（工作流程） — Phase 0aa: Runtime Preflight（按任务核验本机能力） | 22 |
| `references/08-workflow-phase-0ab-interlace-conform-dv-dvd-gate.md` | Workflow（工作流程） — Phase 0ab: Interlace Conform（旧广播 / DV / DVD 条件 gate） | 6 |
| `references/09-workflow-phase-0ac-frame-rate-conform-vfr.md` | Workflow（工作流程） — Phase 0ac: Frame-rate Conform（手机 / 录屏 VFR 可选） | 17 |
| `references/10-workflow-phase-0ad-edge-black-trim.md` | Workflow（工作流程） — Phase 0ad: Edge-black Trim（片头 / 片尾黑场可选） | 19 |
| `references/11-workflow-phase-0ae-loop-fill.md` | Workflow（工作流程） — Phase 0ae: Loop Fill（短背景 / 环境片填满固定时长） | 18 |
| `references/12-workflow-phase-0af-ping-pong-loop.md` | Workflow（工作流程） — Phase 0af: Ping-pong Loop（短动作正放倒放循环） | 18 |
| `references/13-workflow-phase-0ag-clip-assembly.md` | Workflow（工作流程） — Phase 0ag: Clip Assembly（多源视频安全拼接） | 21 |
| `references/14-workflow-phase-0b-production-authorization.md` | Workflow（工作流程） — Phase 0b: Production Authorization（按确切范围授权） | 30 |
| `references/15-workflow-phase-0-media-library-setup.md` | Workflow（工作流程） — Phase 0: Media Library Setup（素材库初始化） | 95 |
| `references/16-workflow-phase-0-25-creator-owned-edit-style-pro.md` | Workflow（工作流程） — Phase 0.25: Creator-owned Edit Style Profile（个人/品牌剪辑风格，可选） | 22 |
| `references/17-workflow-phase-0-5-source-receipts-proof-deck.md` | Workflow（工作流程） — Phase 0.5: Source Receipts（事实来源 proof deck，可选但推荐） | 17 |
| `references/18-workflow-phase-1-audio-extraction.md` | Workflow（工作流程） — Phase 1: Audio Extraction（音频提取） | 10 |
| `references/19-workflow-phase-2-speech-recognition.md` | Workflow（工作流程） — Phase 2: Speech Recognition（语音识别） | 49 |
| `references/20-workflow-phase-2a-video-keyframe-extraction.md` | Workflow（工作流程） — Phase 2a: Video Keyframe Extraction（视频关键帧提取） | 53 |
| `references/21-workflow-phase-2a-adaptive-scene-boundaries.md` | Workflow（工作流程） — Phase 2a: Adaptive Scene Boundaries（自适应视觉场景边界） | 16 |
| `references/22-workflow-phase-2b-visual-dedupe.md` | Workflow（工作流程） — Phase 2b: Visual Dedupe（跨素材重复镜头复核） | 14 |
| `references/23-workflow-phase-2c-video-understanding-yolo.md` | Workflow（工作流程） — Phase 2c: Video Understanding（抽样帧 + 可选 YOLO） | 44 |
| `references/24-workflow-phase-2-5-transcript-review.md` | Workflow（工作流程） — Phase 2.5: Transcript Review（转录文字校验） | 62 |
| `references/25-workflow-phase-2-5a-target-script-alignment.md` | Workflow（工作流程） — Phase 2.5a: Target Script Alignment（按确认稿装配原话，可选） | 22 |
| `references/26-workflow-phase-2-6-asr-rough-cut.md` | Workflow（工作流程） — Phase 2.6: ASR Rough Cut（口头禅/重复句粗剪，可选） | 20 |
| `references/27-workflow-phase-2-6b-multimodal-dead-air.md` | Workflow（工作流程） — Phase 2.6b: Multimodal Dead-Air（静音 + 静帧保守去死区，可选） | 22 |
| `references/28-workflow-phase-3-user-interaction.md` | Workflow（工作流程） — Phase 3: User Interaction（用户交互） | 69 |
| `references/29-workflow-phase-4-render-config.md` | Workflow（工作流程） — Phase 4: Render Config（渲染配置） | 434 |
| `references/30-workflow-phase-4-8-edit-revision-artifact.md` | Workflow（工作流程） — Phase 4.8: Edit Revision（剪辑 artifact 可逆修订，可选） | 17 |
| `references/31-workflow-phase-4-85-portable-edit-recipe.md` | Workflow（工作流程） — Phase 4.85: Portable Edit Recipe（可移植剪辑配方，可选） | 15 |
| `references/32-workflow-phase-4-9-platform-safe-area-qa-ui.md` | Workflow（工作流程） — Phase 4.9: Platform Safe Area QA（平台 UI 安全区门禁） | 19 |
| `references/33-workflow-phase-4-95-subtitle-style-preview.md` | Workflow（工作流程） — Phase 4.95: Subtitle Style Preview（真实画面字幕样式预览） | 26 |
| `references/34-workflow-phase-5-single-pass-render.md` | Workflow（工作流程） — Phase 5: Single-Pass Render（单次渲染） | 58 |
| `references/35-workflow-phase-5b-export-to-jianying-capcut.md` | Workflow（工作流程） — Phase 5b: Export to JianYing / CapCut（导出剪映工程） | 81 |
| `references/36-workflow-phase-5c-nle-handoff-edl-fcpxml-otio-pr.md` | Workflow（工作流程） — Phase 5c: NLE Handoff EDL / FCPXML / OTIO（交给 Premiere / FCP / Resolve） | 15 |
| `references/37-workflow-phase-5d-final-audio-storyboard-edl.md` | Workflow（工作流程） — Phase 5d: Final Audio Storyboard（视觉 EDL 锁定后重建声音） | 53 |
| `references/38-workflow-phase-6-post-render-validation.md` | Workflow（工作流程） — Phase 6: Post-render Validation（渲染后验证） | 71 |
| `references/39-workflow-caption-speech-qa.md` | Workflow（工作流程） — Caption / Speech QA（字幕与独立人声活动对齐） | 16 |
| `references/40-workflow-subtitle-glyph-qa-emoji.md` | Workflow（工作流程） — Subtitle Glyph QA（生僻字 / emoji / 多语言字幕时推荐） | 17 |
| `references/41-workflow-subtitle-render-review.md` | Workflow（工作流程） — Subtitle Render Review（有烧录字幕的最终成片必跑） | 327 |
| `references/42-important-notes.md` | Important Notes（注意事项） | 27 |
| `references/43-remotion-voiceover-workflow.md` | Remotion Voiceover Workflow（语音生成视频） | 167 |
| `references/44-font-catalog.md` | Font Catalog（字体目录） | 103 |
| `references/45-faq-troubleshooting.md` | FAQ / Troubleshooting（常见问题诊断） | 123 |
| `references/46-known-issues-solutions.md` | Known Issues & Solutions（已知问题与解决方案） | 89 |
| `references/47-audiogram.md` | 纯音频播客竖版 Audiogram | 6 |
| `references/48-gif.md` | 短动图预览 GIF | 6 |
| `references/49-logo.md` | 已审成片叠加品牌 Logo | 4 |
| `references/50-hls.md` | 已审成片打包 HLS 点播 | 6 |

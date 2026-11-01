### Subtitle Render Review（有烧录字幕的最终成片必跑）

```bash
python3 scripts/subtitle_render_review.py prepare \
  --project-dir . \
  --video output/final.mp4 \
  --subtitle-pack output/subtitles/final.json \
  --proof-dir verify/subtitle_render \
  --output work/subtitle_render_review_request.json \
  --markdown work/subtitle_render_review_request.md \
  --response-template work/subtitle_render_review_response.json

# 完整 1× 看完 final，并逐条填写 response 后：
python3 scripts/subtitle_render_review.py audit \
  --request work/subtitle_render_review_request.json \
  --response work/subtitle_render_review_response.json \
  --output work/subtitle_render_review.json \
  --markdown work/subtitle_render_review.md --strict
python3 scripts/subtitle_render_review.py verify \
  --report work/subtitle_render_review.json --project-dir . --strict
```

脚本从确切 final 选择首尾、最长、最高 CPS、最短、中段和均匀分布 cue，导出带声 1× context clips 与字幕中点原尺寸 JPEG。通过要求完整播放全片，且每个样本均为 `visible / matches / readable / clear / repair_action=none`；缺失、旧文案、不可读、裁切、遮挡或不可观察都会 fail closed。报告绑定 final、subtitle pack、proof bytes、媒体契约、采样设置、人工 response 与 canonical id；任何重渲染或证据漂移后都要重做。它不做 OCR 或自动可读性评分，默认抽样也不替代逐条完整审片。详见 [docs/prompts/111-subtitle-render-review.md](docs/prompts/111-subtitle-render-review.md)。

**6a2. 闪烁 / 光敏风险启发式预检（最终 master 和重要平台版必跑）**：
```bash
python3 scripts/flash_safety_qa.py analyze final.mp4 \
  --project-dir . \
  --output verify/flash_safety_qa.json \
  --markdown verify/flash_safety_qa.md \
  --strict

python3 scripts/flash_safety_qa.py verify \
  --report verify/flash_safety_qa.json \
  --project-dir . \
  --strict
```

`flash_safety_qa.py` 用本地 FFmpeg 低分辨率逐帧采样，分别记录覆盖至少 25% 画面的亮度与饱和红相反 transition，并配成 flash；滚动 1 秒超过 3 次、或滚动 5 秒至少 10 次会阻断。命中后按 Markdown 时间段正常速度播放，优先删除重复闪白/闪红、降低反差/红饱和度、缩小闪烁面积或降频，再从时间线重渲染。报告绑定 source SHA-256、媒体契约、参数、算法合同和现场重算证据；`pipeline_manifest.py --require flash_safety_qa --strict` 可设为发布 gate。它只是启发式筛查，不检测有害空间 pattern，也不是医疗建议、法律合规证据或 WCAG/Harding/广播认证；高风险或受监管交付必须升级到认可的专业 photosensitivity analyzer。详见 [docs/prompts/104-flash-safety-qa.md](docs/prompts/104-flash-safety-qa.md)。

**6a3. 单帧 / 少数帧瞬态伪影（最终 master 和生成素材推荐）**：
```bash
python3 scripts/temporal_artifact_qa.py analyze final.mp4 \
  --project-dir . \
  --evidence-dir verify/temporal_artifact_frames \
  --output verify/temporal_artifact_qa.json \
  --markdown verify/temporal_artifact_qa.md \
  --response-template work/temporal_artifact_response.json \
  --strict
```

脚本寻找 1–3 个采样帧短暂偏离、随后回到近似原画面的局部 spike；普通 hard cut 不应满足双边突变与恢复相似合同。命中候选后，必须完整 1× 播放，再逐张描述 `before / suspect / after`，填写 `intentional_edit|artifact|uncertain` 并运行 `audit`。后两种决定保持阻塞；source、算法、分析、JPEG、response 或派生状态漂移都会让 live gate 失效。它不识别人脸、身份、物理或语义，也可能漏掉持续漂移和小区域问题。详见 [docs/prompts/108-temporal-artifact-qa.md](docs/prompts/108-temporal-artifact-qa.md)。

**6b. 镜头色彩 / 曝光 QA（多机位、B-roll、生成素材或调色后推荐）**：
```bash
python3 scripts/shot_color_qa.py final.mp4 \
  --output verify/shot_color_qa.json \
  --markdown verify/shot_color_qa.md \
  --strict
```

`shot_color_qa.py` 在最终编码文件上用 FFmpeg `signalstats` 按镜头聚合亮度、对比、U/V、饱和度和 broadcast-range 指标，并比较相邻镜头的亮度/色度差。视觉跳变默认只 WARN，必须结合 Markdown 时间码和 `timeline_view.py` 看 master；非 full-range 输出的持续越界或镜头无 sample 默认阻塞。可用 `--scene-boundaries work/scene_boundaries.json` 复用已审场景，或由脚本自动检测。它不是校准 scopes、HDR proof、白平衡/肤色判断或审美评分。`pipeline_manifest.py --require shot_color_qa --strict` 可把报告设为发布必需项。

**6c. 留存节奏风险审计（短视频 master / platform export 推荐）**：
```bash
python3 scripts/subtitle_pack.py \
  --config render_config.json \
  --output-dir output/subtitles \
  --basename final_master \
  --speed 1.25 \
  --offset 2.0

python3 scripts/retention_rhythm_qa.py final.mp4 \
  --timed-text output/subtitles/final_master.json \
  --output verify/retention_rhythm_qa.json \
  --markdown verify/retention_rhythm_qa.md \
  --strict
```

`retention_rhythm_qa.py` 在**已渲染成片**上复用 FFmpeg scene score，并可合并 output-aligned subtitle JSON，检查前三秒 scene/subtitle activity、长视觉 hold、scene + subtitle attention gap、机械等距节奏、过密快切和字幕长时间不刷新。没有 timed text 时，inactive hook 只警告，避免把持续运镜或轻微动效误判成硬失败；高置信严重长 hold / attention gap 会写入 `summary.blocking`。这是可观测节奏风险，不是平台留存率或爆款预测。命中后先看 Markdown 时间范围和 master，再回到源 timeline 重渲染。`pipeline_manifest.py --require retention_rhythm_qa --strict` 可把报告设为发布必需项。

**6c.1. 参考视频剪辑节奏量化（用户明确给参考片时跑）**：
```bash
python3 scripts/reference_edit_rhythm.py analyze \
  --project-dir . \
  --reference origin/reference-ad.mp4 \
  --candidate final.mp4 \
  --evidence-dir verify/reference_edit_rhythm \
  --output work/reference_edit_rhythm.json \
  --markdown work/reference_edit_rhythm.md \
  --strict

python3 scripts/reference_edit_rhythm.py verify \
  --report work/reference_edit_rhythm.json \
  --strict
```

`reference_edit_rhythm.py` 对参考片和候选片运行同一套 hard scene detection，绑定两条视频和两张 contact sheet 的 SHA-256/媒体契约，并比较 cuts/minute、median shot、final-hold 比例、归一化切点位置及 opening/middle/closing cut share。默认偏差只 WARN；只有结构匹配是明确验收条件时才加 `--require-match`。完整看两条视频，只借鉴结构，不复制参考片的画面、音频、品牌或故事。scene score 会漏掉部分 dissolve 与镜头内动作，contact sheet 也不能替代 1× 播放。详见 [docs/prompts/92-reference-edit-rhythm.md](docs/prompts/92-reference-edit-rhythm.md)。

**6c.2. 最终成片 Lip-sync 复核（数字人 / 生成口播 / 对口型 close-up）**：
```bash
python3 scripts/lip_sync_review.py prepare \
  --project-dir . \
  --video final.mp4 \
  --segment hook=2.40:6.10 \
  --anchor hook="把品牌卖点说清楚" \
  --proof-dir verify/lip_sync \
  --output work/lip_sync_review_request.json \
  --markdown work/lip_sync_review_request.md \
  --response-template work/lip_sync_review_response.json

# 看完 1× 带声和 0.25× 静音 proofs、填写 response 后：
python3 scripts/lip_sync_review.py audit \
  --request work/lip_sync_review_request.json \
  --response work/lip_sync_review_response.json \
  --output work/lip_sync_review.json \
  --markdown work/lip_sync_review.md \
  --strict
python3 scripts/lip_sync_review.py verify --report work/lip_sync_review.json --strict
```

短语必须来自最终 master 且完整可见，长度 1–10 秒，优先包含 p/b/m 类闭唇锚点。`pass` 要求爆破音闭唇、元音 timing、讲话时嘴部运动、可见说话人和音频质量全部通过；`not_observable` fail closed。脚本只绑定人工审过的 master/proof bytes，不做人脸或自动音素识别。任何剪切、变速、换音、重编码或 evidence 漂移都要重新 `prepare → audit`。详见 [docs/prompts/93-lip-sync-review.md](docs/prompts/93-lip-sync-review.md)。

**6d. 完整审片代理（需要分享整条视频或精确时间码反馈时跑）**：
```bash
python3 scripts/review_proxy.py final.mp4 \
  --output verify/final_review_proxy.mp4 \
  --manifest verify/final_review_proxy.json \
  --markdown verify/final_review_proxy.md
```

`review_proxy.py` 不修改 master；它输出最大 720p、24fps、H.264/AAC、`+faststart` 的轻量 MP4，并在左上角烧入 `REVIEW PROXY` 和 elapsed timecode。审片意见应引用可见时间码，最终 QA 和发布仍使用 master / platform export。`--dry-run` 只写可复现命令和 artifact，`--no-timecode` 可关闭时间码。

**6e. 可视化复盘（QA 有 WARN/FAIL 或抽查切点时跑）**：
```bash
python3 scripts/timeline_view.py final.mp4 --at 42.5 --radius 1.5 --output verify/42_5s.png
python3 scripts/timeline_view.py origin/talking.mp4 --cut-list work/jumpcut.json --output-dir verify/cuts --limit 12
python3 scripts/timeline_view.py output/rough_cut.mp4 --rendered-cut-list work/rough_cut.json --output-speed 1.25 --output-offset 1.0 --output-dir verify/rendered_cuts --json verify/rendered_cuts.json
```

`timeline_view.py` 会生成 filmstrip + waveform PNG；上半部分看画面连续性，下半部分看人声/静音边界。`--cut-list` 查看源素材时间轴，`--rendered-cut-list` 则按 `keep_segments` 累计时长映射到成片的实际拼接点；有全局变速或片头封面时同步传 `--output-speed` / `--output-offset`。JSON 会保留输出切点和前后 source range；无音频视频会自动只输出 filmstrip。

**6f. 原片/成片 source-time 对照（结构剪辑复核时跑）**：
```bash
python3 scripts/edit_compare.py \
  origin/talking.mp4 final.mp4 \
  --cut-list work/rough_cut.json \
  --output-speed 1.25 \
  --output-offset 2.0 \
  --output verify/source_vs_final.mp4 \
  --report verify/edit_compare.json \
  --markdown verify/edit_compare.md
```

左栏连续播放原片；右栏把最终交付像素投回同一 source clock，被删除范围显示黑屏。脚本会检查时长、双栏尺寸、source-clock 音轨、删段黑屏和代表性保留段像素。V1 只支持单来源、时间升序、无重叠的 `keep_segments` 加全局 speed/offset；重排、多来源或非线性变速要回到 NLE/OTIO 时间线复核。详细说明见 [docs/prompts/74-edit-compare.md](docs/prompts/74-edit-compare.md)。

**6g. 字幕 sidecar 交付（平台需要 SRT/VTT 时跑）**：
```bash
python3 scripts/subtitle_pack.py \
  --config render_config.json \
  --output-dir output/subtitles \
  --basename final_master \
  --speed 1.25 \
  --offset 2.0 \
  --formats srt vtt ass json
```

`subtitle_pack.py` 可从 `transcript.json` 或 `render_config.json` 生成 SRT/VTT/ASS/JSON。`--config` 会按最终 clips 顺序串接字幕时间线；`--speed` 对齐 `render_final.py --primary-speed`；`--offset` 对齐片头封面秒数。JSON manifest 保留每条 cue 的来源片段和 `over_max_chars` 之类校对警告。

播放器需要可开关字幕时，用已审、与最终 MP4 对齐的 SRT 运行 `soft_subtitles.py mux final.mp4 output/subtitles/final_master.srt --language zho --output output/final-soft.mp4 --receipt verify/soft_subtitles.json`，再运行 `soft_subtitles.py verify verify/soft_subtitles.json`。脚本仅接受单视频、最多单音频、无其他轨的源片；复制音视频流，加入一条 `mov_text` 字幕轨，检查 SRT 时间、抽回的字幕内容、源/成片流哈希、完整解码和文件漂移。`ready_for_human_review` 后仍要在目标播放器以 1× 带声看完，确认字幕开关、中文显示和音画同步。已有烧录字幕的画面不会被此命令移除，交付前应确认是否会出现双层字幕。

长视频需要播放器内可跳转章节时，先用 `chapter_markers.py` 生成并人工核对 `chapters.json`，确保末章结束时间与最终 MP4 一致；再运行 `chapter_mux.py mux output/master.mp4 output/chapters/chapters.json --output output/master-chapters.mp4 --receipt verify/chapter_mux.json` 和 `chapter_mux.py verify verify/chapter_mux.json`。脚本接受未带章节的单视频、最多单音频 MP4，复制音视频流并核对每章标题/时间、流哈希和完整解码。最终仍需在目标播放器检查章节跳转；上传平台若不读取 MP4 内嵌章节，另交付 `chapters-youtube.txt`。

网页播放器可将同次导出的 `chapters.vtt` 作为 `<track kind="chapters" src="chapters.vtt" srclang="zh">` 加到与章节时间线一致的 `<video>`；VTT 使用无重叠章节、毫秒时间码和纯文本标题。浏览器是否呈现章节菜单取决于播放器实现，交付时实际试跳转；片头或重新剪辑改变时间线后需按最终视频时长重新导出。

公开分享 MP4 前可运行 `metadata_scrub.py scrub output/master.mp4 --output output/share.mp4 --receipt verify/metadata_scrub.json`，再运行 `metadata_scrub.py verify verify/metadata_scrub.json`。它只保留第一条视频和可选第一条音频，移除容器/流的非结构性标签、章节和字幕/数据等额外轨；核对音视频编码流 SHA-256、时长、完整解码和输出标签。分享版若需要章节或软字幕，应在清理后明确重新封装并复核。该工具只检查 FFprobe 可见的容器/流标签，不扫描画面、音频内容或编码流内部可能携带的信息；仍需正常速度审看分享版。

生成 JSON 后，对最终字幕执行只读发布门禁：

```bash
python3 scripts/subtitle_readability_qa.py \
  output/subtitles/final_master.json \
  --media final.mp4 \
  --output verify/subtitle_readability_qa.json \
  --markdown verify/subtitle_readability_qa.md \
  --strict
```

`subtitle_readability_qa.py` 检查 output-timeline 的无效时间、乱序、重叠、极短闪现、CPS、持续时间、行数/行长，并可用 FFprobe 验证 cue 没有超过成片结尾。普通 CPS/排版风险只 WARN，必须看正常速度 master；确定性时间事故和极端阅读速度写入 `summary.blocking`。它不做 OCR，不替代字体、描边、位置或遮挡人工审片。`pipeline_manifest.py --require subtitle_readability_qa --strict` 可把报告设为发布必需项。

**6g.1 平台画幅处理预览（master 与目标比例不同或画面含受保护信息时跑）**：

```bash
python3 scripts/framing_preview.py create \
  --project-dir . --video output/master.mp4 \
  --platforms xhs douyin wxch \
  --preview-dir verify/framing \
  --output work/framing_preview.json \
  --markdown work/framing_preview.md \
  --require-selection

python3 scripts/framing_preview.py select \
  --report work/framing_preview.json --platform xhs --strategy contain
python3 scripts/multi_export.py output/master.mp4 \
  --output-dir output --platforms xhs douyin wxch \
  --framing-preview work/framing_preview.json
```

逐平台看真实早/中/晚 JPEG。`cover` 不能裁掉脸、手、多人关系、可读 UI、logo、产品边缘或文档边界；有风险时选 `contain` 或 `blur`。源/预览 bytes、显示方向、平台画布、filter digest 或选择漂移都会在编码前阻断。抽样图不替代完整 1× 平台导出审片；详见 [docs/prompts/103-framing-preview.md](docs/prompts/103-framing-preview.md)。

**6h. 发布上传包（最终上传前跑）**：
```bash
python3 scripts/publish_package.py \
  --project-dir work/day58 \
  --platforms xhs douyin wxch \
  --output work/day58/publish_package.json \
  --markdown work/day58/publish_package.md \
  --strict
```

`publish_package.py` 不上传、不调用平台 API；它只把 `multi_export.py` 的平台 MP4、`generate_caption.py` 的标题/正文/tags、封面、SRT/VTT、章节文本和 `pipeline_manifest` gate 状态合成 `publish_package.v1`。如果存在 `cover_variants.json` 且 `selected_cover` 文件有效，会优先使用已复核封面；显式 `--cover` 可覆盖。如果缺少某个平台视频、caption 为空、或 pipeline manifest 已 blocked，`--strict` 返回 2。需要交给外部发布 connector 时，用这份 JSON 作为 handoff；手工上传时看 Markdown checklist。

**6i. 最终审批收据（客户/人工确认后跑）**：
```bash
python3 scripts/approval_receipt.py create \
  --project-dir work/day58 \
  --artifact output/day58_xhs.mp4 \
  --artifact output/day58_douyin.mp4 \
  --artifact output/day58_wxch.mp4 \
  --artifact output/cover.png \
  --artifact output/day58_caption.json \
  --artifact verify/render_qa.json \
  --approved-by "reviewer label" \
  --output verify/approval_receipt.json \
  --markdown verify/approval_receipt.md

python3 scripts/publish_package.py \
  --project-dir work/day58 \
  --require-approval-receipt \
  --strict
```

`approval_receipt.py` 只绑定显式列出的稳定交付件；不要把每次都会重写的 pipeline manifest、publish package 或 dashboard 放进收据。`verify --strict` 和 `pipeline_manifest.py --require approval_receipt --strict` 会重新读取当前文件并比较 SHA-256；任何重渲染、换封面、改文案、删字幕或路径变成 symlink 都让旧审批过期。`approved_by` 只是本地标签，不是身份认证或数字签名。详细说明见 [docs/prompts/77-approval-receipt.md](docs/prompts/77-approval-receipt.md)。

**6j. 续跑上下文包（跨会话/自动化收尾时跑）**：
```bash
python3 scripts/project_resume.py \
  --project-dir work/day58 \
  --target-stage publish_ready \
  --output work/day58/project_resume.json \
  --markdown work/day58/project_resume.md \
  --agent-note work/day58/CLAUDE.md \
  --strict
```

`project_resume.py` 复用 `pipeline_manifest.py` 的本地 gate，不渲染、不上传、不提交生成任务。它输出 `project_resume.v1`，包含 `phase`、`recommended_first_action`、`next_actions[]`、最近 artifacts、关键 gate snapshot 和一句可直接交给下一位 agent 的 `suggested_prompt`。长流程被压缩上下文、自动化结束、或要交给另一位 agent 时，优先把 Markdown/agent note 作为接手入口。

**6k. 人工复核面板（最终确认/交接前跑）**：
```bash
python3 scripts/review_dashboard.py \
  --project-dir work/day58 \
  --target-stage publish_ready \
  --output work/day58/review_dashboard.json \
  --html work/day58/review_dashboard.html \
  --strict
```

`review_dashboard.py` 复用 `pipeline_manifest.py` 的本地 gate，输出 `review_dashboard.v1` 和一个可直接在浏览器打开的 HTML。它把 blocking/missing/warning gate 放进 `review_items[]`，同时列出 `next_actions[]`、最新 artifacts 和完整 gate snapshot。适合用户最终确认，也适合自动化结束时留给下一位 agent。

**6l. 成片复读 / 口吃门禁**：
```bash
python3 scripts/extract_audio.py output/final.mp4
python3 scripts/transcribe.py output/final_audio.wav --model auto --language zh --word-timestamps
python3 scripts/speech_continuity_qa.py output/final_transcript.json \
  --output verify/speech_continuity_qa.json \
  --markdown verify/speech_continuity_qa.md \
  --strict
```

必须对**已渲染 master**重新转录，不能复用源素材 transcript。`speech_continuity_qa.py` 会检查相邻 segment 的结尾/开头精确复读、相邻近重复 take 和句内即时口吃；不同 speaker 默认不互判。命中后先按时间码试听 master，再调整源 `render_config` / cut list，重新渲染并复跑。`pipeline_manifest.py --require speech_continuity_qa --strict` 可把这份报告设为发布必需项。

**6m. PQ/HLG HDR → Rec.709 SDR 交付（HDR master 面向普通社媒/网页时跑）**：
```bash
python3 scripts/hdr_sdr.py plan output/final_hdr.mp4 \
  --delivery output/final_sdr.mp4 \
  --output work/hdr_sdr_plan.json \
  --markdown work/hdr_sdr_plan.md
python3 scripts/hdr_sdr.py apply work/hdr_sdr_plan.json
python3 scripts/hdr_sdr.py verify work/hdr_sdr_plan.json
```

`hdr_sdr.py` 只接受 metadata 明确的 `smpte2084` PQ 或 `arib-std-b67` HLG，并要求 BT.2020 primaries/matrix；未知/矛盾 color tags 会 fail closed。正确转换必须同时有 FFmpeg `zscale` + `tonemap`，不允许用裸 tonemap 或只降到 `yuv420p` 的退化回退。apply 用 linear-light float + Hable 生成 H.264/AAC、`yuv420p`、BT.709 limited-range MP4，显式验证四项 color tag、时长/尺寸/fps/音轨、hash 和全长解码后才原子提升。Dolby Vision/HDR10+ 动态 metadata 不保留；必须在可信 SDR 屏完整复核肤色、高光、阴影、渐变和饱和色，再对 SDR 文件重跑 QA 和审批。详见 [docs/prompts/87-hdr-sdr.md](docs/prompts/87-hdr-sdr.md)。

**6n. 目标大小交付编码（有明确 MB 上限时跑）**：
```bash
python3 scripts/delivery_encode.py plan output/final.mp4 \
  --delivery output/final_delivery.mp4 \
  --max-size-mib 18 \
  --output work/delivery_encode_plan.json \
  --markdown work/delivery_encode_plan.md
python3 scripts/delivery_encode.py apply work/delivery_encode_plan.json \
  --markdown work/delivery_encode_plan.md
python3 scripts/delivery_encode.py verify work/delivery_encode_plan.json
```

`delivery_encode.py` 绑定 master SHA-256，用两遍 `libx264` 在 6% 容器余量内计算 H.264/AAC 码率；输出超过硬上限、容器/流/尺寸/fps/时长/音频不符或完整 FFmpeg decode 失败都会阻塞。apply 只先写同目录临时 MP4，技术验证通过后才原子晋升，不覆盖源文件。完整解码不是画质批准；若构图/时间线未变，紧接着运行 `encode_quality_qa.py`，再正常速度看完交付版、跑 `render_qa.py` 并把最终 SHA-256 放入 `approval_receipt.py`。详见 [docs/prompts/85-delivery-encode.md](docs/prompts/85-delivery-encode.md) 与 [docs/prompts/107-encode-quality-qa.md](docs/prompts/107-encode-quality-qa.md)。

**6o. 字幕文字最终校验**：
1. 读取最终视频使用的所有 transcript 片段的文字
2. 按最终视频的片段顺序，逐条检查以下问题：
   - **语音识别残留错误**：Phase 2.5 可能遗漏的同音字、专有名词错误
   - **口误未清理**：说话人的口误（如说反了、重复了）是否仍然保留在最终视频中
   - **上下文连贯性**：跨视频拼接后，相邻片段之间是否存在语义断裂或逻辑跳跃
   - **字幕一致性**：同一个词/名称在不同片段中是否拼写一致
3. 如发现问题，列出问题清单并展示给用户：
   ```
   字幕校验结果：
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     #  | 问题类型     | 原文 → 建议修正
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     3  | 识别错误     | "检映" → "剪映"
     7  | 口误        | "先说了结果" → 建议删除此片段
    12  | 名称不一致   | "opencloud" → 统一为 "OpenClaw"
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```
4. 用户确认修正后，修改对应的 transcript.json，然后重新执行 Phase 5 渲染

### Phase 4: Render Config（渲染配置）

根据用户的选择，生成 `render_config.json` 配置文件。

**重要说明：渲染配置是项目级文件**

SKILL 中展示的 render_config.json 格式只是**模板/参考**，不要直接修改 Skill 仓库中的任何文件。每个视频项目应在**用户工作目录**下创建独立的渲染配置：

```bash
# 在用户的视频项目工作目录下创建 script/ 文件夹
mkdir -p script/

# 在 script/ 下为每个视频项目创建独立的渲染配置文件
# 例如：script/render_config.json
```

**目录结构示例**：
```
~/Videos/my-project/          ← 用户工作目录
├── script/                   ← 渲染配置目录（每个项目独立）
│   └── render_config.json    ← 本项目的渲染配置
├── media/
│   ├── raw/                  ← 原始素材
│   ├── broll/
│   └── output/               ← 最终输出
├── *_audio.wav               ← 提取的音频
└── *_transcript.json         ← 转录文件
```

**渲染配置文件格式**（`script/render_config.json`）：

```json
{
  "clips": [
    {"video": "path/to/video1.MOV", "segment_id": 4, "transcript": "path/to/transcript1.json"},
    {"video": "path/to/video1.MOV", "segment_id": 5, "transcript": "path/to/transcript1.json"},
    {"video": "path/to/video2.MOV", "segment_id": 1, "transcript": "path/to/transcript2.json",
     "broll": "path/to/cityscape.mp4", "broll_start": 5.0}
  ],
  "title": "封面标题文字",
  "subtitle": "副标题/情感钩子（可选）",
  "cover_style": "news",
  "cover_duration": 2.0,
  "cover_image": "path/to/custom_cover.png",
  "cover_use_frame": false,
  "video_overlay": "path/to/overlay.png",
  "rec_blink": {
    "dot_image": "path/to/dot.png",
    "x": 55, "y": 66,
    "period": 1.0
  },
  "end_cards": [
    {"text": "感谢观看\n更多内容敬请期待", "duration": 3.5}
  ],
  "bgm": "path/to/background_music.mp3",
  "bgm_volume": 0.15,
  "bgm_fade_out": 3.0,
  "bgm_ducking": true,
  "bgm_ducking_threshold": 0.03,
  "bgm_ducking_ratio": 8,
  "bgm_ducking_attack_ms": 20,
  "bgm_ducking_release_ms": 500,
  "subtitle_style": "karaoke",
  "subtitle_highlight_color": "#FFFF00",
  "chapters": [
    {"title": "章节名", "start": 0.0, "end": 30.0}
  ],
  "text_badges": [
    {"text": "关键结论", "start": 12.0, "end": 13.5}
  ],
  "broll_overlays": [
    {"video": "path/to/cityscape.mp4", "start": 8.0, "end": 10.0, "source_start": 2.0}
  ],
  "image_overlays": [
    {"image": "path/to/generated.png", "start": 18.0, "end": 21.0, "fit": "cover"}
  ],
  "pip_overlays": [
    {"video": "path/to/facecam.mp4", "start": 0.0, "end": 42.0, "position": "bottom_right", "sync_offset": 0.18}
  ]
}
```

**使用渲染配置**：
```bash
# 渲染时指定 script/ 下的配置文件
python3 scripts/render_final.py --config script/render_config.json --output media/output/final.mp4
```

**B-roll 替换**（`broll` 字段）：
- 在 clip 中添加 `"broll": "path/to/video.mp4"` 可替换该片段的画面，同时保留原始音频
- `broll_start` 指定从 B-roll 视频的哪个时间点开始截取（默认 0.0）
- B-roll 视频会自动缩放/裁切以匹配主视频分辨率
- 适用场景：屏幕录制口播配城市街景、音频配音配画面等

**Auto-Enrich 自动接入**（推荐）：
- 先运行 `auto_enrich.py --output work/enrich_plan.json`
- 渲染时加 `--enrich-plan work/enrich_plan.json`
- `broll[].suggested_asset` 会转成定时 B-roll video overlay；`chapter_cards[]`、`stickers[]` 和 `emphasis_cues[]` 会转成 ASS badge；`emphasis_cues[]` 还可生成无红框的轻微 center push-in；`chapter_cards[].png` / `imagegen[].image_path` / `imagegen[].generated_path` 会转成定时图片 overlay
- `pip_overlays[]` 会转成定时 facecam / camera 小窗；camera audio 默认忽略，主音频仍来自 render config
- 没有实际生成文件的 imagegen cue 只作为提示输出，不会阻塞渲染
- 合并后的可见文字仍会走 `_internal_text_guard` 和 `content_guard.py`

**Beat Edit Plan 节拍剪辑骨架**（音乐视频 / 卡点 montage 可选）：
- 运行 `beat_sync.py --bgm origin/bgm.mp3 --generate-plan --duration 30 --beats-per-cut 4 --min-segment 0.75 --max-segment 3 --output work/beat_edit_plan.json --markdown work/beat_edit_plan.md`
- 输出 `beat_edit_plan.v1`：`cut_times[]`、program-time `segments[]`、逐切点 `boundary_evidence[]`、检测方法和 `summary`
- 默认每 4 拍提出一个切点；最短/最长镜头守卫会优先改选附近 beat，实在没有合适 beat 才插入 `duration_guard`
- `librosa` 不可用或读取失败时只生成固定 BPM 网格，并把状态标为 `review`；必须听音乐复核，不能把 fallback 当作真实节拍
- 计划只定义时间槽，不选择素材、不渲染、不改源文件；确认后再把镜头映射进 `render_config` / EDL / OTIO
- 已有 cut times 仍使用原命令 `beat_sync.py --bgm origin/bgm.mp3 --cuts work/cut_times.json --window 0.2`

**Speed Ramp 局部慢动作 / velocity edit**（动作、产品 reveal、游戏、montage 可选）：
- 先逐帧找到 impact frame，再运行 `speed_ramp.py plan origin/action.mp4 --ramp 4.6,5.0,1,0.25,s_curve --hold 5.0,5.8,0.25 --ramp 5.8,6.2,0.25,1,ease --interpolate-fps 120 --output work/speed_ramp_plan.json --markdown work/speed_ramp_plan.md`
- `verify` 会重算 plan id、源文件 SHA-256、source/output coverage 和逐段 `duration / speed`；源片或 pieces 漂移立即阻塞
- `apply` 用同目录临时文件渲染，成功后才替换目标；默认不覆盖、不跟随 output symlink，也不能覆盖 source
- `--interpolate-fps` 是 FFmpeg motion interpolation，可能产生肢体 / 边缘伪影；极慢音频必须试听，必要时 plan 阶段加 `--mute-audio`
- 最终必须用 1×、带声音完整播放；变速后重新生成字幕 / timecoded artifacts、跑 render QA，并重新做最终审批。详见 `docs/prompts/83-speed-ramp.md`

**Freeze-Punch 关键帧定格强调**（表情峰值、动作落点、产品揭晓可选）：
- 先逐帧确定 impact，再运行 `freeze_punch.py plan origin/reaction.mp4 --freeze 4.8,0.8,1.08,0.5,0.42 --delivery work/reaction-freeze-punched.mp4 --output work/freeze_punch_plan.json --markdown work/freeze_punch_plan.md`
- 它用 impact frame 替换其后的短画面窗口；音频和总时长保持不变，所以不会因本操作漂移字幕、章节或 cue 时间码
- pending plan 会阻塞；读完 Markdown 后运行 `apply`，再运行 `verify --strict`。apply 只有在 H.264/AAC、yuv420p、尺寸/fps/时长/音轨契约和全长解码通过后才原子提升输出并写回 hash
- 必须 1× 带音频检查 freeze 入口/出口、可见说话人冻嘴、动作跳跃、主体裁切和放大软化。源片/plan/成片漂移会让 live gate 失效；旧 QA、approval receipt 和 publish package 必须重做。详见 `docs/prompts/101-freeze-punch.md`

**J-cut / L-cut 声音先行 / 延续转场**（访谈、叙事、场景切换可选）：
- 只在人工明确选定的边界运行：`audio_transition.py plan work/render_config.json --transition 1,j_cut,0.4 --transition 3,l_cut,0.5 --output work/audio_transition_plan.json --markdown work/audio_transition_plan.md`
- J-cut 使用下一 clip 入点之前的真实源音频 handle；L-cut 使用上一 clip 出点之后的 handle，并跳过下一 clip 等长的开头音频以恢复同步。handle 不足直接阻塞，不用静音伪造
- 计划绑定 render config、transcript、源片/B-roll SHA-256 和 canonical plan id；`verify` 会从 live inputs 重新编译，手改 digest 不能隐藏漂移
- 用 `audio_transition.py apply ... --output output/master.mp4 --receipt work/audio_transition_apply.json`，或给 `render_final.py` 加 `--audio-transition-plan`；字幕、overlay、BGM 和错位主音频仍在一次 FFmpeg 编码中完成
- 必须在 1× 用耳机和手机逐个试听改变的边界，确认无吞字、复读、双人声、click、泵动和环境底噪跳变。机器只能验证时序/hash，不能判断交叠对白是否合适。详见 [docs/prompts/86-audio-transition.md](docs/prompts/86-audio-transition.md)

**Audio Cue Mix 音效 cue 单轨混音**（`audio_cue_sheet.v1` 已审后运行）：
- 用最终独立旁白执行 `audio_cue_mix.py plan --project-dir . --cue-sheet work/audio_cue_sheet.json --voice work/final_narration.wav --delivery work/audio_cue_mix.wav --output work/audio_cue_mix.json --markdown work/audio_cue_mix.md`；本地音效必须位于项目内并绑定 SHA-256/媒体契约
- 缺少 `transition_whoosh / emphasis_ping / success_chime / warning_tick` 时，可显式加 `--synthesize-missing` 使用确定性 FFmpeg recipe；未知类别、显式素材丢失、cue 越界或非法增益保持阻塞
- `apply` 统一 48 kHz stereo、trim/pad、短 fade、毫秒级 `adelay` 和受限增益；`amix normalize=0` 保持旁白电平，limiter 只做峰值保护，完整解码通过后才原子提升输出
- 完整 1× 听完后运行 `confirm`，逐项确认 `speech_intelligibility / cue_timing / sfx_level / creative_fit / clicks_or_clipping`；随后 `verify --strict`。cue sheet、旁白、音效、输出或 review 绑定漂移都会重新阻塞
- 该输出不含 BGM；音乐继续走 `render_final.py --bgm-ducking`，混入音乐后重新完整试听并运行最终音频 QA。详见 [docs/prompts/123-audio-cue-mix.md](docs/prompts/123-audio-cue-mix.md)

**Video Stabilization source-bound 手持防抖**（仅用于不想要的抖动）：
- 先运行 `video_stabilization.py doctor`。`plan --backend auto` 优先两遍 `vidstab`；缺少该 filter 时会把单遍 `deshake` 明确写进计划并保留降级 warning，不会在 apply 时静默换后端
- 原片看过后，用 `plan origin/handheld.mp4 --decision stabilize --reviewed-by editor --output work/video_stabilization_plan.json --markdown work/video_stabilization_plan.md` 记录源 SHA-256、profile 和人工决定；有意手持 / pan 应改用 `--decision keep`
- `apply ... --output work/handheld-stabilized.mp4 --comparison verify/handheld-stabilization-compare.mp4` 只写新工作副本与全长左/右 A/B；随后必须 1× 看完整 comparison，再运行 `confirm --reviewed-by ... --note ...`
- `pipeline_manifest.py` 会实时检查源片、稳定版、comparison 的 hash 与复核状态。稳定化不能修复滚动快门、运动模糊或失焦；后续用工作副本，不覆盖 `origin/`。详见 `docs/prompts/84-video-stabilization.md`

**Video Enhancement 本地放大 / 补帧交付**（现有成片需要更高尺寸或帧率时运行）：
- 先跑 `runtime_preflight.py analyze --profile video_enhancement ... --strict`，再用 `video_enhancement.py plan output/master.mp4 --target-short-edge 1080 --fps 60 --enhanced output/master-enhanced.mp4 --comparison verify/video-enhancement-ab.mp4 --output work/video_enhancement_plan.json --markdown work/video_enhancement_plan.md`
- `--target-short-edge` 同时适配横竖屏，也可改用 `--scale 2`；只补帧时省略尺寸参数。脚本只接受放大和不低于源 cadence 的目标，源 hash、显示尺寸、目标设置、filter、输出与 review 都进入 canonical plan
- `apply` 用 Lanczos 与可选 FFmpeg motion-compensated `minterpolate`，输出 H.264/AAC；尺寸、帧率、时长、音轨存在性和两份 MP4 的完整解码都通过后才原子提升
- 完整正常速度看 source-left/enhanced-right A/B，再单独带声看完整增强件；`confirm` 必须逐项给 `detail / edges / motion_cadence / audio_sync` 的 `pass|fail`。任一 fail 继续阻断
- Lanczos 只是确定性 resize，不能恢复源片不存在的细节；补帧可能在切点、遮挡、手、脸和高速运动产生 ghost/warp。需要 ML VSR 或生成式修复时另走经授权工具，并重新执行真实输出复核。详见 [docs/prompts/126-video-enhancement.md](docs/prompts/126-video-enhancement.md)

**Chroma Key 绿幕 / 蓝幕抠像与换背景**（仅用于明确纯色幕布）：
- 先运行 `chroma_key.py prepare --project-dir . --foreground origin/presenter-green.mp4 --background origin/studio.png --output-video output/presenter-studio.mp4 --preview-dir verify/chroma_key --report work/chroma_key.json --markdown work/chroma_key.md`
- `prepare` 在默认 15%/50%/85% 时间点各生成 composite 与黑白 matte；检查头发/手/衣物边缘、主体缺口、绿/蓝溢色和背景透视/光色，必要时只改一项 `--similarity / --blend / --despill` 后重新预览
- 四项均确认后运行 `review --edge-quality pass --subject-integrity pass --spill-control pass --background-fit pass --reviewer ... --note ...`，再运行 `apply --strict` 和 `verify --strict`
- 图片背景保持，视频背景从第一帧循环且忽略其音轨；最终声音只沿用前景。源/背景/预览/filter/output 任一漂移都会让 live gate 失效
- 这不是无幕布 AI matting 或逐帧 roto；复杂透明物、反光、幕布皱褶或主体同色应重拍或交给专业 keyer。完整说明见 `docs/prompts/99-chroma-key.md`

**PIP Overlay 录屏摄像头小窗**（录屏教程可选）：
- 运行 `pip_overlay.py --camera origin/facecam.mp4 --segment "0,18,bottom_right" --segment "18,42,top_right" --sync-offset 0.18 --output work/pip_overlay_plan.json --markdown work/pip_overlay_plan.md`
- 渲染时追加 `--enrich-plan work/pip_overlay_plan.json`；可和 `screen_focus_plan.json`、`enrich_plan.json` 重复传入
- 输出 `pip_overlay_plan.v1`，包含 `pip_overlays[]`、每段位置、source_start、sync offset、尺寸比例、透明度和淡入淡出
- `render_final.py` 会随 `--primary-speed` / `--speed` 同步压缩 camera 小窗时间线，避免变速输出时 PIP 和主画面错位

**Audio Sync 外录音频自动对齐**（相机内录 + 外录麦克风时推荐）：
- 运行 `audio_sync.py --reference-media origin/camera.mp4 --external-audio origin/lav.wav --output work/audio_sync_plan.json --markdown work/audio_sync_plan.md --replace-output output/camera_lav_synced.mp4 --strict`
- 输出 `audio_sync_plan.v1`，包含 `alignment.offset_seconds`、`confidence`、`replace_audio.command`、Markdown 复核表和 `summary.blocking`
- 正数 offset 表示延迟外录音轨；负数 offset 表示裁掉外录音轨开头
- 确认计划后再加 `--apply` 执行 FFmpeg 替换音轨；脚本会 copy 原视频流、用同步后的外录音轨编码 AAC
- 如果自动估计低置信度，可用 `--offset 0.18` 这类手动偏移跳过估计；`pipeline_manifest.py` 会拦截低置信度或缺文件的 audio sync artifact

**Multicam Sync 多机位可逆同步计划**（两台以上设备录制同一事件时推荐）：
- 运行 `multicam_sync.py --reference-media origin/cam-a.mp4 --angle origin/cam-b.mp4 --angle origin/cam-c.mp4 --measure-clock-drift --output work/multicam_sync_plan.json --markdown work/multicam_sync_plan.md --preview-output output/verify/multicam_sync_preview.mp4 --apply-preview --strict`
- 输出 `multicam_sync_plan.v1`：每路 offset/confidence、自动最响音轨、reference/source coverage、公共 overlap、pairwise 一致性、可选 drift probes/线性 fit 和 preview command
- 原片不修改、不重编码；只有 `--apply-preview` 会生成短网格预览。正 offset 表示该机位 `t=0` 位于参考时间线更晚的位置
- 多音轨相机可用 `--audio-stream "origin/cam-b.mp4=2"` 指定有效轨；无音轨/人工拍板用 `--manual-offset "origin/cam-c.mp4=1.24"`
- 漂移测量默认关闭；启用后默认取 5 个 20 秒窗口，至少 4 个共识 inlier 才拟合 `offset(R)=intercept+slope*R`，报告明确符号的 ppm、测量分辨率、累计漂移、残差和未应用的 `atempo/setpts` advisory factors
- 漂移证据只覆盖选择的参考/源音轨；不能据此自动断言视频 PTS 或其他音轨共享同一时钟
- 漂移超阈值或拟合不可靠会进入 review gate；脚本不自动校正，音画必须使用同一仿射映射。未启用时，30 分钟以上仍必须复核头/中/尾
- 详细使用与边界见 [docs/prompts/76-multicam-sync.md](docs/prompts/76-multicam-sync.md)

**Audio-guided Multicam Switch 按说话者音频生成导播草稿**（同步通过后可选）：
- 运行 `multicam_switch.py plan --sync-plan work/multicam_sync_plan.json --speaker angle_00_cam-a=主持人 --speaker angle_01_cam-b=嘉宾 --program-audio angle_00_cam-a --delivery output/multicam_switch_draft.mp4 --output work/multicam_switch_plan.json --markdown work/multicam_switch_plan.md --strict`
- 每路音频分别按 P10 噪声底/P95 峰值归一；只有活动分数和领先 margin 同时达标才换机位，含糊窗口保持上一机位，短于 `--min-shot` 的闪切折回相邻镜头
- 高相关音频默认按共享混音/强串音阻断；`--allow-correlated-audio` 只保留显式 override warning，不能证明 speaker detection 可靠。广角、节目 master 或没有独立说话者音轨的机位不要映射成 speaker candidate
- `--program-audio` 指定连续节目声音，不随画面换麦。apply 统一画布/FPS/SAR 后硬切渲染，完成媒体合同与全量解码才提升输出
- 完整带声 1× 播放后，confirm 必须逐项记录 `speaker_selection / cut_timing / sync / audio_continuity`；源、同步计划、设置、输出或 review 漂移都会使 manifest gate 失效
- 详细使用与边界见 [docs/prompts/127-multicam-switch.md](docs/prompts/127-multicam-switch.md)

**Storyboard Plan 分镜与生成路由**（生成素材前推荐）：
- 运行 `storyboard_plan.py --transcript work/transcript.json --clean-script work/clean_script.md --output work/storyboard_plan.json --markdown work/storyboard_plan.md`
- 输出每个 shot 的时间码、narration、first/motion/last-frame 描述、`codex_imagegen` / `dreamina_video` / `remotion_hyperframes` / `media_library_broll` 路由、fallback 和 continuity anchors
- 使用生成视频 provider 前先运行 `provider_capability.py verify --bundle work/provider_capabilities.json --max-age-days 30 --strict`，核对 exact UI/API surface、model、mode、画幅、时长、分辨率、参考上限和证据日期
- 可选运行 `video_prompt_pack.py --storyboard-plan work/storyboard_plan.json --asset-root work --style-reference work/imagegen/style-key.png --capability-profile work/provider_capabilities.json --require-capability-profile --resolution 720p --output work/video_prompt_pack.json --markdown work/video_prompt_pack.md --strict`，把分镜转成 Dreamina/即梦 Seedance、Veo、LTX、Wan、Sora 提示词包、共享 style lock、approval 和 capability gate
- image-to-video 提交前运行 `reference_frame_preflight.py --prompt-pack work/video_prompt_pack.json --output work/reference_frame_preflight.json --markdown work/reference_frame_preflight.md --require-style-reference --strict`，拦截缺失/损坏/方向冲突/严重画幅冲突参考帧
- 再运行 `storyboard_assets.py --storyboard-plan work/storyboard_plan.json --asset-root work --media-library . --output work/storyboard_assets.json --markdown work/storyboard_assets.md --strict`，渲染前确认素材 `ready`
- `dreamina_video` 只表示适合视频生成，不会自动提交任务；提交 Dreamina/即梦前必须确认，因为可能消耗 credits
- 生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。

**Reference Story Formula 参考片故事公式迁移**（用户要求借鉴参考片情绪机制时运行）：
- 把参考视频和其 timecoded transcript 放进项目，再运行 `reference_story_formula.py prepare --project-dir . --reference-video origin/reference.mp4 --reference-transcript origin/reference_transcript.json --target-storyboard work/storyboard_plan.json --output work/reference_story_formula_request.json --markdown work/reference_story_formula_request.md --response-template work/reference_story_formula_response.json --strict`
- 完整看参考片并填写每个 beat 的 `mechanism / viewer_state_before / viewer_state_after / trigger / camera_function / transferable_rule / do_not_copy`；每个 reference transcript segment 必须恰好属于一个有序 beat
- 为目标 storyboard 的每个 shot 填 `beat_id / content_anchor / viewer_shift / surface_change / visual_action`，顺序不能倒退；同时明确排除参考片 pixels、audio、wording、branding 和 specific plot
- 运行 `audit --request ... --response ... --output work/reference_story_formula.json --markdown work/reference_story_formula.md --strict`，再执行 `verify --report work/reference_story_formula.json --strict`。输入、response 或派生报告漂移会 fail closed；长原文重合进入可见 warning
- 给 `video_prompt_pack.py` 加 `--reference-story-formula work/reference_story_formula.json`。脚本会 live-verify 与当前 storyboard 的 byte binding，并给每条 prompt 注入对应的结构、目标内容锚点和禁止复制合同。它不证明版权、原创度、留存效果或生成质量。详见 [docs/prompts/125-reference-story-formula.md](docs/prompts/125-reference-story-formula.md)

**Storyboard Animatic 分镜时长预演**（付费生成或正式剪辑前推荐）：
- 为每个 storyboard shot 准备一张已审静帧，再运行 `storyboard_animatic.py plan --project-dir . --storyboard work/storyboard_plan.json --panel shot_001=work/storyboard/shot_001.png --panel shot_002=work/storyboard/shot_002.png --delivery verify/storyboard_animatic.mp4 --output work/storyboard_animatic.json --markdown work/storyboard_animatic.md`
- `--panel SHOT_ID=PATH` 必须精确覆盖全部 shots；可选加 `--audio work/narration.wav`。工具绑定 storyboard、panels、音频的 SHA-256 和媒体元数据，按 shot starts 生成带镜头 ID/时间码的 CFR H.264 MP4
- 执行 `apply` 后完整 1× 播放，检查 `shot_order / timing_rhythm / panel_legibility / visual_continuity / audio_sync`，再运行 `confirm`；无音频时 `audio_sync=not_applicable`
- `verify --strict` 与 `pipeline_manifest.py --require storyboard_animatic --strict` 会现场重读全部输入、完整解码交付件并核对 review/output 绑定。Animatic 只验证静帧顺序和节奏，后续生成片与成片仍需各自 review。详见 [docs/prompts/121-storyboard-animatic.md](docs/prompts/121-storyboard-animatic.md)

**Sequence Handoff 生成前镜头接力与剪辑边界**（两条以上生成镜头时推荐）：
- 运行 `sequence_handoff.py prepare --project-dir . --storyboard work/storyboard_plan.json --output work/sequence_handoff_request.json --markdown work/sequence_handoff_request.md --response-template work/sequence_handoff_response.json --strict`
- 逐相邻镜头复核 `carrier_type / offer_from / receive_in / edit_type / match_requirement`，同时声明 180° 轴、屏幕运动方向、音频桥、头尾 edit handles、风险、fallback 和具体 review note；自动建议只读 storyboard 文本，不能代替人的空间/动作判断
- 用 `audit --request work/sequence_handoff_request.json --response work/sequence_handoff_response.json --output work/sequence_handoff.json --markdown work/sequence_handoff.md --strict` 生成报告，再以 `verify --report work/sequence_handoff.json --strict` 现场重算；`revise`、缺字段、非法轴线/方向翻转、源分镜或决定漂移都 fail closed
- 最终 prompt pack 加 `--project-dir . --sequence-handoff work/sequence_handoff.json`；工具会先 live-verify，再将首镜 handoff-out、末镜 receive-in 和中间镜头的双向合同写进对应 provider prompt
- 文本合同不证明最终像素连续；生成后仍执行 `generated_clip_review.py` 和 `generated_sequence_review.py`，组装后正常速度复核所有边界。详见 [docs/prompts/120-sequence-handoff.md](docs/prompts/120-sequence-handoff.md)

**Video Prompt Pack + Reference Frame Preflight 视频生成提示词与参考帧门禁**（生成视频前推荐）：
- 先按 [docs/prompts/96-provider-capability.md](docs/prompts/96-provider-capability.md) 建立 `provider_capabilities.json`，再运行 `provider_capability.py verify --bundle work/provider_capabilities.json --max-age-days 30 --strict`；profile 绑定 exact provider/surface/model 和来源，默认超过 30 天就阻塞
- 运行 `video_prompt_pack.py --project-dir . --storyboard-plan work/storyboard_plan.json --sequence-handoff work/sequence_handoff.json --asset-root work --character "same host" --brand-anchor "palette=charcoal,white,signal yellow" --style-reference work/imagegen/style-key.png --capability-profile work/provider_capabilities.json --require-capability-profile --resolution 720p --output work/video_prompt_pack.json --markdown work/video_prompt_pack.md --strict`
- 输出 `global.character_sheet_prompt`、`global.style_reference`、`global.sequence_handoff`、`items[].prompt`、`items[].sequence_handoff`、`items[].negative_prompt`、`items[].surface/model/resolution`、`items[].capability_profile`、`items[].capability_issues`、`items[].approval_status` 和 `summary.blocking`
- `--style-reference` 会把同一 style key 绑定到所有 shot，并在每条 provider prompt 加同一条 `STYLE LOCK`
- 参考图落盘后运行 `reference_frame_preflight.py --prompt-pack work/video_prompt_pack.json --output work/reference_frame_preflight.json --markdown work/reference_frame_preflight.md --require-style-reference --strict`
- `reference_frame_preflight.v1` 检查首帧/style key 是否存在、可解码、方向/画幅是否匹配、分辨率是否过低和透明背景；阻塞项接入 `pipeline_manifest.py`
- `--provider veo|ltx|wan|sora|dreamina_seedance` 可把同一分镜改写成指定模型提示词；`--animate-stills` 会把 `codex_imagegen` 参考图 route 转为 image-to-video 提示词
- `--strict` 会在 generated-video provider 还没 `--approved`，或 capability profile 缺失/过期/设置越界时返回 2；脚本不提交 provider 任务、不消耗 credits
- 生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。

**Generation Reference Preflight 图片 / 视频 / 音频生成参考门禁**（使用多模态 reference 时必跑）：
- provider profile 的 `reference_media` 要记录 frame/reference 是否互斥、是否支持 audio-only、总文件数，以及图片/视频/音频的扩展名、字节、单条时长和总时长上限；未核验的限制不得靠猜测补齐
- 先用 `generation_reference_preflight.py template --project-dir . --prompt-pack work/video_prompt_pack.json --output work/generation_references.json` 建清单；每个实际提交素材填写 `kind / path / role / exclude`，顺序就是各类型的 `@ImageN / @VideoN / @AudioN` 顺序
- 运行 `generation_reference_preflight.py analyze --project-dir . --prompt-pack work/video_prompt_pack.json --references work/generation_references.json --capability-profile work/provider_capabilities.json --output work/generation_reference_preflight.json --markdown work/generation_reference_preflight.md --strict`
- 报告会完整解码本地 reference，检查类型、扩展名、大小、单条/合计时长、数量、audio-only、frame/reference 模式互斥和 capability profile 绑定，并输出带明确角色与排除项的 `shots[].provider_prompt`
- 提交时使用 ready 报告里的有序素材清单和 `provider_prompt`；之后以 `verify --report ... --strict` 或 `pipeline_manifest.py --require generation_reference_preflight --strict` 现场复查。详见 [docs/prompts/122-generation-reference-preflight.md](docs/prompts/122-generation-reference-preflight.md)

**Generation Task Log 异步生成任务台账**（提交生成任务后推荐）：
- 从 provider 决策生成待审批台账：`generation_task_log.py import-provider-decision --provider-decision work/provider_decision.json --log work/generation_tasks.json --markdown work/generation_tasks.md --strict`
- Dreamina/即梦提交后必须保存 `submit_id`：`generation_task_log.py add --log work/generation_tasks.json --provider dreamina --task-id <submit_id> --shot-id shot_002 --expected-path work/generated_video/shot_002.mp4 --status submitted`
- 下载完成后更新本地文件：`generation_task_log.py update --log work/generation_tasks.json --provider dreamina --task-id <submit_id> --status downloaded --asset-path work/generated_video/shot_002.mp4 --markdown work/generation_tasks.md`
- 输出 `generation_task_log.v1`，包含 `poll_command`、`download_command`、`readiness` 和 `summary.blocking`
- `completed` 但没有本地 `asset_path` 仍会阻塞；`pipeline_manifest.py` 会自动识别 `generation_tasks.json` 并把未清零任务列为 gate

**Generated Clip Review 生成视频片段复核**（生成结果下载后、组装前必跑）：
- 先刷新 `storyboard_assets.json`，再运行 `generated_clip_review.py prepare --project-dir . --asset-manifest work/storyboard_assets.json --contact-sheet-dir verify/generated_clips --output work/generated_clip_review_request.json --markdown work/generated_clip_review_request.md --response-template work/generated_clip_review_response.json`
- reviewer 必须完整执行 1× 带声、0.25×、静音看画面、只听声音四遍检查；contact sheet 只是抽样导航，不能代替播放完整片段
- response 对每条 clip 记录 identity/wardrobe、action/end state、motion/anatomy/physics、camera、frame integrity、look consistency 六项 1–5 分，以及 hard-fail code、`keep_ranges` / `remove_ranges`、是否重生和具体 `prompt_fix`
- `pass` 要求加权分 ≥80 且无删段；`pass_with_edits` 要求 ≥65，并由 keep/remove 精确覆盖全片；常识/物理、身份、道具、文字水印、连续性或音画 hard fail 无论总分多高都必须 `fail`
- 填完 response 后运行 `generated_clip_review.py audit --request work/generated_clip_review_request.json --response work/generated_clip_review_response.json --output work/generated_clip_review.json --markdown work/generated_clip_review.md --strict`；任何 clip/contact sheet 漂移、缺审、非法区间或需重生都会阻塞
- 组装/发布前再运行 `generated_clip_review.py verify --report work/generated_clip_review.json --strict`，也可用 `pipeline_manifest.py --require generated_clip_review --strict`。reviewer label 不是身份认证或数字签名

**Generation Chain Handoff 已审生成片末帧接力**（同一场景连续生成时运行）：
- 仅在 `sequence_handoff.v1` 已批准该相邻边界、上一镜 `generated_clip_review.v1` 为 `pass` 或 `pass_with_edits` 时使用；换场、时间跳跃、故意跳切和普通剪辑匹配不要强行接力
- 运行 `generation_chain_handoff.py prepare --project-dir . --clip-review work/generated_clip_review.json --sequence-handoff work/sequence_handoff.json --boundary boundary_001 --frame-output work/generation_chain/boundary_001_tail.png --output work/generation_chain_handoff.plan.json --markdown work/generation_chain_handoff.plan.md`；脚本枚举 decoded frames，从完整 clip 或最后一个 approved keep range 取确切末帧，并要求源帧/PNG 的 RGB24 像素摘要一致
- 看完上一镜和 PNG 后执行 `confirm --decision use_exact_start_frame --reviewed-by ... --same-scene-confirmed --tail-frame-accepted --original-anchors-preserved --notes ... --output work/generation_chain_handoff.json --strict`；尾帧不适合时用 `reject` 并返回分镜、生成或普通剪辑边界
- 提交下一镜前运行 `verify --plan work/generation_chain_handoff.json --strict`，再给 `video_prompt_pack.py` 加 `--generation-chain-handoff work/generation_chain_handoff.json`。目标镜头改为 `image_to_video`，已审末帧成为 exact first frame；prompt 同时保留原角色/产品/style anchors，并限制为一个主动作和一种机位行为
- 上游报告、clip、批准区间、frame index/PTS、PNG bytes/pixels、人工决定或 canonical artifact ID 漂移都会阻塞；每条新生成片仍需逐片 review，全部完成后再跑跨镜头 review。详见 [docs/prompts/124-generation-chain-handoff.md](docs/prompts/124-generation-chain-handoff.md)

**Generated Motion Window 生成视频有效运动窗口**（逐片视觉 review 之后、跨镜头组装前运行）：
- contact sheet 可能漏掉 0.25–1 秒的冻结开头或短暂运动；对每条通过视觉复核的生成片运行 `generated_motion_window.py analyze work/generated_video/shot_001.mp4 --project-dir . --output work/generated_motion_window/shot_001.json --markdown work/generated_motion_window/shot_001.md`
- 脚本用本地 FFmpeg `freezedetect` 保存 `freezes[]` 与其补集 `active_intervals[]`，绑定 source SHA-256、媒体契约、参数和 canonical plan id；刚 analyze 固定阻塞，不能把 detector 建议当批准
- 完整 1× 播放源片后运行 `confirm ... --decision trim|keep|reject --reviewed-by ... --note ...`。`trim` 默认使用建议区间，也可显式 `--start/--end`；两个边界都必须落在 active interval 内
- `trim` 在 apply 前继续阻塞；`apply ... --output work/generated_motion_window/shot_001-active.mp4` 只写新 H.264/AAC、`yuv420p` working copy，验证时长/尺寸/fps/音轨并完整解码后才原子提升。原片、计划、检测证据或 output 漂移都会 fail closed
- 新 working copy 必须重新完整播放，并重跑 generated-clip review、sequence/final QA 和下游审批；`pipeline_manifest.py --require generated_motion_window --strict` 会逐个 live verify `work/generated_motion_window/*.json`。FFmpeg freeze 只衡量全帧相似度，不能判断动作意义、表演、身份、物理或产品质量。详见 [docs/prompts/102-generated-motion-window.md](docs/prompts/102-generated-motion-window.md)

**Scoped Video Edit Review 局部 AI 视频编辑范围复核**（换装/换背景/换包装/局部 VFX 等 edit mode 后必跑）：
- 每次 provider call 只声明一个确切变化；运行 `scoped_video_edit_review.py prepare --project-dir . --source origin/source.mp4 --edited work/scoped_video_edit.mp4 --change-category wardrobe --change "change only the jacket from blue to red" --preserve subject_identity --preserve performance_motion --preserve camera_motion --preserve framing_composition --preserve source_audio --evidence-dir verify/scoped_video_edit --output work/scoped_video_edit_review_request.json --markdown work/scoped_video_edit_review_request.md --response-template work/scoped_video_edit_review_response.json`
- `prepare` 绑定原片/编辑结果 SHA-256 与媒体契约，生成范围内 15%/50%/85% 同时间点左右并排 JPEG，以及完整左右并排 H.264 preview；两条输入音轨存在时，preview 把 source/edited 分别保留为独立音轨
- reviewer 必须分别以 1×、带声完整看原片与编辑结果，再看完整 A/B scope preview；目标变化和每个 `--preserve` 只允许 `pass|fail|not_observable`，不能看不清仍猜 pass
- `audit --strict` 只在目标确实完成、全部保护项通过、三遍播放确认齐全、时长/尺寸/帧率未漂移时 ready；失败必须写具体 `repair_action`
- 组装/发布前运行 `verify --report work/scoped_video_edit_review.json --strict`，或 `pipeline_manifest.py --require scoped_video_edit_review --strict`。脚本不调用 provider、不上传素材、不消耗 credits；建议 prompt 是 provider-neutral contract，不能替代当前 surface 的 capability 核验。详见 `docs/prompts/100-scoped-video-edit-review.md`

**Generated Sequence Review 跨镜头连续性复核**（两条以上生成片段逐片通过后、组装前必跑）：
- 运行 `generated_sequence_review.py prepare --project-dir . --clip-review work/generated_clip_review.json --storyboard-plan work/storyboard_plan.json --evidence-dir verify/generated_sequence --output work/generated_sequence_review_request.json --markdown work/generated_sequence_review_request.md --response-template work/generated_sequence_review_response.json`
- 脚本按 storyboard 顺序，为每个相邻边界提取批准范围内的上一镜尾帧、下一镜首帧、并排图和“尾部 + 头部”无声 1× preview；如果上游是 `pass_with_edits`，只使用批准的首个/最后一个 keep range
- 完整查看 preview 和 comparison 后，为 identity/wardrobe、prop state、spatial orientation、action end state、camera framing、lighting/palette 填 `match|intentional_change|mismatch|not_applicable`。至少两项必须真实评估；`mismatch` 必须 `fail`，给 failure code 和具体 `repair_action`
- 运行 `generated_sequence_review.py audit --request work/generated_sequence_review_request.json --response work/generated_sequence_review_response.json --output work/generated_sequence_review.json --markdown work/generated_sequence_review.md --strict`，组装/发布前再 `verify --report work/generated_sequence_review.json --strict`；clip、上游 review、storyboard 或任一 evidence bytes 漂移都会阻塞
- `pipeline_manifest.py --require generated_clip_review --require generated_sequence_review --strict` 可把逐片和跨镜头两层都设为门禁。preview 无声，不能替代最终 master 的完整声画复核；reviewer label 和 SHA-256 不是身份认证或签名

**Generation Lessons 生成视频经验闭环**（可选；只沉淀可泛化且人工明确批准的经验）：
- 从已完成的 `generated_clip_review.json` 选定一条 clip，运行 `generation_lessons.py add --library work/generation_lessons.json --review work/generated_clip_review.json --clip-id shot_002 --category hand_contact --lesson "For hand-to-prop contact, isolate one interaction and keep the hand visible through release." --approved-by "<reviewer-label>" --model seedance-2.0`
- `add` 会实时重算 canonical review，允许“片段确实需要重生”这一预期 blocker，但拒绝 source/contact-sheet 漂移、漏审、非法 response、stored summary/report-id 篡改；entry 绑定 report/request/clip/contact-sheet SHA-256。`approved_by` 只是审计标签，不是身份认证或签名
- 复用前运行 `generation_lessons.py verify --library work/generation_lessons.json --strict`；按 provider/model/category 预览可用 `generation_lessons.py select --library work/generation_lessons.json --provider dreamina_seedance --model seedance-2.0 --limit 3 --output work/selected_generation_lessons.json --markdown work/selected_generation_lessons.md`
- 新证据与旧规则冲突时，不删除旧 entry；新建 lesson 并加 `--supersedes <old-lesson-id>`。旧 evidence 继续留在 library，但只要新 entry 也匹配当前 provider/model/category，`select` 就排除被替代规则
- 下一次生成提示词包显式加 `video_prompt_pack.py ... --lesson-library work/generation_lessons.json --lesson-model seedance-2.0 --lesson-limit 3`。provider 专属规则优先，未给 `--lesson-model` 时不会误用 model-specific 经验；脚本只追加人工批准的 `lesson`，不会自动把 clip-specific `prompt_fix` 当成通用规则，也不会自动重生或消费 credits
- 生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。
- 详细说明见 [docs/prompts/89-generated-clip-review.md](docs/prompts/89-generated-clip-review.md)

**Storyboard Assets 素材清单与预检**（分镜后、渲染前推荐）：
- 运行 `storyboard_assets.py --storyboard-plan work/storyboard_plan.json --asset-root work --media-library . --output work/storyboard_assets.json --markdown work/storyboard_assets.md`
- 输出每个 shot 的素材状态：`ready` / `candidate_found` / `needs_generation` / `needs_approval` / `needs_render` / `search_needed`
- 如果传入 `--media-library`，`media_library_broll` shot 会从素材索引里生成 `candidate_paths` + `candidate_scores`，按 tag、文件名、metadata、时长和画幅透明排名
- 加 `--strict` 时，任何素材未 ready 都会返回退出码 2，适合放在最终渲染前
- `needs_approval` 代表 Dreamina/即梦等可能消耗 credits 的任务，必须先确认再提交；生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。

**自定义封面**（`cover_image`）：
- 提供自定义封面 PNG 路径，优先于自动生成的封面
- 尺寸应与视频分辨率匹配（如 1080x1920）

**持续叠加层**（`video_overlay`）：
- 提供透明 PNG 路径，在封面之后的整个视频上持续叠加显示
- 适用场景：品牌水印、系列标识（如 DAY 标签、数据指标）等
- PNG 必须包含 Alpha 通道（RGBA），透明区域不会遮挡视频

**闪烁圆点**（`rec_blink`）：
- 在视频上叠加一个周期性闪烁的小圆点 PNG（如录像机 REC 标志）
- `dot_image`：圆点 PNG 路径（建议 12-16px，RGBA 格式）
- `x`, `y`：圆点在视频画面中的像素坐标
- `period`：闪烁周期（秒），默认 1.0（0.5 秒亮 + 0.5 秒灭）

**结尾卡片**（`end_cards`）：
- 在视频末尾追加黑屏文字卡片，每张卡片有 300ms 淡入淡出
- `text`：卡片文字内容，用 `\n` 换行
- `duration`：每张卡片显示时长（秒），建议 3.0-4.0
- 文字居中显示，字号为正文字幕的 1.4 倍

**口播稳态底噪清理**（`speech_denoise`）：
- 默认 `off`；只有空调、风扇、电流声、轻微房间底噪相对稳定时才启用 `"light"` / `"medium"` / `"strong"`
- CLI 可用 `--speech-denoise light`；配置已开启时可用 `--no-speech-denoise` 临时关闭
- 三档固定 80 Hz、2-pole 高通，FFT reduction 为 6/9/12 dB；`strong` 不会超过 12 dB
- 顺序固定为 `highpass → afftdn → atempo → dynaudnorm → acompressor → loudnorm → cover delay → BGM ducking/mix`
- 已做 VAD/noise gate、Adobe Podcast、Descript、RX 或机内强降噪的音轨通常保持 off；数字静音、噪声突变、多麦、瞬态敲击/咳嗽和混响必须另行处理
- 先渲染 10–20 秒 off/light/medium A/B，戴耳机正常速度试听辅音、尾音和停顿；渲染后继续运行 `audio_master_report.py --strict`

**背景音乐**（`bgm`）：
- 提供背景音乐文件路径（MP3/M4A/WAV 等 FFmpeg 支持的格式）
- `bgm_volume`：BGM 音量（0.0-1.0），默认 0.15（人声为主，BGM 为辅）
- `bgm_fade_out`：结尾淡出时长（秒），默认 3.0
- `bgm_ducking: true` 或 CLI `--bgm-ducking`：用最终旁白轨作为 sidechain，旁白出现时自动压低 BGM；封面、停顿和片尾无旁白时音乐会自然恢复
- 默认 ducking 参数是 threshold `0.03`、ratio `8`、attack `20ms`、release `500ms`；只有试听或 `audio_master_report.py` 证据表明需要时才调整
- ducking 分支用 `amix normalize=0` 保留人声响度，并在混音末尾加 `alimiter=0.95` 防止峰值溢出；旧配置默认仍关闭，保持已有输出兼容
- BGM 自动循环播放直到视频结束，不需要预先剪辑长度
- 推荐免费可商用音乐源：Pixabay Music、Mixkit、YouTube Audio Library
- 选曲建议：口播/教程用轻柔纯音乐（无人声），节奏不要太强，避免抢人声

**字幕风格预设**（`subtitle_style`）：
| 风格 | 效果 | 适用场景 |
|------|------|---------|
| `normal` | 白字黑描边（默认） | 适合所有场景 |
| `karaoke` | 逐词高亮 | 音乐/节奏感内容 |
| `bold_pop` | 粗描边高对比 | MrBeast/Hormozi 风格 |
| `pop_in` | 每条字幕入场缩放后回弹 | 节奏较快的短视频；短于 0.3 秒的字幕保持静态 |
| `neon` | 霓虹灯青紫色 | 科技/潮流内容 |
| `minimal` | 极简无描边 | 文艺/安静内容 |
| `yellow_pop` | 黄字黑描边 | 高可见度，户外/嘈杂画面 |

**卡拉OK字幕 / 逐词高亮**（`subtitle_style: "karaoke"`）：
- 在 config 中设置 `"subtitle_style": "karaoke"` 启用逐词高亮字幕
- 需要先用 `--word-timestamps` 参数进行语音识别，获取逐词时间戳
- `subtitle_highlight_color`：当前词高亮颜色，默认 `"#FFFF00"`（黄色）
- `subtitle_base_color`：未说到的词底色，默认 `"#FFFFFF"`（白色）
- `subtitle_base_alpha`：底色透明度 hex，默认 `"80"`（半透明）
- 如果 transcript 中没有 word 级时间戳，会自动回退到按字符均匀分布（效果稍差）
- 也可通过 CLI 参数 `--subtitle-style karaoke` 覆盖 config
- 典型工作流：
  ```bash
  # 1. 转录时开启逐词时间戳
  python3 scripts/transcribe.py audio.wav --model auto --language zh --word-timestamps
  # 2. 渲染时选择 karaoke 字幕风格
  python3 scripts/render_final.py --config render_config.json --output final.mp4 --subtitle-style karaoke
  ```

**逐条弹入字幕**（`subtitle_style: "pop_in"`）：用 `render_final.py --subtitle-style pop_in`，或在 render config 中设 `"subtitle_style": "pop_in"`。每条字幕按成片速度后的时长独立做 80% → 108% → 100% 缩放；短于 0.3 秒的字幕直接全尺寸显示。`subtitle_style_preview.py --styles pop_in` 的静帧只能检查最终字形、位置和对比度，须在最终 MP4 中按正常速度检查入场动画及安全区。

**音频源替代（M4A/独立音频）**：
- 如果有独立录制的音频文件（M4A 等），可先用 ffmpeg 转为带黑屏视频轨的 MP4：
  ```bash
  ffmpeg -f lavfi -i "color=c=black:s=1080x1920:r=30:d=60" -i audio.m4a -c:v libx264 -c:a aac -shortest audio.mp4
  ```
- 然后在 clip 中用 `"video": "audio.mp4"` 提供音频源，用 `"broll"` 提供画面
- 这样可以将补录的配音与任意画面组合

**封面标题**：
1. 如果用户提供了标题，直接使用。
2. 如果用户没有特别要求，**站在观众角度**总结一个吸引人的标题（6-15 个字）。
3. `subtitle` 可选，用于补充情感钩子或关键信息。
4. **移动端优先**：封面在手机列表页里只是一个缩略图，标题必须先保证可读性，再考虑画面细节。

**封面文字排版规则**：
- 标题按**一行最多约 8 个汉字**来设计；超过时自动换行，不要把单行塞得过满。
- 英文/数字按**约半个汉字宽度**估算；例如 `AI`、`GPT-5` 之类不应把整行宽度挤爆。
- `subtitle` 字号默认按标题的**约 50%** 处理，只承担补充信息，不和主标题争抢视觉中心。
- 如果标题超过两行，优先**缩短文案**，不要继续缩小字号来硬塞。
- 做教程/工具类封面时，主标题尽量控制在 **4-8 个字**，副标题控制在 **6-12 个字**。

**封面风格**（`cover_style`）— 根据视频内容选择最合适的风格：
| 风格 | 适用场景 | 视觉效果 |
|------|---------|---------|
| `bold` | 教程、科普、技术 | 黑底 + 大号白色粗体字，简洁有力 |
| `news` | 热点、观点、争议 | 深色渐变底 + 白色标题 + 黄色副标题，冲击力强 |
| `frame` | Vlog、实拍、场景 | 视频首帧做背景 + 暗色遮罩 + 描边白字 |
| `gradient` | 生活、情感、艺术 | 紫粉渐变底 + 发光白字，温柔优雅 |
| `minimal` | 思考、文化、深度 | 纯黑底 + 细体白字，极简克制 |
| `white` | 教程、产品、品牌化内容 | 纯白底 + 深色字，现代感更强 |
| `techcard` | 屏幕录制、软件教程、AI 工具演示 | 左侧大标题 + 右侧画面卡片，兼顾信息量和可读性 |

AI agent 应根据视频主题和内容语气自动选择：
- 科技/工具类 → `bold` 或 `news`
- 争议/观点类 → `news`（白标题+黄副标题效果最抢眼）
- Vlog/实拍类 → `frame`
- 情感/生活类 → `gradient`
- 深度/文化类 → `minimal`
- 纯桌面录屏 / 软件教程 → `techcard` 优先；如果画面太杂，就退回 `bold` / `white`

**背景取帧规则**：
- 不要机械地使用第一帧。对于录屏教程，优先选择**信息密度更高**、界面更完整的一帧做背景或卡片图。
- 如果背景画面会影响标题识别，优先使用 `bold` / `white` / `minimal` 这类纯底风格。
- 单独预览封面时，可用 `scripts/generate_cover_image.py --frame-timestamp 00:10:00` 指定取帧时间。

**多封面 A/B 方案与最终选择**：
```bash
python3 scripts/cover_variants.py output/final_xhs.mp4 \
  --title "20分钟出片" \
  --subtitle "AI剪辑完整流程" \
  --caption output/caption.json \
  --platform xhs \
  --frame-timestamp 12.5 \
  --output-dir output/covers \
  --render \
  --output work/cover_variants.json \
  --markdown work/cover_variants.md
```

默认产出 3 套方案和 `*_preview.png` 小图。先按 feed-size 预览比较，再重跑并加 `--select cover-c --require-selection --strict` 记录最终封面。标题负责主题/关键词，封面负责结果/情绪/反差/证据；需要强制不重复时加 `--require-distinct-cover-text`。`pipeline_manifest.py --require cover_variants` 可把选择设为发布 gate。若需要 AI 生成或编辑封面底图，生图优先使用 Codex 内置 `image_gen` 工具，即 OpenAI GPT Image 2（`gpt-image-2`）。

**封面时长**（`cover_duration`）：
- 默认 2.0 秒，将第一帧冻结并叠加封面
- 也可通过 `--cover-duration` 命令行参数覆盖

**章节划分**：
- 根据视频内容逻辑划分章节，建议 **不超过 4 个章节**
- 章节名要**简短**（2-4 个字），如：痛点、原因、方案、工具
- 章节时间需要根据选定片段的累计时长精确计算

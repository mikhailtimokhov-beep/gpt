### Phase 6: Post-render Validation（渲染后验证）

渲染完成后，对最终视频执行验证流程：

**6a. 机器质检（先跑）**：
```bash
python3 scripts/render_qa.py final.mp4 \
  --platform douyin \
  --json final_qa.json \
  --review-dir verify/final_qa \
  --review-clips
```

`render_qa.py` 会检查容器元数据、平台尺寸、视频/音频流、黑屏、长静帧和长静音。对小红书派生文件使用 `--platform xhs`，对抖音/视频号使用 `--platform douyin` 或 `--platform wxch`。`--review-dir` 会写 `render_qa_review.json` / `.md`，`--review-clips` 会为可疑区间抽取短 MP4；如果只想快速查元数据，可加 `--no-filters`。

**6a00. 最终音视频轨覆盖（master 和每个重要平台版必跑）**：
```bash
python3 scripts/stream_coverage_qa.py analyze final.mp4 \
  --project-dir . \
  --output verify/stream_coverage_qa.json \
  --markdown verify/stream_coverage_qa.md \
  --strict
python3 scripts/stream_coverage_qa.py verify \
  --report verify/stream_coverage_qa.json \
  --project-dir . --strict
```

该门禁完整解码成片，并对首条视频/音频流分别统计 decoded frame count、首帧 PTS、尾帧结束时间和 timeline digest；默认阻断音视频首尾偏移或各流未覆盖容器时间线。render plan 有确切时长/帧数时追加 `--expected-duration`、`--expected-video-frames`。AAC priming/discard 不使用 `nb_frames` 作硬门禁，视频帧数仍会核对。报告通过后完整 1× 播放确切交付文件。详见 [docs/prompts/114-stream-coverage-qa.md](docs/prompts/114-stream-coverage-qa.md)。

**6a0. 同时间线重编码画质（压缩 / 转码衍生件必跑）**：
```bash
python3 scripts/encode_quality_qa.py analyze output/master.mp4 output/final_delivery.mp4 \
  --project-dir . \
  --output verify/encode_quality_qa.json \
  --markdown verify/encode_quality_qa.md \
  --strict
python3 scripts/encode_quality_qa.py verify \
  --report verify/encode_quality_qa.json --project-dir . --strict
```

仅在 reference/candidate 保持同一时间线和同一构图时使用；fps 差超过 `0.01`、时长差超过 1 帧或显示画幅不同会直接拒绝。默认 mean SSIM `≥0.95`、P05 SSIM `≥0.88`、有限帧 mean PSNR `≥35 dB`；候选分辨率不同但画幅一致时才 Lanczos 归一并 WARN。按 Markdown 最差帧时间码 A/B 查看并完整 1× 播放，不能把指标当成人工画质批准。它不测音频，也不适用于 crop/grade/HDR/retime/interpolation；本实现不调用 `libvmaf`，不声称 VMAF。`pipeline_manifest.py --require encode_quality_qa --strict` 可设为发布 gate。详见 [docs/prompts/107-encode-quality-qa.md](docs/prompts/107-encode-quality-qa.md)。

**6a1. 音频声道完整性（最终 master 和重要平台版必跑）**：
```bash
python3 scripts/audio_channel_qa.py analyze final.mp4 \
  --project-dir . \
  --output verify/audio_channel_qa.json \
  --markdown verify/audio_channel_qa.md \
  --strict

python3 scripts/audio_channel_qa.py verify \
  --report verify/audio_channel_qa.json \
  --project-dir . \
  --strict
```

`audio_channel_qa.py` 用本地 FFmpeg 固定窗口测量左右声道活动、起始偏移、能量平衡、相位相关和 mono fold-down 能量损失。mono 直接通过声道专项；stereo 会现场测量；多声道要求先定义明确 downmix。它不改音频，也不替代完整 1× stereo/mono 试听、`audio_master_report.py` 的响度/爆峰检查或同步复核。详见 [docs/prompts/106-audio-channel-qa.md](docs/prompts/106-audio-channel-qa.md)。

**6a2. 短促音频掉点（最终独立人声优先）**：
```bash
python3 scripts/audio_dropout_qa.py analyze work/final_narration.wav \
  --project-dir . \
  --evidence-dir verify/audio_dropout_clips \
  --output verify/audio_dropout_qa_scan.json \
  --markdown verify/audio_dropout_qa_scan.md \
  --response-template verify/audio_dropout_qa_response.json \
  --strict
```

默认以 20 ms 窗口定位活跃音频之间 `40–400 ms` 的短近静音。出现候选时完整 1× 播放输入与全部 WAV，填写 `dropout | intentional_pause | uncertain`，再运行 `audit` 和 `verify`。确认掉点与不确定继续阻断；刻意停顿保留 warning。优先使用最终独立对白/旁白 stem，BGM/SFX 可能掩盖掉点。它不识别语音、不修音，也不替代 `audio_master_report.py`。详见 [docs/prompts/113-audio-dropout-qa.md](docs/prompts/113-audio-dropout-qa.md)。

### Phase 5d: Final Audio Storyboard（视觉 EDL 锁定后重建声音）

多段生成视频或连续短片先锁定视觉 EDL，再按最终 record timeline 重建旁白、对白、环境声、Foley 与音乐；不要把剪辑前整片 audio plan 原样套回删短画面。EDL 每个 event 的 label 应对应 `storyboard_plan.json` 的 shot id：

```bash
python3 scripts/export_edl.py \
  --config work/render_config.json \
  --output work/locked_visual.edl \
  --manifest work/locked_visual.edl.json \
  --fps 30

python3 scripts/final_audio_storyboard.py prepare \
  --project-dir . \
  --edl work/locked_visual.edl.json \
  --storyboard work/storyboard_plan.json \
  --output work/final_audio_storyboard_request.json \
  --markdown work/final_audio_storyboard_request.md \
  --response-template work/final_audio_storyboard_response.json \
  --strict

# 填完 response 后：
python3 scripts/final_audio_storyboard.py audit \
  --project-dir . \
  --request work/final_audio_storyboard_request.json \
  --response work/final_audio_storyboard_response.json \
  --output work/final_audio_storyboard.json \
  --markdown work/final_audio_storyboard.md \
  --strict
python3 scripts/final_audio_storyboard.py verify \
  --project-dir . \
  --report work/final_audio_storyboard.json \
  --strict
```

每个 final section 必须明确 `single_track / sectioned_tracks / stems`、shared tone、voice、sound、music、stems 与原生声音保留理由；每个完全删除的 story beat 必须选择 `remove / rewrite_into_adjacent / offscreen_bridge`。重复 voiced line、漏审、时间映射或输入/response/report 漂移 fail closed。脚本不生成音频、不提交 provider、不消耗 credits；批准 JSON 仍要按实际音频工具改写成 timed cue sheet，付费生成前另行确认。详见 [docs/prompts/95-final-audio-storyboard.md](docs/prompts/95-final-audio-storyboard.md)。

如果最终旁白由多次 TTS、分段录音或逐句后处理拼成，在混入 BGM/SFX 前对**最终独立旁白音轨**逐短语测量：

```bash
python3 scripts/narration_loudness_qa.py analyze work/final_narration.wav \
  --segments work/final_narration_segments.json \
  --project-dir . \
  --output verify/narration_loudness_qa.json \
  --markdown verify/narration_loudness_qa.md \
  --strict
python3 scripts/narration_loudness_qa.py verify \
  --report verify/narration_loudness_qa.json \
  --project-dir . \
  --strict
```

默认每段目标 `-18 LUFS ±2 LU`、非例外段 spread `≤1 LU`、true peak `≤-2 dBTP`、LRA `≤5 LU`。创意例外必须逐段写 `reason + reviewer`，且不能绕过 peak ceiling；至少保留两段非例外短语才能判断 spread。报告绑定旁白、segment manifest、媒体契约、算法和现场复测。它不评判音色、发音、呼吸、接缝或表演，也不替代混音后 `audio_master_report.py` 的全片 `-16 LUFS` 检查。详见 [docs/prompts/105-narration-loudness-qa.md](docs/prompts/105-narration-loudness-qa.md)。

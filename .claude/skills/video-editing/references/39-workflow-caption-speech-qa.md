### Caption / Speech QA（字幕与独立人声活动对齐）

```bash
python3 scripts/caption_speech_qa.py analyze work/final_narration.wav \
  --subtitle-pack output/subtitles/final.json \
  --project-dir . \
  --output verify/caption_speech_qa.json \
  --markdown verify/caption_speech_qa.md \
  --strict
python3 scripts/caption_speech_qa.py verify \
  --report verify/caption_speech_qa.json \
  --project-dir . --strict
```

只把最终独立对白/旁白轨，或明确没有 BGM/SFX 的 speech-dominant 轨交给此脚本。它用本地 FFmpeg `silencedetect` 把静音区间反转成 audio-activity intervals，再逐条检查 `subtitle_pack.v1` cue 是否整条无活动、有效活动比例过低、头尾静音过长、内部停顿过长或超出音轨时间线。报告绑定人声轨、字幕 JSON、媒体契约、参数、完整测量和 canonical id；`pipeline_manifest.py --require caption_speech_qa --strict` 可设为发布 gate。振幅活动不是 speech recognition / forced alignment；有 BGM/SFX 会造成假通过，ready 也不能替代最终混音下完整 1× 字幕审看。详见 [docs/prompts/109-caption-speech-qa.md](docs/prompts/109-caption-speech-qa.md)。

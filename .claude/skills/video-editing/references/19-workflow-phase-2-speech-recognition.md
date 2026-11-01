### Phase 2: Speech Recognition（语音识别）

使用 [transcribe.py](./scripts/transcribe.py) 对音频进行语音识别，生成带时间戳的逐句文本：

```bash
python3 scripts/transcribe.py "<audio_path>" --model auto --language zh --detect-fillers
```

- `--model auto`：根据硬件自动选择最佳模型（NVIDIA GPU → large-v3，Apple Silicon → large-v3-turbo，集成显卡 → medium，纯 CPU → small）
- 也可手动指定：`tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo`
- `--engine auto`：自动检测 faster-whisper（推荐）或 openai-whisper
- `--mirror`：中国用户使用镜像源下载模型
- `--language`：`zh`（中文），`en`（英文），`ja`（日文）等，也可省略让 whisper 自动检测
- `--silence-threshold 1.0`：静音检测阈值（秒），默认 1.0。设为 0 关闭
- `--word-timestamps`：启用逐词时间戳（卡拉OK字幕必需）
- `--detect-fillers`：检测填充词（中文：嗯/呃/那个/就是说；英文：um/uh/like/you know），标记纯填充词片段为建议跳过

输出：与音频同目录下的 `<video_name>_transcript.json` 文件，格式如下：

```json
{
  "segments": [
    {"id": 1, "start": 0.0, "end": 2.5, "text": "大家好"},
    {"id": 2, "start": 2.5, "end": 5.1, "text": "今天我们来聊一个话题"}
  ],
  "silences": [
    {"start": 15.2, "end": 18.5, "duration": 3.3, "before_segment": 5, "after_segment": 6}
  ],
  "filler_words": [
    {"segment_id": 3, "text": "嗯那个", "fillers_found": ["嗯", "那个"], "is_filler_only": true},
    {"segment_id": 7, "text": "就是说我觉得这个方案", "fillers_found": ["就是说"], "is_filler_only": false}
  ]
}
```

**静音检测**：transcribe.py 会自动分析相邻语音片段之间的间隙。超过阈值（默认 1 秒）的间隙会被标记为静音并输出到 `silences` 字段中。这些静音通常是说话人的停顿、卡壳或口误，在构建 render_config.json 选片时应注意避开这些区域。

对独立人声或没有持续音乐的口播音轨，再运行原始转写静音核对：

```bash
python3 scripts/transcript_silence_qa.py analyze origin/talking_audio.wav \
  origin/talking_transcript.json --output verify/transcript_silence_qa.json
python3 scripts/transcript_silence_qa.py verify verify/transcript_silence_qa.json
```

报告逐段记录实际静音秒数、占比及源文件哈希；默认 `-40 dBFS`、最短静音 `0.15s`，静音占比达到 `0.8` 标为 `review`。按标记时间码回听，再在转写审校中更正。它不会自动删字或改时间码；安静的人声可能被误标，音乐、环境声可能掩盖幻觉。`verify` 会重新测量并拒绝报告或输入漂移。

长 transcript 需要找某句原话时，用 `python3 scripts/transcript_lookup.py work/transcript.json search "产品发布时间" --limit 10`；要看源片某段文字，用 `python3 scripts/transcript_lookup.py work/transcript.json span --start 90 --end 120`。输出是有界 JSON，含源段 ID、源时间码和 transcript SHA-256；搜索忽略大小写、空格与标点，可跨间隔不超过 2 秒的相邻段。它只定位原话，不推断语义相似内容；切点和措辞仍需回看原媒体并校稿。

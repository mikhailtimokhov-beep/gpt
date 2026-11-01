## Known Issues & Solutions（已知问题与解决方案）

以下问题在实际视频制作（Day 7-8）中遇到并验证了解决方案。

### K1: 混合帧率源素材用 concat copy 导致视频冻结

**症状**：使用 `ffmpeg -f concat -c copy` 拼接多段 B-roll 素材后，视频在约 1 分钟处画面冻结。

**根因**：DJI 素材为 30/1 fps，部分 DJI 和所有 iPhone MOV 文件为 30000/1001 (29.97fps)。`-c copy` 拼接不会重新编码，帧率不同导致时间戳不连续，播放器在切换点卡死。

**解决**：用 source-bound clip assembly 在同一条输出编码里统一每段的画布、CFR、SAR、时间戳、像素格式和音频布局：
```bash
python3 scripts/clip_assembly.py plan \
  origin/clip-a.MOV origin/clip-b.mp4 \
  --width 1080 --height 1920 --fps 30 \
  --delivery output/assembled.mp4 \
  --boundary-proof verify/clip-assembly-boundaries.mp4 \
  --project-dir . \
  --output work/clip_assembly_plan.json
python3 scripts/clip_assembly.py apply work/clip_assembly_plan.json
```
完整播放交付件和全部接缝 proof，确认后再运行 `confirm` / `verify --strict`。**禁止对混合帧率、画布、SAR、time base 或音频布局使用 `-c copy` concat。**

**检测方法**：`clip_assembly.py plan` 会读取每条源片的完整 decoded `best_effort_timestamp_time`、媒体合同和源 hash；只看 `r_frame_rate` 或 FFmpeg 退出码无法证明拼接结果连续。

---

### K2: 复杂 filter_complex 中音频被截断

**症状**：音频在视频中途（如 1:55 处）突然消失，画面正常继续播放。

**根因**：在单个 `filter_complex` 中同时使用 `amix`（混合 `anullsrc` 做静音填充）+ `atempo`（变速）+ 视频处理，`amix` 的 `duration=longest` 与合成的 null 音频源配合不可靠，导致音频流提前结束。

**解决**：将音频处理拆为独立步骤，不要在一个 filter_complex 中同时做音频填充+变速+视频处理：
1. `adelay` 添加封面静音段
2. `atempo=1.25` 变速处理
3. `apad=whole_dur=X` 填充到目标时长
4. 导出为 WAV，然后用 `-c:v copy -c:a aac` 与视频合并

**原则**：音频填充 + 变速 + 视频处理，三者不要放在同一个 filter_complex 中。

---

### K3: render_final.py select filter 在大量片段时 OOM

**症状**：使用 render_final.py 渲染 100+ 片段（如语音旁白配 B-roll 场景）时报 "Cannot allocate memory"。

**历史根因**：早期 `_clips_in_temporal_order()` 只检查是否所有 clip 来自同一视频且时间顺序递增，不检查是否有 broll 字段。当所有 clip 引用同一个语音视频（配不同 B-roll 画面）时，仍会走 select filter 路径，生成包含 100+ 个 `between()` 表达式的巨型 select 过滤器，导致 OOM。

**解决**：
- clip 级 `broll` 已会强制走 trim/concat，不再走 select filter。
- 对于 `auto_enrich.py` 产出的 B-roll cue，优先用 `render_final.py --enrich-plan work/enrich_plan.json`，它会以定时 video overlay 接入，不需要把口播切成大量小片段。
- 如果仍然手工构造 100+ 个 clip 片段，建议使用手动 ffmpeg 管线：
  1. 将所有 B-roll 片段统一帧率后 concat 拼接
  2. 单独处理音频（提取、裁切、变速、填充）
  3. 用 `-c:v copy -c:a aac` 合并视频和音频
- 如果必须使用 render_final.py 的大量 clip 模式，确保片段数量在合理范围内（建议 < 50 个片段）

---

### K4: 中文字幕中英文单词被截断

**症状**：字幕换行时英文单词（如 "OpenClaw"、"Claude Code"）被从中间劈开。

**根因**：`wrap_subtitle_text()` 的中文模式按字符数计算行宽，将英文字母视为与汉字等宽的单个字符。在中间位置换行时不感知 ASCII 单词边界，直接截断。

**解决**：换行函数需要：
1. 使用显示宽度计算：CJK 字符 = 1 单位，ASCII 字符约 0.5 单位
2. 在查找换行点时，检测 ASCII 单词边界（连续的字母/数字视为一个词），不在英文单词或数字中间断行
3. 优先在标点、空格、CJK/ASCII 边界处换行

---

### K5: 封面/结尾卡片不出现

**症状**：渲染配置中配置了 end_cards，但最终视频中看不到结尾卡片。

**根因**：B-roll 拼接后的总时长远超所需（如实际需要 215 秒但 B-roll 拼了 431 秒）。将封面+B-roll+结尾卡片 concat 后，用 `-t` 参数限制总时长时，结尾卡片被截断在时长限制之外。

**解决**：在拼接封面和结尾卡片之前，必须先将 B-roll 精确裁切到与音频时长匹配：
```bash
# 1. 获取音频时长
audio_dur=$(ffprobe -v 0 -show_entries format=duration -of csv=p=0 audio.wav)
# 2. 裁切 B-roll 到音频时长
ffmpeg -i broll_concat.mp4 -t $audio_dur -c copy broll_trimmed.mp4
# 3. 再拼接封面 + 裁切后的 B-roll + 结尾卡片
```
**原则**：拼接前确保每个部分的时长是精确已知的，不要依赖 `-t` 来事后截断。

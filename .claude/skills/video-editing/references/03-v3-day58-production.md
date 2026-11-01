## V3 Day58 production 教训（已编码进默认行为）

| 教训 | V3 怎么解决 |
|---|---|
| 顶部漏 `1.25x` 这种内部 token | `_internal_text_guard` 自动拒绝，规则在 [scripts/_internal_text_guard.py](scripts/_internal_text_guard.py) |
| 字幕 Hiragino W3 太细 | `find_chinese_font()` 默认排序：Source Han Sans Heavy > Smiley Sans > STHeiti Medium > PingFang Semibold |
| 加速后中段听不清 | render_final 默认 `dynaudnorm=f=250:g=15 + acompressor=threshold=-18dB:ratio=3 + loudnorm=I=-16:TP=-1.5:LRA=11` |
| 1.25× 想做主输出但 `--speed` 还留 1.0× | 新增 `--primary-speed` 一等公民 |
| 字幕里 Whisper 错词（ChatGPTT 等） | `rewrite_script.py` 走清稿优先，原 Whisper 词只供时间戳 |
| 平台违规词被发现才知道（限流） | `content_guard.py` 渲染前自动 lint |

---

# 旧版（V2）参考资料

下面是 V2 时代的工作流文档。仍然有效，但日常使用推荐先看 docs/prompts/15。

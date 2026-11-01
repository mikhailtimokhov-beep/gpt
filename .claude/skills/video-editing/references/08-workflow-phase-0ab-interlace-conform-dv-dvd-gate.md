### Phase 0ab: Interlace Conform（旧广播 / DV / DVD 条件 gate）

素材出现梳齿、`TFF/BFF`、`1080i/576i/480i` 或 telecine 线索时，先运行 `interlace_conform.py analyze`。它对头、中、尾执行 FFmpeg `idet`，分类为 progressive、真实 TFF/BFF 交错、telecine candidate 或 mixed/uncertain。telecine 必须停下来走 IVTC；progressive 保持原样；不确定素材只能在逐帧证据支持下使用 classification override。

确认是真实交错后，用 `plan --reviewed-by --note --delivery work/<name>-progressive.mp4 --comparison verify/<name>-interlace-compare.mp4` 绑定决定。默认优先 bwdif，yadif 是有 warning 的 fallback；`frame` 保持帧率，`field` 保留每个 field 的运动并精确加倍 rate。apply 通过 progressive field flag、live idet、尺寸/帧率/时长/音画起止和完整解码后才提升；随后完整 1× 看 A/B，并对 combing、motion、line detail、field order、audio sync 全部 `pass` 后 confirm。详见 [Interlace Conform](./docs/prompts/116-interlace-conform.md)。

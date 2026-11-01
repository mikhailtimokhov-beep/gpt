## V3 新增 render_final.py 标志位

| 标志 | 默认 | 说明 |
|---|---|---|
| `--profile tech_pro` | 关 | 加载 [scripts/profiles/tech_pro.yaml](scripts/profiles/tech_pro.yaml) 的节奏/字幕/BGM 默认值 |
| `--style-profile work/edit_style_profile.json` | 关 | 验证个人/品牌剪辑风格档案，仅填充 config 中缺失或 `null` 的受控字段 |
| `--primary-speed 1.25` | 1.0 | 主输出速度。`--speed` 仍可加额外变种 |
| `--no-loudnorm` | 不传 = 开启响度规范化 | 关闭 `dynaudnorm + acompressor + loudnorm` |
| `--speech-denoise light|medium|strong` | off | 80 Hz 高通 + 6/9/12 dB `afftdn`，在变速/响度/BGM ducking 前清理稳态底噪；`--no-speech-denoise` 覆盖 config |
| `--no-content-guard` | 不传 = 开启 lint | 关闭平台规则检查（不推荐） |
| `--subtitle-style karaoke` | normal | 逐词卡拉 OK 字幕 |
| `--enrich-plan work/enrich_plan.json` | 关 | 可重复传入；自动接入 B-roll / 章节卡 / 贴纸 / 生成图 / focus_events / pip_overlays |
| `--color-grade work/color_grade.json` | 关 | 接入 `color_grade.py` 输出或 preset，放在字幕/HUD 前 |
| `--bgm-ducking` | 关 | 用最终旁白轨触发 FFmpeg sidechain，动态压低 BGM；`--no-bgm-ducking` 可覆盖 config |
| `--versioned-output` | 关 | 输出到下一个 `<name>_V<N>.mp4`，避免覆盖上一版成片 |

### Phase 5: Single-Pass Render（单次渲染）

使用 [render_final.py](./scripts/render_final.py) 从原始视频**一次编码**生成最终视频：

```bash
# 如没有在 Phase 0.25 生成 profile，删去 --style-profile。
python3 scripts/render_final.py --config render_config.json \
  --style-profile work/edit_style_profile.json \
  --enrich-plan work/enrich_plan.json \
  --output final.mp4 --speed 1.25 1.5
```

**核心原理**：
- **单视频**（最常见场景）：使用 `select/aselect` + `between()` 表达式一次性筛选所有保留片段，FFmpeg 解码完整源视频但只编码选中的帧，配合 `-crf 18 -preset medium` 只编码一次
- **多视频混剪**：使用 `trim/atrim` 裁切 + `concat` 拼接（自动降级）
- 封面使用 `tpad` 冻结第一帧 + `adelay` 添加静音，字幕时间自动偏移，全部在**一次编码**中完成
- 章节时间轴不烧入视频，渲染完成后以文本形式输出，供用户手动粘贴到小红书等平台

参数说明：
- `--config`：渲染配置 JSON 路径
- `--style-profile`：可选，验证后仅填充 config 中缺失的个人/品牌风格默认值
- `--enrich-plan`：可选，读取 `auto_enrich.py` 输出的 JSON，把 B-roll / 章节卡 / 贴纸 / 强调点 / 已生成图片 cue 自动接回渲染
- `--output`：输出文件路径
- `--speed 1.25 1.5`：同时输出变速版本（每个变速版本也是从原始视频直接编码，不是从已编码视频二次压缩）
- `--cover-duration 2.0`：封面冻结时长（秒），覆盖配置中的 `cover_duration`
- `--font-path`：自定义字体文件
- `--font-size`：字幕字号（默认 120，即竖屏宽度 1080 ÷ 9 = 120，每个汉字占屏幕宽度的 1/9，基于实际分辨率自动缩放）
- `--no-subtitles`、`--no-cover`：跳过对应功能

**输出**：
- `final.mp4`（原速）
- `final_1_25x.mp4`（1.25 倍速）
- `final_1_5x.mp4`（1.5 倍速）
- 渲染完成后终端输出章节时间轴文本，可直接复制到小红书

**多平台格式导出**：
```bash
python3 scripts/render_final.py --config render_config.json --output final.mp4 \
  --formats vertical square horizontal
```

同时输出：
- `final_vertical.mp4`（9:16 抖音/小红书/TikTok）
- `final_square.mp4`（1:1 Instagram）
- `final_horizontal.mp4`（16:9 YouTube/B站）

裁切策略为中心裁切（center-crop），保持画面主体不变。

**自动功能**：
- 字幕自动检测语言、自动折行、竖屏优化定位
- 封面自动叠加标题文字（带描边和阴影），冻结首帧 1-2 秒
- 变速版本的字幕时间自动缩放
- B-roll 自动缩放裁切匹配主视频分辨率
- `--enrich-plan` 的定时 B-roll / image overlay 自动缩放裁切匹配主视频分辨率
- 结尾卡片自动拼接黑帧 + 静音 + 淡入淡出字幕
- 持续叠加层和闪烁圆点在封面之后自动启用
- 视频/音频时长自动对齐（`-shortest`），避免平台上传时的时长不匹配问题

### Phase 4.95: Subtitle Style Preview（真实画面字幕样式预览）

最终编码前先把真实 ASS 预设渲染到源片早/中/晚代表帧：

```bash
python3 scripts/subtitle_style_preview.py create \
  --project-dir . \
  --video origin/talking.mp4 \
  --platform xhs \
  --text "这句字幕要覆盖中英文和数字 2026" \
  --preview-dir verify/subtitle_styles \
  --output work/subtitle_style_preview.json \
  --markdown work/subtitle_style_preview.md \
  --require-selection

python3 scripts/subtitle_style_preview.py select \
  --report work/subtitle_style_preview.json \
  --style normal

python3 scripts/subtitle_style_preview.py verify \
  --report work/subtitle_style_preview.json \
  --strict
```

默认比较 `normal` / `minimal` / `bold_pop`，并使用 `render_final.py` 的同一 ASS builder、字体、字号和目标画幅中心裁切。手机尺寸与全尺寸都要看；确认后把所选值传给 `render_final.py --subtitle-style`。源片、字体、样式定义或 JPEG bytes 变化会让旧选择失效。`karaoke` 预览只证明视觉样式，真实逐词节奏仍取决于词级时间戳；最终还要跑 safe-area、readability QA 和 1× 成片审片。详见 [docs/prompts/94-subtitle-style-preview.md](docs/prompts/94-subtitle-style-preview.md)。

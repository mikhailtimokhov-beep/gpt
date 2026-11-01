### Subtitle Glyph QA（生僻字 / emoji / 多语言字幕时推荐）

```bash
python3 scripts/subtitle_glyph_qa.py analyze \
  --subtitle-pack output/subtitles/final.json \
  --font 'fonts/NotoSansSC[wght].ttf' \
  --project-dir . \
  --output verify/subtitle_glyph_qa.json \
  --markdown verify/subtitle_glyph_qa.md \
  --strict
python3 scripts/subtitle_glyph_qa.py verify \
  --report verify/subtitle_glyph_qa.json \
  --project-dir . --strict
```

脚本直接读取 TTF/OTF/TTC/OTC 的 Unicode `cmap`，覆盖 `subtitle_pack.v1` 中全部可见字符，并把字幕、主字体、显式 fallback、覆盖分配和 canonical report id 绑定起来。系统隐式字体替换不算证据；缺字会阻断，显式 fallback 默认警告，`--require-primary` 可禁止 fallback。它不证明 shaping、彩色 emoji、ASS 布局或视觉可读性，最终仍要完整 1× 看字幕和全分辨率抽帧。详见 [docs/prompts/110-subtitle-glyph-qa.md](docs/prompts/110-subtitle-glyph-qa.md)。

### Phase 4.9: Platform Safe Area QA（平台 UI 安全区门禁）

在渲染或多平台导出前，按目标平台分别检查字幕、强调 badge、PIP 人像、CTA、章节卡和点击 marker 是否会进入顶部状态栏、底部文案区或右侧互动按钮栏：

```bash
python3 scripts/platform_safe_area_qa.py \
  --config work/render_config.json \
  --enrich-plan work/enrich_plan.json \
  --platform xhs \
  --output verify/xhs_platform_safe_area_qa.json \
  --markdown verify/xhs_platform_safe_area_qa.md \
  --guide verify/xhs_platform_safe_area_guide.svg \
  --strict
```

抖音和视频号派生版分别改用 `--platform douyin` / `--platform wxch`。脚本按 `render_final.py` 的默认 ASS、PIP 和 focus-marker 几何规则估算 bbox；renderer 之外的 CTA/Logo 可以通过 `--elements custom_elements.json` 提供像素或 normalized bbox。平台 App UI 变化时用 `--safe-left` / `--safe-top` / `--safe-right` / `--safe-bottom` 覆盖实测边距。

这是本地、可审计的 layout gate：不上传、不调用 LLM、不做 OCR，不推断生成图或封面内部的主体/文字位置。已有整图章节卡会标记 `uncheckable`，需要打开 SVG guide 或渲染帧人工复核。`summary.blocking > 0` 会让 `--strict` 返回 2；需要设为生产线必需项时用 `pipeline_manifest.py --require platform_safe_area_qa --strict`。

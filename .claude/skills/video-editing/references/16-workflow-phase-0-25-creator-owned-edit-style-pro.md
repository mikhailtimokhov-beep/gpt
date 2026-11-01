### Phase 0.25: Creator-owned Edit Style Profile（个人/品牌剪辑风格，可选）

当用户希望多个项目保持同一套创意方向、剪辑节奏、字幕/封面/调色/BGM 习惯和标题拼写时，先生成并人工编辑 spec，再创建可移植 profile：

```bash
python3 scripts/edit_style_profile.py template \
  --output work/edit_style_profile_spec.json

# 编辑 spec 中的真实偏好和 approval basis 后：
python3 scripts/edit_style_profile.py create \
  --spec work/edit_style_profile_spec.json \
  --output work/edit_style_profile.json \
  --markdown work/edit_style_profile.md \
  --strict

python3 scripts/edit_style_profile.py verify \
  --profile work/edit_style_profile.json \
  --strict
```

渲染时加 `render_final.py --style-profile work/edit_style_profile.json`；生成标题文案和封面时，分别给 `generate_caption.py` 和 `cover_variants.py` 加同一参数。Profile 只填充 config 中缺失或 `null` 的受控字段；项目 config 和显式 CLI（包括封面 `--style`）始终优先。它描述“通常怎么剪”，而 `edit_recipe.py` 保存“这条时间线怎么复刻”，两者不互相替代。Profile 的 digest 只能发现文件漂移，不是签名、身份认证或权利证明。完整用法见 [docs/prompts/98-edit-style-profile.md](docs/prompts/98-edit-style-profile.md)。

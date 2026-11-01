### Phase 4.85: Portable Edit Recipe（可移植剪辑配方，可选）

当用户要把已审 `render_config.json` 保存为模板，或换一批素材复刻同一时间线/字幕/BGM/overlay 结构时，先导出无路径 recipe：

```bash
python3 scripts/edit_recipe.py export \
  --config work/render_config.json \
  --name fast-tech-explainer \
  --description "快节奏科技口播" \
  --output work/recipes/fast-tech-explainer_edit_recipe.json \
  --markdown work/recipes/fast-tech-explainer_edit_recipe.md
```

导出前必须通过 source preflight；本地文件引用会变成 typed slots，同一路径只占一个槽位，recipe 不保存原路径。新项目打开 Markdown slot 表，为每槽各传一次 `--bind SLOT=PATH` 运行 `replay`，同时写 `--receipt` 和 `--markdown`；脚本会验证 portable digest、槽位集合、文件类型与存在性，记录新 binding hash，并对输出 config 再跑 preflight。默认不覆盖，只有明确目标正确时加 `--force`。recipe hash 不是签名或人工批准；回放后仍必须渲染并看完整成片。详细流程见 [docs/prompts/82-edit-recipe.md](docs/prompts/82-edit-recipe.md)。

## Workflow（工作流程）

### Phase 0a: Project Bootstrap（项目启动 / 原始素材导入）

当用户给的是一个原始素材文件夹、下载目录或一组还没整理的素材时，先用 [project_bootstrap.py](./scripts/project_bootstrap.py) 建立稳定项目结构，而不是直接在外部原始路径上剪辑：

```bash
python3 scripts/project_bootstrap.py \
  --source ~/Downloads/raw-shoot \
  --project-dir work/day61 \
  --title "Day61 launch edit" \
  --output work/day61/work/source_inventory.json \
  --markdown work/day61/work/source_inventory.md \
  --project-note work/day61/project.md \
  --strict
```

输出：
- `origin/raw|broll|audio|bgm|images|assets|sidecars/`：项目内 working copy。
- `work/source_inventory.json`：`project_bootstrap.v1`，记录外部 `source_path`、项目内 `project_path`、分类、动作和 next actions。
- `work/source_inventory.md`：给人审的素材清单。
- `project.md`：跨会话项目记忆。
- `next_steps.md`：下一步命令清单。

默认 `--mode copy`，同名文件自动加后缀，不覆盖。大素材同盘可用 `--mode hardlink`，失败会回退 copy 并写入 warning。此脚本不转码、不渲染、不上传、不调用 LLM，也不提交任何生成任务。需要把素材导入作为 analysis gate 时，跑：

```bash
python3 scripts/pipeline_manifest.py \
  --project-dir work/day61 \
  --target-stage analysis \
  --require source_inventory \
  --strict
```

### Phase 4.8: Edit Revision（剪辑 artifact 可逆修订，可选）

当用户要求修改 `render_config.json`、`enrich_plan.json`、caption 或字幕 sidecar，同时需要完整审稿、依赖防漂移和 undo/redo 时，先准备 proposal：

```bash
python3 scripts/edit_revision.py prepare \
  --project-dir . \
  --artifact work/render_config.json \
  --artifact work/enrich_plan.json \
  --depends-on work/transcript_reviewed.json \
  --title "收紧开头并调整 B-roll" \
  --reason "已完成时间码审片，采用第二版开头。" \
  --output work/edit_revision_proposal.json
```

只改 proposal 的 `artifacts[].proposed_content`，再运行 `audit`。合法 audit 的 `pending_approval` 在 `--strict` 下返回 2 是预期人工 gate；必须另存绑定相同 `review_id`、`decision: approve` 和非空 `approved_by_label` 的 approval JSON，`apply` 才会把多个文件作为一个 revision 成组写入并创建 `work/edit_revision_history.json`。运行期写入错误会尝试恢复旧 bytes，但跨文件不承诺操作系统级原子提交；进程异常后先跑 `status --strict`。status 会实时检查 artifact、已应用 dependency 和 content-addressed before/after blobs；外部手改、依赖漂移、symlink 或 blob 损坏时拒绝 undo/redo。原始媒体、代码、输出成片和 `verify/` 不在管理范围。详细流程见 [docs/prompts/80-edit-revision.md](docs/prompts/80-edit-revision.md)。

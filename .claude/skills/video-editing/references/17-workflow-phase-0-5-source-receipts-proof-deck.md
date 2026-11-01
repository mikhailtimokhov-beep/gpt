### Phase 0.5: Source Receipts（事实来源 proof deck，可选但推荐）

如果视频包含新闻、数据、产品事实、健康/金融/法律判断、来源页截图或“官方说法”，在进入分镜/发布前先把 claim 和证据落成 source receipts：

```bash
python3 scripts/source_receipts.py \
  --claims work/source_claims.json \
  --project-dir . \
  --output work/source_receipts.json \
  --markdown work/source_receipts.md \
  --html work/source_receipts.html \
  --require-primary-source \
  --strict
```

`source_receipts.py` 只验证已提供的 URL 和本地截图/证据文件；不联网抓取、不截图、不上传。`source_claims.json` 里的 `screenshot` / `source_file` 相对 claims JSON 所在目录解析。新闻、数据、金融、健康、法律等高风险 claim 必须有 `source_url`；需要视觉 proof card 时加 `--require-screenshot`。发布门禁可用 `pipeline_manifest.py --require source_receipts --strict` 强制检查，`summary.blocking > 0` 会阻塞。

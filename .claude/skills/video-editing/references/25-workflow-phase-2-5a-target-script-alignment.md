### Phase 2.5a: Target Script Alignment（按确认稿装配原话，可选）

如果客户、编导或用户已经确认成片稿，而同一句话录了多个 take 或分散在不同素材里，先把目标稿按“一行一个完整 spoken unit”整理，再匹配 reviewed transcript：

```bash
python3 scripts/script_alignment.py \
  --target-script work/target_script.md \
  --transcript take-a=work/take-a_transcript_reviewed.json \
  --transcript take-b=work/take-b_transcript_reviewed.json \
  --media take-a=origin/take-a.mp4 \
  --media take-b=origin/take-b.mp4 \
  --output work/script_alignment.json \
  --markdown work/script_alignment.md \
  --render-config work/render_config.json \
  --clean-script work/clean_script.md \
  --strict
```

脚本只做本地词面匹配，不调用 LLM、不改源文件、不判断表情/镜头/表演质量。它输出每句的稳定 candidate id、source time、原话和 sequence/coverage/ngram/length evidence；word timestamps 存在时优先收紧到词边界，只有 segment 时间戳时保守保留整段。低分、前两名过近、无候选、素材缺失或源时间重复占用会写 `summary.blocking` 并让 `--strict` 返回 2。

同文案多个 take 出现 `ambiguous_match` 时，必须看/听 Markdown 里的候选，把确认结果写成 `{"choices":{"target-001":"<candidate-id>"}}`，再用 `--choices work/script_alignment_choices.json` 重跑。人工 choice 只能解决词面低分/多解，不能绕过缺文件或时间重叠。`summary.blocking=0` 后再进入 `edit_preflight.py` / `render_final.py`；详细用法见 [docs/prompts/78-script-alignment.md](docs/prompts/78-script-alignment.md)。

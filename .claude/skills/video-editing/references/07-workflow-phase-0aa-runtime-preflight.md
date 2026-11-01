### Phase 0aa: Runtime Preflight（按任务核验本机能力）

在打开媒体或启动渲染前，运行 [runtime_preflight.py](./scripts/runtime_preflight.py)。只转写、probe 或抽流用 `media_io`；会编码最终画面的任务用 `core_edit`，再按需要追加 `hls_vod / soft_subtitles / gif_preview / logo_overlay / podcast_audiogram / ping_pong_loop / multicam_switch / video_enhancement / storyboard_animatic / audio_cue_mix / generation_chain_handoff / captions / qa / edge_black_trim / hdr_sdr / stabilization / interlace / remotion`：

```bash
python3 scripts/runtime_preflight.py analyze \
  --profile core_edit \
  --profile captions \
  --profile qa \
  --output work/runtime_preflight.json \
  --markdown work/runtime_preflight.md \
  --strict
python3 scripts/runtime_preflight.py verify \
  --report work/runtime_preflight.json --strict
python3 scripts/pipeline_manifest.py . \
  --require runtime_preflight --strict
```

必须分别对待 `missing` 和 `unknown`：前者表示可解析清单中明确没有组件，后者表示版本命令或 FFmpeg listing 失败、超时或不可解析；两者都停止当前 workflow。按 Markdown 的 action 修好环境后重新 `analyze`，不要手改 JSON。报告会绑定所选 profile、相关命令版本、FFmpeg component states 和 `report_id`；`pipeline_manifest.py` 现场复验，环境或报告漂移后旧结果立即失效。

这一步只做 introspection，不运行真实编码、GPU、字体或 provider job。通过后仍要执行项目输入 preflight、真实媒体 probe、完整解码和最终视听 QA。详见 [Runtime Preflight](./docs/prompts/115-runtime-preflight.md)。

### Phase 2.5: Transcript Review（转录文字校验）

转录完成后，**必须**对所有 transcript.json 中的文字进行逐条审查，修正以下两类问题：

**1. 语音识别错误（ASR errors）**：
Whisper 常见的识别错误类型：
- **专有名词/产品名**：如 "opencloud" → "OpenClaw"、"cloudcode" → "Claude Code"、"cloud ops" → "Claude Opus"
- **同音字错误**：如 "小红树" → "小红书"、"检映" → "剪映"、"断耕" → "断更"、"懒得讲" → "懒得剪"
- **英文拼写**：如 "scale" → "skill"、"箱子" → "视频"
- **尾部幻觉**：Whisper 有时在安静片段末尾生成无意义的重复文字，应直接删除

**2. 口误标记（Speaker errors）**：
- **重复/卡壳**：说话人重复说同一句话或卡住后重新说，标记为可跳过
- **乱码片段**：语音模糊导致识别为无意义文字的片段（如连续的单字碎片），标记为可跳过

专业术语、人名、同音字或中英混说较多时，先运行 `semantic_transcript_review.py prepare`，让当前 Agent/模型填写 provider-neutral response；再运行 `audit`。不要把模型 confidence 当批准：从 audit Markdown 复制绑定 `source_sha256 + review_id` 的 choices 模板，逐项 `approve` / `reject` 后才运行 `apply`。`audit` 会从源 transcript 推导完整覆盖率，并拒绝整句润色、非最小字符补丁、数字/标点变化、越界/重叠补丁和旧 transcript hash。成功 apply 后，把 `transcript_semantic_reviewed.json` 交给下面的同步媒体 HTML 继续听审；详见 [docs/prompts/79-semantic-transcript-review.md](docs/prompts/79-semantic-transcript-review.md)。

```bash
python3 scripts/semantic_transcript_review.py prepare \
  --transcript work/transcript.json \
  --output work/semantic_review_request.json \
  --markdown work/semantic_review_request.md

python3 scripts/semantic_transcript_review.py audit \
  --transcript work/transcript.json \
  --response work/semantic_review_response.json \
  --output work/transcript_semantic_review.json \
  --markdown work/transcript_semantic_review.md \
  --strict

python3 scripts/semantic_transcript_review.py apply \
  --transcript work/transcript.json \
  --audit work/transcript_semantic_review.json \
  --choices work/semantic_review_choices.json \
  --output work/transcript_semantic_reviewed.json
```

**校验流程**：
1. 用 `transcript_review.py html` 生成一个无外部依赖的本地页面；纯终端环境用 `export` 生成文本。
2. 页面里点击时间码对着媒体校稿；播放时当前段自动高亮。行内编辑支持本地自动保存、查找替换和 CPS 标黄。
3. 显式保存 `transcript_review.txt`，不要让页面或 agent 直接覆盖原始 transcript。
4. 用 `apply` 生成 `transcript_reviewed.json`；后续清稿、粗剪、分镜和字幕统一使用 reviewed 文件。
5. 对于口误/乱码片段，在展示片段列表时（Phase 3）标注为建议跳过。

```bash
python3 scripts/transcript_review.py html \
  --transcript work/transcript.json \
  --video origin/talking.mp4 \
  --corrections work/corrections.json \
  --output work/transcript_review.html \
  --max-cps 20

python3 scripts/transcript_review.py apply \
  --transcript work/transcript.json \
  --review work/transcript_review.txt \
  --output work/transcript_reviewed.json
```

HTML 和媒体只在本机打开，不上传、不调用 LLM。浏览器不能直接写文件时会下载 `transcript_review.txt`；把它放回 `work/` 后再 apply。CPS 是预渲染提示，最终还要跑 `subtitle_readability_qa.py --strict`。

**注意**：此步骤必须在 Phase 5（渲染）之前完成，因为字幕文字来源于 transcript.json。修正后再渲染，才能保证最终视频中的字幕文字正确。

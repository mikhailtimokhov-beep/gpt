## 纯音频播客竖版 Audiogram

只有音频和封面、需要发短视频时，选出有完整语义的短段，准备与该摘录从 0 秒开始对齐的 SRT。若有原生视频，优先剪真实说话画面。需要新封面时优先用 Codex 内置 `image_gen`（GPT Image 2）；已有封面直接使用。

运行 `runtime_preflight.py analyze --profile podcast_audiogram --output work/runtime_preflight.json --strict`，再运行 `podcast_audiogram.py render origin/episode.wav origin/cover.png work/excerpt.srt --start 32 --duration 28 --output output/audiogram.mp4 --receipt verify/podcast_audiogram.json`。脚本把音频、封面、字幕、设置和成片绑定，输出 720×1280 H.264/AAC、辅助声波和烧录字幕；单条最长 600 秒。`podcast_audiogram.py verify verify/podcast_audiogram.json` 会重查哈希、媒体规格和完整解码。`ready_for_human_review` 只表示技术检查通过，交付前仍须以 1× 带声看完，核对字幕与语音、封面权利与辨识度、波形位置和末尾裁切。修改任一输入后重新渲染并复核。

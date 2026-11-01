## 已审成片打包 HLS 点播

网站需要静态 HLS 点播文件时，先确认最终 MP4 已完成带声审片、音频和画质 QA。运行 `runtime_preflight.py analyze --profile hls_vod --output work/runtime_preflight.json --strict`，再运行 `hls_vod.py package output/master.mp4 --output-dir output/hls --receipt verify/hls_vod.json --segment-seconds 6`。输入限单视频、最多单 AAC 音轨、H.264/yuv420p、SDR、CFR MP4；HDR、VFR、旋转元数据和额外字幕/章节流先制作合适的 SDR/CFR master。输出目录及收据须为新路径，脚本不覆盖现有文件。

脚本按分片间隔强制关键帧并输出 `index.m3u8` 与 TS，`hls_vod.py verify verify/hls_vod.json` 现场核对每个分片首视频包是关键帧、源/输出视频帧数、播放列表时长、所有文件 SHA-256 和整条播放列表解码。它只生成单码率 VOD，未实现自适应码率或上传。部署时连同整个目录上传，配置 `.m3u8` 与 `.ts` MIME，并在目标播放器完整带声测试拖动、起止、字幕和同步；转码画质需与已审 MP4 人工 A/B。

## 已审成片叠加品牌 Logo

需要给已审 MP4 加固定 PNG Logo 时，运行 `runtime_preflight.py analyze --profile logo_overlay --output work/runtime_preflight.json --strict`，再运行 `logo_overlay.py render output/master.mp4 media/assets/logo.png --corner bottom-right --width-fraction 0.15 --opacity 0.7 --margin 24 --output output/master-logo.mp4 --receipt verify/logo_overlay.json`。宽度占画面 5%–40%，可选四角；margin 是输出像素，Logo 须完整落在画面内。脚本重新编码 H.264/yuv420p 视频、复制可选单音轨，验证帧数、时长、画布、完整解码，并用 SHA-256 绑定原片、Logo 与输出。`logo_overlay.py verify verify/logo_overlay.json` 现场复查；改动任何文件后重新渲染与审看。交付前以 1× 带声看完整片，检查 Logo 位置、透明度、字幕/平台 UI 遮挡和音画同步。

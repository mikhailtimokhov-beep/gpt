## FAQ / Troubleshooting（常见问题诊断）

遇到错误时，先运行环境诊断：
```bash
python3 scripts/utils.py
```

### Q1: `No such filter: 'drawtext'` 或 `No such filter: 'ass'`

**原因**：ffmpeg 编译时未包含 `libfreetype`（drawtext 所需）或 `libass`（字幕所需）。

**诊断**：
```bash
ffmpeg -hide_banner -filters 2>/dev/null | grep -E "drawtext|ass|subtitles"
```
如果无输出，说明缺少对应滤镜。

**解决**：
- **macOS**：标准 `brew install ffmpeg` 可能不包含这些库。使用第三方 tap 安装完整版：
  ```bash
  brew tap homebrew-ffmpeg/ffmpeg
  brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-fdk-aac
  ```
  该 tap 默认启用 `--enable-libfreetype --enable-libass --enable-libfontconfig`。
- **Linux/WSL**：`apt install ffmpeg` 通常已包含。如果缺少，安装开发依赖后从源码编译：
  ```bash
  sudo apt install libfreetype6-dev libfontconfig1-dev libass-dev
  ```
- **影响范围**：缺少 drawtext 时，字幕烧录和封面文字会失败或自动降级。

### Q2: `Undefined constant or missing '(' in 'iw*0.5-tw/2'`

**原因**：ffmpeg drawtext 的 `x` 表达式中使用了 `tw`（text width），但某些 ffmpeg 版本中 `tw` 在 `x` 参数的上下文中不可用。

**解决**：脚本已修复此问题（使用像素值 `{pixel_x}-text_w/2` 代替 `iw*{frac}-tw/2`）。如果你修改了脚本并遇到此错误，请使用 `text_w` 而非 `tw`，并确保 `x` 表达式中不包含 `iw*` 动态计算。

### Q3: `Invalid alpha value specifier '%{eif:...}'` (drawtext fontcolor)

**原因**：试图在 `fontcolor` 参数中嵌入 `%{eif}` 表达式来实现透明度渐变，但 ffmpeg 不支持在颜色值中使用此语法。

**解决**：使用 drawtext 的 `alpha` 参数（独立于 fontcolor），而非试图在 `fontcolor=white@'%{eif:...}'` 中嵌入表达式。正确写法：
```
drawtext=text='hello':fontcolor=white:alpha='if(lt(t,1),t,1)'
```
错误写法（会报错）：
```
drawtext=text='hello':fontcolor=white@'%{eif:if(lt(t,1),t,1):d:2}'
```

### Q4: ffmpeg 硬件编码器失败 (`h264_videotoolbox` / `h264_nvenc` / `h264_qsv` 报错)

**原因**：检测到的硬件编码器不支持当前的视频参数（如特殊分辨率、色彩空间），或驱动版本不兼容。

**诊断**：
```bash
ffmpeg -encoders 2>/dev/null | grep -E "nvenc|videotoolbox|qsv|amf"
```

**解决**：在 `scripts/utils.py` 中临时修改 `get_ffmpeg_encoder()` 函数，让它直接返回 `("libx264", ["-preset", "fast", "-crf", "18"])`。

### Q5: 中文字幕显示为方框（豆腐块）

**原因**：系统中没有可用的中文字体文件。

**诊断**：
```bash
python3 -c "from scripts.utils import find_chinese_font; print(find_chinese_font())"
```
如果返回 `(None, ...)`，说明未找到中文字体。

**解决**：
- **macOS**：系统自带 PingFang SC，一般不会出现此问题。
- **Linux/WSL**：安装中文字体包：
  ```bash
  sudo apt install fonts-noto-cjk
  ```
- **WSL 备选**：脚本会自动尝试 `/mnt/c/Windows/Fonts/msyh.ttc`（微软雅黑），前提是 Windows 已安装该字体。
- **手动指定**：使用 `--font-path /path/to/your/font.ttf` 参数。
- **自动下载**：脚本首次运行时会尝试从 Google Fonts（中国用户使用 jsDelivr CDN）下载 Noto Sans SC，缓存到 `fonts/` 目录。

### Q6: Whisper 模型下载失败 / 超时

**原因**：网络问题，尤其是中国用户无法访问 HuggingFace。

**解决**：
- 使用 `--mirror` 参数：`python3 scripts/transcribe.py audio.wav --mirror --model auto`
- 或手动设置环境变量：
  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  ```
- 使用 faster-whisper 时，模型从 HuggingFace 下载；设置 `HF_ENDPOINT` 后会自动走镜像。
- 使用 openai-whisper 时，模型从 GitHub 下载，中国用户可能需要代理。建议改用 faster-whisper。

### Q7: `pip install faster-whisper` 安装失败 / 超时

**解决**：中国用户使用清华镜像：
```bash
pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### Q8: WSL 环境下 ffmpeg 找不到或版本过旧

**诊断**：
```bash
which ffmpeg && ffmpeg -version | head -1
```

**解决**：
```bash
sudo apt update && sudo apt install ffmpeg
```
如果系统源的 ffmpeg 版本过旧（< 4.0），使用 PPA：
```bash
sudo add-apt-repository ppa:savoury1/ffmpeg4
sudo apt update && sudo apt install ffmpeg
```

### Q9: 视频质量差 / 模糊

**原因**：视频经过了多次重编码，每次编码都有质量损失。

**解决**：必须使用 `render_final.py` 单次编码。检查是否在流程中使用了 `split_video.py` + `burn_subtitles.py` + `merge_clips.py` + `generate_cover.py` + `add_chapter_bar.py` 的旧流程（会导致 4-5 次重编码）。改用 `render_final.py --config` 一步到位。

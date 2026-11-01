## Remotion Voiceover Workflow（语音生成视频）

当用户只有语音（或音频文件）但没有画面时，使用 Remotion 生成配合语音的视频画面。

详细的 Remotion API 参考、模板样式、组件结构见 [REMOTION_VOICEOVER.md](./REMOTION_VOICEOVER.md)。

### 适用场景

- **纯音频口播** — 有录音/TTS 语音，需要生成匹配的画面
- **音频 + 静态图片** — 有语音和图片素材，需要组合成动态视频
- **播客可视化** — 将播客/对话音频转为带字幕和视觉效果的视频
- **解说视频** — 配音 + 文字动画 + 背景图的组合

### Remotion Workflow（工作流）

1. **音频准备** — 使用 `extract_audio.py` 提取音频，或直接使用用户提供的音频文件
2. **语音识别** — 使用 `transcribe.py` 生成 transcript.json（逐句时间戳）
3. **时间轴生成** — AI Agent 根据 transcript 内容分析语义，生成 `timeline.json`：
   - 将多个 segments 按语义分组为 scenes
   - 为每个 scene 选择类型（title/content/kinetic/quote 等）
   - 选择背景视觉、文字动画、转场效果
   - 配置字幕样式（TikTok 逐词高亮 / 底部字幕 / 全屏文字）
4. **素材准备** — 收集/生成场景所需的图片素材
5. **Remotion 渲染** — 使用 `npx remotion render` 根据 timeline.json 渲染最终视频
6. **后处理（可选）** — 使用 `render_final.py` 与其他视频片段合并

### 视频模板风格选择

| 风格 | 适用场景 | 视觉效果 |
|------|---------|---------|
| `tiktok` | 短视频口播、知识分享 | 渐变背景 + 关键词卡片 + TikTok 风格逐词字幕 + 进度条 |
| `tutorial` | 教程、科普、产品介绍 | 图文分栏 + Ken Burns 图片 + 要点逐行淡入 + 底部字幕 |
| `kinetic` | 情感类、激励类、文案 | 全屏大号文字逐行弹入 + 弹性动效 |
| `podcast` | 播客、访谈、对话 | 头像 + 音频波形可视化 + 引用文字 |
| `news` | 新闻播报、行业资讯 | 顶部横幅 + Lower Third 信息条 + 滚动字幕 |
| `slideshow` | 产品介绍、旅行、相册 | 多图 Ken Burns + 转场效果 + 说明文字 |

### Remotion 环境要求

```bash
# 需要 Node.js 18+ 和 npm
node --version  # >= 18.0.0
npm --version

# 安装 Remotion standup 项目依赖
cd remotion-standup
npm install
```

### 脱口秀/纯音频视频生成（Standup Comedy Workflow）

当用户有一段脱口秀音频（或任何纯语音内容）但没有画面时，可以生成带文字动效的视频：

**Step 1: 语音识别**
```bash
python3 scripts/transcribe.py audio.wav --model auto --language zh
```

**Step 2: 生成时间轴**
```bash
# 默认风格
python3 scripts/generate_standup_timeline.py transcript.json \
    --audio audio/standup.wav \
    --output remotion-standup/public/timeline.json

# 活力风格（更多夸张动效）
python3 scripts/generate_standup_timeline.py transcript.json \
    --audio audio/standup.wav \
    --style energetic \
    --output remotion-standup/public/timeline.json

# 选择特定片段 + 自定义字体
python3 scripts/generate_standup_timeline.py transcript.json \
    --audio audio/standup.wav \
    --segments 1-10,12,15-20 \
    --font "LXGW WenKai, sans-serif" \
    --output remotion-standup/public/timeline.json
```

**Step 3: 预览和渲染**
```bash
cd remotion-standup

# 把音频文件复制到 public 目录
cp /path/to/audio.wav public/audio/standup.wav

# 开发预览
npx remotion studio

# 渲染最终视频
npx remotion render StandupVideo out/standup.mp4 --codec=h264 --crf=18
```

**脚本会自动：**
- 检测笑点/短句（感叹号、关键词、短句跟长句的对比）→ 用 slam/shake/bounce 等夸张动效
- 短句放大字号（emphasis 1.3-1.6x），长句缩小避免溢出
- 笑点使用径向渐变 + 醒目配色（红/橙/金/绿）
- 常规句子使用深色渐变背景 + 不同动画循环
- 自动在中文长句中间插入换行

**12 种文字动画效果：**

| 动画 | 效果 | 适合场景 |
|------|------|---------|
| `fadeIn` | 渐显 | 平稳叙述 |
| `springIn` | 弹性入场 | 正常对话 |
| `scaleUp` | 由小放大 | 强调 |
| `scaleDown` | 由大缩小 | 砸入感 |
| `typewriter` | 打字机 | 引述/对话 |
| `bounce` | 弹跳 | 活泼/搞笑 |
| `shake` | 抖动 | 笑点/吐槽 |
| `slam` | 急速砸入 | 重磅笑点 |
| `wave` | 逐字波浪 | 开场/结尾 |
| `glitch` | 故障闪烁 | 意外/反转 |
| `rotateIn` | 旋转入场 | 切换话题 |
| `splitReveal` | 中间展开 | 揭示/揭晓 |

**3 种风格预设：**

| 风格 | 说明 |
|------|------|
| `default` | 均衡混合所有动画，适合大多数内容 |
| `calm` | 只用平缓动画（fadeIn/springIn/typewriter），适合讲故事/深度内容 |
| `energetic` | 偏重夸张动画（slam/shake/bounce/glitch），适合脱口秀/搞笑内容 |

### timeline.json 配置格式

```json
{
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "audioSrc": "public/audio/voiceover.wav",
  "style": "tiktok",
  "font": {
    "family": "Noto Sans SC",
    "titleWeight": "700",
    "bodyWeight": "400",
    "titleSize": 72,
    "bodySize": 48
  },
  "colors": {
    "background": "#1a1a2e",
    "text": "#ffffff",
    "highlight": "#FFD700",
    "accent": "#e94560"
  },
  "scenes": [
    {
      "id": 1,
      "startMs": 0,
      "endMs": 5000,
      "type": "title",
      "title": "今天聊一个话题",
      "background": { "type": "gradient", "colors": ["#667eea", "#764ba2"] },
      "transition": { "type": "fade", "durationMs": 500 }
    }
  ],
  "captions": {
    "enabled": true,
    "style": "tiktok",
    "fontSize": 56,
    "highlightColor": "#FFD700"
  }
}
```

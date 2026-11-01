## Font Catalog（字体目录）

项目内置了一套可下载的免费字体目录，覆盖中文和英文视频制作常用字体。

### 字体管理

```bash
# 查看环境报告（包含已缓存字体列表）
python3 scripts/utils.py

# 在 Python 中使用字体 API
python3 -c "
from scripts.utils import list_available_fonts, download_font

# 列出所有可用字体
for f in list_available_fonts():
    status = '✓' if f['cached'] else '○'
    print(f\"{status} {f['id']:25s} {f['name']:25s} {f['use_case']:8s} {f['description']}\")

# 下载指定字体
download_font('lxgw-wenkai')
download_font('inter')
"
```

### 中文字体

| 字体 ID | 名称 | 风格 | 用途 | 许可证 |
|---------|------|------|------|--------|
| `noto-sans-sc` | Noto Sans SC（思源黑体） | 万能黑体 | 全场景 | SIL OFL |
| `noto-serif-sc` | Noto Serif SC（思源宋体） | 正式宋体 | 文化/古典/深度 | SIL OFL |
| `lxgw-wenkai` | LXGW WenKai（霞鹜文楷） | 手写楷体 | 文艺/文化/情感（~24MB） | SIL OFL |
| `lxgw-wenkai-lite` | LXGW WenKai Lite（轻便版） | 手写楷体 | 同上，体积更小（~13MB） | SIL OFL |
| `lxgw-wenkai-bold` | LXGW WenKai Medium | 手写楷体粗 | 标题 | SIL OFL |
| `zcool-kuaile` | ZCOOL KuaiLe（站酷快乐体） | 圆润可爱 | 轻松/娱乐标题 | SIL OFL |
| `zcool-qingke-huangyou` | ZCOOL QingKe HuangYou（庆科黄油体） | 手写潮流 | 时尚/年轻标题 | SIL OFL |
| `zcool-xiaowei` | ZCOOL XiaoWei（站酷小薇体） | 清秀端正 | 正文/字幕 | SIL OFL |

### 英文字体

| 字体 ID | 名称 | 风格 | 用途 | 许可证 |
|---------|------|------|------|--------|
| `inter` | Inter | 现代无衬线 | 全场景 | SIL OFL |
| `montserrat` | Montserrat | 几何无衬线 | 标题 | SIL OFL |
| `poppins` | Poppins | 圆润几何 | 标题 | SIL OFL |
| `roboto` | Roboto | 中性现代 | 全场景 | Apache 2.0 |
| `oswald` | Oswald | 窄体无衬线 | 新闻/头条标题 | SIL OFL |
| `playfair-display` | Playfair Display | 优雅衬线 | 文艺/高端标题 | SIL OFL |

### 字体选择建议

**默认字体：LXGW WenKai Medium（霞鹜文楷中粗体）** — 手写楷体风格，兼具美观性和可读性，是口播/Vlog 类视频的最佳选择。如果未缓存，会自动下载。

**默认字号：120**（竖屏 1080px 宽度 ÷ 9 = 120），即每个汉字占屏幕宽度的约 1/9，在手机竖屏上清晰易读。

| 视频类型 | 推荐中文字体 | 推荐英文字体 |
|---------|------------|------------|
| **口播/Vlog（默认）** | **LXGW WenKai Medium** | Inter / Roboto |
| 科技/教程 | Noto Sans SC | Inter / Roboto |
| 新闻/资讯 | Noto Sans SC | Oswald / Montserrat |
| 文化/深度 | LXGW WenKai / Noto Serif SC | Playfair Display |
| 娱乐/轻松 | ZCOOL KuaiLe | Poppins |
| 时尚/潮流 | ZCOOL QingKe HuangYou | Montserrat |
| 正式/商务 | Noto Sans SC | Inter |

### 字体在 FFmpeg 中的使用

```bash
# 下载字体后，通过 --font-path 参数指定
python3 scripts/render_final.py --config render_config.json --output final.mp4 \
  --font-path fonts/LXGWWenKai-Regular.ttf
```

### 字体在 Remotion 中的使用

```tsx
// 方式 1: @remotion/google-fonts（英文字体推荐）
import { loadFont } from "@remotion/google-fonts/Inter";
const { fontFamily } = loadFont();

// 方式 2: @remotion/fonts（本地/CJK 字体推荐）
import { loadFont } from "@remotion/fonts";
loadFont({
  family: "LXGW WenKai",
  url: staticFile("fonts/LXGWWenKai-Regular.ttf"),
  format: "truetype",
});

// 方式 3: @remotion/google-fonts 加载 CJK
import { loadFont } from "@remotion/google-fonts/NotoSansSC";
const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["chinese-simplified"],  // 重要：指定子集减小体积
});
```

### 注意事项

- **CJK 字体体积大**（10-20MB），使用 `@remotion/google-fonts` 时务必指定 `subsets: ["chinese-simplified"]` 减小体积
- **字体缓存**：下载的字体保存在项目 `fonts/` 目录，`.gitignore` 已排除
- **中国用户**：字体下载自动使用 jsDelivr CDN 加速
- **商用安全**：目录中所有字体均为 SIL OFL 或 Apache 2.0 许可，可免费商用

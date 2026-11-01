## Prerequisites（前置要求）

在执行任何操作之前，先运行环境检测：

```bash
python3 scripts/utils.py
```

这会自动检测平台（macOS/Linux/WSL/Windows）、GPU 类型、可用编码器、Whisper 引擎，并给出诊断报告。

如果缺少依赖，提示用户安装：
- **ffmpeg**: `brew install ffmpeg`（macOS）或 `apt install ffmpeg`（Linux/WSL）或下载 Windows 版本
- **whisper**:
  - **Apple Silicon (M1/M2/M3/M4)**: `pip install mlx-whisper`（推荐，Metal 加速最快）
  - **NVIDIA / CPU**: `pip install faster-whisper`（推荐，速度快 4 倍）或 `pip install openai-whisper`
- **中国用户**加速安装（Apple Silicon）：`pip install mlx-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple`
  其他平台：`pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple`

如果项目根目录有 `.venv` 虚拟环境，运行 Python 脚本前先激活：
```bash
source .venv/bin/activate  # macOS/Linux/WSL
# Windows: .venv\Scripts\activate
```

### 平台说明

- **macOS (Apple Silicon)**: 自动使用 VideoToolbox 硬件编码加速；Whisper 引擎自动选 `mlx-whisper`（已安装），推荐 large-v3-turbo 模型（走 `mlx-community/whisper-large-v3-turbo`）
- **字幕字体（短视频）**: 默认优先选 Heavy / Medium 字重的中文字体：用户库的 `Source Han Sans SC Heavy` / `Smiley Sans` > 系统 `STHeiti Medium` > `PingFang SC Semibold`。如果都没有，会自动从 [adobe-fonts/source-han-sans](https://github.com/adobe-fonts/source-han-sans) 下载 Heavy 字重缓存到 `~/.cache/video-editing/fonts/`。绝不再默认使用 Hiragino W3 这类细字
- **macOS (Intel)**: 使用 VideoToolbox 编码，Whisper 使用 CPU 模式
- **Linux**: 自动检测 NVIDIA GPU (NVENC)、Intel QSV、AMD AMF
- **WSL**: 支持，自动检测 Windows 字体路径 (`/mnt/c/Windows/Fonts/`)
- **Windows**: 建议使用 WSL2 环境运行；支持 QSV/AMF 硬件编码
- **无独显 (集成显卡)**: Intel iGPU 使用 QSV 编码，AMD iGPU 使用 AMF 编码；Whisper 建议 medium 模型（而非 large）
- **中国用户**: 自动检测中国区域，使用清华 pip 镜像和 HuggingFace 镜像下载模型，也可通过 `--mirror` 参数强制启用

### Linux GPU 配置指南（NVIDIA / Intel Arc）

在 Linux 上使用 GPU 加速 Whisper 语音识别时，不同显卡需要不同的配置方案。运行 `python3 scripts/utils.py` 会自动检测显卡型号并给出建议，但如果遇到问题，请参考以下方案。

#### 方案 A：NVIDIA 40 系列显卡（RTX 4060 / 4070 / 4080 / 4090）

40 系列（Ada Lovelace 架构，Compute Capability 8.9）对 faster-whisper 支持最成熟，开箱即用。

**安装步骤：**
```bash
# 1. 安装 NVIDIA 驱动（535+）和 CUDA Toolkit 12.4+
sudo apt install nvidia-driver-535 nvidia-cuda-toolkit
# 或从 NVIDIA 官网安装最新驱动：https://www.nvidia.com/drivers

# 2. 验证 CUDA
nvidia-smi  # 应显示驱动版本和 CUDA 版本

# 3. 安装 faster-whisper（自动安装匹配的 CTranslate2）
pip install faster-whisper>=1.1.0
```

**配置说明：**
- CUDA Toolkit: 12.4+（推荐 12.6）
- CTranslate2: >= 4.5.0（自动随 faster-whisper 安装）
- 计算精度: `float16`（默认）, `int8_float16`, `int8` 均可使用
- Whisper 模型: 推荐 `large-v3`（VRAM >= 6GB）
- 无需特殊配置，`python3 scripts/transcribe.py` 会自动检测并使用 CUDA

#### 方案 B：NVIDIA 50 系列显卡（RTX 5060 / 5060 Ti / 5070 / 5080 / 5090）

50 系列（Blackwell 架构，Compute Capability 12.0，sm_120）需要额外注意 CUDA 版本和计算精度设置。

**已知问题：**
CTranslate2 在 Blackwell 架构上使用 INT8 精度时会报错 `cuBLAS failed with status CUBLAS_STATUS_NOT_SUPPORTED`，
这是因为 Blackwell 的 INT8 Tensor Core 需要矩阵维度为 16 的倍数对齐。CTranslate2 >= 4.7.1 已修复此问题，
但为保险起见，本工具在检测到 50 系列显卡时会自动使用 `float16` 精度。

**安装步骤：**
```bash
# 1. 安装 NVIDIA 驱动（565+，必须支持 Blackwell）
#    从 NVIDIA 官网下载最新驱动：https://www.nvidia.com/drivers
#    或使用包管理器安装 565 以上版本
sudo apt install nvidia-driver-565

# 2. 安装 CUDA Toolkit 12.8+（Blackwell 最低要求）
#    推荐从 NVIDIA 官网安装：https://developer.nvidia.com/cuda-downloads
#    选择 Linux > x86_64 > Ubuntu > deb (network)

# 3. 验证 CUDA
nvidia-smi  # 应显示 CUDA 12.8+

# 4. 安装 faster-whisper 和最新 CTranslate2
pip install faster-whisper>=1.1.0
pip install --upgrade ctranslate2>=4.7.1  # 确保包含 Blackwell 修复

# 5. 如果仍然报错，强制使用 float16 精度（本工具已自动处理）
#    手动测试：
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cuda', compute_type='float16')
print('CUDA float16 OK')
"
```

**配置说明：**
- CUDA Toolkit: >= 12.8（推荐 13.0+，最新为 13.2）
- NVIDIA 驱动: >= 565
- CTranslate2: >= 4.7.1（包含 INT8 padding 修复）
- 计算精度: 推荐 `float16`（最稳定）；`int8_float16` 在 CTranslate2 >= 4.7.1 上可能可用
- 如果 `int8` 仍然报错，工具会自动降级到 `float16`
- Whisper 模型: 推荐 `large-v3`（VRAM >= 6GB）
- `utils.py` 会自动检测 50 系列显卡（通过 `nvidia-smi` 查询 GPU 名称中的 "RTX 50"），并选择安全的 `float16` 精度

**排错：**
如果出现 `CUBLAS_STATUS_NOT_SUPPORTED` 错误：
1. 确认 CTranslate2 版本 >= 4.7.1：`python3 -c "import ctranslate2; print(ctranslate2.__version__)"`
2. 确认 CUDA 版本 >= 12.8：`nvidia-smi` 或 `nvcc --version`
3. 尝试手动指定 `--compute-type float16`（如果直接使用 transcribe.py 的话）
4. 确认驱动版本 >= 565：`nvidia-smi` 查看 Driver Version

#### 方案 C：Intel Arc 独立显卡（A770 / A750 / B580）

Intel Arc 显卡**不支持 CUDA**，因此 faster-whisper（依赖 CTranslate2/CUDA）无法直接在 Intel Arc 上 GPU 加速。
需要使用替代方案。

**推荐方案：OpenVINO + Whisper（最易用）**
```bash
# 1. 安装 OpenVINO
pip install openvino openvino-genai

# 2. 使用 OpenVINO GenAI 的 WhisperPipeline
python3 -c "
import openvino_genai as ov_genai
pipe = ov_genai.WhisperPipeline('OpenVINO/whisper-large-v3-fp16-ov', device='GPU')
result = pipe.generate('audio.wav', language='<|zh|>')
print(result.texts[0])
"

# 3. 或使用 Hugging Face 预转换模型
pip install optimum[openvino]
# 从 HuggingFace 下载 OpenVINO 格式 Whisper 模型
# https://huggingface.co/OpenVINO/whisper-medium-int8-ov
```

**备选方案：whisper.cpp + SYCL（性能更好，配置更复杂）**
```bash
# 1. 安装 Intel oneAPI Base Toolkit
#    https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
  | gpg --dearmor | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] \
  https://apt.repos.intel.com/oneapi all main" \
  | sudo tee /etc/apt/sources.list.d/oneAPI.list
sudo apt update && sudo apt install intel-oneapi-base-toolkit

# 2. 编译 whisper.cpp（启用 SYCL 后端）
source /opt/intel/oneapi/setvars.sh
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
cmake -B build -DWHISPER_SYCL=ON
cmake --build build --config Release

# 3. 下载 Whisper 模型并运行
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh
```

**配置说明：**
- Intel Arc 不支持 CUDA，faster-whisper 在 Intel Arc 上只能用 CPU 模式
- OpenVINO 方案最简单，支持 Arc A770/A750/B580 和集成显卡
- whisper.cpp + SYCL 性能更好（A770 上接近 NVIDIA 中端显卡水平），但需要 oneAPI 环境
- B580（Battlemage 架构）的 SYCL 支持尚在优化中，A770 目前更稳定
- 推荐 Whisper 模型: `medium`（12GB VRAM 的 A770）或 `small`（8GB VRAM 的 A750）
- 如果用户有 Intel Arc 显卡，脚本会自动检测并使用 CPU 模式运行 faster-whisper（作为 fallback）

#### GPU 配置速查表

| 显卡系列 | 架构 | CUDA Toolkit | 驱动版本 | CTranslate2 | 计算精度 | Whisper 引擎 |
|---------|------|-------------|---------|-------------|---------|-------------|
| RTX 40xx | Ada Lovelace (sm_89) | >= 12.4 | >= 535 | >= 4.5.0 | float16 / int8 均可 | faster-whisper |
| RTX 50xx | Blackwell (sm_120) | >= 12.8 | >= 565 | >= 4.7.1 | **float16**（推荐） | faster-whisper |
| Intel Arc | Xe HPG / Battlemage | N/A | i915 | N/A | N/A | OpenVINO 或 whisper.cpp+SYCL |
| Intel iGPU | 集成显卡 | N/A | i915 | N/A | int8 (CPU) | faster-whisper (CPU 模式) |
| 无独显 | CPU | N/A | N/A | 任意版本 | int8 (CPU) | faster-whisper (CPU 模式) |

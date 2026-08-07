# AB Video Processor

用于视频帧混合、格式转换与视觉特征实验的桌面工具。

项目通过对两段视频进行抽帧、混合与重新编码，研究不同帧率、编码参数和 GPU 加速方案对输出视频视觉表现及数据特征的影响。

> 请仅处理拥有合法使用权的素材。本项目不用于绕过平台审核、版权识别或其他安全机制。

## 项目背景

在视频处理和内容生产流程中，经常需要验证不同帧率、分辨率、混合策略和编码方式对输出结果的影响。手工执行 FFmpeg 命令不利于非技术用户重复调整和比较参数。

本项目将相关处理流程封装为图形化工具，提供可重复的参数配置与进度反馈。

## 主要能力

- 读取两段视频并分析基础媒体信息
- 按配置进行抽帧与帧混合
- 统一分辨率、帧率和编码参数
- 支持多档处理强度
- 在兼容环境下启用 NVIDIA GPU 加速
- 通过 PyQt5 界面展示任务状态和进度

## 技术流程

```text
Video A + Video B
    -> Media inspection
    -> Resolution alignment
    -> Frame sampling and mixing
    -> FFmpeg encoding
    -> Output validation
```

主要技术：Python、PyQt5、NumPy、OpenCV、FFmpeg。

## 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（需加入 `PATH`）

```bash
git clone https://github.com/toki-plus/AB-Video-Deduplicator.git
cd AB-Video-Deduplicator
python -m venv venv
```

激活虚拟环境后安装依赖：

```bash
pip install -r requirements.txt
pyrcc5 src/resources.qrc -o src/resources.py
python src/main.py
```

## 使用说明

1. 选择两段拥有合法使用权的视频素材。
2. 选择处理参数和输出目录。
3. 如本机具备兼容的 NVIDIA 环境，可启用 GPU 加速。
4. 启动任务并检查输出视频的画面、音频和时长。

## 当前限制

- 输出效果受源视频分辨率、帧率和编码格式影响。
- GPU 加速依赖本机 FFmpeg 构建与驱动环境。
- 当前仅包含基础测试工具，尚未建立完整的自动化回归测试。

## License

See [LICENSE](./LICENSE).

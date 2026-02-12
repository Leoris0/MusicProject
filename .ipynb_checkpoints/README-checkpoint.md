# 🎭 Maestro WebUI

> 统一的 AI 创作平台 - 整合 LongCat-Video 和 SongGeneration

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

</div>

## 📖 简介

Maestro WebUI 是一个统一的前端界面，将 **LongCat-Video** 和 **SongGeneration** 两个强大的 AI 项目整合在一起，让您可以通过一个美观的界面轻松使用各种 AI 创作功能。

## ✨ 功能特性

### 🎬 视频生成 (LongCat-Video)

| 功能 | 描述 |
|------|------|
| 📝 文本生成视频 | 根据文本描述生成高质量视频 |
| 🖼️ 图片生成视频 | 让静态图片动起来 |
| 🎤 音频驱动数字人 | 根据音频生成说话的数字人视频 |
| 🔄 视频延续 | 延长现有视频的长度 |

### 🎵 歌曲生成 (SongGeneration)

| 功能 | 描述 |
|------|------|
| 📝 歌词生成歌曲 | 根据歌词和风格描述生成完整歌曲 |
| 🎭 多种风格 | 支持 Pop, R&B, Rock, Jazz 等多种音乐风格 |
| 🔊 分离输出 | 可分别生成人声、伴奏或混合音频 |
| 🎨 风格迁移 | 使用参考音频进行风格迁移 |

## 📁 项目结构

```
WebUI/
├── app.py              # 主应用入口
├── config.py           # 配置文件
├── requirements.txt    # 依赖列表
├── 启动WebUI.bat       # Windows 启动脚本
├── start_webui.sh      # Linux/Mac 启动脚本
├── modules/
│   ├── __init__.py
│   ├── longcat_module.py   # LongCat-Video 模块
│   └── song_module.py      # SongGeneration 模块
├── static/             # 静态资源
└── outputs/            # 输出文件夹
    ├── videos/         # 生成的视频
    └── songs/          # 生成的歌曲
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统满足以下要求：
- Python 3.8+
- CUDA 支持的 GPU（推荐）
- 足够的磁盘空间用于模型权重

### 2. 安装依赖

```bash
# 安装 WebUI 基础依赖
cd WebUI
pip install -r requirements.txt

# 安装 LongCat-Video 依赖
cd ../LongCat-Video
pip install -r requirements.txt

# 安装 SongGeneration 依赖
cd ../SongGeneration
pip install -r requirements.txt
```

### 3. 配置模型

确保已下载并放置好模型权重文件：

- **LongCat-Video**: `LongCat-Video/weights/LongCat-Video/`
- **LongCat-Video-Avatar**: `LongCat-Video/weights/LongCat-Video-Avatar/`
- **SongGeneration**: `SongGeneration/ckpt/songgeneration_base/`

### 4. 启动服务

**Windows:**
```bash
双击 启动WebUI.bat
```

**Linux/Mac:**
```bash
chmod +x start_webui.sh
./start_webui.sh
```

**或直接运行:**
```bash
cd WebUI
python app.py
```

### 5. 访问界面

启动后在浏览器中访问：
```
http://localhost:7860
```

## 🎨 界面设计

Maestro WebUI 采用现代化的赛博朋克风格设计：

### 📱 入口页面
- **双模块卡片展示** - 清晰展示两大功能模块
- **悬停动画效果** - 卡片悬停时的发光和上移效果
- **一键进入** - 点击对应模块卡片即可进入功能页面

### 🎨 设计特色
- 🌌 赛博朋克风格的渐变背景
- ✨ 霓虹灯光边框效果
- 📱 响应式布局设计
- 🎯 直观的操作界面
- ⬅️ 便捷的返回导航

## ⚙️ 配置说明

您可以在 `config.py` 中修改以下配置：

```python
# Web 服务配置
SERVER_HOST = "0.0.0.0"  # 服务地址
SERVER_PORT = 7860       # 服务端口
SHARE = False            # 是否生成公共链接

# 默认参数
DEFAULT_VIDEO_PARAMS = {...}
DEFAULT_SONG_PARAMS = {...}
```

## 🎼 歌词格式说明

SongGeneration 使用特定的歌词格式：

```
[intro-short]

[verse]
第一段歌词
每行一句

[chorus]
副歌歌词

[outro-short]
```

**结构标签说明：**
- `[intro]`, `[intro-short]`, `[intro-medium]` - 前奏（无歌词）
- `[verse]` - 主歌
- `[chorus]` - 副歌
- `[bridge]` - 过渡段
- `[inst]`, `[inst-short]`, `[inst-medium]` - 纯器乐段（无歌词）
- `[outro]`, `[outro-short]`, `[outro-medium]` - 尾奏（无歌词）

## 🔧 常见问题

### Q: 界面启动后看不到视频/音频输出？
A: 当前版本显示的是任务配置信息。实际生成需要正确配置模型权重文件。

### Q: 生成过程中显存不足？
A: 尝试勾选"低显存模式"选项，或降低分辨率和帧数。

### Q: 如何使用自定义模型？
A: 将模型放置到对应的 weights/ckpt 目录下，重启服务即可自动识别。

## 📝 注意事项

1. 首次运行可能需要下载模型权重，请确保网络连接稳定
2. GPU 显存建议 8GB 以上
3. 生成的文件保存在 `outputs/` 目录下
4. 本项目仅供学习研究使用，请遵守相关开源协议

## 🙏 致谢

- [LongCat-Video](https://github.com/xxx/LongCat-Video) - 视频生成模型
- [SongGeneration](https://github.com/tencent-ailab/SongGeneration) - 歌曲生成模型
- [Gradio](https://gradio.app/) - Web UI 框架

## 📄 许可证

本项目采用 MIT 许可证，详情请参阅各子项目的许可证文件。

---

<div align="center">
<p>Made with ❤️ by Maestro Team</p>
</div>


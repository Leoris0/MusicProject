"""
Maestro WebUI 配置文件
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent

# LongCat-Video 配置
LONGCAT_DIR = PROJECT_DIR / "LongCat-Video"
LONGCAT_CHECKPOINT_DIR = LONGCAT_DIR / "weights" / "LongCat-Video"
LONGCAT_AVATAR_CHECKPOINT_DIR = LONGCAT_DIR / "weights" / "LongCat-Video-Avatar"

# SongGeneration 配置
SONG_DIR = PROJECT_DIR / "SongGeneration"
SONG_CKPT_DIR = SONG_DIR / "ckpt"

# 输出目录
OUTPUT_DIR = BASE_DIR / "outputs"
VIDEO_OUTPUT_DIR = OUTPUT_DIR / "videos"
SONG_OUTPUT_DIR = OUTPUT_DIR / "songs"
AVATAR_OUTPUT_DIR = OUTPUT_DIR / "avatar"

# 创建输出目录
for dir_path in [OUTPUT_DIR, VIDEO_OUTPUT_DIR, SONG_OUTPUT_DIR, AVATAR_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Web 服务配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 7860
SHARE = False

# 模型配置
DEFAULT_VIDEO_PARAMS = {
    "height": 480,
    "width": 832,
    "num_frames": 93,
    "num_inference_steps": 50,
    "guidance_scale": 4.0,
    "seed": 42
}

DEFAULT_SONG_PARAMS = {
    "max_duration": 160,
    "cfg_coef": 1.5,
    "temperature": 0.9,
    "top_k": 50,
    "top_p": 0.0
}

# 可用风格列表
AVAILABLE_STYLES = [
    'Pop', 'R&B', 'Dance', 'Jazz', 'Folk', 'Rock',
    'Chinese Style', 'Chinese Tradition', 'Metal',
    'Reggae', 'Chinese Opera', 'Auto'
]

# 生成类型
GENERATION_TYPES = ['mixed', 'vocal', 'bgm', 'separate']

# Avatar 配置
DEFAULT_AVATAR_PARAMS = {
    "resolution": "480p",
    "num_inference_steps": 50,
    "text_guidance_scale": 4.0,
    "audio_guidance_scale": 4.0,  # 建议 3-5
    "seed": 42,
    "num_segments": 1,
    "ref_img_index": 10,  # 0-24
    "mask_frame_range": 3
}

# Avatar 生成模式
AVATAR_STAGE_TYPES = ['ai2v', 'at2v']  # ai2v: 图片+音频, at2v: 文本+音频

# Avatar 音频模式
AVATAR_AUDIO_TYPES = ['para', 'add']  # para: 并行, add: 顺序




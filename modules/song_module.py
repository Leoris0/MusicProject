"""
SongGeneration 模块
通过 HTTP API 调用 SongGeneration 服务
"""
import os
import json
import time
import requests
from pathlib import Path

# API 服务地址
SONG_API_URL = os.environ.get("SONG_API_URL", "http://localhost:8002")

# 可用的自动风格类型
AUTO_PROMPT_TYPES = [
    'Pop', 'R&B', 'Dance', 'Jazz', 'Folk', 'Rock', 
    'Chinese Style', 'Chinese Tradition', 'Metal', 
    'Reggae', 'Chinese Opera', 'Auto'
]

# 生成类型
GENERATION_TYPES = ['mixed', 'vocal', 'bgm', 'separate']


class SongGenerationModule:
    """SongGeneration 功能模块 - HTTP API 版本"""
    
    def __init__(self, api_url=None):
        self.api_url = api_url or SONG_API_URL
        self.output_dir = Path(__file__).parent.parent / "outputs" / "songs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_service(self):
        """检查服务是否可用"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def generate_song(self, lyrics, description=None, prompt_audio_path=None,
                      auto_prompt_type=None, gen_type="mixed",
                      model_name=None, max_duration=160,
                      cfg_coef=1.5, temperature=0.9, top_k=50, top_p=0.0,
                      low_mem=False, progress_callback=None):
        """
        生成歌曲 - 通过 API 调用
        """
        timestamp = int(time.time())
        local_output_path = self.output_dir / f"song_{timestamp}.wav"
        
        config = {
            "type": "song_generation",
            "lyrics": lyrics,
            "description": description,
            "auto_prompt_type": auto_prompt_type,
            "gen_type": gen_type,
            "max_duration": max_duration,
            "cfg_coef": cfg_coef,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
        }
        
        if progress_callback:
            progress_callback(0.1, "检查服务状态...")
        
        # 检查服务
        if not self._check_service():
            config["error"] = f"SongGeneration 服务未启动，请先运行: python SongGeneration/api_server.py --port 8002"
            return None, config
        
        if progress_callback:
            progress_callback(0.2, "发送生成请求...")
        
        try:
            # 发送请求
            resp = requests.post(
                f"{self.api_url}/generate",
                json={
                    "lyrics": lyrics,
                    "description": description,
                    "auto_prompt_type": auto_prompt_type,
                    "gen_type": gen_type,
                    "max_duration": max_duration,
                    "cfg_coef": cfg_coef,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                timeout=600  # 10分钟超时
            )
            
            if progress_callback:
                progress_callback(0.8, "下载生成结果...")
            
            result = resp.json()
            
            if result.get("success") and result.get("filename"):
                # 下载文件
                download_resp = requests.get(
                    f"{self.api_url}/download/{result['filename']}",
                    timeout=60
                )
                
                if download_resp.status_code == 200:
                    with open(local_output_path, 'wb') as f:
                        f.write(download_resp.content)
                    
                    if progress_callback:
                        progress_callback(1.0, "生成完成!")
                    
                    config["success"] = True
                    config["output_path"] = str(local_output_path)
                    return str(local_output_path), config
            
            config["error"] = result.get("error", "生成失败")
            return None, config
            
        except requests.exceptions.Timeout:
            config["error"] = "请求超时，生成时间过长"
            return None, config
        except Exception as e:
            config["error"] = str(e)
            return None, config
    
    def get_example_lyrics(self):
        """获取示例歌词"""
        return """[intro-short]

[verse]
夜晚的街灯闪烁
我漫步在熟悉的角落
回忆像潮水般涌来
你的笑容如此清晰

[chorus]
回忆的温度还在
你却已不在
我的心被爱填满
却又被思念刺痛

[outro-short]"""
    
    def format_lyrics(self, raw_lyrics):
        """格式化歌词"""
        lyrics = raw_lyrics.replace("[intro]", "[intro-short]")
        lyrics = lyrics.replace("[inst]", "[inst-short]")
        lyrics = lyrics.replace("[outro]", "[outro-short]")
        
        paragraphs = [p.strip() for p in lyrics.strip().split('\n\n') if p.strip()]
        
        formatted_parts = []
        for para in paragraphs:
            lines = para.splitlines()
            if not lines:
                continue
            
            struct_tag = lines[0].strip().lower()
            instrumental_tags = ['[intro-short]', '[intro-medium]', '[inst-short]', 
                               '[inst-medium]', '[outro-short]', '[outro-medium]']
            
            if struct_tag in instrumental_tags:
                formatted_parts.append(struct_tag)
            else:
                lyrics_lines = [line.strip() for line in lines[1:] if line.strip()]
                if lyrics_lines:
                    lyrics_text = '.'.join(lyrics_lines)
                    formatted_parts.append(f"{struct_tag} {lyrics_text}")
                else:
                    formatted_parts.append(struct_tag)
        
        return " ; ".join(formatted_parts)


# 全局实例
song_module = None

def get_song_module():
    global song_module
    if song_module is None:
        song_module = SongGenerationModule()
    return song_module

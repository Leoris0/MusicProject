"""
LongCat-Video 模块
通过 HTTP API 调用 LongCat-Video 服务
"""
import os
import json
import time
import requests
from pathlib import Path

# API 服务地址
LONGCAT_API_URL = os.environ.get("LONGCAT_API_URL", "http://localhost:8001")


class LongCatVideoModule:
    """LongCat-Video 功能模块 - HTTP API 版本"""
    
    def __init__(self, api_url=None):
        self.api_url = api_url or LONGCAT_API_URL
        self.output_dir = Path(__file__).parent.parent / "outputs" / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_service(self):
        """检查服务是否可用"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def text_to_video(self, prompt, negative_prompt="", height=480, width=832, 
                      num_frames=93, num_inference_steps=50, guidance_scale=4.0,
                      seed=42, use_distill=False, progress_callback=None):
        """文本生成视频 - 通过 API 调用"""
        timestamp = int(time.time())
        local_output_path = self.output_dir / f"t2v_{timestamp}.mp4"
        
        config = {
            "type": "text_to_video",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "height": height,
            "width": width,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "use_distill": use_distill,
        }
        
        if progress_callback:
            progress_callback(0.1, "检查服务状态...")
        
        if not self._check_service():
            config["error"] = f"LongCat-Video 服务未启动，请先运行: python LongCat-Video/api_server.py --port 8001"
            return None, config
        
        if progress_callback:
            progress_callback(0.2, "发送生成请求...")
        
        try:
            resp = requests.post(
                f"{self.api_url}/text_to_video",
                json=config,
                timeout=1200  # 20分钟超时
            )
            
            if progress_callback:
                progress_callback(0.8, "下载生成结果...")
            
            result = resp.json()
            
            if result.get("success") and result.get("filename"):
                download_resp = requests.get(
                    f"{self.api_url}/download/{result['filename']}",
                    timeout=120
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
    
    def image_to_video(self, image_path, prompt, negative_prompt="", 
                       resolution="480p", num_frames=93, num_inference_steps=50,
                       guidance_scale=4.0, seed=42, use_distill=False,
                       progress_callback=None):
        """图片生成视频 - 通过 API 调用"""
        timestamp = int(time.time())
        local_output_path = self.output_dir / f"i2v_{timestamp}.mp4"
        
        config = {
            "type": "image_to_video",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "resolution": resolution,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "use_distill": use_distill,
        }
        
        if progress_callback:
            progress_callback(0.1, "检查服务状态...")
        
        if not self._check_service():
            config["error"] = f"LongCat-Video 服务未启动，请先运行: python LongCat-Video/api_server.py --port 8001"
            return None, config
        
        if progress_callback:
            progress_callback(0.2, "上传图片并发送请求...")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {
                    'prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'resolution': resolution,
                    'num_frames': num_frames,
                    'num_inference_steps': num_inference_steps,
                    'guidance_scale': guidance_scale,
                    'seed': seed,
                    'use_distill': str(use_distill).lower(),
                }
                
                resp = requests.post(
                    f"{self.api_url}/image_to_video",
                    files=files,
                    data=data,
                    timeout=1200
                )
            
            if progress_callback:
                progress_callback(0.8, "下载生成结果...")
            
            result = resp.json()
            
            if result.get("success") and result.get("filename"):
                download_resp = requests.get(
                    f"{self.api_url}/download/{result['filename']}",
                    timeout=120
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
    
    def audio_to_video_single(self, audio_path, image_path=None, prompt="",
                              resolution="480p", num_frames=93, 
                              num_inference_steps=50, text_guidance_scale=4.0,
                              audio_guidance_scale=4.0, seed=42,
                              num_segments=1, stage_1="ai2v",
                              progress_callback=None):
        """音频驱动视频 - 暂未实现"""
        config = {
            "type": "audio_to_video_single",
            "note": "Avatar 功能需要额外的模型权重，暂未实现 API 接口"
        }
        return None, config
    
    def audio_to_video_multi(self, audio_paths, image_path=None, prompt="",
                             resolution="480p", num_frames=93,
                             num_inference_steps=50, text_guidance_scale=4.0,
                             audio_guidance_scale=4.0, seed=42,
                             num_segments=1, progress_callback=None):
        """多人音频驱动视频 - 暂未实现"""
        config = {
            "type": "audio_to_video_multi",
            "note": "多人 Avatar 功能暂未实现"
        }
        return None, config
    
    def video_continuation(self, video_path, prompt, num_continuation_frames=93,
                          num_inference_steps=50, guidance_scale=4.0,
                          seed=42, progress_callback=None):
        """视频延续 - 暂未实现"""
        config = {
            "type": "video_continuation",
            "note": "视频延续功能暂未实现"
        }
        return None, config


# 全局实例
longcat_module = None

def get_longcat_module():
    global longcat_module
    if longcat_module is None:
        longcat_module = LongCatVideoModule()
    return longcat_module

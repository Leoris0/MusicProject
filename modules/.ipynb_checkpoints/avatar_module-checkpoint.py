"""
Avatar 模块
通过 HTTP API 调用 LongCat-Video Avatar 服务
支持单人说话视频和双人对话视频生成
"""
import os
import json
import time
import requests
from pathlib import Path

# API 服务地址
AVATAR_API_URL = os.environ.get("AVATAR_API_URL", "http://localhost:8003")


class AvatarModule:
    """Avatar 功能模块 - HTTP API 版本"""
    
    def __init__(self, api_url=None):
        self.api_url = api_url or AVATAR_API_URL
        self.output_dir = Path(__file__).parent.parent / "outputs" / "avatar"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_service(self):
        """检查服务是否可用"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except:
            return False, None
    
    def single_avatar(self, audio_path, image_path=None, prompt="A person is speaking.",
                      stage_1="ai2v", resolution="480p", num_inference_steps=50,
                      text_guidance_scale=4.0, audio_guidance_scale=4.0,
                      seed=42, num_segments=1, ref_img_index=10, mask_frame_range=3,
                      progress_callback=None):
        """单人说话视频生成
        
        Args:
            audio_path: 音频文件路径
            image_path: 参考图片路径 (ai2v 模式必需)
            prompt: 场景描述
            stage_1: 生成模式 - "ai2v" (图片+音频) 或 "at2v" (文本+音频)
            resolution: 分辨率 - "480p" 或 "720p"
            num_inference_steps: 推理步数
            text_guidance_scale: 文本引导比例
            audio_guidance_scale: 音频引导比例 (建议 3-5)
            seed: 随机种子
            num_segments: 视频段数 (用于长视频)
            ref_img_index: 参考图像索引 (0-24)
            mask_frame_range: 遮罩帧范围
            progress_callback: 进度回调函数
        
        Returns:
            (output_path, config): 输出视频路径和配置信息
        """
        timestamp = int(time.time())
        local_output_path = self.output_dir / f"single_avatar_{timestamp}.mp4"
        
        config = {
            "type": "single_avatar",
            "prompt": prompt,
            "stage_1": stage_1,
            "resolution": resolution,
            "num_inference_steps": num_inference_steps,
            "text_guidance_scale": text_guidance_scale,
            "audio_guidance_scale": audio_guidance_scale,
            "seed": seed,
            "num_segments": num_segments,
            "ref_img_index": ref_img_index,
            "mask_frame_range": mask_frame_range,
        }
        
        if progress_callback:
            progress_callback(0.1, "检查服务状态...")
        
        is_available, health_info = self._check_service()
        if not is_available:
            config["error"] = "Avatar API 服务未启动，请先运行: python LongCat-Video/api_server_avatar.py --port 8003"
            return None, config
        
        # 检查模型类型
        if health_info and health_info.get("model_type") != "single":
            if progress_callback:
                progress_callback(0.15, "切换到单人模型...")
            try:
                requests.post(f"{self.api_url}/load_model", json={"model_type": "single"}, timeout=300)
            except:
                pass
        
        if progress_callback:
            progress_callback(0.2, "上传文件并发送请求...")
        
        try:
            files = {}
            data = {
                'prompt': prompt,
                'stage_1': stage_1,
                'resolution': resolution,
                'num_inference_steps': num_inference_steps,
                'text_guidance_scale': text_guidance_scale,
                'audio_guidance_scale': audio_guidance_scale,
                'seed': seed,
                'num_segments': num_segments,
                'ref_img_index': ref_img_index,
                'mask_frame_range': mask_frame_range,
            }
            
            # 添加音频文件
            audio_file = open(audio_path, 'rb')
            files['audio'] = audio_file
            
            # 添加图片文件 (如果有)
            image_file = None
            if image_path and os.path.exists(image_path):
                image_file = open(image_path, 'rb')
                files['image'] = image_file
            
            resp = requests.post(
                f"{self.api_url}/single_avatar",
                files=files,
                data=data,
                #timeout=1800  # 30分钟超时
                timeout=None
            )
            
            # 关闭文件
            audio_file.close()
            if image_file:
                image_file.close()
            
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

    def multi_avatar(self, image_path, audio1_path=None, audio2_path=None,
                     prompt="Two people are having a conversation.",
                     audio_type="para", resolution="480p", num_inference_steps=50,
                     text_guidance_scale=4.0, audio_guidance_scale=4.0,
                     seed=42, num_segments=1, ref_img_index=10, mask_frame_range=3,
                     bbox1=None, bbox2=None, progress_callback=None):
        """双人对话视频生成
        
        Args:
            image_path: 参考图片路径
            audio1_path: Person1 音频路径
            audio2_path: Person2 音频路径
            prompt: 场景描述
            audio_type: 音频模式 - "para" (并行) 或 "add" (顺序)
            resolution: 分辨率 - "480p" 或 "720p"
            num_inference_steps: 推理步数
            text_guidance_scale: 文本引导比例
            audio_guidance_scale: 音频引导比例 (建议 3-5)
            seed: 随机种子
            num_segments: 视频段数 (用于长视频)
            ref_img_index: 参考图像索引 (0-24)
            mask_frame_range: 遮罩帧范围
            bbox1: Person1 边界框 [y_min, x_min, y_max, x_max]
            bbox2: Person2 边界框 [y_min, x_min, y_max, x_max]
            progress_callback: 进度回调函数
        
        Returns:
            (output_path, config): 输出视频路径和配置信息
        """
        timestamp = int(time.time())
        local_output_path = self.output_dir / f"multi_avatar_{timestamp}.mp4"
        
        config = {
            "type": "multi_avatar",
            "prompt": prompt,
            "audio_type": audio_type,
            "resolution": resolution,
            "num_inference_steps": num_inference_steps,
            "text_guidance_scale": text_guidance_scale,
            "audio_guidance_scale": audio_guidance_scale,
            "seed": seed,
            "num_segments": num_segments,
            "ref_img_index": ref_img_index,
            "mask_frame_range": mask_frame_range,
        }
        
        if progress_callback:
            progress_callback(0.1, "检查服务状态...")
        
        is_available, health_info = self._check_service()
        if not is_available:
            config["error"] = "Avatar API 服务未启动，请先运行: python LongCat-Video/api_server_avatar.py --port 8003"
            return None, config
        
        # 检查模型类型
        if health_info and health_info.get("model_type") != "multi":
            if progress_callback:
                progress_callback(0.15, "切换到多人模型...")
            try:
                requests.post(f"{self.api_url}/load_model", json={"model_type": "multi"}, timeout=300)
            except:
                pass
        
        if progress_callback:
            progress_callback(0.2, "上传文件并发送请求...")
        
        try:
            files = {}
            data = {
                'prompt': prompt,
                'audio_type': audio_type,
                'resolution': resolution,
                'num_inference_steps': num_inference_steps,
                'text_guidance_scale': text_guidance_scale,
                'audio_guidance_scale': audio_guidance_scale,
                'seed': seed,
                'num_segments': num_segments,
                'ref_img_index': ref_img_index,
                'mask_frame_range': mask_frame_range,
            }
            
            # 添加 bbox (如果有)
            if bbox1:
                data['bbox1'] = ','.join(map(str, bbox1))
            if bbox2:
                data['bbox2'] = ','.join(map(str, bbox2))
            
            # 添加图片文件
            image_file = open(image_path, 'rb')
            files['image'] = image_file
            
            # 添加音频文件
            audio1_file = None
            audio2_file = None
            
            if audio1_path and os.path.exists(audio1_path):
                audio1_file = open(audio1_path, 'rb')
                files['audio1'] = audio1_file
            
            if audio2_path and os.path.exists(audio2_path):
                audio2_file = open(audio2_path, 'rb')
                files['audio2'] = audio2_file
            
            resp = requests.post(
                f"{self.api_url}/multi_avatar",
                files=files,
                data=data,
                #timeout=1800  # 30分钟超时
                timeout=None
            )
            
            # 关闭文件
            image_file.close()
            if audio1_file:
                audio1_file.close()
            if audio2_file:
                audio2_file.close()
            
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


# 全局实例
avatar_module = None

def get_avatar_module():
    global avatar_module
    if avatar_module is None:
        avatar_module = AvatarModule()
    return avatar_module

"""
LongCat-Video 模块
提供视频生成功能的后端接口 - 真正的模型推理版本
"""
import os
import sys
import json
import time
import torch
import numpy as np
import PIL.Image
from pathlib import Path

# 添加 LongCat-Video 项目路径
LONGCAT_DIR = Path(__file__).parent.parent.parent / "LongCat-Video"
sys.path.insert(0, str(LONGCAT_DIR))

_original_cwd = os.getcwd()


class LongCatVideoModule:
    """LongCat-Video 功能模块 - 真正的模型推理"""
    
    def __init__(self, checkpoint_dir=None):
        self.checkpoint_dir = checkpoint_dir or str(LONGCAT_DIR / "weights" / "LongCat-Video")
        self.avatar_checkpoint_dir = str(LONGCAT_DIR / "weights" / "LongCat-Video-Avatar")
        self.output_dir = Path(__file__).parent.parent / "outputs" / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型相关
        self.pipe = None
        self.avatar_pipe = None
        self._model_loaded = False
        self._avatar_model_loaded = False
        self._current_model_type = None  # 'video' or 'avatar'
        
    def _load_video_model(self, progress_callback=None):
        """加载视频生成模型"""
        if self._model_loaded and self._current_model_type == 'video':
            return True
        
        # 如果加载了其他模型，先卸载
        if self._current_model_type == 'avatar':
            self._unload_avatar_model()
        
        try:
            os.chdir(str(LONGCAT_DIR))
            
            if progress_callback:
                progress_callback(0.1, "加载 tokenizer...")
            
            from transformers import AutoTokenizer, UMT5EncoderModel
            from longcat_video.pipeline_longcat_video import LongCatVideoPipeline
            from longcat_video.modules.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
            from longcat_video.modules.autoencoder_kl_wan import AutoencoderKLWan
            from longcat_video.modules.longcat_video_dit import LongCatVideoTransformer3DModel
            
            checkpoint_dir = self.checkpoint_dir
            
            print(f"[LongCat-Video] 加载模型: {checkpoint_dir}")
            
            if progress_callback:
                progress_callback(0.2, "加载 text encoder...")
            
            tokenizer = AutoTokenizer.from_pretrained(
                checkpoint_dir, subfolder="tokenizer", torch_dtype=torch.bfloat16
            )
            
            if progress_callback:
                progress_callback(0.3, "加载 text encoder...")
            
            text_encoder = UMT5EncoderModel.from_pretrained(
                checkpoint_dir, subfolder="text_encoder", torch_dtype=torch.bfloat16
            )
            
            if progress_callback:
                progress_callback(0.5, "加载 VAE...")
            
            vae = AutoencoderKLWan.from_pretrained(
                checkpoint_dir, subfolder="vae", torch_dtype=torch.bfloat16
            )
            
            if progress_callback:
                progress_callback(0.6, "加载 scheduler...")
            
            scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(
                checkpoint_dir, subfolder="scheduler", torch_dtype=torch.bfloat16
            )
            
            if progress_callback:
                progress_callback(0.7, "加载 DiT 模型...")
            
            dit = LongCatVideoTransformer3DModel.from_pretrained(
                checkpoint_dir, subfolder="dit", torch_dtype=torch.bfloat16
            )
            
            if progress_callback:
                progress_callback(0.9, "构建 Pipeline...")
            
            self.pipe = LongCatVideoPipeline(
                tokenizer=tokenizer,
                text_encoder=text_encoder,
                vae=vae,
                scheduler=scheduler,
                dit=dit,
            )
            self.pipe.to('cuda')
            
            self._model_loaded = True
            self._current_model_type = 'video'
            
            print("[LongCat-Video] 模型加载完成!")
            return True
            
        except Exception as e:
            print(f"[LongCat-Video] 模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            os.chdir(_original_cwd)
    
    def _unload_video_model(self):
        """卸载视频模型"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        self._model_loaded = False
        if self._current_model_type == 'video':
            self._current_model_type = None
        torch.cuda.empty_cache()
        print("[LongCat-Video] 视频模型已卸载")
    
    def _unload_avatar_model(self):
        """卸载 Avatar 模型"""
        if self.avatar_pipe is not None:
            del self.avatar_pipe
            self.avatar_pipe = None
        self._avatar_model_loaded = False
        if self._current_model_type == 'avatar':
            self._current_model_type = None
        torch.cuda.empty_cache()
        print("[LongCat-Video] Avatar 模型已卸载")

    
    def text_to_video(self, prompt, negative_prompt="", height=480, width=832, 
                      num_frames=93, num_inference_steps=50, guidance_scale=4.0,
                      seed=42, use_distill=False, progress_callback=None):
        """
        文本生成视频 - 真正的模型推理
        
        Args:
            prompt: 描述视频内容的文本提示
            negative_prompt: 负面提示词
            height: 视频高度
            width: 视频宽度
            num_frames: 视频帧数
            num_inference_steps: 推理步数
            guidance_scale: 引导比例
            seed: 随机种子
            use_distill: 是否使用蒸馏模式(更快)
            progress_callback: 进度回调函数
        
        Returns:
            tuple: (生成视频的路径, 配置信息)
        """
        timestamp = int(time.time())
        output_path = self.output_dir / f"t2v_{timestamp}.mp4"
        
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
            "output_path": str(output_path),
            "checkpoint_dir": self.checkpoint_dir
        }
        
        if progress_callback:
            progress_callback(0.05, "正在加载模型...")
        
        # 加载模型
        if not self._load_video_model(progress_callback):
            return None, {"error": "模型加载失败"}
        
        try:
            os.chdir(str(LONGCAT_DIR))
            
            if progress_callback:
                progress_callback(0.3, "开始生成视频...")
            
            # 设置随机种子
            generator = torch.Generator(device='cuda')
            generator.manual_seed(int(seed))
            
            # 如果使用蒸馏模式，加载 LoRA
            if use_distill:
                cfg_step_lora_path = os.path.join(self.checkpoint_dir, 'lora/cfg_step_lora.safetensors')
                if os.path.exists(cfg_step_lora_path):
                    self.pipe.dit.load_lora(cfg_step_lora_path, 'cfg_step_lora')
                    self.pipe.dit.enable_loras(['cfg_step_lora'])
                    num_inference_steps = 16
                    guidance_scale = 1.0
            
            # 生成视频
            output = self.pipe.generate_t2v(
                prompt=prompt,
                negative_prompt=negative_prompt if not use_distill else "",
                height=int(height),
                width=int(width),
                num_frames=int(num_frames),
                num_inference_steps=int(num_inference_steps),
                guidance_scale=float(guidance_scale),
                generator=generator,
                use_distill=use_distill,
            )[0]
            
            # 禁用 LoRA
            if use_distill:
                self.pipe.dit.disable_all_loras()
            
            if progress_callback:
                progress_callback(0.9, "保存视频文件...")
            
            # 保存视频
            self._save_video(output, str(output_path), fps=15)
            
            if progress_callback:
                progress_callback(1.0, "生成完成!")
            
            # 清理显存
            del output
            torch.cuda.empty_cache()
            
            config["success"] = True
            return str(output_path), config
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            config["error"] = str(e)
            return None, config
        finally:
            os.chdir(_original_cwd)
    
    def image_to_video(self, image_path, prompt, negative_prompt="", 
                       resolution="480p", num_frames=93, num_inference_steps=50,
                       guidance_scale=4.0, seed=42, use_distill=False,
                       progress_callback=None):
        """
        图片生成视频 - 真正的模型推理
        """
        timestamp = int(time.time())
        output_path = self.output_dir / f"i2v_{timestamp}.mp4"
        
        config = {
            "type": "image_to_video",
            "image_path": image_path,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "resolution": resolution,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "use_distill": use_distill,
            "output_path": str(output_path),
        }
        
        if progress_callback:
            progress_callback(0.05, "正在加载模型...")
        
        # 加载模型
        if not self._load_video_model(progress_callback):
            return None, {"error": "模型加载失败"}
        
        try:
            os.chdir(str(LONGCAT_DIR))
            
            from diffusers.utils import load_image
            
            if progress_callback:
                progress_callback(0.3, "加载输入图片...")
            
            # 加载图片
            image = load_image(image_path)
            target_size = image.size
            
            # 设置随机种子
            generator = torch.Generator(device='cuda')
            generator.manual_seed(int(seed))
            
            if progress_callback:
                progress_callback(0.4, "开始生成视频...")
            
            # 如果使用蒸馏模式
            if use_distill:
                cfg_step_lora_path = os.path.join(self.checkpoint_dir, 'lora/cfg_step_lora.safetensors')
                if os.path.exists(cfg_step_lora_path):
                    self.pipe.dit.load_lora(cfg_step_lora_path, 'cfg_step_lora')
                    self.pipe.dit.enable_loras(['cfg_step_lora'])
                    num_inference_steps = 16
                    guidance_scale = 1.0
            
            # 生成视频
            output = self.pipe.generate_i2v(
                image=image,
                prompt=prompt,
                negative_prompt=negative_prompt if not use_distill else "",
                resolution=resolution,
                num_frames=int(num_frames),
                num_inference_steps=int(num_inference_steps),
                guidance_scale=float(guidance_scale),
                generator=generator,
                use_distill=use_distill,
            )[0]
            
            if use_distill:
                self.pipe.dit.disable_all_loras()
            
            if progress_callback:
                progress_callback(0.9, "保存视频文件...")
            
            # 处理输出并保存
            output_frames = [(output[i] * 255).astype(np.uint8) for i in range(output.shape[0])]
            output_frames = [PIL.Image.fromarray(img) for img in output_frames]
            output_frames = [frame.resize(target_size, PIL.Image.BICUBIC) for frame in output_frames]
            
            self._save_video_from_frames(output_frames, str(output_path), fps=15)
            
            if progress_callback:
                progress_callback(1.0, "生成完成!")
            
            del output
            torch.cuda.empty_cache()
            
            config["success"] = True
            return str(output_path), config
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            config["error"] = str(e)
            return None, config
        finally:
            os.chdir(_original_cwd)

    
    def audio_to_video_single(self, audio_path, image_path=None, prompt="",
                              resolution="480p", num_frames=93, 
                              num_inference_steps=50, text_guidance_scale=4.0,
                              audio_guidance_scale=4.0, seed=42,
                              num_segments=1, stage_1="ai2v",
                              progress_callback=None):
        """
        单人音频驱动视频生成 (Avatar) - 配置生成版本
        注意：Avatar 模型需要单独的权重文件，这里先返回配置
        """
        timestamp = int(time.time())
        output_path = self.output_dir / f"avatar_single_{timestamp}.mp4"
        
        config = {
            "type": "audio_to_video_single",
            "audio_path": audio_path,
            "image_path": image_path,
            "prompt": prompt,
            "resolution": resolution,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "text_guidance_scale": text_guidance_scale,
            "audio_guidance_scale": audio_guidance_scale,
            "seed": seed,
            "num_segments": num_segments,
            "stage_1": stage_1,
            "output_path": str(output_path),
            "checkpoint_dir": self.avatar_checkpoint_dir
        }
        
        # 检查 Avatar 模型是否存在
        avatar_model_path = Path(self.avatar_checkpoint_dir)
        if not avatar_model_path.exists() or not any(avatar_model_path.iterdir()):
            config["error"] = "Avatar 模型权重未找到，请确保已下载 LongCat-Video-Avatar 模型"
            config["note"] = "请将模型放置到: " + self.avatar_checkpoint_dir
            return None, config
        
        # TODO: 实现 Avatar 模型的加载和推理
        # 目前 Avatar 功能需要额外的模型文件，暂时返回配置信息
        config["note"] = "Avatar 功能需要额外配置，请参考 LongCat-Video 文档"
        
        if progress_callback:
            progress_callback(1.0, "配置已生成")
        
        return None, config
    
    def audio_to_video_multi(self, audio_paths, image_path=None, prompt="",
                             resolution="480p", num_frames=93,
                             num_inference_steps=50, text_guidance_scale=4.0,
                             audio_guidance_scale=4.0, seed=42,
                             num_segments=1, progress_callback=None):
        """
        多人音频驱动视频生成 - 配置生成版本
        """
        timestamp = int(time.time())
        output_path = self.output_dir / f"avatar_multi_{timestamp}.mp4"
        
        config = {
            "type": "audio_to_video_multi",
            "audio_paths": audio_paths,
            "image_path": image_path,
            "prompt": prompt,
            "resolution": resolution,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "text_guidance_scale": text_guidance_scale,
            "audio_guidance_scale": audio_guidance_scale,
            "seed": seed,
            "num_segments": num_segments,
            "output_path": str(output_path),
            "checkpoint_dir": self.avatar_checkpoint_dir,
            "note": "多人 Avatar 功能需要额外配置"
        }
        
        if progress_callback:
            progress_callback(1.0, "配置已生成")
        
        return None, config
    
    def video_continuation(self, video_path, prompt, num_continuation_frames=93,
                          num_inference_steps=50, guidance_scale=4.0,
                          seed=42, progress_callback=None):
        """
        视频延续生成 - 配置生成版本
        """
        timestamp = int(time.time())
        output_path = self.output_dir / f"continuation_{timestamp}.mp4"
        
        config = {
            "type": "video_continuation",
            "video_path": video_path,
            "prompt": prompt,
            "num_continuation_frames": num_continuation_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "output_path": str(output_path),
            "checkpoint_dir": self.checkpoint_dir,
            "note": "视频延续功能开发中"
        }
        
        if progress_callback:
            progress_callback(1.0, "配置已生成")
        
        return None, config
    
    def _save_video(self, output, output_path, fps=15):
        """保存视频（从 numpy 数组）"""
        from torchvision.io import write_video
        
        output_tensor = torch.from_numpy(np.array(output))
        output_tensor = (output_tensor * 255).clamp(0, 255).to(torch.uint8)
        write_video(output_path, output_tensor, fps=fps, video_codec="libx264", options={"crf": "18"})
    
    def _save_video_from_frames(self, frames, output_path, fps=15):
        """保存视频（从 PIL Image 列表）"""
        from torchvision.io import write_video
        
        output_tensor = torch.from_numpy(np.array(frames))
        write_video(output_path, output_tensor, fps=fps, video_codec="libx264", options={"crf": "18"})
    
    def unload_model(self):
        """卸载所有模型释放显存"""
        self._unload_video_model()
        self._unload_avatar_model()
        print("[LongCat-Video] 所有模型已卸载")


# 创建全局实例
longcat_module = None

def get_longcat_module():
    """获取 LongCat 模块实例"""
    global longcat_module
    if longcat_module is None:
        longcat_module = LongCatVideoModule()
    return longcat_module

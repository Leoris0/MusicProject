"""
SongGeneration 模块
提供歌曲生成功能的后端接口 - 真正的模型推理版本
"""
import os
import sys
import json
import time
import torch
import torchaudio
import numpy as np
from pathlib import Path

# 添加 SongGeneration 项目路径
SONG_DIR = Path(__file__).parent.parent.parent / "SongGeneration"
sys.path.insert(0, str(SONG_DIR))

# 切换工作目录以便加载相对路径的资源
_original_cwd = os.getcwd()

# 可用的自动风格类型
AUTO_PROMPT_TYPES = [
    'Pop', 'R&B', 'Dance', 'Jazz', 'Folk', 'Rock', 
    'Chinese Style', 'Chinese Tradition', 'Metal', 
    'Reggae', 'Chinese Opera', 'Auto'
]

# 生成类型
GENERATION_TYPES = ['mixed', 'vocal', 'bgm', 'separate']


class SongGenerationModule:
    """SongGeneration 功能模块 - 真正的模型推理"""
    
    def __init__(self, ckpt_path=None):
        self.ckpt_base_path = ckpt_path or str(SONG_DIR / "ckpt")
        self.output_dir = Path(__file__).parent.parent / "outputs" / "songs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型相关
        self.model = None
        self.separator = None
        self.auto_prompt = None
        self.cfg = None
        self.max_duration = 160
        self.sample_rate = 48000
        self._model_loaded = False
        
        # 查找可用的模型
        self.available_models = self._find_available_models()
        
    def _find_available_models(self):
        """查找可用的歌曲生成模型"""
        models = []
        ckpt_path = Path(self.ckpt_base_path)
        if ckpt_path.exists():
            for item in ckpt_path.iterdir():
                if item.is_dir() and item.name.startswith("songgeneration"):
                    # 检查是否有必要的文件
                    if (item / "config.yaml").exists() and (item / "model.pt").exists():
                        models.append(item.name)
        return models
    
    def _load_model(self, model_name=None):
        """加载模型"""
        if self._model_loaded:
            return True
            
        try:
            # 切换到 SongGeneration 目录
            os.chdir(str(SONG_DIR))
            
            from omegaconf import OmegaConf
            from codeclm.models import builders, CodecLM
            from codeclm.trainer.codec_song_pl import CodecLM_PL
            
            # 注册 OmegaConf 解析器
            if not OmegaConf.has_resolver("eval"):
                OmegaConf.register_new_resolver("eval", lambda x: eval(x))
            if not OmegaConf.has_resolver("concat"):
                OmegaConf.register_new_resolver("concat", lambda *x: [xxx for xx in x for xxx in xx])
            if not OmegaConf.has_resolver("get_fname"):
                OmegaConf.register_new_resolver("get_fname", lambda: 'default')
            if not OmegaConf.has_resolver("load_yaml"):
                OmegaConf.register_new_resolver("load_yaml", lambda x: list(OmegaConf.load(x)))
            
            # 选择模型
            if model_name is None and self.available_models:
                model_name = self.available_models[0]
            
            if not model_name:
                raise ValueError("没有找到可用的模型")
            
            ckpt_path = Path(self.ckpt_base_path) / model_name
            cfg_path = ckpt_path / "config.yaml"
            pt_path = ckpt_path / "model.pt"
            
            print(f"[SongGeneration] 加载模型: {model_name}")
            print(f"[SongGeneration] 配置文件: {cfg_path}")
            
            # 加载配置
            self.cfg = OmegaConf.load(str(cfg_path))
            self.cfg.mode = 'inference'
            self.max_duration = self.cfg.max_dur
            self.sample_rate = self.cfg.get('sample_rate', 48000)
            
            # 加载模型
            torch.backends.cudnn.enabled = False
            model_light = CodecLM_PL(self.cfg, str(pt_path))
            model_light = model_light.eval().cuda()
            model_light.audiolm.cfg = self.cfg
            
            self.model = CodecLM(
                name="webui",
                lm=model_light.audiolm,
                audiotokenizer=model_light.audio_tokenizer,
                max_duration=self.max_duration,
                seperate_tokenizer=model_light.seperate_tokenizer,
            )
            
            # 加载音频分离器
            try:
                from third_party.demucs.models.pretrained import get_model_from_yaml
                dm_model_path = str(SONG_DIR / 'third_party/demucs/ckpt/htdemucs.pth')
                dm_config_path = str(SONG_DIR / 'third_party/demucs/ckpt/htdemucs.yaml')
                if os.path.exists(dm_model_path) and os.path.exists(dm_config_path):
                    demucs_model = get_model_from_yaml(dm_config_path, dm_model_path)
                    demucs_model.to('cuda')
                    demucs_model.eval()
                    self.separator = demucs_model
                    print("[SongGeneration] 音频分离器加载成功")
            except Exception as e:
                print(f"[SongGeneration] 音频分离器加载失败: {e}")
                self.separator = None
            
            # 加载自动风格提示
            auto_prompt_path = SONG_DIR / "tools" / "new_prompt.pt"
            if auto_prompt_path.exists():
                self.auto_prompt = torch.load(str(auto_prompt_path))
                print("[SongGeneration] 自动风格提示加载成功")
            
            self._model_loaded = True
            print("[SongGeneration] 模型加载完成!")
            return True
            
        except Exception as e:
            print(f"[SongGeneration] 模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            os.chdir(_original_cwd)

    
    def _set_generation_params(self, cfg_coef=1.5, temperature=0.9, top_k=50, top_p=0.0, max_duration=None):
        """设置生成参数"""
        if self.model is None:
            return
        
        duration = max_duration or self.max_duration
        self.model.set_generation_params(
            duration=duration,
            extend_stride=5,
            temperature=temperature,
            cfg_coef=cfg_coef,
            top_k=top_k,
            top_p=top_p,
            record_tokens=True,
            record_window=50
        )
    
    def generate_song(self, lyrics, description=None, prompt_audio_path=None,
                      auto_prompt_type=None, gen_type="mixed",
                      model_name=None, max_duration=160,
                      cfg_coef=1.5, temperature=0.9, top_k=50, top_p=0.0,
                      low_mem=False, progress_callback=None):
        """
        生成歌曲 - 真正的模型推理
        
        Args:
            lyrics: 歌词文本
            description: 音乐描述
            prompt_audio_path: 参考音频路径
            auto_prompt_type: 自动风格类型
            gen_type: 生成类型 (mixed/vocal/bgm/separate)
            model_name: 模型名称
            max_duration: 最大时长（秒）
            cfg_coef: CFG 系数
            temperature: 温度参数
            top_k: Top-K 采样
            top_p: Top-P 采样
            low_mem: 是否使用低显存模式
            progress_callback: 进度回调函数
        
        Returns:
            tuple: (生成音频的路径, 配置信息)
        """
        timestamp = int(time.time())
        output_filename = f"song_{timestamp}.wav"
        output_path = self.output_dir / output_filename
        
        # 构建配置信息
        config = {
            "type": "song_generation",
            "lyrics": lyrics,
            "description": description,
            "prompt_audio_path": prompt_audio_path,
            "auto_prompt_type": auto_prompt_type,
            "gen_type": gen_type,
            "model_name": model_name,
            "max_duration": max_duration,
            "cfg_coef": cfg_coef,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "output_path": str(output_path),
            "timestamp": timestamp
        }
        
        if progress_callback:
            progress_callback(0.1, "正在加载模型...")
        
        # 加载模型
        if not self._load_model(model_name):
            return None, {"error": "模型加载失败"}
        
        try:
            os.chdir(str(SONG_DIR))
            
            if progress_callback:
                progress_callback(0.2, "准备生成参数...")
            
            # 设置生成参数
            self._set_generation_params(cfg_coef, temperature, top_k, top_p, max_duration)
            
            # 准备输入
            pmt_wav = None
            vocal_wav = None
            bgm_wav = None
            melody_is_wav = True
            
            # 处理参考音频或自动风格
            if prompt_audio_path and os.path.exists(prompt_audio_path) and self.separator:
                if progress_callback:
                    progress_callback(0.3, "处理参考音频...")
                # 使用参考音频 - 需要分离
                pmt_wav, vocal_wav, bgm_wav = self._separate_audio(prompt_audio_path)
                melody_is_wav = True
            elif auto_prompt_type and self.auto_prompt and auto_prompt_type in self.auto_prompt:
                if progress_callback:
                    progress_callback(0.3, "加载风格模板...")
                # 使用自动风格
                prompt_token = self.auto_prompt[auto_prompt_type][
                    np.random.randint(0, len(self.auto_prompt[auto_prompt_type]))
                ]
                pmt_wav = prompt_token[:, [0], :]
                vocal_wav = prompt_token[:, [1], :]
                bgm_wav = prompt_token[:, [2], :]
                melody_is_wav = False
            
            if progress_callback:
                progress_callback(0.4, "开始生成音乐...")
            
            # 构建生成输入
            generate_inp = {
                'lyrics': [lyrics.replace("  ", " ")],
                'descriptions': [description] if description else [None],
                'melody_wavs': pmt_wav,
                'vocal_wavs': vocal_wav,
                'bgm_wavs': bgm_wav,
                'melody_is_wav': melody_is_wav,
            }
            
            # 生成 tokens
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                with torch.no_grad():
                    tokens = self.model.generate(**generate_inp, return_tokens=True)
            
            if progress_callback:
                progress_callback(0.7, "生成音频波形...")
            
            # 生成音频
            with torch.no_grad():
                if melody_is_wav and pmt_wav is not None:
                    wav_output = self.model.generate_audio(
                        tokens, pmt_wav, vocal_wav, bgm_wav, 
                        chunked=True, gen_type=gen_type
                    )
                else:
                    wav_output = self.model.generate_audio(
                        tokens, chunked=True, gen_type=gen_type
                    )
            
            if progress_callback:
                progress_callback(0.9, "保存音频文件...")
            
            # 保存音频
            torchaudio.save(
                str(output_path), 
                wav_output[0].cpu().float(), 
                self.sample_rate
            )
            
            # 如果是 separate 模式，还要保存人声和伴奏
            if gen_type == 'separate':
                with torch.no_grad():
                    wav_vocal = self.model.generate_audio(tokens, chunked=True, gen_type='vocal')
                    wav_bgm = self.model.generate_audio(tokens, chunked=True, gen_type='bgm')
                
                vocal_path = self.output_dir / f"song_{timestamp}_vocal.wav"
                bgm_path = self.output_dir / f"song_{timestamp}_bgm.wav"
                
                torchaudio.save(str(vocal_path), wav_vocal[0].cpu().float(), self.sample_rate)
                torchaudio.save(str(bgm_path), wav_bgm[0].cpu().float(), self.sample_rate)
                
                config["vocal_path"] = str(vocal_path)
                config["bgm_path"] = str(bgm_path)
            
            if progress_callback:
                progress_callback(1.0, "生成完成!")
            
            # 清理显存
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
    
    def _separate_audio(self, audio_path):
        """分离音频为人声和伴奏"""
        if self.separator is None:
            return None, None, None
        
        try:
            # 加载音频
            audio, sr = torchaudio.load(audio_path)
            if sr != 48000:
                audio = torchaudio.functional.resample(audio, sr, 48000)
            
            # 限制长度
            max_samples = 48000 * 10  # 10秒
            if audio.shape[-1] > max_samples:
                audio = audio[..., :max_samples]
            
            # 分离
            with torch.no_grad():
                # 这里简化处理，实际可能需要调用 separator 的 separate 方法
                full_audio = audio
                # 暂时返回 None，让模型使用默认处理
                return full_audio, None, None
                
        except Exception as e:
            print(f"[SongGeneration] 音频分离失败: {e}")
            return None, None, None

    
    def unload_model(self):
        """卸载模型释放显存"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.separator is not None:
            del self.separator
            self.separator = None
        self._model_loaded = False
        torch.cuda.empty_cache()
        print("[SongGeneration] 模型已卸载")
    
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
        """
        格式化歌词为模型所需格式
        
        Args:
            raw_lyrics: 原始歌词（每段以结构标签开头，空行分隔）
        
        Returns:
            str: 格式化后的歌词
        """
        # 替换完整标签为简短标签
        lyrics = raw_lyrics.replace("[intro]", "[intro-short]")
        lyrics = lyrics.replace("[inst]", "[inst-short]")
        lyrics = lyrics.replace("[outro]", "[outro-short]")
        
        # 按段落分割
        paragraphs = [p.strip() for p in lyrics.strip().split('\n\n') if p.strip()]
        
        formatted_parts = []
        for para in paragraphs:
            lines = para.splitlines()
            if not lines:
                continue
            
            struct_tag = lines[0].strip().lower()
            
            # 检查是否是纯器乐段落
            instrumental_tags = ['[intro-short]', '[intro-medium]', '[inst-short]', 
                               '[inst-medium]', '[outro-short]', '[outro-medium]']
            
            if struct_tag in instrumental_tags:
                formatted_parts.append(struct_tag)
            else:
                # 包含歌词的段落
                lyrics_lines = [line.strip() for line in lines[1:] if line.strip()]
                if lyrics_lines:
                    lyrics_text = '.'.join(lyrics_lines)
                    formatted_parts.append(f"{struct_tag} {lyrics_text}")
                else:
                    formatted_parts.append(struct_tag)
        
        return " ; ".join(formatted_parts)


# 创建全局实例
song_module = None

def get_song_module():
    """获取 SongGeneration 模块实例"""
    global song_module
    if song_module is None:
        song_module = SongGenerationModule()
    return song_module

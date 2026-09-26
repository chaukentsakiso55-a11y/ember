"""On-demand fully local voice turn for EMBER.

After the optional Whisper and Kokoro models are installed/cached, this path does
not use Gemini or any cloud service: microphone -> Whisper -> local LLM -> Kokoro
-> speakers. It is intentionally push-to-talk style rather than always listening.
"""
from __future__ import annotations
import json, threading
from pathlib import Path
import numpy as np
import sounddevice as sd
from core.stt import WhisperSTT, VoskSTT
from core.tts import create_tts_player
from core.local_mode import ask_local
from core.feature_hub import audit, get as feature_get, kill_switch_enabled
from memory.config_manager import CONFIG_FILE

_lock=threading.Lock(); _stt=None; _tts=None

def _cfg():
    try:return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    except Exception:return {}

def _get_stt():
    global _stt
    if _stt is not None:return _stt
    c=_cfg(); eng=str(c.get('stt_engine','whisper')).lower()
    if eng=='vosk':_stt=VoskSTT(c.get('vosk_model_path'),c.get('language','en-us'))
    else:_stt=WhisperSTT(c.get('whisper_model','base'),c.get('language'))
    return _stt

def _get_tts():
    global _tts
    if _tts is not None:return _tts
    c=_cfg(); c=dict(c); c['tts_engine']=c.get('tts_engine') or 'kokoro'
    if str(c.get('tts_engine')).lower()!='kokoro': c['tts_engine']='kokoro'
    _tts=create_tts_player(c);return _tts

def status()->dict:
    c=_cfg()
    return {'stt_engine':c.get('stt_engine','whisper'),'whisper_model':c.get('whisper_model','base'),
            'tts_engine':'kokoro','llm_mode':feature_get('model_mode','auto'),
            'note':'First use may need internet to download optional Whisper/Kokoro models; cached models then run offline.'}

def run_once(duration:float=5.0, sample_rate:int=16000)->dict:
    if kill_switch_enabled():
        return {'heard':'','answer':'','error':'EMBER kill switch is active. Microphone access is blocked.'}
    duration=max(1.5,min(20.0,float(duration)))
    with _lock:
        if kill_switch_enabled():
            return {'heard':'','answer':'','error':'EMBER kill switch is active. Microphone access is blocked.'}
        audit('audio','offline_voice',f'record {duration:.1f}s')
        samples=sd.rec(int(duration*sample_rate),samplerate=sample_rate,channels=1,dtype='float32')
        sd.wait(); audio=np.asarray(samples[:,0],dtype=np.float32)
        stt=_get_stt()
        if hasattr(stt,'transcribe'): text=stt.transcribe(audio)
        else:
            raw=(np.clip(audio,-1,1)*32767).astype(np.int16).tobytes(); text,_=stt.process_chunk(raw)
        text=str(text or '').strip()
        if not text:return {'heard':'','answer':'','error':'No speech was transcribed.'}
        result=ask_local(text,history=None); answer=str(result.get('content') or '').strip()
        if answer:_get_tts().speak(answer)
        return {'heard':text,'answer':answer}

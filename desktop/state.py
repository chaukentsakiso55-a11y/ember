from __future__ import annotations
import copy, json, os, sys, threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('EMBER_DATA_DIR') or (Path(os.environ.get('LOCALAPPDATA', Path.home()/'.local/share'))/'Ember'))
DEFAULTS = dict(default_tab='AI Chat', theme='Cyberpunk', accent='#00d9ff', animations=True, glass=True,
    particles=True, avatar='Reference Female', visual='Avatar', history=False, memory=False,
    tray=True, minimize_tray=True, startup=False, start_minimized=False, notifications=True,
    profile='Balanced', provider='ollama', fallback=True, fallback_provider='openai', temperature=0.7, max_tokens=2048, fastest_model=False, capable_model=False, conversation_mode='Standard', auto_summarize=True, enable_local_models=True, model_path='', gpu_acceleration=False, auto_download_models=False, code_assistant=True, web_search=True, vision_analysis=True, image_generation=True, video_generation=True,
    context=True, style='Friendly', personality='Friendly', humor=True, knowledge_mode='Expanded', language='English', tts=True, tts_engine='Gemini TTS',
    voice='Aoede', whisper_model='base', stt=True, camera=False, automation=False,
    background='', debug=False, clear_exit=False, news_url='https://feeds.bbci.co.uk/news/world/rss.xml',
    browser='System default', file_history=False, plugin_enabled={}, integrations={},
    update_url='', cpu_limit=70, ram_limit=4096, gpu_limit=50, auto_memory=True,detailed_logs=False,console=True,local_core=True,background_limit=True,local_settings=True,quick_actions=True,animated_avatar=True,background_mode="Static Background",sound_effects=False,run_background=True,graceful_shutdown=True,session_save=True,allow_experimental=False,plugin_development=True,response_length="Medium",top_p=.9,local_engine="Ollama",local_model="",auto_updates=False,weather_alerts=False,news_alerts=False,flight_alerts=False,hardware=False,close_idle=False,self_improve=False)

def read_json(path, default):
    try:return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError):return copy.deepcopy(default)

def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(temp,path)

class Store(QObject):
    changed=pyqtSignal()
    def __init__(self):
        super().__init__();DATA.mkdir(parents=True,exist_ok=True)
        self.values={**copy.deepcopy(DEFAULTS),**read_json(DATA/'settings.json',{})}
        if self.values.get('voice')=='Aoede' and self.values.get('tts_engine')=='Edge TTS':self.values['tts_engine']='Gemini TTS'
        self.providers=read_json(DATA/'providers.json',read_json(ROOT/'config/providers.json',{}))
        self.messages=read_json(DATA/'conversation.json',[]) if self.values['history'] else []
        self.memories=read_json(DATA/'memory.json',[])
    def save(self, values=None):
        if values is not None:self.values.update(values)
        write_json(DATA/'settings.json',self.values);write_json(DATA/'providers.json',self.providers)
        if self.values['history']:write_json(DATA/'conversation.json',self.messages)
        else:(DATA/'conversation.json').unlink(missing_ok=True)
        self.changed.emit()
    def get(self,key):return self.values.get(key)
    def remember(self,text):
        self.memories.append(text);write_json(DATA/'memory.json',self.memories)
    def clear(self):
        self.messages=[];self.memories=[]
        for n in ['conversation.json','memory.json','file-history.json']:(DATA/n).unlink(missing_ok=True)
        self.changed.emit()

class Vault:
    @staticmethod
    def get(pid):
        import keyring
        try:return json.loads(keyring.get_password('Ember',pid) or '[]')
        except Exception:return []
    @staticmethod
    def set(pid,keys):
        import keyring
        backend=keyring.get_keyring()
        if backend.priority<=0 or 'plaintext' in type(backend).__name__.lower():
            raise RuntimeError('No secure credential store is available. Configure Windows Credential Manager or use environment variables.')
        keyring.set_password('Ember',pid,json.dumps(keys))

from __future__ import annotations
from memory.config_manager import AVAILABLE_VOICES,get_voice,save_voice
from core.feature_hub import set_value,get
PLUGIN={"permissions":["audio.settings"],"name":"voice_profiles","description":"Manage EMBER voice profiles, Gemini Live voice choice, whisper mode and speaking style preferences.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"status, set_live_voice, whisper, profile"},"value":{"type":"STRING"},"enabled":{"type":"BOOLEAN"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=p.get('action')
    if a=='status':return f"Live voice: {get_voice()}; available: {AVAILABLE_VOICES}; profile: {get('voice_profile','default')}; whisper: {get('whisper_mode',False)}"
    if a=='set_live_voice':save_voice(p.get('value',''));return f"Voice set to {get_voice()}; reconnect the Live session to apply it."
    if a=='whisper':set_value('whisper_mode',bool(p.get('enabled')));return f"Whisper mode {'on' if p.get('enabled') else 'off'}."
    if a=='profile':set_value('voice_profile',p.get('value') or 'default');return f"Voice profile set to {p.get('value') or 'default'}."
    return 'Unknown voice-profile action.'

"""Explicit visual-memory controls for EMBER.

Only saves a screen capture or a user-chosen image file when explicitly invoked.
Nothing is captured in the background.
"""
from __future__ import annotations
from pathlib import Path
from actions.screen_processor import _capture_screen
from core.feature_hub import save_vision_memory, list_vision_memory, delete_vision_memory

PLUGIN={"permissions":["screen.capture","files.read","vision_memory.write"],
"name":"vision_memory","description":"Explicitly save the current screen or a chosen image into EMBER vision memory, list saved visuals, or delete one. It never captures in the background.",
"parameters":{"type":"OBJECT","properties":{
"action":{"type":"STRING","description":"capture_screen, save_file, list, delete"},
"label":{"type":"STRING"},"path":{"type":"STRING"},"name":{"type":"STRING"}},"required":["action"]}}

def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower()
    if a=='capture_screen':
        data,mime=_capture_screen(); ext='.jpg' if 'jpeg' in mime else '.png'
        path=save_vision_memory(p.get('label') or 'screen',data,ext)
        return f"Saved visual memory: {path}"
    if a=='save_file':
        src=Path(str(p.get('path') or '')).expanduser().resolve()
        if not src.is_file(): return 'Image file not found.'
        if src.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.bmp'}: return 'Choose an image file.'
        path=save_vision_memory(p.get('label') or src.stem,src.read_bytes(),src.suffix.lower())
        return f"Saved visual memory: {path}"
    if a=='list':
        data=list_vision_memory(); text='\n'.join(data) or 'No saved visual memories.'
        if player and hasattr(player,'show_content'):player.show_content('VISION MEMORY',text)
        return text
    if a=='delete': return 'Deleted.' if delete_vision_memory(p.get('name') or '') else 'Visual memory not found.'
    return 'Use capture_screen, save_file, list, or delete.'

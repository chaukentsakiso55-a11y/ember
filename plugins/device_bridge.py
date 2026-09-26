from __future__ import annotations
import json
from pathlib import Path
from core.feature_hub import audit, CONFIG_DIR
CLIP=CONFIG_DIR/'cross_device_clipboard.json'

def _server():
    try:
        from dashboard import server as ds
        return getattr(ds,'ACTIVE_SERVER',None)
    except Exception:return None

PLUGIN={"permissions":["devices.manage", "clipboard.local"],"name":"device_bridge","description":"Manage EMBER's currently paired companion devices and synchronize clipboard text between the dashboard and this computer. It never discovers unknown devices.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"list, revoke, label, clipboard_set, clipboard_get"},"device_id":{"type":"STRING"},"name":{"type":"STRING"},"text":{"type":"STRING"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower();did=str(p.get('device_id') or '').strip(); srv=_server()
    if a=='list':
        if not srv:return 'Remote dashboard is not running.'
        return str([{'id':tok[:8],'label':rec.get('label','Phone'),'paired_at':rec.get('paired_at')} for tok,rec in srv._device_sessions.items()])
    if a in {'revoke','label'}:
        if not srv:return 'Remote dashboard is not running.'
        matches=[tok for tok in srv._device_sessions if tok==did or tok.startswith(did)]
        if len(matches)!=1:return 'Device ID did not uniquely match a paired device.'
        tok=matches[0]
        if a=='revoke':srv._device_sessions.pop(tok,None);audit('device','revoke',did);return 'Device revoked.'
        label=str(p.get('name') or '').strip()[:60]
        if not label:return 'A device name is required.'
        srv._device_sessions[tok]['label']=label;return f'Device renamed to {label}.'
    if a=='clipboard_set':
        text=str(p.get('text') or '')[:20000];CLIP.parent.mkdir(parents=True,exist_ok=True);CLIP.write_text(json.dumps({'text':text},ensure_ascii=False,indent=2),encoding='utf-8')
        try:
            import pyperclip;pyperclip.copy(text)
        except Exception:pass
        audit('device','clipboard',f'{len(text)} chars');return 'Cross-device clipboard updated.'
    if a=='clipboard_get':
        try:
            import pyperclip; live=str(pyperclip.paste() or '')
            if live:return live[:20000]
        except Exception:pass
        try:return json.loads(CLIP.read_text(encoding='utf-8')).get('text','') or 'Cross-device clipboard is empty.'
        except Exception:return 'Cross-device clipboard is empty.'
    return 'Unknown device-bridge action.'

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parent.parent;PATH=BASE/'config'/'notifications.json'
def _load():
    try:return json.loads(PATH.read_text(encoding='utf-8'))
    except Exception:return []
def _save(x):PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(x[-300:],indent=2,ensure_ascii=False),encoding='utf-8')
def add(title,text,priority='normal'):
    x=_load();x.append({'title':str(title)[:120],'text':str(text)[:1000],'priority':priority,'ts':datetime.now().isoformat(timespec='seconds'),'read':False});_save(x);return x[-1]
def list_items(unread=False):return [n for n in _load() if not unread or not n.get('read')]
def mark_all_read():
    x=_load()
    for n in x:n['read']=True
    _save(x);return len(x)
def clear():_save([])

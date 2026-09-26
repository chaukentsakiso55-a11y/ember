"""Local workflow recorder/builder for EMBER.

Workflows are transparent JSON. Recording stores tool name + arguments after the
user explicitly starts recording. Replays are dispatched by main.py through the
same registered actions/plugins (so there is no arbitrary shell execution here).
"""
from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parent.parent
PATH=BASE/'config'/'automations.json'

def _load():
    try:
        d=json.loads(PATH.read_text(encoding='utf-8'))
        return d if isinstance(d,dict) else {'workflows':{}}
    except Exception:return {'workflows':{}}
def _save(d):PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def _slug(s): return re.sub(r'[^a-z0-9_-]+','-',str(s).casefold()).strip('-')[:60] or 'workflow'

def create(name:str, trigger:str, steps:list):
    d=_load(); key=_slug(name)
    norm=[]
    for x in (steps or [])[:50]:
        if isinstance(x,dict) and x.get('tool'):
            norm.append({'tool':str(x.get('tool'))[:64],'args':x.get('args') if isinstance(x.get('args'),dict) else {}})
        else:norm.append({'note':str(x)[:500]})
    d.setdefault('workflows',{})[key]={'id':key,'name':name,'trigger':trigger or 'manual','steps':norm,'enabled':True,'created':datetime.now().isoformat(timespec='seconds')}
    _save(d);return d['workflows'][key]
def list_all(): return list(_load().get('workflows',{}).values())
def get(name:str):
    d=_load().get('workflows',{}); key=_slug(name)
    if key in d:return d[key]
    matches=[v for k,v in d.items() if key in k or key in str(v.get('name','')).casefold()]
    return matches[0] if len(matches)==1 else None
def delete(name:str):
    d=_load(); k=_slug(name);ok=d.get('workflows',{}).pop(k,None) is not None;_save(d);return ok

def start_recording():
    d=_load();d['recording']={'started':datetime.now().isoformat(timespec='seconds'),'steps':[]};_save(d);return d['recording']
def is_recording()->bool:return isinstance(_load().get('recording'),dict)
def record_step(text:str):
    d=_load(); rec=d.setdefault('recording',{'started':datetime.now().isoformat(timespec='seconds'),'steps':[]});rec.setdefault('steps',[]).append({'note':str(text)[:500]});_save(d);return len(rec['steps'])
def record_tool(tool:str,args:dict):
    d=_load();rec=d.get('recording')
    if not isinstance(rec,dict):return 0
    rec.setdefault('steps',[]).append({'tool':str(tool)[:64],'args':dict(args or {})});_save(d);return len(rec['steps'])
def finish_recording(name:str,trigger:str='manual'):
    d=_load();rec=d.pop('recording',None);_save(d)
    steps=(rec or {}).get('steps',[]) if isinstance(rec,dict) else []
    return create(name,trigger,steps)
def cancel_recording():
    d=_load();had=d.pop('recording',None) is not None;_save(d);return had
def recording(): return _load().get('recording') or {}

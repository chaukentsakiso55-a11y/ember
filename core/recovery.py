"""Crash-recovery journal for EMBER tool tasks, including nested workflow steps."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parent.parent; PATH=BASE/'config'/'recovery_journal.json'
def _load():
    try:
        d=json.loads(PATH.read_text(encoding='utf-8'));return d if isinstance(d,dict) else {'events':[]}
    except Exception:return {'events':[]}
def _save(d):PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def begin(tool,args):
    d=_load();rec={'id':datetime.now().strftime('%Y%m%d%H%M%S%f'),'tool':tool,'args':args,'started':datetime.now().isoformat(timespec='seconds'),'state':'running'}
    stack=d.get('current_stack');stack=list(stack) if isinstance(stack,list) else []
    # Migrate an older single current record if present.
    old=d.get('current')
    if old and not stack and isinstance(old,dict):stack=[old]
    stack.append(rec);d['current_stack']=stack;d['current']=rec;d.setdefault('events',[]).append(rec);d['events']=d['events'][-300:];_save(d);return rec['id']
def finish(tool,result=''):
    d=_load();stack=d.get('current_stack');stack=list(stack) if isinstance(stack,list) else ([] if not d.get('current') else [d.get('current')])
    idx=next((i for i in range(len(stack)-1,-1,-1) if stack[i].get('tool')==tool),None)
    if idx is None:return
    cur=stack.pop(idx);cur['state']='done';cur['finished']=datetime.now().isoformat(timespec='seconds');cur['result']=str(result)[:500]
    for r in reversed(d.get('events',[])):
        if r.get('id')==cur.get('id'):r.update(cur);break
    d['current_stack']=stack
    if stack:d['current']=stack[-1]
    else:d.pop('current',None)
    _save(d)
def last_incomplete():
    d=_load();return d.get('current')
def history(limit=20):return _load().get('events',[])[-max(1,min(100,int(limit))):]

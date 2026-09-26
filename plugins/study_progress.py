"""Workspace-scoped study progress and weak-topic tracking."""
from __future__ import annotations
import json
from datetime import datetime
from core.feature_hub import workspace_path, temporary_memory_enabled
PLUGIN={"permissions":["study.local","workspace.write"],"name":"study_progress","description":"Track study quiz results in the active workspace and identify weak topics from recorded scores.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"record, progress, weak_topics, reset"},"subject":{"type":"STRING"},"topic":{"type":"STRING"},"score":{"type":"NUMBER"},"total":{"type":"NUMBER"}},"required":["action"]}}
def _path():return workspace_path()/'study_progress.json'
def _load():
    try:return json.loads(_path().read_text(encoding='utf-8'))
    except Exception:return []
def _save(x):_path().write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower();rows=_load()
    if a=='record':
        if temporary_memory_enabled():return 'Temporary memory is on; study progress was not saved.'
        total=float(p.get('total') or 0);score=float(p.get('score') or 0)
        if total<=0:return 'total must be greater than zero.'
        rows.append({'subject':p.get('subject') or 'General','topic':p.get('topic') or 'General','score':score,'total':total,'pct':round(score/total*100,1),'ts':datetime.now().isoformat(timespec='seconds')});_save(rows);return str(rows[-1])
    if a=='reset':
        if temporary_memory_enabled():return 'Temporary memory is on.'
        _save([]);return 'Study progress reset.'
    stats={}
    for r in rows:
        k=f"{r.get('subject','General')} · {r.get('topic','General')}";stats.setdefault(k,[]).append(float(r.get('pct',0)))
    avg={k:round(sum(v)/len(v),1) for k,v in stats.items()}
    if a=='weak_topics':data=dict(sorted(((k,v) for k,v in avg.items() if v<70),key=lambda x:x[1]))
    else:data=dict(sorted(avg.items(),key=lambda x:x[0]))
    text='\n'.join(f'{k}: {v}%' for k,v in data.items()) or 'No study results recorded yet.'
    if player and hasattr(player,'show_content'):player.show_content('WEAK TOPICS' if a=='weak_topics' else 'STUDY PROGRESS',text)
    return text

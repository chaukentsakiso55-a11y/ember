from __future__ import annotations
import subprocess
from pathlib import Path
from datetime import datetime
from core.feature_hub import active_workspace_meta

def status(path:str='')->dict:
    chosen=str(path or active_workspace_meta().get('project_path') or '').strip()
    p=Path(chosen or '.').expanduser().resolve()
    out={'path':str(p),'exists':p.exists(),'checked':datetime.now().isoformat(timespec='seconds')}
    if not p.is_dir():return out
    try:
        r=subprocess.run(['git','status','--short','--branch'],cwd=p,text=True,capture_output=True,timeout=10)
        out['git']=r.stdout.strip()[:6000]
    except Exception as e:out['git_error']=str(e)
    artifacts=[]
    for rel in ('build','dist','app/build/outputs','reports'):
        q=p/rel
        if q.exists():
            latest=max((f.stat().st_mtime for f in q.rglob('*') if f.is_file()),default=q.stat().st_mtime)
            artifacts.append({'path':str(q),'latest_modified':datetime.fromtimestamp(latest).isoformat(timespec='seconds')})
    if artifacts:out['artifacts']=artifacts
    try:
        candidates=[f for f in p.rglob('*') if f.is_file() and '.git' not in f.parts and 'node_modules' not in f.parts]
        recent=sorted(candidates,key=lambda f:f.stat().st_mtime,reverse=True)[:8]
        out['recent_files']=[{'path':str(f.relative_to(p)),'modified':datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec='seconds')} for f in recent]
    except Exception:pass
    return out

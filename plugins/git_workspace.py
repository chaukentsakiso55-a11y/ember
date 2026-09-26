from __future__ import annotations
import subprocess
from pathlib import Path
from core.feature_hub import active_workspace_meta
PLUGIN={"permissions":["git.read", "git.commit", "project.test"],"name":"git_workspace","description":"Coding workspace tools for an authorized local project: inspect tree/status/diff/branches/log, search source text, run the project's standard test task, or commit already-tracked changes when explicitly requested.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"tree, status, diff, branches, log, search, test, commit"},"path":{"type":"STRING","description":"Project path; defaults to active workspace project_path."},"message":{"type":"STRING"},"query":{"type":"STRING"}},"required":["action"]}}
def _path(raw=''):
    chosen=str(raw or active_workspace_meta().get('project_path') or '').strip()
    return Path(chosen or '.').expanduser().resolve()
def _git(path,*args):
    p=_path(path)
    if not (p/'.git').exists(): return 'That folder is not a Git repository.'
    r=subprocess.run(['git',*args],cwd=p,text=True,capture_output=True,timeout=30)
    return (r.stdout+r.stderr).strip()[:12000]
def _tree(path):
    p=_path(path)
    if not p.is_dir(): return 'Project folder not found.'
    rows=[]
    for q in sorted(p.rglob('*')):
        try: rel=q.relative_to(p)
        except Exception: continue
        if any(part in {'.git','.gradle','node_modules','build','dist','__pycache__','.venv','venv'} for part in rel.parts): continue
        if len(rel.parts)>4: continue
        rows.append(('DIR ' if q.is_dir() else 'FILE ')+str(rel))
        if len(rows)>=220: break
    return '\n'.join(rows)
def _search(path,query):
    p=_path(path); q=str(query or '').casefold()
    if not q:return 'query required.'
    hits=[]
    for f in p.rglob('*'):
        if not f.is_file() or f.stat().st_size>1_000_000 or any(x in f.parts for x in ('.git','node_modules','build','.gradle')):continue
        try:
            for i,line in enumerate(f.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
                if q in line.casefold():hits.append(f'{f.relative_to(p)}:{i}: {line[:240]}')
                if len(hits)>=100:return '\n'.join(hits)
        except Exception:pass
    return '\n'.join(hits) or 'No matches.'
def _test(path):
    p=_path(path)
    if (p/'gradlew').exists() or (p/'gradlew.bat').exists(): cmd=[str(p/('gradlew.bat' if (p/'gradlew.bat').exists() else 'gradlew')),'test']
    elif (p/'package.json').exists(): cmd=['npm','test','--','--runInBand']
    elif (p/'pyproject.toml').exists() or (p/'pytest.ini').exists() or (p/'tests').exists(): cmd=['python','-m','pytest','-q']
    else:return 'No standard Gradle, npm, or pytest test entry point was detected.'
    try:
        r=subprocess.run(cmd,cwd=p,text=True,capture_output=True,timeout=180)
        return f'exit={r.returncode}\n'+(r.stdout+r.stderr)[-12000:]
    except subprocess.TimeoutExpired:return 'Tests exceeded the 180-second limit.'
    except Exception as e:return f'Test launch failed: {e}'
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower(); path=p.get('path','')
    if a=='tree':return _tree(path)
    if a=='status': return _git(path,'status','--short','--branch')
    if a=='diff': return _git(path,'diff','--stat')+'\n'+_git(path,'diff')
    if a=='branches': return _git(path,'branch','-a')
    if a=='log': return _git(path,'log','--oneline','-n','15')
    if a=='search':return _search(path,p.get('query',''))
    if a=='test':return _test(path)
    if a=='commit':
        msg=str(p.get('message') or '').strip()
        if not msg:return 'A commit message is required.'
        return _git(path,'commit','-am',msg)
    return 'Use tree, status, diff, branches, log, search, test, or commit.'

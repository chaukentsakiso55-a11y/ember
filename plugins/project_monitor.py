from __future__ import annotations
from core.project_monitor import status
PLUGIN={"permissions":["files.read","git.read"],"name":"project_monitor","description":"Check the active workspace project (or an explicitly supplied project folder) for Git changes, recent files and common build/output folders; usable from desktop or phone dashboard.","parameters":{"type":"OBJECT","properties":{"path":{"type":"STRING","description":"Optional; defaults to active workspace project path."}}},"behavior":"NON_BLOCKING","scheduling":"SILENT"}
def run(p,player=None,session_memory=None):return str(status(p.get('path','')))

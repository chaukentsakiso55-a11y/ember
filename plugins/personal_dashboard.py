from __future__ import annotations
import json
from core.notifications import add,list_items,mark_all_read,clear
from core.feature_hub import system_summary,list_workspaces,list_vision_memory,active_workspace_meta,workspace_path
from core.automation_engine import list_all
from core.model_manager import status as model_status

PLUGIN={"permissions":["notifications.local","privacy.read","workspace.read"],"name":"personal_dashboard","description":"EMBER personal dashboard widgets: notifications, daily briefing, workspace/project/model status, open tasks, workflows and saved vision-memory list.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"briefing, notifications, notify, read_notifications, clear_notifications, vision_memory, status"},"title":{"type":"STRING"},"text":{"type":"STRING"},"priority":{"type":"STRING"}},"required":["action"]}}

def _count_tasks():
    try:
        items=json.loads((workspace_path()/'tasks.json').read_text(encoding='utf-8'))
        return sum(1 for x in items if not x.get('done'))
    except Exception:return 0

def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower()
    if a=='notify':return str(add(p.get('title','EMBER'),p.get('text',''),p.get('priority','normal')))
    if a=='notifications':
        data=list_items(); text='\n'.join(f"[{x.get('priority','normal')}] {x.get('title')}: {x.get('text')}" for x in data) or 'No notifications.'
        if player and hasattr(player,'show_content'):player.show_content('NOTIFICATION CENTER',text)
        return text
    if a=='read_notifications':return f"Marked {mark_all_read()} notifications read."
    if a=='clear_notifications':clear();return 'Notifications cleared.'
    if a=='vision_memory':
        text='\n'.join(list_vision_memory()) or 'No saved visual memories.'
        if player and hasattr(player,'show_content'):player.show_content('VISION MEMORY',text)
        return text
    if a in {'briefing','status'}:
        st=system_summary(); meta=active_workspace_meta(); ms=model_status()
        out=(f"EMBER {'DAILY BRIEF' if a=='briefing' else 'DASHBOARD'}\n"
             f"Model route: {st['model_mode']} · Local: {ms.get('provider')}/{ms.get('model')} ({'online' if ms.get('reachable') else 'offline'})\n"
             f"Workspace: {st['workspace']}\nProject: {meta.get('project_path') or 'not linked'}\n"
             f"Open tasks: {_count_tasks()}\nUnread notifications: {len(list_items(True))}\n"
             f"Workspaces: {len(list_workspaces())}\nAutomations: {len(list_all())}\nVision memories: {len(list_vision_memory())}\n"
             f"Performance: {st['performance_profile']}\nKill switch: {'ON' if st['kill_switch'] else 'OFF'}")
        if player and hasattr(player,'show_content'):player.show_content('DAILY BRIEF' if a=='briefing' else 'EMBER DASHBOARD',out)
        return out
    return 'Unknown dashboard action.'

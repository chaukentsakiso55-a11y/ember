from __future__ import annotations
from core.agent_supervisor import choose, plan, consult
PLUGIN={"permissions":["planning.local","models.local"],"name":"agent_supervisor","description":"Route a complex request to EMBER's research, coding, study, file, vision and planning specialists; show a transparent plan, or run a real local multi-agent consultation when a local model is configured.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"choose, plan, or consult"},"task":{"type":"STRING"},"max_agents":{"type":"INTEGER"}},"required":["task"]},"behavior":"NON_BLOCKING","scheduling":"WHEN_IDLE"}
def run(p,player=None,session_memory=None):
    action=str(p.get('action') or 'plan').lower()
    if action=='choose': data={'agents':choose(p.get('task',''))}
    elif action=='consult': data=consult(p.get('task',''),p.get('max_agents') or 3)
    else:data=plan(p.get('task',''))
    text=(data.get('synthesis') or '\n'.join(data.get('steps',[])) or str(data))
    if player and hasattr(player,'show_content'):player.show_content('AGENT PLAN' if action!='consult' else 'MULTI-AGENT RESULT',text)
    return str(data)

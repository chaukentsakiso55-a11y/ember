from __future__ import annotations
from core.recovery import last_incomplete,history
PLUGIN={"permissions":["recovery.read"],"name":"recovery_manager","description":"Inspect EMBER's crash-recovery task journal and show the last incomplete action after a crash.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"last or history"},"limit":{"type":"INTEGER"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    data=last_incomplete() if p.get('action')=='last' else history(p.get('limit') or 20)
    text=str(data or 'No incomplete task recorded.')
    if player and hasattr(player,'show_content'):player.show_content('RECOVERY',text)
    return text

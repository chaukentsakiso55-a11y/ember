from __future__ import annotations
from core import undo
PLUGIN={"permissions":["undo.local"],"name":"undo_history","description":"Show EMBER's reversible-action history or undo the most recent reversible change.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"list or undo"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    if str(p.get('action','list')).lower()=='undo': return undo.undo_last()
    items=undo.history(); text='\n'.join(f"{i+1}. {x}" for i,x in enumerate(items)) or 'Nothing reversible is in the undo history.'
    if player and hasattr(player,'show_content'):player.show_content('UNDO HISTORY',text)
    return text

from __future__ import annotations
from core.feature_hub import privacy_tail,set_kill_switch,kill_switch_enabled,set_value
PLUGIN={"permissions":["privacy.read", "security.control"],"name":"privacy_center","description":"Inspect EMBER's local privacy access log, control privacy logging, and activate/deactivate the emergency kill switch.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"log, logging, kill_switch"},"enabled":{"type":"BOOLEAN"},"limit":{"type":"INTEGER"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower()
    if a=='log':
        text='\n'.join(str(x) for x in privacy_tail(p.get('limit') or 50)) or 'No logged privacy events.'
        if player and hasattr(player,'show_content'):player.show_content('PRIVACY AUDIT',text)
        return text
    if a=='logging':set_value('privacy_logging',bool(p.get('enabled')));return f"Privacy logging {'on' if p.get('enabled') else 'off'}."
    if a=='kill_switch':set_kill_switch(bool(p.get('enabled')));return f"Kill switch {'ON' if kill_switch_enabled() else 'OFF'}."
    return 'Unknown privacy action.'

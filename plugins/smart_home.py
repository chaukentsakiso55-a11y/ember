"""Optional Home Assistant connector. Disabled until URL/token are configured."""
from __future__ import annotations
import requests
from memory.config_manager import get_plugin_config
PLUGIN={"permissions":["network.lan","smart_home.control"],"name":"smart_home","description":"Control the user's own Home Assistant instance on the local network after they configure its URL and access token.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"state or service"},"entity_id":{"type":"STRING"},"domain":{"type":"STRING"},"service":{"type":"STRING"}},"required":["action"]}}
PLUGIN_SETTINGS={"namespace":"smart_home","title":"Smart Home (Home Assistant)","fields":[{"key":"url","label":"Home Assistant URL","type":"text"},{"key":"token","label":"Long-lived access token","type":"password"}]}
def run(p,player=None,session_memory=None):
    cfg=get_plugin_config('smart_home');url=str(cfg.get('url') or '').rstrip('/');tok=str(cfg.get('token') or '')
    if not url or not tok:return 'Configure the Home Assistant URL and token in Plugin Settings first.'
    h={'Authorization':f'Bearer {tok}','Content-Type':'application/json'};a=p.get('action')
    if a=='state':
        eid=p.get('entity_id','');r=requests.get(f'{url}/api/states/{eid}',headers=h,timeout=8);r.raise_for_status();return str(r.json())
    if a=='service':
        domain=p.get('domain','');service=p.get('service','');eid=p.get('entity_id','');r=requests.post(f'{url}/api/services/{domain}/{service}',headers=h,json={'entity_id':eid},timeout=8);r.raise_for_status();return 'Smart-home service request completed.'
    return 'Use state or service.'

from __future__ import annotations
from core import plugin_store as ps
PLUGIN={"permissions":["plugins.manage"],"name":"plugin_store","description":"List, enable, disable or locally install EMBER plugins and manage plugin permission decisions.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"list, enable, disable, install_local, permissions, set_permission"},"name":{"type":"STRING"},"path":{"type":"STRING"},"permission":{"type":"STRING"},"allowed":{"type":"BOOLEAN"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower(); n=p.get('name','')
    if a=='list': return str(ps.list_installed())
    if a=='enable': return f"{n}: enabled={ps.set_enabled(n,True)}"
    if a=='disable': return f"{n}: enabled={ps.set_enabled(n,False)}"
    if a=='install_local': return ps.install_local(p.get('path',''))
    if a=='permissions': return str(ps.get_permissions())
    if a=='set_permission': return f"{n}/{p.get('permission','')}: {ps.set_permission(n,p.get('permission',''),bool(p.get('allowed')))}"
    return 'Unknown plugin-store action.'

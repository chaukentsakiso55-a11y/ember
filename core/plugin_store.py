"""Local plugin store / permission metadata helper."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from memory.config_manager import get_plugin_enabled, save_plugin_enabled
BASE=Path(__file__).resolve().parent.parent
PLUGINS=BASE/"plugins"
PERMS=BASE/"config"/"plugin_permissions.json"

def list_installed():
    out=[]
    for p in sorted(PLUGINS.glob("*.py")):
        if p.name.startswith("_"): continue
        out.append({"name":p.stem,"enabled":get_plugin_enabled(p.stem),"file":p.name})
    return out

def set_enabled(name:str, enabled:bool): save_plugin_enabled(name,bool(enabled)); return bool(enabled)
def install_local(path:str):
    src=Path(path).expanduser().resolve()
    if not src.is_file() or src.suffix.lower()!=".py": return "Choose a local .py plugin file."
    dst=PLUGINS/src.name; shutil.copy2(src,dst); return f"Installed {dst.name}. Restart EMBER to load it."
def get_permissions():
    try:return json.loads(PERMS.read_text(encoding="utf-8"))
    except Exception:return {}
def set_permission(plugin:str, permission:str, allowed:bool):
    d=get_permissions(); d.setdefault(plugin,{})[permission]=bool(allowed); PERMS.parent.mkdir(parents=True,exist_ok=True); PERMS.write_text(json.dumps(d,indent=2),encoding="utf-8"); return bool(allowed)

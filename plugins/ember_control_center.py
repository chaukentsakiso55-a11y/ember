"""EMBER control center: model routing, memory mode, workspaces, appearance and safety."""
from __future__ import annotations
from core import feature_hub as fh
from memory.config_manager import save_hud_style

PLUGIN={"permissions":["config.write", "memory.write", "security.control"],
"name":"ember_control_center",
"description":"Manage EMBER model mode (auto/online/local), temporary memory, workspaces/project paths, searchable workspace memory, HUD themes/avatar, mini HUD, voice profile, performance profile, privacy log, and emergency kill switch.",
"parameters":{"type":"OBJECT","properties":{
"action":{"type":"STRING","description":"status, model_mode, temp_memory, workspace_create, workspace_list, workspace_select, workspace_project, memory, theme, avatar, mini_hud, voice_profile, performance, privacy_log, kill_switch"},
"value":{"type":"STRING","description":"Primary value for the action."},
"name":{"type":"STRING","description":"Workspace or memory item name."},
"description":{"type":"STRING","description":"Workspace description or memory value."},
"path":{"type":"STRING","description":"Project path for a workspace."},
"query":{"type":"STRING","description":"Memory search query."},
"enabled":{"type":"BOOLEAN","description":"On/off value."}
},"required":["action"]},
"behavior":"NON_BLOCKING","scheduling":"SILENT"}

def run(parameters, player=None, session_memory=None):
    a=str(parameters.get("action") or "status").strip().lower(); v=parameters.get("value")
    if a=="status": return str({**fh.system_summary(),"workspace_meta":fh.active_workspace_meta(),"themes":fh.THEME_PRESETS})
    if a=="model_mode": return f"Model mode set to {fh.set_model_mode(str(v or 'auto'))}."
    if a=="temp_memory": fh.set_value("temporary_memory",bool(parameters.get("enabled"))); return f"Temporary memory {'enabled' if fh.temporary_memory_enabled() else 'disabled'}."
    if a=="workspace_create": return str(fh.create_workspace(parameters.get("name") or v or "workspace", parameters.get("description") or "", parameters.get("path") or ""))
    if a=="workspace_list": return str(fh.list_workspaces())
    if a=="workspace_select": return f"Active workspace: {fh.select_workspace(parameters.get('name') or v or 'default')}"
    if a=="workspace_project": return str(fh.set_workspace_project(parameters.get('path') or v or ''))
    if a=="memory":
        data=fh.workspace_memory(parameters.get("value") or "list", parameters.get("name") or "", parameters.get("description") or "", parameters.get("query") or "")
        text=str(data)
        if player and hasattr(player,'show_content') and (str(parameters.get('value') or '').lower() in {'list','search'}): player.show_content('WORKSPACE MEMORY',text)
        return text
    if a=="theme":
        theme=fh.set_theme(str(v or 'amber'))
        return f"HUD theme set to {theme}. It applies on the next EMBER window launch."
    if a=="avatar":
        style=str(v or 'face').strip().lower()
        if style not in {'face','core'}: return "Avatar style must be 'face' or 'core'."
        save_hud_style(style); fh.set_value('avatar',style)
        return f"Avatar/HUD center style set to {style}."
    if a=="mini_hud": fh.set_value('mini_hud',bool(parameters.get('enabled'))); return f"Mini HUD {'enabled' if parameters.get('enabled') else 'disabled'}."
    if a in {"voice_profile","performance"}:
        key="performance_profile" if a=="performance" else a; fh.set_value(key,str(v or "default")); return f"{key.replace('_',' ').title()} set to {v or 'default'}."
    if a=="privacy_log": return "\n".join(str(x) for x in fh.privacy_tail(40)) or "No privacy events logged yet."
    if a=="kill_switch": return f"Kill switch {'ON' if fh.set_kill_switch(bool(parameters.get('enabled'))) else 'OFF'}."
    return "Unknown control-center action."

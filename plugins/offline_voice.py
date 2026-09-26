from __future__ import annotations
PLUGIN={"permissions":["microphone.local","speaker.local","models.local"],"name":"offline_voice","description":"Run an explicit fully local push-to-talk voice turn using cached Whisper + local LLM + Kokoro. No cloud is used after the optional models are installed.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"status or talk"},"duration":{"type":"NUMBER","description":"Recording seconds, 1.5 to 20."}},"required":["action"]},"behavior":"NON_BLOCKING","scheduling":"SILENT"}
def run(p,player=None,session_memory=None):
    try:
        from core.offline_voice import status, run_once
    except Exception as e:
        return f"Offline voice dependencies are not ready: {e}. Install the normal EMBER audio dependencies plus optional faster-whisper and kokoro packages."
    if str(p.get('action','status')).lower()=='status':return str(status())
    r=run_once(p.get('duration') or 5)
    if player and hasattr(player,'write_log'):
        if r.get('heard'):player.write_log('You [offline]: '+r['heard'])
        if r.get('answer'):player.write_log('EMBER [offline]: '+r['answer'])
    return str(r)

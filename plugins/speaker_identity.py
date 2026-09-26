from __future__ import annotations
from core.speaker_id import enroll,verify,profiles
PLUGIN={"permissions":["biometrics.local","files.read"],"name":"speaker_identity","description":"Optional local speaker identification using user-supplied WAV samples. Voice embeddings stay on the computer.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"enroll, verify, profiles"},"name":{"type":"STRING"},"wav_path":{"type":"STRING"},"threshold":{"type":"NUMBER"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=p.get('action')
    if a=='enroll':return enroll(p.get('name','User'),p.get('wav_path',''))
    if a=='verify':return str(verify(p.get('wav_path',''),p.get('threshold') or .72))
    if a=='profiles':return str(profiles())
    return 'Use enroll, verify, or profiles.'

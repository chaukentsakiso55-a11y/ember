from __future__ import annotations
from core import automation_engine as ae
PLUGIN={"permissions":["automation.write"],"name":"automation_builder","description":"Build, record, list, replay, and delete explicit local workflows. Recording captures EMBER tool calls only after the user starts it; workflows are stored as inspectable JSON.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"create, list, delete, start_recording, record_step, finish_recording, cancel_recording, recording, run"},"name":{"type":"STRING"},"trigger":{"type":"STRING"},"steps":{"type":"ARRAY","items":{"type":"STRING"}},"text":{"type":"STRING"}},"required":["action"]}}
def run(p,player=None,session_memory=None):
    a=str(p.get('action','')).lower()
    if a=='create': return str(ae.create(p.get('name','Workflow'),p.get('trigger','manual'),p.get('steps') or []))
    if a=='list': return str(ae.list_all())
    if a=='delete': return 'Deleted.' if ae.delete(p.get('name','')) else 'Workflow not found.'
    if a=='start_recording': return str(ae.start_recording())
    if a=='record_step': return f"Recorded step {ae.record_step(p.get('text',''))}."
    if a=='finish_recording': return str(ae.finish_recording(p.get('name','Recorded workflow'),p.get('trigger','manual')))
    if a=='cancel_recording': return 'Recording cancelled.' if ae.cancel_recording() else 'No recording was active.'
    if a=='recording': return str(ae.recording())
    if a=='run':
        wf=ae.get(p.get('name',''))
        return f"__EMBER_WORKFLOW__:{wf['id']}" if wf else 'Workflow not found.'
    return 'Unknown automation action.'

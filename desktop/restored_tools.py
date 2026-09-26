from pathlib import Path
import json
import threading
from core.action_loader import discover_actions
from core.plugin_loader import discover_plugins
from core.llm_client import _normalise_schema

class RestoredTools:
    def __init__(self, engine):
        self.engine=engine
        root=Path(__file__).resolve().parent.parent
        self.actions=discover_actions(root/'actions',logger=engine.log)
        self.plugins=discover_plugins(root/'plugins',self.actions.names(),logger=engine.log,notify=engine.log)
    def declarations(self):
        rows=self.actions.get_tool_declarations()+self.plugins.get_tool_declarations()
        return [{'type':'function','function':{'name':x['name'],'description':x['description'],'parameters':_normalise_schema(x['parameters'])}} for x in rows]
    def run(self,name,args):
        if not self.engine.store.get('automation'):
            return 'Action execution is disabled. Enable Automation Agent in Advanced Settings.'
        gate={'name':name,'args':args,'event':threading.Event(),'accepted':False}
        self.engine.action_requested.emit(gate)
        if not gate['event'].wait(120) or not gate['accepted']:
            return 'Action cancelled or confirmation timed out. Nothing was executed.'
        self.engine.log('Executing action: '+name)
        ctx={'player':self,'speak':self.speak,'session_memory':None,'response':None}
        if self.actions.has(name):return self.actions.run(name,args,ctx)
        if self.plugins.has(name):return self.plugins.run(name,args,player=self,session_memory=None)
        return 'Unknown action: '+name
    def write_log(self,value):self.engine.event_logged.emit(str(value))
    def show_content(self,title,value):self.engine.content_ready.emit(str(title),str(value))
    def speak(self,value):self.engine.response.emit(str(value))

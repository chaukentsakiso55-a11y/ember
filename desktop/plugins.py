from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from PyQt6.QtWidgets import QDialog,QVBoxLayout,QTextEdit,QFileDialog,QInputDialog,QMessageBox
from desktop.widgets import NeonButton,label
from desktop.state import DATA,read_json,write_json

def dialog(host):
    d=QDialog(host);d.setWindowTitle('Plugin Manager');v=QVBoxLayout(d);out=QTextEdit();out.setReadOnly(True);v.addWidget(out)
    registry=read_json(DATA/'plugins.json',[])
    def refresh():out.setPlainText('\n\n'.join(x['name']+'\n'+x['file'] for x in registry) or 'No plugins installed. Plugins are trusted Python programs; each run requires approval.')
    def add():
        p,_=QFileDialog.getOpenFileName(d,'Choose plugin manifest','','JSON (*.json)')
        if not p:return
        try:
            manifest=read_json(p,{});path=(Path(p).parent/manifest['entry']).resolve()
            if path.suffix!='.py' or not path.is_file():raise ValueError('Manifest must point to an existing Python entry file.')
            registry.append({'name':str(manifest['name']),'file':str(path),'permissions':manifest.get('permissions',[]),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});write_json(DATA/'plugins.json',registry);refresh()
        except Exception as e:host.notice(str(e))
    def run():
        if not registry:return
        name,ok=QInputDialog.getItem(d,'Run plugin','Plugin',[x['name'] for x in registry],0,False)
        if not ok:return
        row=next(x for x in registry if x['name']==name);path=Path(row['file']);digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=row['sha256']:host.notice('Plugin code has changed. Remove and import it again before running.');return
        prompt='Run '+name+'?\n\nDeclared permissions: '+', '.join(row['permissions'])+'\n\nThis native Python plugin runs with your user account privileges. It is not sandboxed. Run only code you trust.'
        if QMessageBox.question(d,'Approve plugin execution',prompt)!=QMessageBox.StandardButton.Yes:return
        payload,ok=QInputDialog.getMultiLineText(d,'Plugin input','JSON input','{}')
        if not ok:return
        try:json.loads(payload)
        except ValueError:host.notice('Input must be valid JSON.');return
        def execute():
            r=subprocess.run([sys.executable,str(path)],input=payload,capture_output=True,text=True,timeout=120,cwd=path.parent)
            if r.returncode:raise RuntimeError(r.stderr[-2000:])
            return r.stdout[-10000:]
        host.jobs.run('plugin',execute)
    def remove():
        if not registry:return
        name,ok=QInputDialog.getItem(d,'Remove plugin','Plugin',[x['name'] for x in registry],0,False)
        if ok:registry[:]=[x for x in registry if x['name']!=name];write_json(DATA/'plugins.json',registry);refresh()
    for title,fn in [('Import manifest',add),('Run selected plugin',run),('Remove plugin',remove)]:b=NeonButton(title);b.clicked.connect(fn);v.addWidget(b)
    refresh();d.resize(700,450);d.exec()

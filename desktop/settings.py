from __future__ import annotations
import copy,json,os,sys,threading
from pathlib import Path
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QScrollArea,QStackedWidget,QComboBox,QLineEdit,QSlider,QSpinBox,QDoubleSpinBox,QMessageBox,QFileDialog,QDialog,QTextEdit,QProgressBar
from desktop.widgets import Panel,NeonButton,Toggle,Artwork,label,CYAN,MAGENTA
from desktop.state import DEFAULTS,DATA,ROOT,Vault

class Settings(Panel):
    applied=pyqtSignal()
    def __init__(self,host):
        super().__init__(magenta=True);self.host=host;self.store=host.store;self.fields={};self.provider_fields={}
        self.box.addWidget(label('⚙  SETTINGS',23,CYAN,True));self.box.addWidget(label('Customize Ember to match your workflow.',11))
        tabs=QHBoxLayout();self.tabs=[];self.pages=QStackedWidget()
        for i,n in enumerate(['General','AI & Models','Appearance','System','Integrations','Advanced']):
            b=NeonButton(n);b.setCheckable(True);b.clicked.connect(lambda _,i=i:self.select(i));tabs.addWidget(b);self.tabs.append(b)
        self.box.addLayout(tabs);self.box.addWidget(self.pages,1)
        for build in [self.general,self.models,self.appearance,self.system,self.integrations,self.advanced]:self.pages.addWidget(build())
        foot=QHBoxLayout();b=NeonButton('↻  Reset to Defaults');b.clicked.connect(self.reset);foot.addWidget(b);foot.addStretch();b=NeonButton('Cancel');b.clicked.connect(self.reload);foot.addWidget(b);b=NeonButton('▣  Save Settings',True);b.clicked.connect(self.save);foot.addWidget(b);self.box.addLayout(foot);self.select(0)
    def select(self,i):
        self.pages.setCurrentIndex(i)
        for j,b in enumerate(self.tabs):b.setChecked(i==j)
    def page(self):
        s=QScrollArea();s.setWidgetResizable(True);w=QWidget();g=QGridLayout(w);g.setContentsMargins(4,4,4,4);g.setSpacing(12);g.setColumnStretch(0,1);g.setColumnStretch(1,1);s.setWidget(w);return s,g
    def card(self,g,title,row,col,span=1):
        p=Panel(title);p.box.setAlignment(Qt.AlignmentFlag.AlignTop);p.box.setSpacing(6);p.box.setContentsMargins(13,11,13,11);g.addWidget(p,row,col,1,span);return p.box
    def field(self,layout,text,key,choices=None,kind=None,disabled=None):
        h=QHBoxLayout();l=label(text,10);l.setWordWrap(True);h.addWidget(l,1);value=self.store.get(key)
        if choices:
            w=QComboBox();w.addItems(choices);w.setCurrentText(str(value));w.setMinimumWidth(120)
        elif kind=='int':w=QSpinBox();w.setRange(1,100000);w.setValue(int(value or 1))
        elif kind=='float':w=QDoubleSpinBox();w.setRange(0,2);w.setSingleStep(.1);w.setValue(float(value or 0))
        elif isinstance(value,bool):w=Toggle(value)
        else:w=QLineEdit(str(value or ''))
        if disabled:w.setEnabled(False);w.setToolTip(disabled);l.setToolTip(disabled)
        self.fields.setdefault(key,[]).append(w);h.addWidget(w);layout.addLayout(h);return w
    def button(self,v,text,fn,primary=False):
        b=NeonButton(text,primary);b.clicked.connect(fn);v.addWidget(b);return b
    def general(self):
        s,g=self.page();v=self.card(g,'▣  Application',0,0)
        for t,k in [('Start Ember on Windows startup','startup'),('Minimize to system tray','minimize_tray'),('Show notifications','notifications')]:self.field(v,t,k)
        self.field(v,'Auto-check for updates','auto_updates',disabled='No signed update channel has been supplied.')
        v=self.card(g,'ϟ  Default Behavior',0,1);self.field(v,'Default Tab','default_tab',['Home','AI Chat','System Intel','Settings']);self.field(v,'Theme Mode','theme',['Cyberpunk','OLED Dark','Matrix Green','Sunset Orange']);self.field(v,'Language','language',['English','Afrikaans','isiZulu','Sesotho','中文']);self.field(v,'Start Minimized','start_minimized')
        v=self.card(g,'◴  Performance',1,0);self.field(v,'Performance profile','profile',['Balanced','Performance','Efficient']);self.field(v,'Enable animations','animations');self.field(v,'Enable glass effects','glass')
        v=self.card(g,'♧  Data & Privacy',1,1);self.field(v,'Save chat history','history');self.field(v,'Keep file analysis history','file_history');self.field(v,'Use approved conversation memory','memory');self.button(v,'Clear all local conversation data',self.clear)
        v=self.card(g,'♧  Notifications',2,0)
        for t,k in [('System alerts','notifications'),('Weather updates','weather_alerts'),('News notifications','news_alerts'),('Flight price alerts','flight_alerts')]:self.field(v,t,k,disabled=None if k=='notifications' else 'Background notification scheduling is not connected in this build.')
        v=self.card(g,'▣  System Tray',2,1);self.field(v,'Show system tray icon','tray');self.field(v,'Minimize to tray instead of closing','minimize_tray');self.button(v,'Review / edit memory',self.host.memory_dialog);g.setRowStretch(3,1);return s
    def models(self):
        s,g=self.page();v=self.card(g,'♧  Model Providers',0,0)
        for p in self.store.providers['providers']:
            row=QHBoxLayout();row.addWidget(label(p['name'],10),1);enabled=Toggle(p.get('enabled',True));row.addWidget(enabled)
            model=QLineEdit(p.get('model',''));model.setPlaceholderText('Auto-discover model');row.addWidget(model,2);b=NeonButton('Test');b.setFixedWidth(55);b.clicked.connect(lambda _,pid=p['id']:self.host.test_provider(pid));row.addWidget(b)
            cfg=NeonButton('⚙');cfg.setFixedWidth(35);cfg.clicked.connect(lambda _,pid=p['id']:self.provider_dialog(pid));row.addWidget(cfg);v.addLayout(row);self.provider_fields[p['id']]=(enabled,model)
        v=self.card(g,'⚙  Model Behavior',0,1);self.field(v,'Creativity / Temperature','temperature',kind='float');self.field(v,'Max Tokens','max_tokens',kind='int');self.field(v,'Default provider','provider',[p['id'] for p in self.store.providers['providers']]);self.field(v,'Auto-switch model on error','fallback');self.field(v,'Response Style','style',['Friendly','Formal','Business','Concise']);self.field(v,'Remember Context','context')
        v=self.card(g,'▤  Conversation Settings',1,0);self.field(v,'Language','language',['English','Afrikaans','isiZulu','Sesotho','中文']);self.field(v,'Use conversation memory','memory');self.field(v,'Voice (TTS)','tts');self.field(v,'Voice engine','tts_engine',['Gemini TTS','Edge TTS','Kokoro (Offline)']);self.field(v,'Voice ID','voice');self.field(v,'Whisper STT model','whisper_model');self.button(v,'Test voice',lambda:self.host.voice.speak('Ember voice test.'))
        v=self.card(g,'▥  Local Models',1,1);v.addWidget(label('Ollama • llama.cpp / compatible local servers',10));self.button(v,'Manage Local Models',self.host.model_manager);self.button(v,'Configure local server',lambda:self.provider_dialog('ollama'));self.button(v,'Open media generation tools',self.host.media_dialog);g.setRowStretch(2,1);return s
    def appearance(self):
        s,g=self.page();v=self.card(g,'◉  Theme Presets',0,0);h=QHBoxLayout()
        for i,n in enumerate(['Cyberpunk','OLED Dark','Matrix Green','Sunset Orange']):
            col=QVBoxLayout();pic=Artwork('appearance',(290+i*125,347,104,94));pic.setFixedHeight(85);col.addWidget(pic);b=NeonButton(n);b.clicked.connect(lambda _,n=n:self.set_field('theme',n));col.addWidget(b);h.addLayout(col)
        v.addLayout(h)
        v=self.card(g,'♙  Avatar Selection',0,1);h=QHBoxLayout()
        for n,src in [('Reference Female',(831,348,220,191)),('Current Ember',(1084,348,221,191))]:
            col=QVBoxLayout();pic=Artwork('appearance',src);pic.setMinimumHeight(155);col.addWidget(pic);b=NeonButton(n);b.clicked.connect(lambda _,n=n:self.set_field('avatar',n));col.addWidget(b);h.addLayout(col)
        v.addLayout(h);self.field(v,'Avatar','avatar',['Reference Female','Current Ember','Original Hologram']);self.field(v,'Visualization','visual',['Avatar','Core'])
        v=self.card(g,'◉  Accent Color',1,0);h=QHBoxLayout()
        for c in ['#00d9ff','#ef24ff','#9655ff','#007fff','#00eeee','#00ec87','#ffde00','#ff9c00','#ff334d']:
            b=NeonButton('●');b.setStyleSheet('color:'+c);b.setFixedWidth(35);b.clicked.connect(lambda _,c=c:self.set_field('accent',c));h.addWidget(b)
        v.addLayout(h);self.field(v,'Selected color','accent')
        v=self.card(g,'▧  Background',1,1);self.field(v,'Custom Image','background');self.button(v,'Change Background',self.background)
        v=self.card(g,'⌁  UI Effects',2,0,2)
        for t,k in [('Enable animations','animations'),('Enable glass effects','glass'),('Enable particle background','particles')]:self.field(v,t,k)
        g.setRowStretch(3,1);return s
    def system(self):
        s,g=self.page();v=self.card(g,'◴  Performance',0,0);self.field(v,'Performance Profile','profile',['Balanced','Performance','Efficient']);self.field(v,'Enable hardware acceleration','hardware',disabled='QPainter renderer uses Qt raster rendering. GPU acceleration is not implemented.');self.field(v,'Close idle processes','close_idle',disabled='Automatic process termination is not implemented.')
        v=self.card(g,'Resource Limits',0,1)
        for t,k in [('CPU Usage Limit (%)','cpu_limit'),('RAM Usage Limit (MB)','ram_limit'),('GPU Usage Limit (%)','gpu_limit')]:self.field(v,t,k,kind='int',disabled='Hard process resource limits are not implemented; these controls are disabled.')
        v=self.card(g,'ϟ  Startup & Shutdown',1,0);self.field(v,'Start minimized','start_minimized');self.field(v,'Start on Windows startup','startup');self.field(v,'Clear conversation data on exit','clear_exit')
        v=self.card(g,'▤  Storage',1,1);l=label(str(DATA),10);l.setWordWrap(True);v.addWidget(l);self.button(v,'Open data folder',self.host.open_data);self.button(v,'Clear cached generated media',self.host.clear_cache);g.setRowStretch(2,1);return s
    def integrations(self):
        s,g=self.page()
        for col,items in enumerate([['WhatsApp Web','YouTube','TikTok','Browser Control'],['Browser','Email','Windows System','Plugins']]):
            v=self.card(g,'Apps & Services',0,col)
            for name in items:
                p=Panel();p.box.addWidget(label(name,13,CYAN));self.button(p.box,'Manage' if name=='Plugins' else 'Configure',lambda _,n=name:self.host.integration(n));v.addWidget(p)
        g.setRowStretch(1,1);return s
    def advanced(self):
        s,g=self.page();v=self.card(g,'▣  Developer Options',0,0);self.field(v,'Show detailed event logs','debug');self.button(v,'Open event console',lambda:self.host.navigate('System Intel'));self.button(v,'Manage plugins',self.host.plugin_dialog)
        v=self.card(g,'◈  Experimental Features',0,1);self.field(v,'Multi-Model Routing','fallback');self.field(v,'Voice Interaction','stt');self.field(v,'PC Automation (explicit actions)','automation');self.field(v,'Self-Improvement','self_improve',disabled='Automatic code promotion is not implemented.')
        v=self.card(g,'♧  Data & Privacy',1,0);self.field(v,'Save chat history','history');self.field(v,'Clear all local conversation data on exit','clear_exit');self.button(v,'Clear Data',self.clear)
        v=self.card(g,'↻  Reset',1,1);self.button(v,'Reset All Settings',self.reset);g.setRowStretch(2,1);return s
    def set_field(self,key,value):
        for w in self.fields.get(key,[]):
            if isinstance(w,Toggle):w.setChecked(bool(value))
            elif isinstance(w,QComboBox):w.setCurrentText(str(value))
            elif isinstance(w,(QSpinBox,QDoubleSpinBox)):w.setValue(value)
            else:w.setText(str(value or ''))
    def reload(self):
        for key in self.fields:self.set_field(key,self.store.get(key))
    def save(self):
        values={}
        for key,widgets in self.fields.items():
            enabled=[w for w in widgets if w.isEnabled()]
            if not enabled:continue
            old=self.store.get(key)
            def value(w):
                if isinstance(w,Toggle):return w.isChecked()
                if isinstance(w,QComboBox):return w.currentText()
                if isinstance(w,(QSpinBox,QDoubleSpinBox)):return w.value()
                return w.text()
            changed=[value(w) for w in enabled if value(w)!=old];values[key]=changed[-1] if changed else old
        for p in self.store.providers['providers']:
            enabled,model=self.provider_fields[p['id']];p['enabled']=enabled.isChecked();p['model']=model.text().strip()
        if values.get('startup')!=self.store.get('startup'):
            try:self.autostart(values['startup'])
            except Exception as e:QMessageBox.warning(self,'Startup',str(e));return
        self.store.save(values);self.reload();self.host.engine.log('Settings saved.');self.applied.emit()
    def autostart(self,on):
        if sys.platform!='win32':raise RuntimeError('Windows startup registration is available only on Windows.')
        import winreg,subprocess
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            if on:winreg.SetValueEx(key,'Ember',0,winreg.REG_SZ,subprocess.list2cmdline([sys.executable,str(ROOT/'main.py')]))
            else:
                try:winreg.DeleteValue(key,'Ember')
                except FileNotFoundError:pass
    def clear(self):
        if QMessageBox.question(self,'Clear data','Delete saved conversations, file history and approved memories?')==QMessageBox.StandardButton.Yes:self.store.clear();self.host.clear_chat();self.host.engine.log('Conversation data cleared.')
    def reset(self):
        if QMessageBox.question(self,'Reset settings','Reset settings to defaults? API credentials remain in the secure store.')==QMessageBox.StandardButton.Yes:
            if self.store.get('startup'):self.autostart(False)
            self.store.values=copy.deepcopy(DEFAULTS);self.store.save();self.reload();self.applied.emit()
    def background(self):
        p,_=QFileDialog.getOpenFileName(self,'Select background','','Images (*.png *.jpg *.webp)')
        if p:self.set_field('background',p)
    def provider_dialog(self,pid):
        p=next(p for p in self.store.providers['providers'] if p['id']==pid);d=QDialog(self);d.setWindowTitle(p['name']);v=QVBoxLayout(d)
        v.addWidget(label('API endpoint'));url=QLineEdit(p['base_url']);v.addWidget(url);v.addWidget(label('API keys — one per line; blank preserves existing keys'))
        keys=QLineEdit();keys.setEchoMode(QLineEdit.EchoMode.Password);v.addWidget(keys);note=label('Credentials use the operating system secure vault.',9);v.addWidget(note)
        b=NeonButton('Save provider',True)
        def save():
            try:
                from urllib.parse import urlparse
                u=urlparse(url.text().strip())
                if not u.hostname or u.scheme not in ('https','http') or (u.scheme=='http' and u.hostname not in ('localhost','127.0.0.1','::1')):raise ValueError('Use HTTPS, or HTTP for a loopback local server.')
                if keys.text().strip():
                    Vault.set(pid,[keys.text().strip()]);self.store.values['provider']=pid;p['enabled']=True
                p['base_url']=url.text().strip().rstrip('/');self.store.save();self.reload();d.accept()
            except Exception as e:note.setText(str(e))
        b.clicked.connect(save);v.addWidget(b);d.resize(600,230);d.exec()

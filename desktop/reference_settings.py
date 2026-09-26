from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QStackedWidget,QScrollArea,QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox,QSlider
from desktop.settings import Settings as Base
from desktop.widgets import Toggle,Artwork
from desktop.reference_style import Frame,Button,Swatch,text,CYAN,MAGENTA

class Settings(Base):
    def __init__(self,host):
        QWidget.__init__(self);self.host=host;self.store=host.store;self.fields={};self.provider_fields={};self.setObjectName('referenceSettings')
        self.frame=Frame(kind='settings',parent=self);self.box=self.frame.box;self.box.setContentsMargins(17,16,17,14);self.box.setSpacing(10)
        self.box.addWidget(text('⚙  SETTINGS',33,CYAN,True,True));self.subtitle=text('Customize Ember to match your workflow.',19);self.box.addWidget(self.subtitle)
        tabs=QHBoxLayout();tabs.setSpacing(7);self.tabs=[];self.pages=QStackedWidget()
        for i,n in enumerate(['General','AI & Models','Appearance','System','Integrations','Advanced']):
            b=Button(n,n);b.setMinimumHeight(51);b.setCheckable(True);b.clicked.connect(lambda _,i=i:self.select(i));tabs.addWidget(b);self.tabs.append(b)
        self.box.addLayout(tabs);self.box.addWidget(self.pages,1)
        for build in [self.general,self.models,self.appearance,self.system,self.integrations,self.advanced]:self.pages.addWidget(build())
        foot=QHBoxLayout();self.reset_button=Button('Reset to Defaults','reset');self.reset_button.clicked.connect(self.reset);self.reset_button.setFixedWidth(200);foot.addWidget(self.reset_button);foot.addStretch();b=Button('Cancel');b.setFixedWidth(140);b.clicked.connect(self.reload);foot.addWidget(b);b=Button('Save Settings','save',True);b.setFixedWidth(197);b.clicked.connect(self.save);foot.addWidget(b);self.box.addLayout(foot);self.select(0);self.bind_fields()
    def bind_fields(self):
        for key,widgets in self.fields.items():
            for w in widgets:
                signal=(w.toggled if isinstance(w,Toggle) else w.currentTextChanged if isinstance(w,QComboBox) else w.valueChanged if isinstance(w,(QSpinBox,QDoubleSpinBox)) else w.textChanged)
                signal.connect(lambda value,key=key:self.set_field(key,value))
    def set_field(self,key,value):
        if getattr(self,'_syncing',False):return
        self._syncing=True
        try:super().set_field(key,value)
        finally:self._syncing=False
    def resizeEvent(self,e):self.frame.setGeometry(self.rect());QWidget.resizeEvent(self,e)
    def paintEvent(self,e):pass
    def select(self,i):
        self.pages.setCurrentIndex(i)
        for j,b in enumerate(self.tabs):b.setChecked(i==j)
        self.subtitle.setText(['Customize Ember to match your workflow.',"Configure Ember’s AI models, providers, and intelligence behavior.","Customize Ember to match your workflow.",'Configure system performance and resources.','Connect Ember with your favorite apps and services.','Advanced options for power users.'][i])
    def page(self):
        s=QScrollArea();s.setWidgetResizable(True);s.setFrameShape(QScrollArea.Shape.NoFrame);w=QWidget();g=QGridLayout(w);g.setContentsMargins(2,2,2,2);g.setSpacing(12);g.setColumnStretch(0,1);g.setColumnStretch(1,1);s.setWidget(w);return s,g
    def card(self,g,title,row,col,span=1):
        p=Frame(title);p.box.setAlignment(Qt.AlignmentFlag.AlignTop);p.box.setSpacing(4);p.box.setContentsMargins(17,9,17,9);g.addWidget(p,row,col,1,span);return p.box
    def field(self,layout,title,key,choices=None,kind=None,disabled=None):
        row=QHBoxLayout();row.setSpacing(8);lab=text(title,18);lab.setWordWrap(True);row.addWidget(lab,1);value=self.store.get(key)
        if choices:w=QComboBox();w.addItems(choices);w.setCurrentText(str(value));w.setMinimumWidth(160);w.setMaximumWidth(240)
        elif kind=='int':w=QSpinBox();w.setRange(1,100000);w.setValue(int(value or 1));w.setFixedWidth(100)
        elif kind=='float':w=QDoubleSpinBox();w.setRange(0,2);w.setSingleStep(.1);w.setValue(float(value or 0));w.setFixedWidth(100)
        elif isinstance(value,bool):w=Toggle(value)
        else:w=QLineEdit(str(value or ''));w.setMaximumWidth(260)
        w.setAccessibleName(title);lab.setBuddy(w)
        if disabled:w.setEnabled(False);w.setToolTip(disabled);lab.setToolTip(disabled)
        if not isinstance(w,Toggle):w.setMinimumHeight(0);w.setFixedHeight(27)
        self.fields.setdefault(key,[]).append(w);row.addWidget(w);layout.addLayout(row);return w
    def button(self,v,title,fn,primary=False):
        b=Button(title,primary=primary);b.setFixedHeight(32);b.clicked.connect(fn);v.addWidget(b);return b
    def general(self):
        s,g=self.page();v=self.card(g,'▣  Application',0,0)
        for title,key in [('Start Ember on Windows startup','startup'),('Minimize to system tray','minimize_tray'),('Show notifications','notifications')]:self.field(v,title,key)
        self.field(v,'Auto-check for updates','auto_updates',disabled='An update source has not been configured.')
        v=self.card(g,'ϟ  Default Behavior',0,1)
        for title,key,options in [('Default Tab','default_tab',['Home','AI Chat','System Intel','Settings']),('Theme Mode','theme',['Cyberpunk','OLED Dark','Matrix Green','Sunset Orange']),('Language','language',['English','Afrikaans','isiZulu','Sesotho','中文'])]:self.field(v,title,key,options)
        self.field(v,'Start Minimized','start_minimized')
        v=self.card(g,'◴  Performance',1,0);self.field(v,'Enable hardware acceleration','hardware',disabled='This desktop renderer uses Qt raster drawing.');self.field(v,'Limit background resource usage','background_limit');self.field(v,'Enable animations','animations');self.field(v,'Performance profile','profile',['Balanced','Performance','Efficient'])
        v=self.card(g,'♧  Data & Privacy',1,1);self.field(v,'Save chat history','history');self.field(v,'Keep file analysis history','file_history');self.field(v,'Store settings locally','local_settings',disabled='Local configuration storage is required.');self.button(v,'Clear Data',self.clear)
        v=self.card(g,'♧  Notifications',2,0)
        for title,key in [('System alerts','notifications'),('Weather updates','weather_alerts'),('News notifications','news_alerts'),('Flight price alerts','flight_alerts')]:self.field(v,title,key,disabled=None if key=='notifications' else 'Scheduled alerts require a configured schedule/feed.')
        v=self.card(g,'▣  System Tray',2,1);self.field(v,'Show system tray icon','tray');self.field(v,'Show quick actions','quick_actions');self.field(v,'Minimize to tray instead of closing','minimize_tray');g.setRowStretch(3,1);return s
    def models(self):
        s,g=self.page();v=self.card(g,'♧  Model Providers',0,0);v.addWidget(text('Enable and configure AI providers. Multiple providers can be active.',14))
        order=['openai','gemini','anthropic','grok','xkiro','openrouter']
        for pid in order:
            p=next(p for p in self.store.providers['providers'] if p['id']==pid);row=QHBoxLayout();row.setSpacing(6);brand=text({'openai':'◎','gemini':'✦','anthropic':'AI','grok':'∅','xkiro':'X','openrouter':'⇆'}[pid],25,CYAN,True);brand.setFixedWidth(38);row.addWidget(brand);name=text(p['name'].replace(' Claude',''),17);name.setFixedWidth(113);row.addWidget(name);on=Toggle(p.get('enabled',True));row.addWidget(on);model=QLineEdit(p.get('model',''));model.setPlaceholderText('Select model…');model.setMinimumWidth(65);model.setMaximumWidth(145);model.setFixedHeight(29);row.addWidget(model,1);b=Button('Test');b.setMinimumHeight(29);b.setFixedWidth(49);b.clicked.connect(lambda _,pid=pid:self.host.test_provider(pid));row.addWidget(b);b=Button('⋮');b.setFixedWidth(25);b.setMinimumHeight(29);b.setAccessibleName('Configure '+p['name']);b.clicked.connect(lambda _,pid=pid:self.provider_dialog(pid));row.addWidget(b);v.addLayout(row);self.provider_fields[pid]=(on,model)
        for p in self.store.providers['providers']:
            if p['id'] not in self.provider_fields:
                on=Toggle(p.get('enabled',True));on.hide();model=QLineEdit(p.get('model',''));model.hide();self.provider_fields[p['id']]=(on,model)
        v=self.card(g,'⚙  Model Behavior',0,1);self.slider(v,'Creativity Level','temperature',0,200,.01);self.field(v,'Response Length','response_length',['Short','Medium','Long']);self.slider(v,'Temperature','temperature',0,200,.01);self.slider(v,'Top P','top_p',0,100,.01);self.slider(v,'Max Tokens','max_tokens',64,8192,1);self.field(v,'Use fastest model for simple tasks','fastest_model');self.field(v,'Use most capable model for complex tasks','capable_model');self.field(v,'Default Model','provider',[p['id'] for p in self.store.providers['providers']]);self.field(v,'Auto-switch model on error','fallback')
        lower=QWidget();h=QHBoxLayout(lower);h.setContentsMargins(0,0,0,0);h.setSpacing(11)
        for title in ['Conversation Settings','Local Models','AI Tools']:
            panel=Frame(title);panel.box.setSpacing(5);panel.box.setAlignment(Qt.AlignmentFlag.AlignTop);h.addWidget(panel,1)
            if title=='Conversation Settings':
                self.field(panel.box,'Conversation Mode','conversation_mode',['Standard','Voice','Concise']);self.field(panel.box,'Response Style','style',['Friendly','Formal','Business','Concise']);self.field(panel.box,'Language','language',['English','Afrikaans','isiZulu']);self.field(panel.box,'Remember Context','context');self.field(panel.box,'Use conversation memory','memory');self.field(panel.box,'Auto-summarize long chats','auto_summarize');self.button(panel.box,'Review memory',self.host.memory_dialog)
            elif title=='Local Models':
                self.field(panel.box,'Enable Local Models','enable_local_models');self.field(panel.box,'Local engine','local_engine',['Ollama','Compatible server']);local=self.field(panel.box,'Default Local Model','local_model');self.field(panel.box,'Model Path','model_path');self.field(panel.box,'GPU Acceleration','gpu_acceleration');self.field(panel.box,'Auto-download models','auto_download_models');self.provider_fields['ollama']=(self.provider_fields['ollama'][0],local);self.button(panel.box,'Configure server',lambda:self.provider_dialog('ollama'));self.button(panel.box,'Manage Local Models',self.host.model_manager)
            else:
                self.field(panel.box,'Image Generation','image_generation');self.field(panel.box,'Video Generation','video_generation');self.field(panel.box,'Voice (TTS)','tts');self.field(panel.box,'Speech-to-Text (STT)','stt');self.field(panel.box,'Code Assistant','code_assistant');self.field(panel.box,'Web Search','web_search');self.field(panel.box,'Vision / Image Analysis','vision_analysis');self.button(panel.box,'Voice configuration',self.host.voice_settings);self.button(panel.box,'Image / Video Generation',self.host.media_dialog);self.button(panel.box,'Document Analysis',lambda:self.host.navigate('File Analysis'))
        g.addWidget(lower,1,0,1,2);g.setRowStretch(2,1);return s
    def slider(self,v,title,key,lo,hi,factor):
        row=QHBoxLayout();lab=text(title,17);lab.setFixedWidth(160);row.addWidget(lab);slider=QSlider(Qt.Orientation.Horizontal);slider.setRange(lo,hi);slider.setValue(int(float(self.store.get(key) or 0)/factor));value=text(str(self.store.get(key)),17);value.setFixedWidth(49);row.addWidget(slider,1);row.addWidget(value);v.addLayout(row)
        proxy=QDoubleSpinBox() if factor!=1 else QSpinBox();proxy.setRange(lo*factor,hi*factor) if factor!=1 else proxy.setRange(lo,hi);proxy.setValue(self.store.get(key) or 0);proxy.hide();self.fields.setdefault(key,[]).append(proxy)
        def change(n):proxy.setValue(n*factor if factor!=1 else n);value.setText(f'{n*factor:.2f}' if factor!=1 else str(n))
        slider.valueChanged.connect(change);proxy.valueChanged.connect(lambda n:slider.setValue(int(n/factor)));return slider
    def appearance(self):
        s,g=self.page();left=QWidget();right=QWidget();lv=QVBoxLayout(left);rv=QVBoxLayout(right)
        for layout in [lv,rv]:layout.setContentsMargins(0,0,0,0);layout.setSpacing(12)
        g.addWidget(left,0,0);g.addWidget(right,0,1)
        panel=Frame('◉  Theme Presets');panel.box.addWidget(text("Choose a visual theme for Ember’s interface.",16));lv.addWidget(panel);h=QHBoxLayout();h.setSpacing(8)
        for i,name in enumerate(['Cyberpunk','OLED Dark','Matrix Green','Sunset Orange']):
            col=QVBoxLayout();col.setSpacing(0);pic=Artwork('appearance',(290+i*125,347,104,94));pic.setFixedHeight(90);col.addWidget(pic);b=Button(name.replace(' ','\n'));b.setFixedHeight(40);b.clicked.connect(lambda _,n=name:self.set_field('theme',n));col.addWidget(b);h.addLayout(col)
        panel.box.addLayout(h);hidden=QComboBox();hidden.addItems(['Cyberpunk','OLED Dark','Matrix Green','Sunset Orange']);hidden.setCurrentText(self.store.get('theme'));hidden.hide();self.fields.setdefault('theme',[]).append(hidden)
        panel=Frame('◉  Accent Color');panel.box.setContentsMargins(15,8,15,8);panel.box.setSpacing(4);panel.box.addWidget(text('Select the accent color used throughout the interface.',16));h=QHBoxLayout();h.setSpacing(7)
        for color in ['#00d9ff','#ef24ff','#9655ff','#007fff','#00eeee','#00ec87','#ffde00','#ff9c00','#ff334d']:
            b=Swatch(color);b.clicked.connect(lambda _,c=color:self.set_field('accent',c));h.addWidget(b)
        panel.box.addLayout(h);proxy=QLineEdit(self.store.get('accent'));proxy.hide();self.fields.setdefault('accent',[]).append(proxy);lv.addWidget(panel)
        panel=Frame('⌁  UI Effects');panel.box.setContentsMargins(15,8,15,8);panel.box.setSpacing(4)
        for title,key in [('Enable animations','animations'),('Enable glass effects','glass'),('Enable particle background','particles'),('Enable sound effects','sound_effects'),('Show animated avatar','animated_avatar')]:self.field(panel.box,title,key)
        lv.addWidget(panel);lv.addStretch()
        panel=Frame('♙  Avatar Selection');panel.box.addWidget(text("Choose Ember’s AI avatar.",16));h=QHBoxLayout()
        for title,source in [('Reference Female',(831,348,220,191)),('Current Ember',(1084,348,221,191))]:
            col=QVBoxLayout();col.setSpacing(0);pic=Artwork('appearance',source);pic.setFixedHeight(194);col.addWidget(pic);b=Button(title,primary=title==self.store.get('avatar'));b.clicked.connect(lambda _,n=title:self.set_field('avatar',n));col.addWidget(b);h.addLayout(col)
        panel.box.addLayout(h);proxy=QComboBox();proxy.addItems(['Reference Female','Current Ember','Original Hologram']);proxy.setCurrentText(self.store.get('avatar'));proxy.hide();self.fields.setdefault('avatar',[]).append(proxy);rv.addWidget(panel)
        panel=Frame('▧  Background');panel.box.addWidget(text('Set the background for the interface.',16));self.field(panel.box,'Background mode','background_mode',['Static Background','Animated Background','Custom Image']);self.field(panel.box,'Visualization','visual',['Avatar','Core']);self.button(panel.box,'Change Background',self.background);proxy=QLineEdit(self.store.get('background'));proxy.hide();self.fields.setdefault('background',[]).append(proxy);rv.addWidget(panel);rv.addStretch();return s

    def integrations(self):
        s,g=self.page()
        groups=[['WhatsApp Web','YouTube','TikTok','Browser Control'],['Browser','Email','Windows System','Plugins']]
        for col,names in enumerate(groups):
            v=self.card(g,'Apps & Services' if col==0 else 'Services & Extensions',0,col)
            for name in names:
                row=QHBoxLayout();row.setSpacing(12);glyph=text({'WhatsApp Web':'◉','YouTube':'▶','TikTok':'♪','Browser Control':'✉','Browser':'◈','Email':'@','Windows System':'⊞','Plugins':'⬡'}[name],28,CYAN,True);glyph.setFixedWidth(35);row.addWidget(glyph);info=QVBoxLayout();info.setSpacing(0);info.addWidget(text(name,20));info.addWidget(text({'WhatsApp Web':'Open your authorized session','YouTube':'Search, discover, play','TikTok':'Open user-controlled browser','Browser Control':'Open sites and automate','Browser':'Configure browser application','Email':'Open signed-in mailbox','Windows System':'Control apps and folders','Plugins':'Extend Ember with trusted plugins'}[name],14));row.addLayout(info,1);toggle=Toggle(bool(self.store.get('integrations').get(name,False)));toggle.setAccessibleName('Enable '+name);row.addWidget(toggle);self.integration_fields=getattr(self,'integration_fields',{});self.integration_fields[name]=toggle;b=Button('Manage' if name=='Plugins' else 'Configure');b.setFixedWidth(103);b.setMinimumHeight(36);b.clicked.connect(lambda _,n=name:self.host.integration(n));row.addWidget(b);v.addLayout(row);v.addSpacing(21)
        g.setRowStretch(1,1);return s
    def system(self):
        s,g=self.page();v=self.card(g,'◴  Performance',0,0);self.field(v,'Performance Profile','profile',['Balanced','Performance','Efficient']);self.field(v,'Enable hardware acceleration','hardware',disabled='Qt raster rendering is active.');self.field(v,'Limit background resource usage','background_limit');self.field(v,'Auto-manage memory','auto_memory');self.field(v,'Run background services','run_background');self.field(v,'Graceful shutdown','graceful_shutdown');self.field(v,'Save session on exit','session_save');self.field(v,'Close idle processes','close_idle',disabled='Automatic process termination is unavailable.')
        v=self.card(g,'Resource Limits',0,1)
        for title,key,hi in [('CPU Usage Limit','cpu_limit',100),('RAM Usage Limit (MB)','ram_limit',16384),('GPU Usage Limit','gpu_limit',100)]:
            control=self.slider(v,title,key,1,hi,1);control.setEnabled(False);control.setToolTip('Hard resource caps are unavailable.')
            self.fields[key][-1].setEnabled(False)
        v.addWidget(text('Hard resource caps are not available in this build.',15))
        v=self.card(g,'ϟ  Startup & Shutdown',1,0);self.field(v,'Start minimized','start_minimized');self.field(v,'Save conversation on exit','history');self.field(v,'Minimize to tray','minimize_tray');self.field(v,'Clear local data on exit','clear_exit')
        v=self.card(g,'▤  Storage',1,1);path=text(str(__import__('desktop.state',fromlist=['DATA']).DATA),15);path.setWordWrap(True);v.addWidget(path);self.button(v,'Change / open data location',self.host.open_data);self.field(v,'Maximum cache size (MB)','cache_mb',kind='int');self.button(v,'Clear media cache',self.host.clear_cache);g.setRowStretch(2,1);return s
    def advanced(self):
        s,g=self.page();v=self.card(g,'Developer Options',0,0);self.field(v,'Enable debug mode','debug');self.field(v,'Show detailed logs','detailed_logs');self.field(v,'Enable developer console','console');self.field(v,'Allow experimental features','allow_experimental');self.field(v,'Enable plugin development','plugin_development');self.button(v,'Create Desktop Icon',self.host.create_icon,True);self.button(v,'Open console',lambda:self.host.navigate('System Intel'));self.button(v,'Plugin development',self.host.plugin_dialog)
        v=self.card(g,'Experimental Features',0,1);self.field(v,'Local AI Core (Offline)','local_core');self.field(v,'Multi-Model Routing','fallback');self.field(v,'Fallback provider','fallback_provider',[p['id'] for p in self.store.providers['providers']]);self.field(v,'Personality','personality',['Friendly','Professional','Direct']);self.field(v,'Sense of humor','humor');self.field(v,'Knowledge mode','knowledge_mode',['Expanded','Focused','Offline only']);self.field(v,'Voice Interaction','stt');self.field(v,'Automation Agent','automation');self.field(v,'Self-Improvement','self_improve',disabled='Automatic code promotion is unavailable.')
        v=self.card(g,'Data & Privacy',1,0);self.field(v,'Save chat history','history');self.field(v,'Keep file analysis history','file_history');self.field(v,'Store settings locally','local_settings',disabled='Required for configuration.');self.field(v,'Clear all local data on exit','clear_exit');self.button(v,'Clear Data',self.clear)
        v=self.card(g,'Reset',1,1);v.addWidget(text('Restore default settings.',17));self.button(v,'Reset All Settings',self.reset);g.setRowStretch(2,1);return s
    def save(self):
        for name,w in getattr(self,'integration_fields',{}).items():self.store.values['integrations'][name]=w.isChecked()
        super().save()

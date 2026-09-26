from __future__ import annotations
import html,time
from PyQt6.QtCore import Qt,QRectF,QTimer
from PyQt6.QtGui import QPainter,QColor,QFont,QKeySequence,QShortcut
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QScrollArea,QTextEdit,QLineEdit,QLabel,QDialog,QComboBox,QGraphicsView,QGraphicsScene,QSizePolicy
from desktop.window import Window as BaseWindow,STYLE
from desktop.reference_style import fonts,Frame,Button,Header,text,CYAN,MAGENTA,font,icon
from desktop.reference_visual import Visual,Waveform
from desktop.widgets import Artwork,DropPanel
from desktop.reference_style import Vitals

REFERENCE_STYLE='''
QWidget{font-family:Rajdhani;color:#c9e9ff;font-size:18px;}
QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox{background:#011220;border:1px solid #175074;padding:1px 7px;font-family:Rajdhani;font-size:18px;min-height:18px;}
QComboBox QAbstractItemView{background:#001323;font-family:Rajdhani;font-size:18px;}
QSlider::groove:horizontal{height:7px;background:#173349;border-radius:3px;}
QSlider::sub-page:horizontal{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #b720ef,stop:1 #00d9ff);border-radius:3px;}
QSlider::handle:horizontal{background:#d9f0ff;border:1px solid #68c9fd;width:15px;margin:-5px 0;border-radius:8px;}
QTextEdit{font-family:Rajdhani;font-size:17px;}
'''

class ScaleView(QGraphicsView):
    def __init__(self,stage,parent):
        super().__init__(parent);scene=QGraphicsScene(self);self.setScene(scene);scene.addWidget(stage);scene.setSceneRect(0,0,1672,941);self.setFrameShape(QGraphicsView.Shape.NoFrame);self.setStyleSheet('background:#000610;border:0;');self.setRenderHints(QPainter.RenderHint.Antialiasing|QPainter.RenderHint.SmoothPixmapTransform);self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    def resizeEvent(self,e):super().resizeEvent(e);self.fitInView(self.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)

class ReferenceWindow(BaseWindow):
    def __init__(self):
        fonts();super().__init__();root=self.takeCentralWidget();root.setFixedSize(1672,941);root.layout().setContentsMargins(9,8,9,8);root.layout().setSpacing(8);self.body.setSpacing(12);self.stage=root;self.scaler=ScaleView(root,self);self.setCentralWidget(self.scaler);self.resize(1672,941);self.setStyleSheet(STYLE+REFERENCE_STYLE);root.setStyleSheet(STYLE+REFERENCE_STYLE);self.apply_settings()
    def header(self):
        h=Header(self);self.connection=h.status;self.mode=h.visual;self.local_core=h.local;self.secure_link=h.providers;return h
    def sidebar(self):
        w=QWidget();w.setFixedWidth(230);v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0);v.setSpacing(8);p=Frame(kind='nav');p.box.setContentsMargins(8,9,8,9);p.box.setSpacing(2)
        for name in ['Home','AI Chat','System Intel','Weather','News','Applications','Flight Finder','File Analysis','Settings','About']:
            b=Button(name,name,nav=True);b.setMinimumHeight(56);b.setCheckable(True);b.clicked.connect(lambda _,n=name:self.navigate(n));p.box.addWidget(b);self.nav[name]=b
        p.box.addStretch();v.addWidget(p,1);identity=Frame(kind='nav');identity.setFixedHeight(126);identity.box.setContentsMargins(19,21,17,14);row=QHBoxLayout();ring=text('◯',49,CYAN);row.addWidget(ring);col=QVBoxLayout();col.setSpacing(0);col.addWidget(text('EMBER',23));col.addWidget(text('AI ASSISTANT  v2.0',14));col.addWidget(text('CYBERPUNK HUD',14,CYAN));row.addLayout(col);identity.box.addLayout(row);v.addWidget(identity);return w
    def footer(self):
        p=Frame(kind='footer');p.setFixedHeight(43);p.box.setContentsMargins(26,7,16,6);row=QHBoxLayout();row.setSpacing(30);self.clock=text('',17);row.addWidget(self.clock,3);self.foot_state=text('●  SYSTEM STANDBY',17,'#00f8b2');row.addWidget(self.foot_state,2);self.foot_mic=text('●  MICROPHONE OFF',17,CYAN);row.addWidget(self.foot_mic,2);self.foot_provider=text('●  PROVIDER UNTESTED',17,MAGENTA);row.addWidget(self.foot_provider,3);row.addWidget(text('EMPOWERED BY AI.\nBUILT FOR YOU.',14));p.box.addLayout(row);return p
    def chat_page(self):
        w=QWidget();row=QHBoxLayout(w);row.setContentsMargins(0,0,0,0);row.setSpacing(11);left=Frame(kind='main');left.box.setContentsMargins(12,10,12,15);left.box.setSpacing(8)
        title=Frame();title.setFixedHeight(70);title.box.setContentsMargins(16,8,16,6);h=QHBoxLayout();glyph=text('⌁',42,CYAN);h.addWidget(glyph);col=QVBoxLayout();col.setSpacing(0);col.addWidget(text('Live Chat',28,bold=True));col.addWidget(text('REAL-TIME VOICE CONVERSATION WITH EMBER',16,CYAN));h.addLayout(col,1);self.live_status=text('●  STANDBY',18,'#00f0ac');h.addWidget(self.live_status);title.box.addLayout(h);left.box.addWidget(title)
        self.avatar=Visual(self.store);self.avatar.setFixedHeight(346);self.visuals.append(self.avatar);left.box.addWidget(self.avatar);self.wave=Waveform();left.box.addWidget(self.wave)
        self.transcript=QTextEdit();self.transcript.setReadOnly(True);self.transcript.setStyleSheet('QTextEdit{background:#000d17;border:1px solid #125073;padding:9px;font-family:Rajdhani;font-size:16px;}');self.transcript.document().setMaximumBlockCount(1000);left.box.addWidget(self.transcript,1)
        controls=QHBoxLayout();controls.setSpacing(10)
        for title,glyph,fn,primary in [('Camera','camera',self.camera,False),('Screen Share','monitor',self.screen,False),('End Call','end',self.end_call,True),('Start Voice','mic',self.record,False),('More','more',self.more,False)]:
            b=Button(title,glyph,primary);b.setFixedHeight(49);b.clicked.connect(fn);controls.addWidget(b,6 if title=='End Call' else 5)
            if title=='Start Voice':self.mic_button=b
        left.box.addLayout(controls);row.addWidget(left,67)
        right=Frame(kind='right');right.box.setContentsMargins(17,15,17,17);right.box.setSpacing(5);h=QHBoxLayout();h.addWidget(text('▤  Text Chat',25,bold=True),1);search=Button('','search');search.setFixedSize(37,37);search.setAccessibleName('Search conversation');search.clicked.connect(self.toggle_search);h.addWidget(search);b=Button('','more');b.setFixedSize(37,37);b.clicked.connect(self.more);h.addWidget(b);right.box.addLayout(h)
        self.chat_search=QLineEdit();self.chat_search.setPlaceholderText('Search conversation…');self.chat_search.textChanged.connect(self.search_chat);self.chat_search.hide();right.box.addWidget(self.chat_search)
        self.chat_scroll=QScrollArea();self.chat_scroll.setWidgetResizable(True);self.chat_scroll.setFrameShape(QScrollArea.Shape.NoFrame);self.chat_content=QWidget();self.chat_layout=QVBoxLayout(self.chat_content);self.chat_layout.setContentsMargins(0,6,0,6);self.chat_layout.setSpacing(10);self.chat_layout.addStretch();self.chat_scroll.setWidget(self.chat_content);right.box.addWidget(self.chat_scroll,1);self.typing=text('',16,MAGENTA);right.box.addWidget(self.typing)
        h=QHBoxLayout();h.setSpacing(7);self.input=QLineEdit();self.input.setPlaceholderText('Type a message to Ember…');self.input.setFixedHeight(46);self.input.returnPressed.connect(self.send);h.addWidget(self.input,1);attach=Button('','attach');attach.setFixedSize(45,48);attach.clicked.connect(self.pick_file);h.addWidget(attach);send=Button('','send',True);send.setFixedSize(52,49);send.clicked.connect(self.send);h.addWidget(send);right.box.addLayout(h);row.addWidget(right,33);return w
    def toggle_search(self):self.chat_search.setVisible(not self.chat_search.isVisible());self.chat_search.setFocus()
    def settings_page(self):
        w=QWidget();h=QHBoxLayout(w);h.setContentsMargins(0,0,0,0);h.setSpacing(10);h.addWidget(self.settings,1);side=QWidget();side.setFixedWidth(290);v=QVBoxLayout(side);v.setContentsMargins(0,0,0,0);v.setSpacing(8)
        visual=Visual(self.store,mini=True);visual.setFixedHeight(277);self.visuals.append(visual);v.addWidget(visual)
        vit=Vitals();vit.setFixedHeight(182);self.vitals.append(vit);v.addWidget(vit)
        status=Frame('AI CORE STATUS');status.setFixedHeight(133);self.providers_status=text('Providers have not been tested.',16);self.providers_status.setWordWrap(True);status.box.addWidget(self.providers_status);v.addWidget(status,2);v.addWidget(self.event_panel(),3);h.addWidget(side);return w
    def event_panel(self):
        p=Frame('EVENT STREAM');e=QTextEdit();e.setReadOnly(True);e.document().setMaximumBlockCount(300);e.setStyleSheet('border:0;background:transparent;font-family:Rajdhani;font-size:15px;color:#91c5ed;');p.box.addWidget(e,1);self.streams.append(e);return p
    def add_message(self,m):
        who='EMBER' if m['role']=='assistant' else 'You';color=MAGENTA if m['role']=='assistant' else CYAN
        container=QWidget();v=QVBoxLayout(container);v.setContentsMargins(0,8,0,8);v.setSpacing(5);head=text(who+'  '+m.get('time',''),15,color,True)
        if m['role']=='user':head.setAlignment(Qt.AlignmentFlag.AlignRight)
        v.addWidget(head);h=QHBoxLayout();h.setSpacing(10)
        if m['role']=='assistant':avatar=Artwork('appearance',(1390,124,250,249));avatar.setFixedSize(45,47);h.addWidget(avatar,0,Qt.AlignmentFlag.AlignTop)
        else:h.addSpacing(40)
        bubble=Frame();bubble.setStyleSheet('');bubble.box.setContentsMargins(13,10,13,10);content=text(m['content'],19,color='#dfb6f7' if m['role']=='assistant' else '#a1dbfa');content.setWordWrap(True);content.setTextFormat(Qt.TextFormat.PlainText);content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse);bubble.box.addWidget(content);h.addWidget(bubble,1);v.addLayout(h);container.setProperty('message',m['content'].lower());self.chat_layout.insertWidget(self.chat_layout.count()-1,container)
        self.transcript.append(f'<span style="color:{color};font-weight:bold">● &nbsp;{who.upper()}</span> &nbsp; {html.escape(m["content"])} &nbsp; <span style="color:#578fae">{m.get("time","")}</span>')
        if m['role']=='assistant' and any(w in m['content'].lower() for w in ['haha','😂','lol','that’s funny','that is funny']):
            for visual in self.visuals:
                if hasattr(visual,'emotion'): visual.emotion='laughing';visual.update()
            QTimer.singleShot(1800,lambda:[setattr(v,'emotion','neutral') or v.update() for v in self.visuals if hasattr(v,'emotion')])
        QTimer.singleShot(0,lambda:self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum()))
    def voice_settings(self):
        d=QDialog(self);d.setWindowTitle('Voice configuration');v=QVBoxLayout(d)
        engine=QComboBox();engine.addItems(['Edge TTS','Kokoro (Offline)']);engine.setCurrentText(self.store.get('tts_engine'));voice=QLineEdit(self.store.get('voice'));model=QLineEdit(self.store.get('whisper_model'))
        for title,w in [('Voice engine',engine),('Voice ID',voice),('Whisper model',model)]:v.addWidget(text(title));v.addWidget(w)
        b=Button('Save','save',True);b.clicked.connect(lambda:(self.store.save({'tts_engine':engine.currentText(),'voice':voice.text(),'whisper_model':model.text()}),d.accept()));v.addWidget(b);d.resize(500,300);d.exec()
    def apply_settings(self):
        super().apply_settings()
        import desktop.reference_style as rs
        presets={'OLED Dark':'#8ebed0','Matrix Green':'#00ee88','Sunset Orange':'#ff9c00'}
        color=presets.get(self.store.get('theme'),self.store.get('accent'))
        rs.CYAN=color
        sheet=(STYLE+REFERENCE_STYLE).replace('#00d9ff',color)
        self.setStyleSheet(sheet)
        if hasattr(self,'stage'):self.stage.setStyleSheet(sheet)
        for panel in self.findChildren(Frame):panel.update()
    def tick(self):
        super().tick();self.providers_status.setText('AI CORE    '+self.engine.state+'\nPROVIDERS    '+str(sum(v=='Connected' for v in self.engine.provider_state.values()))+' tested connections\nLOCAL CORE    '+self.engine.provider_state.get('ollama','Untested'));online=any(v=='Connected' for v in self.engine.provider_state.values())
        self.connection.setText('ONLINE' if online else 'OFFLINE');self.secure_link.setText('SECURE LINK' if online else 'SECURE LINK');self.local_core.setText('LOCAL CORE');self.mode.setText('AI CORE')
        self.clock.setText(__import__('datetime').datetime.now().strftime('%a, %b %d, %Y   %I:%M %p').upper())
    def system_page(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(8,5,8,5);v.setSpacing(14);top=QHBoxLayout();top.setSpacing(15)
        vit=Vitals(large=True);self.vitals.append(vit);top.addWidget(vit,5);core=Visual(self.store,core=True);self.visuals.append(core);top.addWidget(core,6);events=self.event_panel();top.addWidget(events,5);v.addLayout(top,6)
        bottom=QHBoxLayout();bottom.setSpacing(16);terminal=Frame('›_  Command Terminal',kind='main');terminal.box.setContentsMargins(24,16,24,18);self.terminal=QTextEdit();self.terminal.setReadOnly(True);self.terminal.setStyleSheet('background:transparent;border:0;color:#87e4ff;font-family:Consolas;font-size:18px;');terminal.box.addWidget(self.terminal,1);cmd=QLineEdit();cmd.setPlaceholderText('DARTHWOLF@EMBER:~$');cmd.returnPressed.connect(lambda:(self.command(cmd.text()),cmd.clear()));terminal.box.addWidget(cmd);bottom.addWidget(terminal,8)
        drop=DropPanel();drop.selected.connect(self.file_selected);bottom.addWidget(drop,7);v.addLayout(bottom,4);return w

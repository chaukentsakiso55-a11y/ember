from __future__ import annotations
import math,time
from collections import deque
from PyQt6.QtCore import Qt,QRectF,QPointF,QTimer,pyqtSignal
from PyQt6.QtGui import QColor,QPainter,QPainterPath,QPen,QLinearGradient,QRadialGradient,QPixmap,QFont
from PyQt6.QtWidgets import QWidget,QPushButton,QLabel,QVBoxLayout,QHBoxLayout,QProgressBar,QFileDialog,QSizePolicy
from desktop.state import ROOT
CYAN='#00d9ff';MAGENTA='#ef24ff';TEXT='#c9e9ff'
_PIX={}
def art(name):
    if name not in _PIX:_PIX[name]=QPixmap(str(ROOT/'assets'/f'{name}.png'))
    return _PIX[name]
def polygon(rect,cut=11):
    r=QRectF(rect);x,y,w,h=r.x(),r.y(),r.width(),r.height();p=QPainterPath()
    for i,(a,b) in enumerate([(x+cut,y),(x+w-cut,y),(x+w,y+cut),(x+w,y+h-cut),(x+w-cut,y+h),(x+cut,y+h),(x,y+h-cut),(x,y+cut)]):
        p.moveTo(a,b) if i==0 else p.lineTo(a,b)
    p.closeSubpath();return p

def glow(p,path,color,width=1):
    p.setBrush(Qt.BrushStyle.NoBrush)
    for w,a in [(8,16),(5,28),(3,45),(width,220)]:
        c=QColor(color);c.setAlpha(a);p.setPen(QPen(c,w));p.drawPath(path)

def label(text,size=11,color=TEXT,bold=False):
    w=QLabel(text);w.setFont(QFont('Bahnschrift',size,QFont.Weight.Bold if bold else QFont.Weight.Normal));w.setStyleSheet(f'color:{color};background:transparent;border:none;font-size:{size*1.33:.1f}px;font-weight:{700 if bold else 400};');return w

class Panel(QWidget):
    def __init__(self,title='',magenta=False,parent=None):
        super().__init__(parent);self.magenta=magenta;self.glass=True;self.box=QVBoxLayout(self);self.box.setContentsMargins(16,14,16,14);self.box.setSpacing(7)
        if title:self.box.addWidget(label(title,13,CYAN,True))
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(3,3,-3,-3)
        grad=QLinearGradient(0,0,self.width(),self.height());grad.setColorAt(0,QColor('#031522'));grad.setColorAt(1,QColor('#000711'))
        p.fillPath(polygon(r),grad);glow(p,polygon(r),MAGENTA if self.magenta else CYAN,.7) if self.glass else p.strokePath(polygon(r),QPen(QColor(CYAN),1))
        p.setPen(QPen(QColor('#123243'),.5))
        for gx in range(15,self.width(),43):p.drawLine(gx,8,gx,min(58,self.height()-10))
        p.setPen(QPen(QColor('#164359'),.7));p.drawPath(polygon(r.adjusted(5,5,-5,-5)))
        p.setPen(QPen(QColor(MAGENTA),2));p.drawLine(QPointF(r.right()-58,r.bottom()),QPointF(r.right()-14,r.bottom()))
        p.setPen(QPen(QColor(CYAN),2));p.drawLine(QPointF(r.left(),r.top()+14),QPointF(r.left(),r.top()+45))
        p.setPen(QPen(QColor('#007dbe'),.8))
        for offset in (0,5):
            route=QPainterPath();route.moveTo(r.left()+35,r.bottom()-offset);route.lineTo(r.left()+75,r.bottom()-offset);route.lineTo(r.left()+84,r.bottom()-9-offset);route.lineTo(r.left()+138,r.bottom()-9-offset);p.drawPath(route)

class NeonButton(QPushButton):
    def __init__(self,text='',primary=False,parent=None):
        super().__init__(text,parent);self.primary=primary;self.setMinimumHeight(37);self.setCursor(Qt.CursorShape.PointingHandCursor);self.setFont(QFont('Bahnschrift',10));self.setStyleSheet('font-size:14px;');self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(3,3,-3,-3)
        active=self.primary or self.isChecked();color=MAGENTA if active else CYAN
        g=QLinearGradient(0,0,0,self.height());g.setColorAt(0,QColor('#600573' if active else '#041827'));g.setColorAt(1,QColor('#20072b' if active else '#000a12'))
        p.fillPath(polygon(r,5),g);glow(p,polygon(r,5),color if active or self.underMouse() else '#17618b',1)
        p.setPen(QColor('#ffffff' if self.isEnabled() else '#497086'));p.setFont(QFont('Bahnschrift',10));p.drawText(r.adjusted(6,0,-6,0),Qt.AlignmentFlag.AlignCenter,self.text())
    def enterEvent(self,e):self.update();super().enterEvent(e)
    def leaveEvent(self,e):self.update();super().leaveEvent(e)

class Toggle(QPushButton):
    def __init__(self,checked=False):
        super().__init__();self.setCheckable(True);self.setChecked(checked);self.setFixedSize(44,25);self.setCursor(Qt.CursorShape.PointingHandCursor)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(3,4,37,18);path=QPainterPath();path.addRoundedRect(r,9,9)
        p.fillPath(path,QColor(MAGENTA if self.isChecked() else '#082039'));glow(p,path,MAGENTA if self.isChecked() else '#28627d',.5)
        p.setBrush(QColor('#e6f7ff'));p.setPen(Qt.PenStyle.NoPen);p.drawEllipse(QRectF(23 if self.isChecked() else 5,5,16,16))

class Artwork(QWidget):
    def __init__(self,name,source=None):super().__init__();self.name=name;self.source=source;self.setMinimumSize(60,60)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform);pix=art(self.name);src=QRectF(*(self.source or (0,0,pix.width(),pix.height())))
        target=QRectF(self.rect());p.setClipPath(polygon(target.adjusted(2,2,-2,-2)));p.drawPixmap(target,pix,src);glow(p,polygon(target.adjusted(2,2,-2,-2)),MAGENTA,.8)

class Visual(QWidget):
    def __init__(self,store,core=False,mini=False):
        super().__init__();self.store=store;self.force_core=core;self.mini=mini;self.level=0.;self.openness=0.;self.widthness=.5;self.holo=None;self.last_tick=time.monotonic();self.state='STANDBY';self.start=time.monotonic();self.setMinimumSize(180,150)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(33)
    def tick(self):
        if self.isVisible() and self.store.get('animations'):self.update()
    def audio(self,level,openness=0.,width=.5):self.level=level;self.openness=openness;self.widthness=width;self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform);r=QRectF(self.rect()).adjusted(4,4,-4,-4);p.setClipPath(polygon(r));p.fillRect(r,QColor('#000912'))
        t=time.monotonic()-self.start if self.store.get('animations') else 0
        if self.force_core or self.store.get('visual')=='Core':self.core(p,r,t)
        else:self.face(p,r,t)
        p.setClipping(False);glow(p,polygon(r),CYAN);glow(p,polygon(r.adjusted(5,5,-5,-5)),MAGENTA,.7)
    def face(self,p,r,t):
        if self.store.get('avatar')=='Original Hologram':
            from core.avatar import HoloAvatar
            if self.holo is None:self.holo=HoloAvatar()
            now=time.monotonic();self.holo.step(now-self.last_tick,self.level,speaking=self.state=='SPEAKING',state=self.state,v_open=self.openness,v_wide=self.widthness);self.last_tick=now
            self.holo.paint(p,r.center().x(),r.center().y(),min(r.width(),r.height())*.38,QColor(CYAN),QColor(MAGENTA));return
        if self.store.get('avatar')=='Current Ember':
            side=min(r.width(),r.height());target=QRectF(r.center().x()-side/2,r.center().y()-side/2,side,side);p.drawPixmap(target,art('appearance'),QRectF(1084,348,221,191));return
        pix=art('live')
        custom=self.store.get('background')
        if custom and not QPixmap(custom).isNull():p.drawPixmap(r,QPixmap(custom),QRectF(QPixmap(custom).rect()))
        else:p.drawPixmap(r,pix,QRectF(270,199,900,120))
        shade=QColor('#00101b');shade.setAlpha(155);p.fillRect(r,shade)
        source=QRectF(516,196,440,342)
        if self.mini:
            p.drawPixmap(r,art('appearance'),QRectF(1385,121,257,254));return
        h=r.height();w=h*440/342;dest=QRectF(r.center().x()-w/2,r.top(),w,h)
        for i in range(0,342,3):
            sway=math.sin(t*1.1+i*.009)*(.65 if i<220 else .3)
            p.drawPixmap(QRectF(dest.x()+sway,dest.y()+i*h/342,w,3*h/342+.6),pix,QRectF(516,196+i,440,3))
        scale=h/342
        if self.state=='SPEAKING' and self.openness>.03:
            mouth=QRectF(dest.x()+189*scale,dest.y()+197*scale,60*scale,30*scale)
            p.drawPixmap(mouth.adjusted(-self.widthness*scale,0,self.widthness*scale,self.openness*7*scale),pix,QRectF(705,393,60,30))
        blink=max(0.,1.-abs((t%5.2)-.12)/.12)
        if blink>0:
            p.setPen(QPen(QColor('#74527d'),max(1,9*scale*blink)))
            for x,y in [(177,136),(237,130)]:p.drawLine(QPointF(dest.x()+x*scale,dest.y()+y*scale),QPointF(dest.x()+(x+27)*scale,dest.y()+(y-2)*scale))
        if r.width()>560:
            p.setFont(QFont('Bahnschrift',17,QFont.Weight.Bold));p.setPen(QColor(MAGENTA));p.drawText(QPointF(r.x()+30,r.y()+h*.43),'EMBER')
            p.setFont(QFont('Bahnschrift',8));p.setPen(QColor(CYAN));p.drawText(QRectF(r.x()+30,r.y()+h*.46,190,55),0,'VOICE • VISION • AUTOMATION\nLOCAL INTELLIGENCE')
            p.drawText(QRectF(r.x()+30,r.bottom()-80,180,60),0,'AI CORE     '+self.state+'\nVOICE LINK  USER CONTROLLED\nVISION      ON DEMAND')
            p.drawText(QRectF(r.right()-190,r.bottom()-110,180,95),0,'◇ NATURAL CONVERSATION\n\n◇ CONTEXT AWARE\n\n◇ MULTI-MODAL\n\n◇ PRIVACY FIRST')
    def core(self,p,r,t):
        src=QRectF(548,102,575,447);p.drawPixmap(r,art('core'),src)
        cx,cy=r.center().x(),r.top()+r.height()*.46;radius=min(r.width()*.34,r.height()*.39)
        p.save();p.translate(cx,cy);p.rotate(t*9)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for j in range(4):
            color=QColor(CYAN if j%2==0 else MAGENTA);color.setAlpha(160);p.setPen(QPen(color,1.5+self.level*2));rr=radius*(.85+j*.075)
            p.drawArc(QRectF(-rr,-rr,rr*2,rr*2),j*85*16,55*16)
        p.restore()
        for i in range(18 if self.store.get('particles') else 0):
            a=i*2.399+t*.2;rr=radius*(.4+.5*(math.sin(i*4.3+t*.1)*.5+.5));p.setPen(QColor(CYAN if i%2 else MAGENTA));p.drawEllipse(QPointF(cx+math.cos(a)*rr,cy+math.sin(a)*rr),1.2,1.2)

class Waveform(QWidget):
    def __init__(self):
        super().__init__();self.values=deque([0.]*100,maxlen=100);self.state='MIC OFF';self.seconds=0;self.setFixedHeight(80)
    def audio(self,level,*args):self.values.append(level);self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(3,3,-3,-3);p.fillPath(polygon(r),QColor('#00101e'));glow(p,polygon(r),CYAN,.5)
        p.setFont(QFont('Bahnschrift',9));p.setPen(QColor(MAGENTA));p.drawText(QRectF(18,25,130,30),0,self.state)
        left,right=145,self.width()-140;mid=(left+right)/2;cy=self.height()/2
        p.setPen(QPen(QColor('#104465'),1));p.drawLine(QPointF(left,cy),QPointF(right,cy))
        for i,v in enumerate(self.values):
            x=left+i*(right-left)/100;p.setPen(QPen(QColor(CYAN if x<mid else MAGENTA),2));p.drawLine(QPointF(x,cy-v*29),QPointF(x,cy+v*29))
        p.setBrush(QColor('#021327'));p.setPen(QPen(QColor(CYAN),2));p.drawEllipse(QPointF(mid,cy),29,29);p.setPen(QColor(CYAN));p.drawText(QRectF(mid-20,cy-20,40,40),Qt.AlignmentFlag.AlignCenter,'MIC')
        p.drawText(QRectF(right+20,20,115,45),0,f'LIVE VOICE\n{self.seconds//60:02d}:{self.seconds%60:02d}')

class Vitals(Panel):
    def __init__(self):
        super().__init__('SYSTEM VITALS');self.rows={}
        for name in ['CPU','RAM','GPU','TEMP','NET']:
            row=QHBoxLayout();row.addWidget(label(name,9),1);bar=QProgressBar();bar.setRange(0,100);bar.setValue(0);bar.setTextVisible(False);bar.setFixedHeight(9)
            bar.setStyleSheet('QProgressBar{background:#092336;border:0;}QProgressBar::chunk{background:'+ (MAGENTA if name in ['RAM','TEMP'] else CYAN)+';}');row.addWidget(bar,2)
            val=label('N/A',9);val.setMinimumWidth(62);val.setAlignment(Qt.AlignmentFlag.AlignRight);row.addWidget(val,1);self.box.addLayout(row);self.rows[name]=(bar,val)
    def refresh(self,data):
        for name,(bar,val) in self.rows.items():
            n=data.get(name)
            if n is None:bar.setValue(0);val.setText('N/A');continue
            if name=='NET':val.setText(f'{n/1024:.0f} KB/s');bar.setValue(min(100,int(n/(1024*1024)*10)))
            else:bar.setValue(int(n));val.setText(f'{n:.0f}'+('°C' if name=='TEMP' else '%'))

class DropPanel(Panel):
    selected=pyqtSignal(str)
    def __init__(self):
        super().__init__('▧  Data Intake');self.setAcceptDrops(True);self.box.addStretch();self.box.addWidget(label('DROP FILES INTO EMBER',18,CYAN,True),0,Qt.AlignmentFlag.AlignCenter);self.box.addWidget(label('Documents • Images • Audio • Project Files',10),0,Qt.AlignmentFlag.AlignCenter)
        b=NeonButton('▱  SELECT FILE');b.clicked.connect(self.browse);self.box.addWidget(b);self.box.addStretch()
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Select a file')
        if path:self.selected.emit(path)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls() and any(u.isLocalFile() for u in e.mimeData().urls()):e.acceptProposedAction()
    def dropEvent(self,e):
        for u in e.mimeData().urls():
            if u.isLocalFile():self.selected.emit(u.toLocalFile());break
        e.acceptProposedAction()

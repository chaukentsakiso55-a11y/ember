from __future__ import annotations
import math
from PyQt6.QtCore import Qt,QRectF,QPointF,QTimer
from PyQt6.QtGui import QFont,QFontDatabase,QPainter,QPainterPath,QPen,QColor,QLinearGradient,QRadialGradient,QPixmap
from PyQt6.QtWidgets import QWidget,QPushButton,QLabel,QVBoxLayout,QHBoxLayout,QSizePolicy
from desktop.state import ROOT
from desktop.widgets import art,polygon,glow

CYAN='#00dcff';MAGENTA='#ed20fa';WHITE='#d1eaff';MUTED='#6ca3c6'

def fonts():
    for p in (ROOT/'assets/fonts').glob('*.ttf'):QFontDatabase.addApplicationFont(str(p))

def font(size=18,bold=False,display=False):
    f=QFont('Orbitron' if display else 'Rajdhani');f.setPixelSize(size);f.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Medium);return f

def text(value,size=18,color=WHITE,bold=False,display=False):
    w=QLabel(value);w.setFont(font(size,bold,display));w.setStyleSheet(f'background:transparent;border:0;color:{color};font-family:{"Orbitron" if display else "Rajdhani"};font-size:{size}px;font-weight:{700 if bold else 500};');return w

def lines(p,pts):
    path=QPainterPath()
    for i,(x,y) in enumerate(pts):path.moveTo(x,y) if i==0 else path.lineTo(x,y)
    p.drawPath(path)

def icon(p,name,r,color=CYAN):
    p.save();p.translate(r.x(),r.y());p.scale(r.width()/32,r.height()/32);p.setPen(QPen(QColor(color),1.8,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin));p.setBrush(Qt.BrushStyle.NoBrush)
    if name in ['Home','home']:lines(p,[(2,15),(16,3),(30,15),(26,15),(26,29),(19,29),(19,20),(12,20),(12,29),(6,29),(6,15),(2,15)])
    elif name in ['AI Chat','chat']:p.drawRoundedRect(QRectF(3,5,26,19),6,6);lines(p,[(8,24),(7,30),(15,24)]);[p.drawEllipse(QPointF(x,14),1,1) for x in [10,16,22]]
    elif name in ['System Intel','chart']:
        for x,y in [(4,19),(13,12),(22,5)]:p.drawRect(QRectF(x,y,5,28-y))
    elif name in ['Weather','cloud']:
        path=QPainterPath();path.moveTo(8,25);path.cubicTo(-2,24,1,12,8,12);path.cubicTo(7,0,24,0,24,12);path.cubicTo(34,12,34,25,25,25);path.closeSubpath();p.drawPath(path)
    elif name in ['News','news']:p.drawRoundedRect(QRectF(4,3,24,26),2,2);p.drawRect(QRectF(8,7,7,7));[p.drawLine(19,y,24,y) for y in [8,13]];[p.drawLine(8,y,24,y) for y in [19,24]]
    elif name in ['Applications','apps']:
        for x in [4,18]:
            for y in [4,18]:p.drawRoundedRect(QRectF(x,y,10,10),1,1)
    elif name in ['Flight Finder','flight']:lines(p,[(2,13),(12,11),(23,2),(27,3),(20,14),(28,22),(26,25),(16,19),(10,29),(7,28),(9,17),(2,15),(2,13)])
    elif name in ['File Analysis','file']:lines(p,[(6,2),(21,2),(28,10),(28,30),(6,30),(6,2)]);lines(p,[(21,2),(21,10),(28,10)]);[p.drawLine(11,y,23,y) for y in [15,20,25]]
    elif name in ['Settings','settings']:
        points=[]
        for i in range(32):
            a=i*math.pi/16;rr=14 if i%4 in [1,2] else 11;points.append((16+math.cos(a)*rr,16+math.sin(a)*rr))
        lines(p,points+[points[0]]);p.drawEllipse(QPointF(16,16),5,5)
    elif name in ['About','info']:p.drawEllipse(QPointF(16,16),13,13);p.drawLine(16,14,16,23);p.drawEllipse(QPointF(16,8),.8,.8)
    elif name in ['General','monitor','System']:p.drawRoundedRect(QRectF(3,4,26,18),1,1);p.drawLine(16,22,16,28);p.drawLine(10,28,22,28)
    elif name in ['Appearance','palette']:p.drawEllipse(QPointF(16,15),13,12);[p.drawEllipse(QPointF(x,y),1,1) for x,y in [(10,9),(18,7),(24,13),(8,17)]];p.drawEllipse(QPointF(18,20),4,3)
    elif name in ['Integrations','link']:p.save();p.translate(16,16);p.rotate(40);p.drawRoundedRect(QRectF(-6,-15,12,18),6,6);p.drawRoundedRect(QRectF(-6,-3,12,18),6,6);p.restore()
    elif name in ['Advanced','sliders']:
        for y,x in [(6,11),(16,22),(26,15)]:p.drawLine(2,y,30,y);p.drawRect(QRectF(x-2,y-4,4,8))
    elif name in ['mic','Voice']:p.drawRoundedRect(QRectF(11,3,10,18),5,5);p.drawArc(QRectF(6,6,20,20),180*16,180*16);p.drawLine(16,26,16,30);p.drawLine(10,30,22,30)
    elif name=='camera':p.drawRect(QRectF(3,7,18,18));lines(p,[(21,12),(29,7),(29,25),(21,20)])
    elif name=='search':p.drawEllipse(QRectF(4,3,18,18));p.drawLine(21,20,29,29)
    elif name=='send':lines(p,[(3,3),(30,16),(3,29),(9,16),(3,3)]);p.drawLine(9,16,30,16)
    elif name=='attach':
        path=QPainterPath();path.moveTo(20,7);path.lineTo(9,21);path.cubicTo(5,27,13,29,17,24);path.lineTo(27,11);path.cubicTo(33,0,21,-1,16,6);path.lineTo(5,20);path.cubicTo(-3,32,12,38,21,27);p.drawPath(path)
    elif name=='end':p.drawArc(QRectF(2,11,28,19),15*16,150*16);p.drawRoundedRect(QRectF(2,17,6,8),2,2);p.drawRoundedRect(QRectF(24,17,6,8),2,2)
    elif name=='save':p.drawRect(QRectF(4,3,24,27));p.drawRect(QRectF(8,3,14,10));p.drawRect(QRectF(9,20,14,10))
    elif name=='reset':p.drawArc(QRectF(5,4,23,24),-110*16,290*16);lines(p,[(3,6),(3,15),(12,15)])
    elif name=='shield':lines(p,[(16,2),(28,7),(26,20),(16,30),(6,20),(4,7),(16,2)]);lines(p,[(10,15),(14,20),(23,10)])
    elif name=='more':
        for x in [5,16,27]:p.drawEllipse(QPointF(x,16),1.5,1.5)
    elif name=='AI & Models':
        lines(p,[(15,4),(10,2),(6,7),(2,10),(3,19),(7,21),(7,27),(14,30),(15,4)]);lines(p,[(18,4),(23,2),(27,7),(30,10),(29,19),(25,21),(25,27),(18,30),(18,4)]);lines(p,[(6,10),(11,13),(8,17),(12,23)]);lines(p,[(25,10),(21,13),(24,17),(21,23)])
    else:p.drawEllipse(QPointF(16,16),11,11);p.drawEllipse(QPointF(16,16),5,5)
    p.restore()

SLICES={'main':('live',(249,104,939,785),15),'nav':('live',(13,107,223,648),14),'right':('live',(1196,105,462,783),15),'settings':('appearance',(250,106,1110,781),15),'header':('live',(8,8,1655,91),12),'footer':('live',(8,893,1655,43),8),'portrait':('appearance',(1370,104,289,283),12)}
def frame_skin(p,r,kind):
    name,coords,b=SLICES[kind];sx,sy,sw,sh=coords;pix=art(name);x,y,w,h=r.x(),r.y(),r.width(),r.height()
    segments=[((x,y,b,b),(sx,sy,b,b)),((x+w-b,y,b,b),(sx+sw-b,sy,b,b)),((x,y+h-b,b,b),(sx,sy+sh-b,b,b)),((x+w-b,y+h-b,b,b),(sx+sw-b,sy+sh-b,b,b)),((x+b,y,w-2*b,b),(sx+b,sy,sw-2*b,b)),((x+b,y+h-b,w-2*b,b),(sx+b,sy+sh-b,sw-2*b,b)),((x,y+b,b,h-2*b),(sx,sy+b,b,sh-2*b)),((x+w-b,y+b,b,h-2*b),(sx+sw-b,sy+b,b,sh-2*b))]
    for i,(target,source) in enumerate(segments):
        if kind=='nav' and i>=6:
            p.setPen(QPen(QColor(CYAN if i==6 else MAGENTA),.9));p.drawLine(QPointF(x+7 if i==6 else x+w-7,y+14),QPointF(x+7 if i==6 else x+w-7,y+h-17))
        else:p.drawPixmap(QRectF(*target),pix,QRectF(*source))

class Frame(QWidget):
    def __init__(self,title='',kind='card',parent=None):
        super().__init__(parent);self.kind=kind;self.box=QVBoxLayout(self);self.box.setContentsMargins(15,13,15,13);self.box.setSpacing(8)
        if title:self.box.addWidget(text(title,21,CYAN,True))
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(1,1,-1,-1);g=QLinearGradient(0,0,self.width(),self.height());g.setColorAt(0,QColor('#03131f'));g.setColorAt(.6,QColor('#000b14'));g.setColorAt(1,QColor('#050d1a'));p.fillPath(polygon(r,8),g)
        if self.kind in SLICES:frame_skin(p,QRectF(self.rect()),self.kind)
        else:
            p.setPen(QPen(QColor('#155777'),.8));p.drawPath(polygon(r,7));p.setPen(QPen(QColor('#063247'),.5));p.drawPath(polygon(r.adjusted(3,3,-3,-3),5))
        if self.kind in ['settings','main']:
            p.setPen(QPen(QColor(0,130,185,12),.5))
            for x in range(14,self.width()-10,26):p.drawLine(x,13,x,min(100,self.height()-13))
            for y in range(14,min(100,self.height()-13),20):p.drawLine(14,y,self.width()-14,y)

class Button(QPushButton):
    def __init__(self,title,icon_name='',primary=False,nav=False,parent=None):
        super().__init__(title,parent);self.icon_name=icon_name;self.primary=primary;self.nav=nav;self.setFont(font(19));self.setMinimumHeight(42);self.setCursor(Qt.CursorShape.PointingHandCursor);self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed);self.setAccessibleName(title or icon_name)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(2,2,-2,-2);active=self.primary or self.isChecked();col=MAGENTA if active else CYAN
        if not self.nav or active or self.underMouse() or self.hasFocus():
            g=QLinearGradient(0,0,0,self.height());g.setColorAt(0,QColor('#620a7a' if active else '#021523'));g.setColorAt(.4,QColor('#30023d' if active else '#02111e'));g.setColorAt(1,QColor('#13071f' if active else '#010915'));p.fillPath(polygon(r,6),g)
            glow(p,polygon(r,6),col if active or self.hasFocus() else '#166389',1)
            if active:glow(p,polygon(r.adjusted(2,2,-2,-2),4),'#fd75ff',.8)
        if not self.isEnabled():p.setOpacity(.45)
        if self.icon_name:
            size=31 if self.nav else 24;ix=18 if self.nav else max(10,(self.width()-len(self.text())*8-size-14)/2);iy=(self.height()-size)/2
            if self.nav:
                p.save();p.setOpacity(.20);icon(p,self.icon_name,QRectF(ix-2,iy-2,size+4,size+4),col);p.restore()
            icon(p,self.icon_name,QRectF(ix,iy,size,size),col if self.nav else WHITE)
            tx=ix+size+17 if self.nav else ix+size+9
            rect=QRectF(tx,0,self.width()-tx-5,self.height());align=Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft
        else:rect=r;align=Qt.AlignmentFlag.AlignCenter
        p.setFont(font(21 if self.nav else 18,self.isChecked()));p.setPen(QColor(WHITE));p.drawText(rect,align,self.text())
        if self.hasFocus():p.setPen(QPen(QColor('#ffffff'),1,Qt.PenStyle.DotLine));p.drawPath(polygon(r.adjusted(4,4,-4,-4),3))
    def enterEvent(self,e):self.update();super().enterEvent(e)
    def leaveEvent(self,e):self.update();super().leaveEvent(e)

class Header(Frame):
    def __init__(self,host):
        super().__init__(kind='header');self.setFixedHeight(92);self.host=host
        for i in reversed(range(self.box.count())):self.box.takeAt(i)
        self.status=Button('ONLINE','');self.status.setParent(self);self.status.setGeometry(1141,22,121,49);self.status.clicked.connect(lambda:host.navigate('Settings'))
        self.providers=Button('SECURE LINK','Integrations');self.providers.setParent(self);self.providers.setGeometry(1273,22,147,49);self.providers.clicked.connect(lambda:(host.navigate('Settings'),host.settings.select(1)))
        self.local=Button('LOCAL CORE','');self.local.setParent(self);self.local.setGeometry(1431,22,145,49);self.local.clicked.connect(lambda:(host.navigate('Settings'),host.settings.select(1)))
        self.visual=Button('AI CORE','',True);self.visual.setParent(self);self.visual.setGeometry(1581,22,79,49);self.visual.clicked.connect(host.switch_visual)
    def paintEvent(self,e):
        super().paintEvent(e);p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QColor(CYAN));p.setFont(font(12,False,True));p.drawText(QRectF(388,12,172,35),Qt.AlignmentFlag.AlignCenter,'v2.0 // CYBERPUNK HUD')
        p.setPen(QPen(QColor('#1a5370'),.7));p.drawPath(polygon(QRectF(381,11,179,37),5));f=font(44,True,True);f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing,2.2);p.setFont(f);path=QPainterPath();path.addText(77,52,p.font(),'[ EMBER ]');glow(p,path,MAGENTA,1);p.fillPath(path,QColor('#fc94ff'))
        p.setFont(font(16,True));p.setPen(QColor(CYAN));p.drawText(QRectF(118,56,265,25),Qt.AlignmentFlag.AlignCenter,'N E U R A L  C O M M A N D  N O D E')
        icon(p,'shield',QRectF(26,21,35,39),CYAN)
        p.setFont(font(23,True));p.drawText(QRectF(731,19,383,42),Qt.AlignmentFlag.AlignCenter,'INTELLIGENCE. CONTROL. AMPLIFIED.')
        route=QPainterPath();route.moveTo(680,4);route.lineTo(745,67);route.lineTo(1090,67);route.lineTo(1140,17);glow(p,route,MAGENTA,.7)
        p.setPen(QPen(QColor(MAGENTA),1));lines(p,[(565,55),(585,55),(591,44),(598,64),(605,29),(610,65),(616,18),(621,57),(628,41),(632,58),(640,50),(658,55),(682,55)])

class Swatch(QPushButton):
    def __init__(self,color):super().__init__();self.color=color;self.setFixedSize(44,46);self.setCheckable(True);self.setAccessibleName('Accent '+color)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QPen(QColor(self.color),2 if self.isChecked() else .7));p.setBrush(QColor('#00101b'));p.drawEllipse(QRectF(1,2,41,41));p.setBrush(QColor(self.color));p.drawEllipse(QRectF(6,7,31,31))

class Vitals(Frame):
    def __init__(self,large=False):
        super().__init__(kind='card');self.large=large;self.data={};self.box.setContentsMargins(0,0,0,0)
    def refresh(self,data):self.data=data;self.update()
    def paintEvent(self,e):
        super().paintEvent(e);p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);w,h=self.width(),self.height()
        p.setFont(font(24 if self.large else 20,True));p.setPen(QColor(CYAN));p.drawText(QRectF(17,10,w-34,34),0,'⌁  System Vitals' if self.large else 'SYSTEM VITALS');p.setPen(QPen(QColor('#17506f'),1));p.drawLine(14,44,w-14,44)
        row_h=57 if self.large else 26;start=60 if self.large else 48;names=['CPU','RAM','GPU','NET','TEMP'] if self.large else ['CPU','RAM','GPU','TEMP','NET']
        for i,name in enumerate(names):
            y=start+i*row_h;v=self.data.get(name);col=MAGENTA if name in ['RAM','NET'] else CYAN;p.setFont(font(18 if self.large else 16,True));p.setPen(QColor('#92cdff'));p.drawText(QRectF(18,y,w*.23,25),0,{'CPU':'CPU LOAD','NET':'NETWORK'}.get(name,name) if self.large else name)
            bx=120 if self.large else 86;bw=w-bx-(78 if self.large else 71);bh=17 if self.large else 8;by=y+5
            p.fillRect(QRectF(bx,by,bw,bh),QColor('#092137'));n=0 if v is None else min(100,v/(1024*1024)*10 if name=='NET' else v);gradient=QLinearGradient(bx,0,bx+bw,0);gradient.setColorAt(0,QColor(col));gradient.setColorAt(1,QColor('#8fb2ff' if name=='RAM' else col));p.fillRect(QRectF(bx,by,bw*n/100,bh),gradient)
            if self.large:
                path=polygon(QRectF(bx-3,by-3,bw+6,bh+6),3);glow(p,path,'#17618c',.7)
                p.setPen(QPen(QColor(120,225,255,50),.6))
                for k in range(0,int(bw),8):p.drawLine(QPointF(bx+k,by+2),QPointF(bx+k,by+bh-2))
            value='N/A' if v is None else (f'{v/1024:.0f} KB/s' if name=='NET' else f'{v:.0f}'+('°C' if name=='TEMP' else '%'));p.setPen(QColor(WHITE));p.drawText(QRectF(w-77,y,64,25),Qt.AlignmentFlag.AlignRight,value)
        if self.large:
            by=start+5*row_h+8;bw=(w-42)/3
            for i,(title,value,col) in enumerate([('AI CORE','STANDBY','#00edb7'),('FIREWALL','UNVERIFIED',CYAN),('PROTOCOL','EMBER',MAGENTA)]):
                r=QRectF(14+i*(bw+7),by,bw,70);p.fillPath(polygon(r,8),QColor('#001421'));glow(p,polygon(r,8),col,.6);p.setFont(font(13));p.setPen(QColor(col));p.drawText(r.adjusted(10,10,-5,-35),0,title);p.setFont(font(18,True));p.drawText(r.adjusted(10,35,-5,0),0,value)

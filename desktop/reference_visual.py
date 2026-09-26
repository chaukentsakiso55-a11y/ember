from __future__ import annotations
import math,time
from PyQt6.QtCore import Qt,QRectF,QPointF
from PyQt6.QtGui import QColor,QPainter,QPen,QPainterPath,QLinearGradient,QRadialGradient
from desktop.widgets import Visual as BaseVisual,art,polygon,glow,Waveform as BaseWave
from desktop.reference_style import font,icon,CYAN,MAGENTA,frame_skin

class Visual(BaseVisual):
    def __init__(self,store,core=False,mini=False):
        super().__init__(store,core=core,mini=mini);self.emotion='neutral'
    def face(self,p,r,t):
        if self.store.get('avatar')=='Original Hologram':super().face(p,r,t);return
        if self.mini:
            src=(1385,121,257,254) if self.store.get('avatar')=='Reference Female' else (1084,348,221,191)
            p.drawPixmap(r,art('appearance'),QRectF(*src));return
        if self.store.get('avatar')=='Current Ember':super().face(p,r,t);return
        p.save();p.translate(r.x(),r.y());p.scale(r.width()/906,r.height()/339)
        p.drawPixmap(QRectF(0,0,906,339),art('live'),QRectF(267,197,906,339))
        state_box=QRectF(20,229,222,99)
        gradient=QLinearGradient(0,229,240,330);gradient.setColorAt(0,QColor(0,12,22,180));gradient.setColorAt(1,QColor(1,9,22,210));p.drawPixmap(state_box,art('live'),QRectF(275,212,220,99));p.fillRect(state_box,gradient)
        p.setPen(QPen(QColor('#085071'),.7));p.drawLine(21,229,225,229)
        p.setFont(font(11,True));p.setPen(QColor('#a9d4f8'))
        labels=[('AI CORE',self.state),('VOICE LINK','ACTIVE' if self.state in ['LISTENING','SPEAKING'] else 'STANDBY'),('VISION FEED','ON DEMAND'),('RESPONSE','REAL-TIME' if self.state=='SPEAKING' else 'AWAITING INPUT')]
        for i,(k,v) in enumerate(labels):
            y=253+i*18;p.drawText(QRectF(54,y-10,92,18),0,k);p.setPen(QColor('#00f5bd' if v=='ACTIVE' else CYAN));p.drawText(QRectF(150,y-10,105,18),0,v);p.setPen(QColor('#a9d4f8'))
        if self.store.get('animations') and self.store.get('animated_avatar'):
            # Local mesh strips deform the supplied artwork; no replacement face.
            source=art('live');x0,y0,w,h=521,202,420,332
            head_dx=math.sin(t*.72)*4.8 + (math.sin(t*2.1)*.7 if self.state=='LISTENING' else 0)
            head_dy=math.sin(t*1.15)*1.8
            gaze=math.sin(t*.43)*1.35
            for y in range(0,h,4):
                weight=math.sin(math.pi*y/h)**2
                hair=math.sin(t*(1.35 if self.emotion=='laughing' else .8)+y*.021)*(3.5 if self.emotion=='laughing' else 1.6)*weight
                breath=math.sin(t*1.2)*.4*max(0,(y-200)/132)
                p.drawPixmap(QRectF(x0-267+hair+head_dx,y0-197+y+breath+head_dy,w,4.15),source,QRectF(x0,y0+y,w,4))
            if self.state=='SPEAKING' and self.openness>.02 or self.emotion=='laughing':
                x,y=441+head_dx,199+head_dy;op=(self.openness*7 if self.emotion!='laughing' else 3.5);spread=(self.widthness-.5)*3
                p.drawPixmap(QRectF(x-spread,y,51+spread*2,23+op),source,QRectF(708,396,51,23))
            # Tiny gaze highlights move over the supplied eyes while preserving the reference face.
            p.setPen(QPen(QColor(130,225,255,165),1.2));p.setBrush(QColor(130,225,255,95))
            for ex,ey in [(426,141),(490,133)]: p.drawEllipse(QPointF(ex+gaze,ey),1.8,1.8)
            blink=max(0,1-abs((t%5.6)-4.8)/.095)
            if blink>0:
                p.setPen(QPen(QColor('#83506c'),blink*5))
                for x,y in [(413,136),(477,128)]:p.drawLine(QPointF(x,y),QPointF(x+27,y-2))
            if self.state in ('SPEAKING','LISTENING') or self.emotion=='laughing':
                p.setPen(QPen(QColor(238,38,255,90),1.1))
                for i in range(5):
                    hx=170+i*18+math.sin(t*1.4+i)*3; p.drawArc(QRectF(hx,45+i*4,75,180),40,95)
        p.restore()

class Waveform(BaseWave):
    def __init__(self):super().__init__();self.setFixedHeight(91)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);r=QRectF(self.rect()).adjusted(2,2,-2,-2);p.fillPath(polygon(r),QColor('#00101d'));glow(p,polygon(r),CYAN,.7);p.setPen(QPen(QColor('#104663'),.7));p.drawPath(polygon(r.adjusted(6,6,-6,-6)))
        left=QRectF(19,16,154,60);right=QRectF(self.width()-180,16,154,60)
        for rect in [left,right]:p.fillPath(polygon(rect,6),QColor('#010a17'));glow(p,polygon(rect,6),MAGENTA,.7)
        p.setFont(font(13,True));p.setPen(QColor(MAGENTA));p.drawText(left.adjusted(13,8,-5,-20),0,self.state)
        vals=list(self.values)
        for i in range(13):p.fillRect(QRectF(33+i*9,54,5,14),QColor(MAGENTA if vals[-1]*13>i else '#08253a'))
        p.setFont(font(13));p.setPen(QColor('#83cafb'));p.drawText(right.adjusted(14,5,0,0),0,'LIVE VOICE');p.setFont(font(27));p.drawText(right.adjusted(15,24,0,0),0,f'{self.seconds//60:02d}:{self.seconds%60:02d}')
        x1,x2=181,self.width()-188;cx=(x1+x2)/2;cy=46;p.setPen(QPen(QColor('#034265'),1));p.drawLine(QPointF(x1,cy),QPointF(x2,cy))
        for i,a in enumerate(vals):
            x=x1+i*(x2-x1)/len(vals);path=QPainterPath();path.moveTo(x,cy-a*33);path.lineTo(x,cy+a*33);glow(p,path,CYAN if i%40<20 else MAGENTA,1.2)
        p.setBrush(QColor('#001222'))
        for rr,col in [(41,CYAN),(35,'#1261bf'),(30,MAGENTA)]:p.setPen(QPen(QColor(col),1.3));p.drawEllipse(QPointF(cx,cy),rr,rr)
        icon(p,'mic',QRectF(cx-15,cy-19,30,38),CYAN)

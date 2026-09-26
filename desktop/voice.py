from __future__ import annotations
import asyncio, threading, time
import numpy as np
from PyQt6.QtCore import QObject,pyqtSignal
from desktop.services import Jobs

EDGE_VOICE_ALIASES={}
KOKORO_VOICE_ALIASES={}

class Voice(QObject):
    audio=pyqtSignal(float,float,float)
    heard=pyqtSignal(str)
    status=pyqtSignal(str)
    error=pyqtSignal(str)
    finished=pyqtSignal()
    frame=pyqtSignal(bytes)
    def __init__(self,store):
        super().__init__();self.store=store;self.listening=False;self.speaking=False;self.camera=False;self.stopper=threading.Event();self.play_stop=threading.Event();self.jobs=Jobs();self.jobs.failed.connect(self.failed);self.jobs.done.connect(self.done);self.stt=None;self.capture=None
    def failed(self,name,error):
        self.listening=False;self.speaking=False;self.audio.emit(0,0,.5);self.status.emit('ERROR');self.error.emit(error);self.finished.emit()
    def done(self,name,result):
        if name=='transcribe':
            self.status.emit('MIC OFF')
            if result:self.heard.emit(result)
        if name=='speak':self.speaking=False;self.audio.emit(0,0,.5);self.finished.emit()
    def toggle(self):
        if self.listening:self.stop();return
        self.stopper.clear();self.listening=True;self.status.emit('LISTENING')
        self.jobs.run('record',self.record)
    def record(self):
        import sounddevice as sd
        frames=[];seconds=0
        try:
            with sd.InputStream(samplerate=16000,channels=1,dtype='float32',blocksize=800) as stream:
                while not self.stopper.is_set() and seconds<30:
                    data,_=stream.read(800);frames.append(data.copy());seconds+=.05
                    self.audio.emit(min(1,float(np.sqrt(np.mean(data**2)))*8),0,.5)
        finally:self.listening=False;self.audio.emit(0,0,.5)
        if not frames or self.stopper.is_set():return
        self.transcribe(np.concatenate(frames)[:,0])
    def finish_recording(self):
        if not self.listening:return
        self.stopper.set();self.listening=False
    def transcribe(self,audio):
        self.status.emit('TRANSCRIBING')
        def run():
            from core.stt import WhisperSTT
            if self.stt is None:self.stt=WhisperSTT(self.store.get('whisper_model'))
            return self.stt.transcribe(audio)
        self.jobs.run('transcribe',run)
    def record_turn(self):
        if self.listening:self.status.emit('ALREADY LISTENING');return
        self.stopper.clear();self.listening=True;self.status.emit('LISTENING')
        def run():
            import sounddevice as sd
            frames=[];silent=0;spoken=False
            try:
                with sd.InputStream(samplerate=16000,channels=1,dtype='float32',blocksize=800) as stream:
                    for _ in range(600):
                        if self.stopper.is_set():return
                        data,_=stream.read(800);rms=float(np.sqrt(np.mean(data**2)));self.audio.emit(min(1,rms*8),0,.5)
                        frames.append(data.copy())
                        if rms>.012:spoken=True;silent=0
                        else:silent+=1
                        if spoken and silent>22:break
            finally:self.listening=False;self.audio.emit(0,0,.5)
            if spoken:self.transcribe(np.concatenate(frames)[:,0])
            else:self.status.emit('NO SPEECH')
        self.jobs.run('record',run)
    def speak(self,text):
        if not self.store.get('tts'):return
        self.play_stop.set();self.play_stop=threading.Event();stop=self.play_stop
        def run():
            import sounddevice as sd
            self.status.emit('GENERATING VOICE')
            if self.store.get('tts_engine')=='Gemini TTS' or self.store.get('voice')=='Aoede':
                from desktop.gemini_backend import speech
                raw=speech(text,self.store.get('voice') or 'Aoede');samples=np.frombuffer(raw,dtype='<i2').astype(np.float32)/32768;rate=24000
            elif self.store.get('tts_engine')=='Kokoro (Offline)':
                from kokoro import KPipeline
                generator=KPipeline(lang_code='a')(text,voice=KOKORO_VOICE_ALIASES.get(self.store.get('voice'), self.store.get('voice')) or 'af_heart')
                samples=np.concatenate([np.asarray(a,dtype=np.float32) for _,_,a in generator]);rate=24000
            else:
                import edge_tts,miniaudio
                async def synth():
                    buf=bytearray()
                    async for item in edge_tts.Communicate(text,EDGE_VOICE_ALIASES.get(self.store.get('voice'), self.store.get('voice')) or 'en-US-AriaNeural').stream():
                        if item['type']=='audio':buf.extend(item['data'])
                    return bytes(buf)
                raw=asyncio.run(synth());decoded=miniaudio.decode(raw,output_format=miniaudio.SampleFormat.FLOAT32,nchannels=1,sample_rate=24000)
                samples=np.asarray(decoded.samples,dtype=np.float32);rate=decoded.sample_rate
            if stop.is_set():return
            self.speaking=True;self.status.emit('SPEAKING');hop=int(rate*.02)
            with sd.OutputStream(samplerate=rate,channels=1,dtype='float32') as stream:
                for i in range(0,len(samples),hop):
                    if stop.is_set():break
                    block=samples[i:i+hop];rms=float(np.sqrt(np.mean(block**2)));spectrum=np.abs(np.fft.rfft(block*np.hanning(len(block))))
                    f=np.fft.rfftfreq(len(block),1/rate);low=float(spectrum[(f>150)&(f<500)].sum());high=float(spectrum[(f>500)&(f<1300)].sum());front=float(spectrum[(f>1700)&(f<3200)].sum())
                    level=min(1,rms*7);openness=level*high/(low+high+1e-8);width=front/(front+high+1e-8)
                    self.audio.emit(level,openness,width);stream.write(block[:,None])
            return True
        self.jobs.run('speak',run)
    def stop(self):
        self.stopper.set();self.play_stop.set();self.listening=False;self.speaking=False;self.audio.emit(0,0,.5);self.status.emit('MIC OFF')
    def toggle_camera(self):
        self.camera=not self.camera
        if not self.camera:return
        def run():
            import cv2
            capture=cv2.VideoCapture(0)
            try:
                if not capture.isOpened():raise RuntimeError('Camera is not available.')
                while self.camera:
                    ok,frame=capture.read()
                    if not ok:raise RuntimeError('Camera frame could not be read.')
                    ok,data=cv2.imencode('.jpg',frame)
                    if ok:self.frame.emit(data.tobytes())
                    time.sleep(.08)
            finally:capture.release();self.camera=False
        self.jobs.run('camera',run)

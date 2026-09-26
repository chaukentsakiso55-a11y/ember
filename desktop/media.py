from __future__ import annotations
import base64,json,time
from urllib.parse import urlparse
from pathlib import Path
import requests
from PyQt6.QtWidgets import QDialog,QVBoxLayout,QComboBox,QLineEdit,QTextEdit,QMessageBox
from desktop.widgets import label,NeonButton
from desktop.state import DATA,Vault

def dialog(host):
    d=QDialog(host);d.setWindowTitle('Media Generation');v=QVBoxLayout(d);v.addWidget(label('Use an image-generation API or a compatible video job endpoint.'))
    kind=QComboBox();kind.addItems(['Image','Video job']);v.addWidget(kind);url=QLineEdit();url.setPlaceholderText('HTTPS generation endpoint');v.addWidget(url);model=QLineEdit();model.setPlaceholderText('Model ID');v.addWidget(model);key=QLineEdit();key.setEchoMode(QLineEdit.EchoMode.Password);key.setPlaceholderText('API key — stored in OS vault');v.addWidget(key);prompt=QTextEdit();prompt.setPlaceholderText('Describe what to generate');v.addWidget(prompt)
    b=NeonButton('Generate',True);v.addWidget(b)
    def run():
        endpoint=url.text().strip()
        if urlparse(endpoint).scheme!='https':host.notice('Use an HTTPS endpoint.');return
        if not model.text().strip() or not prompt.toPlainText().strip():host.notice('Enter model and prompt.');return
        if QMessageBox.question(d,'Submit generation','Send this prompt to the configured provider? Its usage charges may apply.')!=QMessageBox.StandardButton.Yes:return
        pid='media:'+urlparse(endpoint).netloc
        try:
            if key.text():Vault.set(pid,[key.text()])
            keys=Vault.get(pid)
        except Exception as e:host.notice(str(e));return
        payload={'model':model.text().strip(),'prompt':prompt.toPlainText(),'n':1};image=kind.currentIndex()==0
        def generate():
            r=requests.post(endpoint,headers={'Authorization':'Bearer '+(keys[0] if keys else '')},json=payload,timeout=180);r.raise_for_status();data=r.json();folder=DATA/'media';folder.mkdir(exist_ok=True)
            if image:
                item=(data.get('data') or [{}])[0]
                if item.get('b64_json'):content=base64.b64decode(item['b64_json'])
                elif item.get('url'):
                    target=item['url']
                    if urlparse(target).scheme!='https':raise ValueError('Provider returned a non-HTTPS image URL.')
                    response=requests.get(target,timeout=60);response.raise_for_status();content=response.content
                else:raise ValueError('Provider returned no image data.')
                path=folder/f'image-{int(time.time())}.png';path.write_bytes(content);return 'Generated image saved:\n'+str(path)
            if not image:
                path=folder/f'video-job-{int(time.time())}.json';path.write_text(json.dumps(data,indent=2))
                status_url=data.get('status_url') or data.get('statusUrl') or data.get('poll_url')
                job_id=data.get('id') or data.get('job_id')
                if status_url and urlparse(status_url).scheme=='https':
                    for _ in range(120):
                        time.sleep(5)
                        check=requests.get(status_url,headers={'Authorization':'Bearer '+(keys[0] if keys else '')},timeout=45);check.raise_for_status();state=check.json();state_name=str(state.get('status') or state.get('state') or '').lower()
                        if state_name in ('failed','error','cancelled'): raise RuntimeError('Video generation failed: '+json.dumps(state)[:300])
                        output=state.get('video_url') or state.get('videoUrl') or state.get('url')
                        if output and urlparse(output).scheme=='https':
                            media=requests.get(output,timeout=180);media.raise_for_status();video=folder/f'video-{int(time.time())}.mp4';video.write_bytes(media.content);return 'Generated video saved:\n'+str(video)
                        if state_name in ('completed','succeeded','done'): break
                return 'Video job submitted; provider did not expose a downloadable completed video. Job response saved:\n'+str(path)
        host.jobs.run('media',generate);d.accept()
    b.clicked.connect(run);d.resize(700,500);d.exec()

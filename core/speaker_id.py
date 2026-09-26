"""Optional local speaker verification from WAV files.
Uses resemblyzer when installed. Embeddings stay in config/speaker_profiles.json.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent.parent;PATH=BASE/'config'/'speaker_profiles.json'
def _load():
    try:return json.loads(PATH.read_text(encoding='utf-8'))
    except Exception:return {}
def _save(d):PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(d,indent=2),encoding='utf-8')
def _embed(wav_path):
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
    except Exception as e: raise RuntimeError('Speaker ID requires: pip install resemblyzer') from e
    wav=preprocess_wav(Path(wav_path));return VoiceEncoder().embed_utterance(wav).astype(float)
def enroll(name,wav_path):
    emb=_embed(wav_path);d=_load();d[str(name)]={'embedding':emb.tolist()};_save(d);return f"Enrolled local voice profile '{name}'."
def verify(wav_path,threshold=0.72):
    emb=_embed(wav_path);d=_load();best=(0.0,None)
    for name,rec in d.items():
        ref=np.asarray(rec.get('embedding',[]),dtype=float)
        if ref.size!=emb.size:continue
        score=float(np.dot(ref,emb)/(np.linalg.norm(ref)*np.linalg.norm(emb)+1e-9))
        if score>best[0]:best=(score,name)
    return {'match':best[1] if best[0]>=float(threshold) else None,'score':round(best[0],4),'threshold':float(threshold)}
def profiles():return list(_load())

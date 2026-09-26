import base64
from google import genai
from google.genai import types
from desktop.state import Vault
import os

def key():
    keys=Vault.get('gemini')
    value=(keys[0] if keys else '') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not value:raise RuntimeError('Add your Gemini API key in Settings > AI & Models > Gemini.')
    return value

def client():return genai.Client(api_key=key(),http_options={'timeout':45000})

def models():
    with client() as c:
        return [m.name.removeprefix('models/') for m in c.models.list() if 'generateContent' in (m.supported_actions or []) and not any(x in m.name.lower() for x in ('tts','image','robotics'))]

def chat(messages,tools,model,max_tokens,temperature):
    system='\n'.join(m['content'] for m in messages if m['role']=='system')
    turns=[]
    for m in messages:
        if m['role']=='system':continue
        value=m['content'];parts=[]
        if isinstance(value,str):parts=[types.Part.from_text(text=value)]
        else:
            for item in value:
                if item.get('type')=='text':parts.append(types.Part.from_text(text=item['text']))
                elif item.get('type')=='image_url':
                    header,data=item['image_url']['url'].split(',',1)
                    parts.append(types.Part.from_bytes(data=base64.b64decode(data),mime_type=header[5:].split(';')[0]))
        turns.append(types.Content(role='model' if m['role']=='assistant' else 'user',parts=parts))
    with client() as c:
        if not model:
            available=[m.name.removeprefix('models/') for m in c.models.list() if 'generateContent' in (m.supported_actions or []) and 'flash' in m.name.lower() and not any(x in m.name.lower() for x in ('tts','image','live','audio'))]
            if not available:raise RuntimeError('No Gemini text model is available to this key; enter a model ID in Settings.')
            model=sorted(available,reverse=True)[0]
        config={'system_instruction':system,'max_output_tokens':max_tokens,'temperature':temperature,'automatic_function_calling':{'disable':True}}
        if tools:config['tools']=[{'function_declarations':[x['function'] for x in tools]}]
        response=c.models.generate_content(model=model,contents=turns,config=config)
        calls=[{'function':{'name':fc.name,'arguments':dict(fc.args or {})}} for fc in (response.function_calls or [])]
        content=''.join(p.text or '' for candidate in (response.candidates or [])[:1] for p in (candidate.content.parts if candidate.content else []) if not getattr(p,'thought',False))
        if not content and not calls:raise RuntimeError('Gemini returned no answer. Check model, quota and provider response in logs.')
        return {'content':content,'tool_calls':calls,'provider':'gemini','model':model}

def speech(text,voice='Aoede',model=''):
    with client() as c:
        if not model:
            names=[m.name.removeprefix('models/') for m in c.models.list() if 'tts' in m.name.lower() and 'generateContent' in (m.supported_actions or [])]
            if not names:raise RuntimeError('No Gemini TTS model available. Choose Edge TTS or configure a TTS model.')
            model=sorted(names,reverse=True)[0]
        r=c.models.generate_content(model=model,contents=text,config={'response_modalities':['AUDIO'],'speech_config':{'voice_config':{'prebuilt_voice_config':{'voice_name':voice}}}})
        for candidate in r.candidates or []:
            for part in candidate.content.parts or []:
                if part.inline_data:return part.inline_data.data
        raise RuntimeError('Gemini returned no speech audio.')

"""Transparent specialist-agent routing for EMBER.

Planning is always available offline. `consult()` becomes a real multi-agent pass
when a configured local LLM server is reachable: selected specialists answer the
same task from their own roles, then a supervisor synthesizes their outputs.
"""
from __future__ import annotations
from core.llm_client import call_llm

KEYWORDS={
'coding':('code','python','bug','github','repo','compile','build','api','android','gradle'),
'study':('study','exam','quiz','school','learn','explain','teacher','subject','homework'),
'vision':('screen','see','image','camera','button','window','visual','ui'),
'files':('file','folder','document','pdf','rename','move','save','archive'),
'research':('research','find','compare','latest','source','search','evidence'),
'planning':('plan','steps','project','workflow','schedule','organize','roadmap'),
}
ROLE_PROMPTS={
'coding':'You are EMBER Coding Agent. Focus on architecture, bugs, tests, implementation details and safe changes.',
'study':'You are EMBER Study Agent. Explain clearly, teach, test understanding and identify weak topics.',
'vision':'You are EMBER Vision Agent. Reason about visual/UI tasks and state what visual evidence would be needed; never pretend to see an image you were not given.',
'files':'You are EMBER File Agent. Focus on file organization, document structure, paths and reversible operations.',
'research':'You are EMBER Research Agent. Focus on evidence, uncertainty, source needs and comparisons. Do not invent fresh facts.',
'planning':'You are EMBER Planning Agent. Break the goal into concrete, verifiable steps with dependencies and checkpoints.',
}

def choose(task:str)->list[str]:
    t=str(task or '').casefold();scores=[]
    for agent,words in KEYWORDS.items():
        score=sum(1 for w in words if w in t)
        if score:scores.append((score,agent))
    scores.sort(key=lambda x:(-x[0],x[1]))
    return [a for _,a in scores[:3]] or ['planning']

def plan(task:str)->dict:
    agents=choose(task)
    return {'task':task,'agents':agents,'steps':[f'{a.title()} agent: inspect its part of the task' for a in agents]+['Supervisor: combine results, call out uncertainty, and verify before acting']}

def consult(task:str,max_agents:int=3)->dict:
    agents=choose(task)[:max(1,min(3,int(max_agents)))]
    outputs={}
    for a in agents:
        try:
            r=call_llm([{'role':'system','content':ROLE_PROMPTS[a]},{'role':'user','content':task}],timeout=90)
            outputs[a]=str(r.get('content') or '').strip()
        except Exception as e:
            outputs[a]=f'[local specialist unavailable: {e}]'
    combined='\n\n'.join(f'{k.upper()}:\n{v}' for k,v in outputs.items())
    try:
        r=call_llm([
            {'role':'system','content':'You are EMBER Supervisor. Synthesize specialist reports into one concise plan. Preserve disagreements and uncertainty; do not claim actions were executed.'},
            {'role':'user','content':f'Task: {task}\n\nSpecialist reports:\n{combined}'},
        ],timeout=90)
        synthesis=str(r.get('content') or '').strip()
    except Exception as e:
        synthesis=f'Local supervisor unavailable: {e}'
    return {'task':task,'agents':agents,'reports':outputs,'synthesis':synthesis}

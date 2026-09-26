from __future__ import annotations
from core.knowledge_base import add, remove, list_docs, search
PLUGIN={"permissions":["files.read", "knowledge.write"],"name":"knowledge_library","description":"Index, search and remove local documents for EMBER's offline knowledge library. Supports common text/code files, PDF, DOCX, PPTX and XLSX.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"add, remove, list, or search"},"path":{"type":"STRING","description":"Local file path to index."},"title":{"type":"STRING"},"query":{"type":"STRING"},"name":{"type":"STRING"}},"required":["action"]}}
def run(parameters,player=None,session_memory=None):
    a=str(parameters.get('action','')).lower()
    if a=='add':return add(parameters.get('path',''),parameters.get('title',''))
    if a=='remove':return 'Removed.' if remove(parameters.get('name') or parameters.get('title') or '') else 'Document not found.'
    if a=='list':return str(list_docs())
    if a=='search':
        r=search(parameters.get('query',''))
        if player and hasattr(player,'show_content'):player.show_content('LOCAL KNOWLEDGE',r)
        return r
    return 'Use add, remove, list, or search.'

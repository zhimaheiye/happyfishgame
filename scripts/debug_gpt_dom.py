import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gpt_collab import call_bridge

js = """(() => {
    return {
        title: document.title,
        url: window.location.href,
        hasPromptTextarea: !!document.querySelector('#prompt-textarea'),
        inputs: Array.from(document.querySelectorAll('textarea, [contenteditable="true"]')).map(el => ({
            tag: el.tagName,
            id: el.id,
            className: el.className,
            contentEditable: el.contentEditable
        }))
    };
})()"""

res = call_bridge('evaluate', {'code': js})
print(json.dumps(res, ensure_ascii=False, indent=2))

#!/usr/bin/env python3
"""Publish research observations; these dated records are not fresh verification."""
import json
from pathlib import Path
from atlas import assets,links,owners
target=Path(__file__).parent/'data'/'atlas.json'
data={'basis':'Kazakhstan External Dependency Atlas v0.4 research; dates and source links must be rechecked',
      'warning':'Relationships are research evidence; related headlines do not establish causation or severity.',
      'assets':assets(),'links':links(),'owners':owners()}
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'assets':len(data['assets']),'links':len(data['links']),'owners':len(data['owners'])}))

#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path.cwd()
index=(root/'index.html').read_text(encoding='utf-8')
checks={
 'Original research replay':all(f'id="{x}"' in index for x in ['recordSelect','windowSlider','timeChart','rawVal','resVal','signalState']),
 'New-data analyzer retained':'id="csvRun"' in index and 'browser-signal.js' in index,
 'Crew self-assessment retained':'id="reportBtn"' in index,
 'Four original views':all(f'id="{x}"' in index for x in ['console','science','nasa','method']),
 'Science dataset retained':(root/'data.js').exists(),
 'Original science JS retained':(root/'app.js').exists() and (root/'browser-signal.js').exists(),
 'Clinical CSS loaded':'href="clinic.css"' in index and (root/'clinic.css').exists(),
 'Clinical JS loaded':'src="clinic.js"' in index and (root/'clinic.js').exists(),
 'No external scripts in added layer':not re.search(r'<script[^>]+src="https?://', (root/'clinic.js').read_text(encoding='utf-8')),
 'No new storage calls':not re.search(r'\b(localStorage|sessionStorage|sendBeacon|XMLHttpRequest)\b',(root/'clinic.js').read_text(encoding='utf-8'))
}
for label,ok in checks.items():print(('PASS' if ok else 'FAIL')+'  '+label)
if not all(checks.values()):sys.exit(1)
print('Static checklist passed. Desktop/mobile interaction tests must still be performed manually.')

#!/usr/bin/env python3
"""Apply the Pulsar visual layer to an existing Pulsar GitHub Pages checkout."""
from __future__ import annotations
import hashlib
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv)>1 else Path.cwd().resolve()
index = TARGET/'index.html'
needed = ['style.css','app.js','data.js','browser-signal.js','index.html']
missing = [name for name in needed if not (TARGET/name).is_file()]
if missing:
    raise SystemExit('Not a complete Pulsar website checkout. Missing: '+', '.join(missing))
source = index.read_text(encoding='utf-8')
anchors = ['id="console"','id="science"','id="nasa"','id="method"','id="recordSelect"','id="windowSlider"','id="timeChart"','id="reportBtn"']
if any(key not in source for key in anchors):
    raise SystemExit('Stopped: website structure differs from the inspected Pulsar version. No files changed.')
if '<link rel="stylesheet" href="clinic.css">' in source and '<script src="clinic.js"></script>' in source:
    print('HTML links already present; checking presentation-layer files.')
else:
    if '<link rel="stylesheet" href="clinic.css">' in source or '<script src="clinic.js"></script>' in source:
        raise SystemExit('Stopped: incomplete prior installation. Inspect index.html manually.')
    if '</head>' not in source or '</body>' not in source:
        raise SystemExit('Stopped: cannot locate HTML injection anchors.')
    backup=TARGET/'.pulsar-backup'
    backup.mkdir(exist_ok=True)
    shutil.copy2(index,backup/'index.html')
    source=source.replace('</head>','<link rel="stylesheet" href="clinic.css"></head>',1)
    source=source.replace('</body>','<script src="clinic.js"></script></body>',1)
    source=source.replace('<meta name="color-scheme" content="dark">','<meta name="color-scheme" content="light">',1)
    index.write_text(source,encoding='utf-8')
    print('Patched index.html; original saved under .pulsar-backup/.')
for filename in ['clinic.css','clinic.js']:
    shutil.copy2(ROOT/filename,TARGET/filename)
    digest=hashlib.sha256((TARGET/filename).read_bytes()).hexdigest()[:16]
    print(f'Installed {filename} — sha256 prefix {digest}')
print('Preserved style.css, app.js, data.js and browser-signal.js unchanged.')
print('Check the site in desktop/mobile browsers, then commit index.html, clinic.css and clinic.js.')

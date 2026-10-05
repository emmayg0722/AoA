#!/usr/bin/env python3
"""Index the existing toolkit and install the project bridge before tool scripts."""
import json
import re
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
report = (ROOT / 'engagement-report.html').read_text()
source = report.split('const REGISTRY = [', 1)[1].split('\n];', 1)[0]
phases = []
pages = [ROOT / 'engagement-report.html', ROOT / 'use-case-discovery-board/index.html']
for title, body in re.findall(r"\{ phase: '([^']+)', tools: \[(.*?)\]\}", source, re.S):
    number = int(re.search(r'Phase (\d+)', title).group(1))
    phase_name = title.split(' — ', 1)[1]
    slug = re.sub(r'[^a-z0-9]+', '-', phase_name.lower()).strip('-')
    phase = {'number': number, 'title': title, 'folder': f'phase-{number:02d}-{slug}', 'tools': []}
    for key, name, href in re.findall(r"\{ key: '([^']+)', title: '([^']+)', href: '([^']+)' \}", body):
        route = unquote(href)
        path = ROOT / route
        if href.endswith('/'):
            path /= 'index.html'
            folder = Path(route).name
        else:
            folder = path.parent.name if path.name == 'console.html' else path.stem
        if not path.is_file():
            raise FileNotFoundError(path)
        phase['tools'].append({'key': key, 'title': name, 'href': href, 'folder': folder})
        pages.append(path)
    phases.append(phase)
if len(phases) != 10 or len({t['key'] for p in phases for t in p['tools']}) != sum(len(p['tools']) for p in phases):
    raise ValueError('Registry must cover ten phases with unique storage keys.')
(HERE / 'registry.json').write_text(json.dumps(phases, indent=2, ensure_ascii=False) + '\n')
for page in set(pages):
    depth = len(page.relative_to(ROOT).parts) - 1
    src = '../' * depth + 'project-workspace/tool-storage.js'
    text = page.read_text()
    text = re.sub(r'\n<script src="[^"]*project-workspace/tool-storage.js[^\n]*</script>', '', text)
    text = text.replace('<head>', f'<head>\n<script src="{src}"></script>', 1)
    page.write_text(text)
print(f'Indexed {sum(len(p["tools"]) for p in phases)} tools across ten phases; bridged {len(set(pages))} original pages.')

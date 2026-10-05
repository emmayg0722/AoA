#!/usr/bin/env python3
"""Generate the public Phase 1 entry from the standalone original workshop."""
from pathlib import Path

here = Path(__file__).resolve().parent
target = here.parent / 'Phase 1 - Discovery & Assessment/use-case-discovery-board/index.html'
html = (here / 'index.html').read_text()
html = html.replace('src="../project-workspace/', 'src="../../project-workspace/')
html = html.replace('href="../project-workspace/', 'href="../../project-workspace/')
html = html.replace('href="../"', 'href="../../"')
html = html.replace('href="../Phase%201%20-%20Discovery%20%26%20Assessment/use-case-prioritization/"', 'href="../use-case-prioritization/"')
html = html.replace("const SAMPLE_BASE = '../Phase%201%20-%20Discovery%20%26%20Assessment/sample-data/';", "const SAMPLE_BASE = '../sample-data/';")
html = html.replace('src="./projects.js', 'src="../../use-case-discovery-board/projects.js')
html = html.replace('src="./github-projects.js', 'src="../../use-case-discovery-board/github-projects.js')
target.write_text(html)
(target.parent / 'config.json').write_text((here / 'config.json').read_text())

"""Refresh commentary in an existing live edition without changing its collection time.

Usage: python scripts/apply_impact_notes.py path/to/politicky-prehled
Commit index.html and data.json together against the original deployment branch head.
"""
import argparse
import json
import re
from pathlib import Path

from update_politics import render_card, with_context
from analysis_progress import decorate


def apply_notes(folder, notes):
    data_path = folder / 'data.json'
    page_path = folder / 'index.html'
    data = json.loads(data_path.read_text())
    page = page_path.read_text()
    current = re.search(r'<script id="initial-data" type="application/json">(.*?)</script>', page, re.S)
    if not current or json.loads(current[1]) != data:
        raise ValueError('HTML and JSON belong to different editions')
    rows = [with_context(row, notes) for row in data['articles']]
    progress_path = folder / 'analysis-progress.json'
    state = json.loads(progress_path.read_text()) if progress_path.exists() else {}
    rows = decorate(rows, state)
    data['articles'] = rows
    payload = json.dumps(data, ensure_ascii=False).replace('<', r'\u003c')
    page = page[:current.start(1)] + payload + page[current.end(1):]
    cards = ''.join(render_card(row) for row in rows)
    page, count = re.subn(r'<!-- NEWS START -->.*?<!-- NEWS END -->',
                          lambda _: '<!-- NEWS START -->' + cards + '<!-- NEWS END -->', page, flags=re.S)
    if count != 1:
        raise ValueError('Expected one live edition')
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    page_path.write_text(page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    apply_notes(args.folder, json.loads(Path(__file__).with_name('impact_notes.json').read_text()))

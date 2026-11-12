"""Prepare a compact, deterministic list for the twice-daily human/AI editorial review.
No AI calls. Reads the published edition and existing verified notes.
Usage: python scripts/prepare_analysis_queue.py path/to/politicky-prehled --limit 8
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SIGNALS = {
    'vláda': 3, 'vlád': 3, 'parlament': 3, 'sněmovn': 3,
    'zákon': 4, 'rozpočet': 4, 'rozpočt': 4, 'soud': 3,
    'prezident': 2, 'ministr': 2, 'volb': 3, 'koalic': 2,
    'eu': 2, 'unie': 2, 'nato': 3, 'sankc': 3, 'válk': 3,
    'ukrajin': 3, 'rusko': 3, 'bezpečnost': 3, 'daň': 3,
    'škol': 2, 'zdravot': 2, 'ekonom': 2
}

def rank(row):
    title = row.get('title', '').casefold()
    summary = row.get('summary', '').casefold()
    score = sum(weight for stem, weight in SIGNALS.items()
                if stem in title or stem in summary)
    try:
        age = max(0, (datetime.now(timezone.utc) -
                      datetime.fromisoformat(row['published_at'])).total_seconds()/3600)
    except (KeyError, ValueError, TypeError):
        age = 48
    return (score, -age)

def queue(folder, limit=8):
    rows = json.loads((folder/'data.json').read_text()).get('articles', [])
    notes_path = Path(__file__).with_name('impact_notes.json')
    notes = json.loads(notes_path.read_text()) if notes_path.exists() else {}
    pending = []
    for row in rows:
        if row.get('importance_kind') == 'analysis':
            continue
        note = notes.get(row['url'])
        if note and note.get('title') == row.get('title') and note.get('paragraphs'):
            continue
        pending.append(row)
    pending.sort(key=rank, reverse=True)
    # Preserve domestic and international coverage without inventing editorial importance.
    selected, used = [], set()
    for category in ('domaci', 'zahranicni'):
        candidate = next((r for r in pending if r.get('category') == category), None)
        if candidate and len(selected) < limit:
            selected.append(candidate)
            used.add(candidate['url'])
    for row in pending:
        if len(selected) >= limit:
            break
        if row['url'] not in used:
            selected.append(row)
            used.add(row['url'])
    return {
        'edition': json.loads((folder/'data.json').read_text()).get('updated_at'),
        'total_pending': len(pending),
        'selected_count': len(selected),
        'selected': [
            {'url': r['url'], 'title': r['title'], 'source': r.get('source'),
             'category': r.get('category'), 'published_at': r.get('published_at'),
             'summary': r.get('summary', '')[:350]} for r in selected
        ]
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--limit', type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.limit <= 40:
        parser.error('--limit must be between 1 and 40')
    print(json.dumps(queue(args.folder, args.limit), ensure_ascii=False, separators=(',', ':')))

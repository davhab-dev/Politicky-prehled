"""Collect one edition into a deployment checkout. Publish its diff before analysis.
Usage: python scripts/collect_cycle.py ../website/politicky-prehled
Failure leaves the previous edition intact. No paid API and no waiting for analysis.
"""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
import update_politics

def collect(folder):
    folder=Path(folder).resolve()
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)/'edition'
        shutil.copytree(folder,stage)
        for name in ('index.html','app.js','sources.json','favicon.svg'):
            if (root/name).exists(): shutil.copy2(root/name,stage/name)
        # A previous worker must never advertise stale estimates for a new cycle.
        progress=stage/'analysis-progress.json'
        state=json.loads(progress.read_text()) if progress.exists() else {}
        state.update(active=False,current=None,queue=[],needs_sources=[])
        progress.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
        old=update_politics.DEST
        try:
            update_politics.DEST=stage
            update_politics.main()
        finally: update_politics.DEST=old
        shutil.copytree(stage,folder,dirs_exist_ok=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    collect(parser.parse_args().folder)

"""Measured queue status for the sequential editorial cycle; no API calls."""
import argparse
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import median

UNKNOWN = 'Čas dokončení zatím nelze spolehlivě odhadnout.'
WAITING = 'Čeká na zpracování a ověření zdrojů.'

def timestamp(value):
    try:
        result = datetime.fromisoformat(value)
        return result if result.tzinfo else None
    except (TypeError, ValueError):
        return None

def waiting_message(row, now=None):
    now = now or datetime.now(timezone.utc)
    if row.get('analysis_status') == 'needs_sources':
        return 'Ověřování podkladů pokračuje. ' + UNKNOWN
    eta, heartbeat = timestamp(row.get('analysis_eta_at')), timestamp(row.get('analysis_estimated_at'))
    if eta and heartbeat and timedelta(0) <= now-heartbeat <= timedelta(minutes=10) and eta > now:
        return f'Odhad zveřejnění rozboru: přibližně za {math.ceil((eta-now).total_seconds()/60)} min.'
    return UNKNOWN

def decorate(rows, state, now=None):
    now = now or datetime.now(timezone.utc)
    heartbeat = timestamp(state.get('heartbeat'))
    samples = [x for x in state.get('samples_seconds', [])[-50:] if isinstance(x,(int,float)) and 1 <= x <= 3600]
    active = state.get('active') and heartbeat and timedelta(0) <= now-heartbeat <= timedelta(minutes=10)
    queue = state.get('queue', [])
    result=[]
    for row in rows:
        row={k:v for k,v in row.items() if k not in ('analysis_eta_at','analysis_estimated_at','analysis_status')}
        if row.get('importance_kind') == 'pending':
            key=[row['url'],row['title']]
            if key in state.get('needs_sources',[]):
                row['analysis_status']='needs_sources'
            elif active and len(samples)>=5 and key in queue:
                seconds=median(samples)*(queue.index(key)+1)
                row['analysis_eta_at']=(heartbeat+timedelta(seconds=seconds)).isoformat()
                row['analysis_estimated_at']=heartbeat.isoformat()
        result.append(row)
    return result

def transition(state, rows, action, url=None, now=None):
    now=now or datetime.now(timezone.utc)
    pending=[[r['url'],r['title']] for r in rows if r.get('importance_kind')=='pending']
    key=next((k for k in pending if k[0]==url),None)
    if action=='start':
        state.update(active=True,queue=pending,needs_sources=[],current=None)
    elif action=='begin':
        if key is None: raise ValueError('Article is not pending')
        state['current']={'key':key,'started_at':now.isoformat()}
    elif action in ('finish','defer'):
        current=state.get('current')
        if not current or current['key'][0]!=url: raise ValueError('No matching started article')
        if action=='finish':
            row=next((r for r in rows if [r['url'],r['title']]==current['key']),None)
            if not row or row.get('importance_kind')!='analysis': raise ValueError('Publish verified analysis before recording completion')
            seconds=(now-timestamp(current['started_at'])).total_seconds()
            if 1<=seconds<=3600: state['samples_seconds']=(state.get('samples_seconds',[])+[seconds])[-50:]
        else:
            state.setdefault('needs_sources',[]).append(current['key'])
        state['queue']=[k for k in state.get('queue',[]) if k!=current['key']]
        state['current']=None
    elif action=='stop': state.update(active=False,current=None)
    else: raise ValueError('Unknown action')
    state['heartbeat']=now.isoformat()
    return state

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('action',choices=['start','begin','finish','defer','stop'])
    parser.add_argument('--url')
    args=parser.parse_args()
    path=args.folder/'analysis-progress.json'
    state=json.loads(path.read_text()) if path.exists() else {}
    rows=json.loads((args.folder/'data.json').read_text())['articles']
    state=transition(state,rows,args.action,args.url)
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    from apply_impact_notes import apply_notes
    notes=json.loads(Path(__file__).with_name('impact_notes.json').read_text())
    apply_notes(args.folder,notes)

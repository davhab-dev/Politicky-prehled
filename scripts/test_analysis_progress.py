import unittest
from datetime import datetime, timezone, timedelta
from analysis_progress import decorate, waiting_message, transition

class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,11,9,tzinfo=timezone.utc)
        self.rows=[dict(url='https://a',title='A',importance_kind='pending'),dict(url='https://b',title='B',importance_kind='pending')]
        self.state=dict(active=True,heartbeat=self.now.isoformat(),queue=[['https://a','A'],['https://b','B']],samples_seconds=[120]*5)
    def test_measured_queue(self):
        rows=decorate(self.rows,self.state,self.now)
        self.assertIn('za 2 min.',waiting_message(rows[0],self.now))
        self.assertIn('za 4 min.',waiting_message(rows[1],self.now))
    def test_no_samples_no_promise(self):
        self.state['samples_seconds']=[120]*4
        self.assertNotIn('analysis_eta_at',decorate(self.rows,self.state,self.now)[0])
    def test_stale_expired_and_future_heartbeat(self):
        row=decorate(self.rows,self.state,self.now)[0]
        for offset in (3,11,-1):
            self.assertNotIn('za ',waiting_message(row,self.now+timedelta(minutes=offset)))
    def test_blocked_stays_visible(self):
        self.state['needs_sources']=[['https://a','A']]
        rows=decorate(self.rows,self.state,self.now)
        self.assertEqual(len(rows),2)
        self.assertIn('Ověřování podkladů pokračuje',waiting_message(rows[0],self.now))
    def test_changed_title_does_not_reuse_estimate(self):
        self.rows[0]['title']='Changed'
        self.assertNotIn('analysis_eta_at',decorate(self.rows,self.state,self.now)[0])
    def test_measure_only_completed_analysis(self):
        state=transition({},self.rows,'start',now=self.now)
        transition(state,self.rows,'begin','https://a',self.now)
        with self.assertRaises(ValueError):transition(state,self.rows,'finish','https://a',self.now+timedelta(seconds=90))
        self.rows[0]['importance_kind']='analysis'
        transition(state,self.rows,'finish','https://a',self.now+timedelta(seconds=90))
        self.assertEqual(state['samples_seconds'],[90])
    def test_stop_removes_estimate(self):
        transition(self.state,self.rows,'stop',now=self.now)
        self.assertNotIn('analysis_eta_at',decorate(self.rows,self.state,self.now)[0])

if __name__=='__main__':unittest.main()

class CacheTests(unittest.TestCase):
    def test_reuse_and_changed_title(self):
        from update_politics import with_context
        row=dict(url='https://ct24.ceskatelevize.cz/a',title='Old',importance_kind='analysis',importance='Verified',analysis_source='ČT24',analysis_url='https://ct24.ceskatelevize.cz/a')
        self.assertEqual(with_context(row,{})['importance_kind'],'analysis')
        notes={row['url']:dict(title='New',url=row['url'],paragraphs=['New verified'],source='ČT24')}
        self.assertEqual(with_context(row,notes)['importance_kind'],'pending')
    def test_apply_preserves_collection_and_articles(self):
        import tempfile,json
        from pathlib import Path
        from apply_impact_notes import apply_notes
        data=dict(updated_at='2026-11-11T08:00:00+00:00',articles=[dict(url='https://ct24.ceskatelevize.cz/a',title='A',summary='Text',source='ČT24',category='domaci',published_at='2026-11-11T07:00:00+00:00',importance_kind='pending',importance='Čeká na zpracování a ověření zdrojů.')])
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/'data.json').write_text(json.dumps(data));(folder/'index.html').write_text('<script id="initial-data" type="application/json">'+json.dumps(data)+'</script><!-- NEWS START --><!-- NEWS END -->')
            apply_notes(folder,{})
            self.assertEqual(json.loads((folder/'data.json').read_text()),data)
            self.assertIn('Čas dokončení zatím nelze', (folder/'index.html').read_text())

import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import relay


def node_op(nid, title='Workshop block', kind='step'):
    return dict(t='node', node=dict(id=nid, type=kind, title=title, detail='', role='',
                                  volume='', pattern='', value='3', effort='3'),
                layout=dict(x=120, y=80, w=190))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sessions.json'
        self.store = relay.Store(self.path)
        self.s = self.store.session('discovery')
        self.a = self.s.join('First participant', relay.blank_doc())

    def test_full_original_board_survives_restart_and_allocations_do_not_collide(self):
        ops = [node_op(self.a['idBase'] + i, kind=kind) for i, kind in enumerate(('step', 'pain', 'system', 'usecase', 'note'))]
        ops.extend([dict(t='edge', edge=dict(id=self.a['idBase'] + 10, **{'from': self.a['idBase'], 'to': self.a['idBase'] + 3}, label='candidate')),
                    dict(t='field', k='process', v='Claims intake'), dict(t='sop', sopDone=[True, False, True])])
        self.s.push(self.a['peerId'], ops)
        before = copy.deepcopy(self.s.doc)
        restarted = relay.Store(self.path).session('discovery')
        second = restarted.join('Returning participant', relay.blank_doc())
        self.assertTrue(second['adopted'])
        self.assertEqual(before, restarted.doc)
        self.assertGreater(second['idBase'], max(n['id'] for n in restarted.doc['nodes']))
        self.assertIsNone(restarted.since(0))

    def test_disk_failure_does_not_acknowledge_or_broadcast_edit(self):
        before = self.path.read_bytes()
        seq = self.s.seq
        with patch('relay.os.replace', side_effect=OSError('Disk unavailable')):
            with self.assertRaises(OSError):
                self.s.push(self.a['peerId'], [node_op(self.a['idBase'])])
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(seq, self.s.seq)
        self.assertEqual([], self.s.doc['nodes'])
        self.assertEqual([], self.s.ops)
        self.assertEqual([], list(self.path.parent.glob('.sessions-*.tmp')))

    def test_validation_is_atomic_and_rejects_missing_connection_endpoint(self):
        with self.assertRaises(ValueError):
            self.s.push(self.a['peerId'], [node_op(self.a['idBase']), dict(t='edge', edge=dict(id=10, **{'from': self.a['idBase'], 'to': 999}, label=''))])
        self.assertEqual([], self.s.doc['nodes'])
        with self.assertRaises(ValueError):
            self.s.push(self.a['peerId'], [node_op(self.a['idBase'], kind='made-up')])
        with self.assertRaises(LookupError):
            self.s.push('not-a-participant', [node_op(1)])

    def test_concurrent_sessions_and_blocks_do_not_overwrite_each_other(self):
        b = self.s.join('Second participant', relay.blank_doc())
        other = self.store.session('other')
        c = other.join('Other workshop', relay.blank_doc())
        errors = []
        def write(s, p):
            try:
                s.push(p['peerId'], [node_op(p['idBase'])])
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=write, args=(s, p)) for s, p in ((self.s, self.a), (self.s, b), (other, c))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(3)
            self.assertFalse(thread.is_alive())
        self.assertEqual([], errors)
        saved = relay.Store(self.path)
        self.assertEqual(2, len(saved.session('discovery').doc['nodes']))
        self.assertEqual(1, len(saved.session('other').doc['nodes']))

    def test_deleting_block_removes_incident_connections_and_position(self):
        self.s.push(self.a['peerId'], [node_op(1), node_op(2), dict(t='edge', edge=dict(id=3, **{'from': 1, 'to': 2}, label=''))])
        self.s.push(self.a['peerId'], [dict(t='nodeDel', id=1)])
        self.assertEqual([2], [n['id'] for n in self.s.doc['nodes']])
        self.assertEqual([], self.s.doc['edges'])
        self.assertNotIn('1', self.s.doc['layout'])


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sessions.json'
        self.server = relay.create_server(port=0, data_file=self.path,
                                          origins=['https://emmayg0722.github.io'], token='test-access-code')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(3)

    def request(self, path, body=None, origin='https://emmayg0722.github.io', token='test-access-code'):
        headers = dict(Origin=origin, Authorization='Bearer ' + token, **{'Content-Type': 'application/json'})
        req = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response), response.headers

    def test_http_two_participants_receive_only_durable_operations(self):
        _, a, _ = self.request('/sync/join', dict(session='team', name='A', doc=relay.blank_doc()))
        _, b, _ = self.request('/sync/join', dict(session='team', name='B', doc=relay.blank_doc()))
        status, ack, headers = self.request('/sync/ops', dict(session='team', peerId=a['peerId'], ops=[node_op(a['idBase'], 'Persistent candidate', 'usecase')]))
        self.assertEqual(200, status)
        self.assertTrue(ack['saved'])
        self.assertEqual('https://emmayg0722.github.io', headers['Access-Control-Allow-Origin'])
        self.assertEqual('Persistent candidate', json.loads(self.path.read_text())['sessions']['team']['doc']['nodes'][0]['title'])
        _, poll, _ = self.request(f"/sync/poll?session=team&peerId={b['peerId']}&since={b['seq']}")
        self.assertEqual('Persistent candidate', poll['ops'][0]['op']['node']['title'])

    def test_http_save_failure_returns_failure_and_keeps_old_state(self):
        _, a, _ = self.request('/sync/join', dict(session='team', name='A', doc=relay.blank_doc()))
        with patch('relay.os.replace', side_effect=OSError('Disk unavailable')):
            with self.assertRaises(HTTPError) as error:
                self.request('/sync/ops', dict(session='team', peerId=a['peerId'], ops=[node_op(a['idBase'])]))
        self.assertEqual(503, error.exception.code)
        error.exception.close()
        _, state, _ = self.request('/sync/state?session=team')
        self.assertEqual([], state['doc']['nodes'])

    def test_authentication_origin_and_private_files(self):
        for kwargs, status in ((dict(token='wrong'), 401), (dict(origin='https://untrusted.example'), 403)):
            with self.assertRaises(HTTPError) as error:
                self.request('/sync/state', **kwargs)
            self.assertEqual(status, error.exception.code)
            error.exception.close()
        for path in ('/use-case-discovery-board/data/sessions.json', '/.git/config', '/use-case-discovery-board/relay.py'):
            with self.assertRaises(HTTPError) as error:
                self.request(path)
            self.assertEqual(404, error.exception.code)
            error.exception.close()


if __name__ == '__main__':
    unittest.main()

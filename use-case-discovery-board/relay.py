#!/usr/bin/env python3
"""Durable relay for the original discovery workshop; standard library only."""
import argparse
import copy
import functools
import json
import math
import os
from pathlib import Path
import secrets
import socket
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse, unquote
from github_store import GitHubRepository, RepositoryConflict

HERE = Path(__file__).resolve().parent
POLL_TIMEOUT = 25
PEER_TTL = 60
OPS_KEPT = 2000
MAX_BODY = 4_000_000
COLOURS = ['#1B1474', '#c0392b', '#1a8a5c', '#d4790e', '#5348c4', '#0e7c86']


def blank_doc():
    return dict(fields={}, nodes=[], layout={}, edges=[], sopDone=[], nextId=1,
                view=dict(x=40, y=40, z=1), lang='en')


def identifier(value):
    return type(value) is int and 0 < value < 9_007_199_254_740_991


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_doc(doc):
    if not isinstance(doc, dict):
        raise ValueError('Board must be an object')
    doc = copy.deepcopy(doc)
    for key, value in blank_doc().items():
        doc.setdefault(key, value)
    if not isinstance(doc['fields'], dict) or len(doc['fields']) > 100:
        raise ValueError('Invalid engagement fields')
    if any(not isinstance(k, str) or not isinstance(v, str) or len(v) > 100000
           for k, v in doc['fields'].items()):
        raise ValueError('Invalid engagement field value')
    if not isinstance(doc['nodes'], list) or len(doc['nodes']) > 5000:
        raise ValueError('Invalid blocks')
    if not isinstance(doc['edges'], list) or len(doc['edges']) > 10000:
        raise ValueError('Invalid connections')
    if not isinstance(doc['layout'], dict):
        raise ValueError('Invalid layout')
    ids = set()
    for node in doc['nodes']:
        if not isinstance(node, dict) or not identifier(node.get('id')):
            raise ValueError('Invalid block id')
        if node['id'] in ids or node.get('type') not in ('step', 'pain', 'system', 'usecase', 'note'):
            raise ValueError('Duplicate block id or unknown block type')
        ids.add(node['id'])
        for key in ('title', 'detail', 'role', 'volume', 'pattern', 'value', 'effort'):
            if key in node and (not isinstance(node[key], str) or len(node[key]) > 100000):
                raise ValueError('Invalid block text')
        pos = doc['layout'].get(str(node['id']))
        if not isinstance(pos, dict) or not all(finite(pos.get(k)) for k in ('x', 'y', 'w')) or pos['w'] <= 0:
            raise ValueError('Each block needs a valid position and width')
    node_ids = set(ids)
    for edge in doc['edges']:
        if not isinstance(edge, dict) or not identifier(edge.get('id')) or edge['id'] in ids:
            raise ValueError('Invalid or duplicate connection id')
        ids.add(edge['id'])
        if edge.get('from') not in node_ids or edge.get('to') not in node_ids:
            raise ValueError('Connection endpoint is missing')
        if not isinstance(edge.get('label', ''), str):
            raise ValueError('Invalid connection label')
    if not isinstance(doc['sopDone'], list) or len(doc['sopDone']) > 100 or any(type(v) is not bool for v in doc['sopDone']):
        raise ValueError('Invalid checklist')
    if not identifier(doc['nextId']):
        raise ValueError('Invalid allocation counter')
    doc['nextId'] = max(doc['nextId'], max(ids, default=0) + 1)
    if not isinstance(doc['view'], dict) or not all(finite(doc['view'].get(k)) for k in ('x', 'y', 'z')) or doc['view']['z'] <= 0:
        raise ValueError('Invalid viewport')
    if doc['lang'] not in ('en', 'da', 'sv'):
        raise ValueError('Invalid language')
    # JSON encoding also rejects non-finite numbers in any extension fields.
    json.dumps(doc, allow_nan=False)
    return doc


def apply_op(doc, op):
    if not isinstance(op, dict):
        raise ValueError('Invalid operation')
    kind = op.get('t')
    if kind == 'doc':
        return validate_doc(op.get('doc'))
    if kind == 'node':
        node = op.get('node')
        if not isinstance(node, dict) or not identifier(node.get('id')):
            raise ValueError('Invalid block')
        doc['nodes'] = [node if n['id'] == node['id'] else n for n in doc['nodes']]
        if not any(n['id'] == node['id'] for n in doc['nodes']):
            doc['nodes'].append(node)
        doc['layout'][str(node['id'])] = op.get('layout')
    elif kind == 'nodeDel':
        nid = op.get('id')
        doc['nodes'] = [n for n in doc['nodes'] if n['id'] != nid]
        doc['layout'].pop(str(nid), None)
        doc['edges'] = [e for e in doc['edges'] if e['from'] != nid and e['to'] != nid]
    elif kind == 'edge':
        edge = op.get('edge')
        if not isinstance(edge, dict) or not identifier(edge.get('id')):
            raise ValueError('Invalid connection')
        doc['edges'] = [edge if e['id'] == edge['id'] else e for e in doc['edges']]
        if not any(e['id'] == edge['id'] for e in doc['edges']):
            doc['edges'].append(edge)
    elif kind == 'edgeDel':
        doc['edges'] = [e for e in doc['edges'] if e['id'] != op.get('id')]
    elif kind == 'field':
        doc['fields'][op.get('k')] = op.get('v')
    elif kind == 'sop':
        doc['sopDone'] = op.get('sopDone')
    else:
        raise ValueError('Unknown operation')
    return doc


class Store:
    def __init__(self, path, github=None):
        self.path = Path(path)
        self.github, self.last_commit = github, None
        self.lock = threading.Lock()
        self.sessions = {}
        saved = github.load() if github else (json.loads(self.path.read_text()) if self.path.exists() else {'schemaVersion': 1, 'sessions': {}})
        if saved.get('schemaVersion') != 1 or not isinstance(saved.get('sessions'), dict):
            raise ValueError('Invalid saved session file')
        self.records = saved['sessions']
        for record in self.records.values():
            record['doc'] = validate_doc(record['doc'])
            if type(record.get('seq')) is not int or record['seq'] < 0 or not identifier(record.get('nextSlot')):
                raise ValueError('Invalid saved counters')

    def storage_info(self):
        if self.github:
            return dict(mode='github', repository=self.github.repository,
                        url='https://github.com/' + self.github.repository,
                        visibility=self.github.visibility, branch=self.github.branch,
                        path=self.github.path, commit=self.last_commit)
        return dict(mode='local', path='use-case-discovery-board/data/sessions.json')

    def projects(self):
        with self.lock:
            return [copy.deepcopy(r['project']) for r in self.records.values() if r.get('project')]

    def project(self, pid):
        with self.lock:
            if pid not in self.records or not self.records[pid].get('project'):
                raise FileNotFoundError('Project not found')
        return self.session(pid)

    def create_project(self, name, display_name):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
            raise ValueError('Enter a project name (up to 120 characters)')
        if not isinstance(display_name, str) or not 1 <= len(display_name.strip()) <= 80:
            raise ValueError('Enter your display name (up to 80 characters)')
        pid = str(uuid.uuid4())
        stamp = datetime.now(timezone.utc).isoformat()
        record = dict(doc=blank_doc(), seeded=True, seq=0, nextSlot=1,
                      project=dict(id=pid, name=name.strip(), createdAt=stamp, updatedAt=stamp,
                                   createdBy=display_name.strip(), members=[]))
        session = Session(self, pid, record)
        joined = session.join(display_name.strip(), blank_doc())
        with self.lock:
            self.sessions[pid] = session
        return joined

    def session(self, name):
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            raise ValueError('Invalid session name')
        with self.lock:
            if name not in self.sessions:
                self.sessions[name] = Session(self, name, self.records.get(name))
            return self.sessions[name]

    def persist(self, name, record):
        with self.lock:
            records = copy.deepcopy(self.records)
            records[name] = copy.deepcopy(record)
            state = {'schemaVersion': 1, 'sessions': records}
            payload = json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
            if self.github:
                try:
                    self.last_commit = self.github.save(state)
                except RepositoryConflict as exc:
                    self.records = exc.state['sessions']
                    raise
                self.records = records
                # GitHub is authoritative; mirror failure must not undo an accepted commit.
                try:
                    self.write_file(payload)
                except OSError:
                    pass
                return
            self.write_file(payload)
            self.records = records

    def write_file(self, payload):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, filename = tempfile.mkstemp(prefix='.sessions-', suffix='.tmp', dir=self.path.parent)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(filename, self.path)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

class Session:
    def __init__(self, store, name, record=None):
        self.store, self.name = store, name
        self.cond = threading.Condition()
        record = record or dict(doc=blank_doc(), seeded=False, seq=0, nextSlot=1)
        self.doc = copy.deepcopy(record['doc'])
        self.seeded, self.seq = record['seeded'], record['seq']
        self.next_slot = max(record['nextSlot'], self.doc['nextId'] // 1_000_000 + 1)
        self.project = copy.deepcopy(record.get('project'))
        self.ops, self.peers = [], {}

    def commit(self, doc, seeded, seq, next_slot, project=None):
        project = copy.deepcopy(project if project is not None else self.project)
        record = dict(doc=doc, seeded=seeded, seq=seq, nextSlot=next_slot)
        if project:
            project['updatedAt'] = datetime.now(timezone.utc).isoformat()
            record['project'] = project
        try:
            self.store.persist(self.name, record)
        except RepositoryConflict as exc:
            current = exc.state['sessions'].get(self.name)
            if current:
                self.doc = validate_doc(current['doc'])
                self.seeded, self.seq, self.next_slot = current['seeded'], current['seq'], current['nextSlot']
                self.project = copy.deepcopy(current.get('project'))
                self.ops = []
                self.cond.notify_all()
            raise
        self.doc, self.seeded, self.seq, self.next_slot = doc, seeded, seq, next_slot
        self.project = project

    def join(self, name, seed):
        if not isinstance(name, str) or len(name) > 120:
            raise ValueError('Invalid participant name')
        with self.cond:
            if self.project and not name.strip():
                raise ValueError('Enter your display name')
            adopted = self.seeded
            doc = self.doc if adopted else validate_doc(seed)
            slot = max(self.next_slot, doc['nextId'] // 1_000_000 + 1)
            project = copy.deepcopy(self.project)
            if project and name.strip() not in project['members']:
                project['members'].append(name.strip())
            self.commit(doc, True, self.seq + (0 if adopted else 1), slot + 1, project)
            pid = secrets.token_hex(12)
            self.peers[pid] = dict(name=name or f'Guest {slot}', colour=COLOURS[(slot - 1) % len(COLOURS)], seen=time.time())
            self.cond.notify_all()
            return dict(peerId=pid, idBase=slot * 1_000_000, seq=self.seq, doc=self.doc,
                        seeded=True, adopted=adopted, peers=self.roster(), session=self.name,
                        project=self.project, storage=self.store.storage_info())

    def roster(self):
        now = time.time()
        self.peers = {pid: p for pid, p in self.peers.items() if now - p['seen'] <= PEER_TTL}
        return [dict(id=pid, name=p['name'], colour=p['colour']) for pid, p in self.peers.items()]

    def touch(self, pid):
        if pid not in self.peers:
            raise LookupError('Session restarted or participant expired; rejoin')
        self.peers[pid]['seen'] = time.time()

    def push(self, pid, ops):
        with self.cond:
            self.touch(pid)
            if not isinstance(ops, list) or not 1 <= len(ops) <= 1000:
                raise ValueError('Invalid operation batch')
            doc = copy.deepcopy(self.doc)
            for op in ops:
                doc = apply_op(doc, op)
            doc = validate_doc(doc)
            seq = self.seq
            self.commit(doc, True, seq + len(ops), self.next_slot)
            self.ops.extend(dict(seq=seq + i + 1, peer=pid, op=copy.deepcopy(op)) for i, op in enumerate(ops))
            self.ops = self.ops[-OPS_KEPT:]
            self.cond.notify_all()
            return self.seq

    def since(self, seq):
        if seq > self.seq or (seq < self.seq and (not self.ops or seq < self.ops[0]['seq'] - 1)):
            return None
        return [o for o in self.ops if o['seq'] > seq]


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if not self.path.startswith('/sync/'):
            super().log_message(fmt, *args)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def allowed(self, authenticate=True):
        origin = self.headers.get('Origin')
        if self.server.server_address[0] in ('127.0.0.1', '::1') and urlparse('http://' + self.headers.get('Host', '')).hostname not in ('localhost', '127.0.0.1', '::1'):
            self.send_json({'error': 'Host is not allowed'}, 403)
            return False
        same = origin and urlparse(origin).netloc == self.headers.get('Host')
        if origin and not same and origin not in self.server.origins:
            self.send_json({'error': 'Origin is not allowed'}, 403)
            return False
        if authenticate and self.server.token and not secrets.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + self.server.token):
            self.send_json({'error': 'Enter the session access code'}, 401)
            return False
        return True

    def cors(self):
        origin = self.headers.get('Origin')
        if origin and (urlparse(origin).netloc == self.headers.get('Host') or origin in self.server.origins):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.cors()
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 < length <= MAX_BODY:
            raise ValueError('Request size is invalid')
        body = json.loads(self.rfile.read(length))
        if not isinstance(body, dict):
            raise ValueError('Request must be an object')
        return body

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def sync_call(self, action):
        if not self.allowed():
            return
        try:
            action()
        except RepositoryConflict as exc:
            self.send_json({'error': str(exc)}, 409)
        except FileNotFoundError as exc:
            self.send_json({'error': str(exc)}, 404)
        except (ValueError, TypeError, KeyError) as exc:
            self.send_json({'error': str(exc)}, 400)
        except LookupError as exc:
            self.send_json({'error': str(exc)}, 410)
        except OSError:
            self.send_json({'error': 'Repository save failed; edits were not acknowledged'}, 503)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/sync/info':
            if self.allowed(authenticate=False):
                return self.send_json(dict(storage=self.server.store.storage_info(), requiresAccessCode=bool(self.server.token)))
            return
        if parsed.path == '/sync/projects':
            return self.sync_call(lambda: self.send_json(dict(projects=self.server.store.projects(), storage=self.server.store.storage_info())))
        if parsed.path in ('/sync/state', '/sync/poll'):
            return self.sync_call(lambda: self.read_sync(parsed))
        # Serve toolkit assets, never session files, source, credentials, or directory listings.
        path = Path(unquote(parsed.path)).parts
        if any(part.startswith('.') or part == 'data' for part in path) or Path(parsed.path).suffix not in ('', '.html', '.css', '.js', '.json', '.svg', '.png', '.jpg', '.jpeg', '.webp'):
            return self.send_error(404)
        return super().do_GET()

    def list_directory(self, path):
        self.send_error(404)

    def read_sync(self, parsed):
        q = parse_qs(parsed.query)
        s = self.server.store.session(q.get('session', ['default'])[0])
        with s.cond:
            if parsed.path == '/sync/state':
                return self.send_json(dict(seq=s.seq, doc=s.doc, seeded=s.seeded, peers=s.roster()))
            pid, seq = q.get('peerId', [''])[0], int(q.get('since', ['0'])[0])
            s.touch(pid)
            deadline = time.monotonic() + POLL_TIMEOUT
            roster_ids = [p['id'] for p in s.roster()]
            while True:
                ops = s.since(seq)
                if ops is None:
                    return self.send_json(dict(resync=True, seq=s.seq, doc=s.doc, peers=s.roster()))
                fresh = [o for o in ops if o['peer'] != pid]
                roster = s.roster()
                if fresh or [p['id'] for p in roster] != roster_ids or time.monotonic() >= deadline:
                    return self.send_json(dict(seq=s.seq, ops=fresh, peers=roster))
                s.cond.wait(min(1, max(.05, deadline - time.monotonic())))

    def do_POST(self):
        if urlparse(self.path).path not in ('/sync/join', '/sync/ops', '/sync/leave', '/sync/projects', '/sync/project/join'):
            return self.send_error(404)
        return self.sync_call(self.write_sync)

    def write_sync(self):
        body = self.body()
        route = urlparse(self.path).path
        if route in ('/sync/projects', '/sync/project/join'):
            if body.get('acknowledged') is not True:
                raise ValueError('Acknowledge project storage before continuing')
            name = body.get('name', '')
            if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
                raise ValueError('Enter your display name (up to 80 characters)')
            if route == '/sync/projects':
                return self.send_json(self.server.store.create_project(body.get('projectName'), name), 201)
            s = self.server.store.project(body.get('projectId', ''))
            return self.send_json(s.join(name.strip(), blank_doc()))
        s = self.server.store.session(body.get('session', 'default'))
        if route == '/sync/join':
            if s.project:
                raise ValueError('Use the project join route and acknowledge its storage notice')
            return self.send_json(s.join(body.get('name', ''), body.get('doc', blank_doc())))
        pid = body.get('peerId', '')
        if route == '/sync/ops':
            return self.send_json(dict(seq=s.push(pid, body.get('ops')), saved=True, storage=self.server.store.storage_info()))
        with s.cond:
            s.peers.pop(pid, None)
            s.cond.notify_all()
        return self.send_json(dict(ok=True))


def create_server(host='127.0.0.1', port=4317, data_file=HERE / 'data/sessions.json', root=HERE.parent, origins=(), token='', github=None):
    server = ThreadingHTTPServer((host, port), functools.partial(Handler, directory=str(root)))
    server.daemon_threads = True
    server.store, server.origins, server.token = Store(data_file, github), set(origins), token
    return server


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=int(os.environ.get('PORT', '4317')))
    ap.add_argument('--session', default='default')
    ap.add_argument('--root', default=str(HERE.parent))
    ap.add_argument('--data', default=str(HERE / 'data/sessions.json'))
    ap.add_argument('--allow-origin', action='append', default=[])
    args = ap.parse_args()
    token = os.environ.get('AOA_RELAY_TOKEN', '')
    if args.host not in ('127.0.0.1', 'localhost', '::1') and not token:
        ap.error('Set AOA_RELAY_TOKEN when binding beyond localhost')
    github_token = os.environ.get('AOA_GITHUB_TOKEN')
    github = GitHubRepository(os.environ.get('AOA_GITHUB_REPOSITORY', 'emmayg0722/AoA'), github_token,
                              os.environ.get('AOA_GITHUB_BRANCH', 'codex/discovery-data'),
                              os.environ.get('AOA_GITHUB_DATA_PATH', 'use-case-discovery-board/data/sessions.json')) if github_token else None
    server = create_server(args.host, args.port, args.data, args.root, args.allow_origin, token, github)
    print(f'Original discovery workshop: http://localhost:{args.port}/use-case-discovery-board/?session={args.session}', flush=True)
    print(f'Saved sessions: {args.data}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

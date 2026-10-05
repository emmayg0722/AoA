import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import relay
from github_store import GitHubRepository, RepositoryConflict
import test_relay
from test_relay import node_op


class ProjectHttpTests(unittest.TestCase):
    setUp = test_relay.HttpTests.setUp
    close_server = test_relay.HttpTests.close_server
    request = test_relay.HttpTests.request

    def test_create_join_isolation_notice_and_restart(self):
        body = dict(projectName='Claims discovery', name='Emma', acknowledged=True)
        with self.assertRaises(HTTPError) as error:
            self.request('/sync/projects', dict(body, acknowledged=False))
        self.assertEqual(400, error.exception.code)
        error.exception.close()
        self.assertFalse(self.path.exists())
        _, a, _ = self.request('/sync/projects', body)
        project_id = a['project']['id']
        self.assertEqual(['Emma'], a['project']['members'])
        self.assertEqual('local', a['storage']['mode'])
        _, b, _ = self.request('/sync/project/join', dict(projectId=project_id, name='Thomas', acknowledged=True))
        self.assertEqual(['Emma', 'Thomas'], b['project']['members'])
        self.assertNotEqual(a['idBase'], b['idBase'])
        _, other, _ = self.request('/sync/projects', dict(projectName='Separate workshop', name='Emma', acknowledged=True))
        self.request('/sync/ops', dict(session=project_id, peerId=a['peerId'], ops=[node_op(a['idBase'], 'Claims intake')]))
        _, shared, _ = self.request(f"/sync/poll?session={project_id}&peerId={b['peerId']}&since={b['seq']}")
        self.assertEqual('Claims intake', shared['ops'][0]['op']['node']['title'])
        _, state, _ = self.request('/sync/state?session=' + other['project']['id'])
        self.assertEqual([], state['doc']['nodes'])
        restarted = relay.Store(self.path)
        self.assertEqual(2, len(restarted.projects()))
        self.assertEqual('Claims intake', restarted.project(project_id).doc['nodes'][0]['title'])
        self.assertEqual(['Emma', 'Thomas'], restarted.project(project_id).project['members'])
        with self.assertRaises(HTTPError) as error:
            self.request('/sync/project/join', dict(projectId='not-a-project', name='Emma', acknowledged=True))
        self.assertEqual(404, error.exception.code)
        error.exception.close()
        self.assertEqual(2, len(restarted.projects()))
        with self.assertRaises(HTTPError) as error:
            self.request('/sync/join', dict(session=project_id, name='Bypass'))
        self.assertEqual(400, error.exception.code)
        error.exception.close()

    def test_configuration_has_no_credential_and_does_not_need_access_code(self):
        _, info, _ = self.request('/sync/info', token='')
        self.assertTrue(info['requiresAccessCode'])
        self.assertNotIn('test-access-code', json.dumps(info))
        for path in ('/sync/projects', '/sync/state'):
            with self.assertRaises(HTTPError) as error:
                self.request(path, token='')
            self.assertEqual(401, error.exception.code)
            error.exception.close()

    def test_failed_creation_never_lists_a_phantom_project(self):
        with patch('relay.os.replace', side_effect=OSError('Disk unavailable')):
            with self.assertRaises(HTTPError) as error:
                self.request('/sync/projects', dict(projectName='Unsaved', name='Emma', acknowledged=True))
        self.assertEqual(503, error.exception.code)
        error.exception.close()
        _, result, _ = self.request('/sync/projects')
        self.assertEqual([], result['projects'])


class GitHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sessions.json'
        self.initial = dict(schemaVersion=1, sessions={})
        self.git = GitHubRepository.__new__(GitHubRepository)
        self.git.repository = 'owner/repository'
        self.git.token = 'server-secret'
        self.git.branch = 'main'
        self.git.path = 'use-case-discovery-board/data/sessions.json'
        self.git.visibility = 'public'
        self.git.sha = 'old-content-sha'

    def test_contents_api_sends_base64_and_current_sha(self):
        with patch.object(self.git, 'request', return_value=dict(content=dict(sha='new-sha'), commit=dict(sha='saved-commit'))) as request:
            self.assertEqual('saved-commit', self.git.save(self.initial))
        route, body = request.call_args.args
        self.assertTrue(route.endswith('/contents/use-case-discovery-board/data/sessions.json'))
        self.assertEqual('old-content-sha', body['sha'])
        self.assertEqual(self.initial, json.loads(base64.b64decode(body['content'])))
        self.assertEqual('new-sha', self.git.sha)
        self.assertNotIn('server-secret', json.dumps(body))

    def test_github_failure_does_not_acknowledge_broadcast_or_change_local_state(self):
        with patch.object(self.git, 'load', return_value=self.initial), patch.object(self.git, 'save', return_value='first-commit'):
            store = relay.Store(self.path, self.git)
            a = store.create_project('Claims', 'Emma')
        session = store.project(a['project']['id'])
        before = self.path.read_bytes()
        with patch.object(self.git, 'save', side_effect=OSError('GitHub unavailable')):
            with self.assertRaises(OSError):
                session.push(a['peerId'], [node_op(a['idBase'])])
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual([], session.doc['nodes'])
        self.assertEqual([], session.ops)
        self.assertEqual('first-commit', store.storage_info()['commit'])

    def test_conflict_refreshes_remote_before_retry_without_overwriting_other_projects(self):
        with patch.object(self.git, 'load', return_value=self.initial), patch.object(self.git, 'save', return_value='first-commit'):
            store = relay.Store(self.path, self.git)
            a = store.create_project('Claims', 'Emma')
        session = store.project(a['project']['id'])
        remote = copy.deepcopy(dict(schemaVersion=1, sessions=store.records))
        remote['sessions']['other'] = dict(doc=relay.blank_doc(), seeded=True, seq=0, nextSlot=1)
        remote['sessions'][session.name]['doc']['fields']['process'] = 'Remote edit'
        remote['sessions'][session.name]['seq'] += 1
        with patch.object(self.git, 'save', side_effect=RepositoryConflict(remote)):
            with self.assertRaises(RepositoryConflict):
                session.push(a['peerId'], [node_op(a['idBase'])])
        self.assertEqual('Remote edit', session.doc['fields']['process'])
        self.assertEqual([], session.ops)
        with patch.object(self.git, 'save', return_value='retry-commit') as save:
            session.push(a['peerId'], [node_op(a['idBase'])])
        saved = save.call_args.args[0]
        self.assertIn('other', saved['sessions'])
        self.assertEqual('Remote edit', saved['sessions'][session.name]['doc']['fields']['process'])
        self.assertEqual(1, len(saved['sessions'][session.name]['doc']['nodes']))

    def test_409_and_new_file_422_refresh_data_and_reject_stale_write(self):
        for code, original_sha in ((409, 'old-content-sha'), (422, None)):
            self.git.sha = original_sha
            def refresh():
                self.git.sha = 'current-remote-sha'
                return self.initial
            error = HTTPError('https://api.github.com', code, 'Conflict', {}, None)
            with patch.object(self.git, 'request', side_effect=error), patch.object(self.git, 'load', side_effect=refresh):
                with self.assertRaises(RepositoryConflict):
                    self.git.save(self.initial)
            error.close()
            self.assertEqual('current-remote-sha', self.git.sha)

    def test_accepted_github_commit_remains_saved_if_secondary_mirror_fails(self):
        with patch.object(self.git, 'load', return_value=self.initial), patch.object(self.git, 'save', return_value='accepted-commit'):
            store = relay.Store(self.path, self.git)
            with patch.object(store, 'write_file', side_effect=OSError('Local mirror unavailable')):
                a = store.create_project('Claims', 'Emma')
        self.assertEqual('accepted-commit', a['storage']['commit'])
        self.assertEqual('github', a['storage']['mode'])
        self.assertEqual('public', a['storage']['visibility'])
        self.assertNotIn('server-secret', json.dumps(a))
        self.assertEqual(1, len(store.projects()))

    def test_invalid_remote_data_never_advances_the_sha_used_for_retries(self):
        self.git.validate = relay.validate_saved
        malformed = dict(schemaVersion=1, sessions={'project': dict(doc=relay.blank_doc(), seeded=True, seq=-1, nextSlot=1)})
        for content in ('not JSON', json.dumps(malformed)):
            payload = dict(sha='newer-remote-sha', content=base64.b64encode(content.encode()).decode())
            with patch.object(self.git, 'request', return_value=payload):
                with self.assertRaises(OSError):
                    self.git.load()
            self.assertEqual('old-content-sha', self.git.sha)


if __name__ == '__main__':
    unittest.main()

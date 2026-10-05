"""Server-only GitHub Contents API persistence for discovery projects."""
import base64
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class RepositoryConflict(Exception):
    def __init__(self, state):
        super().__init__('Repository changed; refreshed the saved project. Retry the edit.')
        self.state = state


class GitHubRepository:
    def __init__(self, repository, token, branch='codex/discovery-data', path='use-case-discovery-board/data/sessions.json'):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid GitHub repository')
        if not token or not path or path.startswith('/') or '..' in path.split('/'):
            raise ValueError('GitHub credential and repository-relative data path are required')
        self.repository, self.token, self.branch, self.path = repository, token, branch, path
        self.sha = None
        self.visibility = self.request('/repos/' + repository).get('visibility', 'private')

    def request(self, route, body=None, accept='application/vnd.github+json'):
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept': accept,
                   'Content-Type': 'application/json', 'User-Agent': 'AoA-discovery-relay',
                   'X-GitHub-Api-Version': '2026-03-10'}
        req = Request('https://api.github.com' + route,
                      data=json.dumps(body).encode() if body is not None else None,
                      headers=headers, method='PUT' if body is not None else 'GET')
        try:
            with urlopen(req, timeout=20) as response:
                return json.load(response)
        except HTTPError as exc:
            # Do not include response bodies, credentials, or authorization headers.
            code = exc.code
            exc.close()
            raise HTTPError(req.full_url, code, 'GitHub request failed', {}, None) from None
        except (URLError, TimeoutError) as exc:
            raise OSError('GitHub is unavailable; project changes were not saved') from None

    def route(self):
        return '/repos/' + self.repository + '/contents/' + quote(self.path, safe='/')

    def load(self):
        try:
            payload = self.request(self.route() + '?ref=' + quote(self.branch, safe=''))
        except HTTPError as exc:
            if exc.code == 404:
                self.sha = None
                return {'schemaVersion': 1, 'sessions': {}}
            raise OSError('Could not read GitHub project data (HTTP %s)' % exc.code) from None
        try:
            state = json.loads(base64.b64decode(payload['content']).decode()) if payload.get('content') else self.request(self.route() + '?ref=' + quote(self.branch, safe=''), accept='application/vnd.github.raw+json')
            validator = getattr(self, 'validate', None)
            if validator:
                state = validator(state)
            elif not isinstance(state, dict) or state.get('schemaVersion') != 1 or not isinstance(state.get('sessions'), dict):
                raise ValueError('Invalid saved data')
        except (ValueError, KeyError, TypeError) as exc:
            # Keep the previous SHA: retries must never overwrite unreadable remote data.
            raise OSError('Saved GitHub project data is invalid; repository contents were left unchanged') from None
        self.sha = payload['sha']
        return state

    def save(self, state):
        body = dict(message='Save discovery project data', branch=self.branch,
                    content=base64.b64encode((json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()).decode())
        if self.sha:
            body['sha'] = self.sha
        # Serialize repository writes at a modest rate; the relay owns one store lock.
        time.sleep(max(0, 2 - (time.monotonic() - getattr(self, 'last_write', 0))))
        self.last_write = time.monotonic()
        try:
            result = self.request(self.route(), body)
        except HTTPError as exc:
            if exc.code in (409, 422):
                previous_sha = self.sha
                remote = self.load()
                if exc.code == 409 or self.sha != previous_sha:
                    raise RepositoryConflict(remote) from None
            raise OSError('GitHub save failed (HTTP %s); edits are still pending' % exc.code) from None
        self.sha = result['content']['sha']
        return result['commit']['sha']

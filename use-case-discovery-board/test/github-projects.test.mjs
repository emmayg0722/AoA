import test from 'node:test';
import assert from 'node:assert/strict';
import '../github-projects.js';

const config = { repository: 'owner/board', branch: 'codex/discovery-data', path: 'use-case-discovery-board/data/sessions.json' };
const copy = value => structuredClone(value);
function github() {
  let state = { schemaVersion: 1, sessions: {} }, version = 1;
  const requests = [];
  const mock = {
    requests, fail: 0, race: null,
    get state() { return copy(state); },
    replace(value) { state = copy(value); version++; },
    async fetch(url, options) {
      requests.push({ url, ...options });
      const respond = (data, status = 200) => new Response(JSON.stringify(data), { status });
      if (url === 'https://api.github.com/user') return respond({ login: 'participant' });
      if (!url.includes('/contents/')) return respond({ private: false, permissions: { push: true } });
      if (options.method !== 'PUT') return respond({ sha: 'blob-' + version, type: 'file', encoding: 'base64', content: Buffer.from(JSON.stringify(state)).toString('base64') });
      if (mock.fail) return respond({}, mock.fail);
      if (mock.race) { const run = mock.race; mock.race = null; run(); }
      const body = JSON.parse(options.body);
      if (body.sha !== 'blob-' + version) return respond({}, 409);
      assert.equal(body.branch, config.branch);
      state = JSON.parse(Buffer.from(body.content, 'base64').toString('utf8')); version++;
      return respond({ commit: { sha: 'commit-' + version } });
    },
  };
  return mock;
}
async function client(mock, token = 'test-token') {
  const service = new AoaGithubProjects(config, { fetch: mock.fetch, sleep: async () => {}, pollMs: 0 });
  if (token) service.setToken(token);
  await service.connect();
  return service;
}
async function request(service, path, body) {
  const response = await service.request(path, body ? { method: 'POST', body: JSON.stringify(body) } : {});
  return { status: response.status, ...(await response.json()) };
}
const create = (service, projectName = 'Verification project', name = 'First participant') => request(service, '/sync/projects', { projectName, name, acknowledged: true });
const ops = (service, project, items) => request(service, '/sync/ops', { session: project.session, peerId: service.peerId, ops: items });

test('two participants share durable GitHub edits and receive confirmed commit links', async () => {
  const mock = github(), first = await client(mock), second = await client(mock);
  const project = await create(first, 'Unicode project æ 中');
  assert.equal(project.status, 201);
  const joined = await request(second, '/sync/project/join', { projectId: project.session, name: 'Second participant', acknowledged: true });
  assert.notEqual(project.idBase, joined.idBase);
  assert.deepEqual(joined.project.members, ['First participant', 'Second participant']);
  const saved = await ops(first, project, [{ t: 'field', k: 'process', v: 'Shared workflow æ 中' }]);
  assert.equal(saved.saved, true);
  assert.match(saved.storage.commit, /^commit-/);
  const polled = await request(second, '/sync/poll?session=' + project.session + '&since=0');
  assert.equal(polled.resync, true);
  assert.equal(polled.doc.fields.process, 'Shared workflow æ 中');
  assert.equal(polled.peers.length, 2);
});

test('new projects are empty and missing joins never create records', async () => {
  const mock = github(), service = await client(mock);
  const first = await create(service);
  await ops(service, first, [{ t: 'field', k: 'client', v: 'Test fixture client' }]);
  const second = await create(service, 'Separate verification project');
  assert.deepEqual(second.doc.fields, {});
  assert.equal((await request(service, '/sync/project/join', { projectId: 'missing', name: 'Participant', acknowledged: true })).status, 404);
  assert.equal(Object.keys(mock.state.sessions).length, 2);
});

test('SHA conflict rebases individual edits and preserves another project', async () => {
  const mock = github(), service = await client(mock);
  const first = await create(service), other = await create(service, 'Other project');
  mock.race = () => {
    const remote = mock.state;
    remote.sessions[first.session].doc.fields.scope = 'Concurrent saved scope';
    remote.sessions[other.session].doc.fields.client = 'Other project data';
    remote.sessions[first.session].seq++;
    mock.replace(remote);
  };
  const saved = await ops(service, first, [{ t: 'field', k: 'process', v: 'My saved edit' }]);
  assert.equal(saved.saved, true);
  assert.equal(mock.state.sessions[first.session].doc.fields.scope, 'Concurrent saved scope');
  assert.equal(mock.state.sessions[first.session].doc.fields.process, 'My saved edit');
  assert.equal(mock.state.sessions[other.session].doc.fields.client, 'Other project data');
});

test('GitHub denial never acknowledges or persists an edit', async () => {
  const mock = github(), service = await client(mock), project = await create(service);
  const before = mock.state;
  mock.fail = 403;
  const failed = await ops(service, project, [{ t: 'field', k: 'process', v: 'Unsent edit' }]);
  assert.equal(failed.status, 403);
  assert.equal(failed.saved, undefined);
  assert.deepEqual(mock.state, before);
  mock.fail = 0;
  assert.equal((await ops(service, project, [{ t: 'field', k: 'process', v: 'Unsent edit' }])).saved, true);
});

test('invalid repository records are never overwritten during a save or conflict retry', async () => {
  const mock = github(), service = await client(mock), project = await create(service);
  mock.race = () => { const remote = mock.state; remote.sessions[project.session].doc.nodes = [{ id: 1, type: 'unknown' }]; mock.replace(remote); };
  const failed = await ops(service, project, [{ t: 'field', k: 'process', v: 'Retained edit' }]);
  assert.equal(failed.saved, undefined);
  assert.equal(mock.state.sessions[project.session].doc.nodes[0].type, 'unknown');
  assert.equal(mock.requests.filter(r => r.method === 'PUT').length, 2); // create + rejected competing write
});

test('credential stays out of records and non-GitHub destinations, and can be forgotten', async () => {
  const mock = github(), service = await client(mock);
  await create(service);
  assert.equal(JSON.stringify(mock.state).includes('test-token'), false);
  assert.equal(JSON.stringify(service).includes('test-token'), false);
  await assert.rejects(service.api('https://other.invalid/'), /Invalid GitHub destination/);
  assert.ok(mock.requests.every(r => r.url.startsWith('https://api.github.com/') && r.credentials === 'omit' && r.redirect === 'error'));
  service.disconnect();
  assert.equal(service.connected, false);
  await request(service, '/sync/projects');
  assert.equal(mock.requests.at(-1).headers.Authorization, undefined);
  assert.equal((await create(service, 'Denied project')).status, 400);
});

test('public projects can be listed without a token, but creation requires credentials and disclosure', async () => {
  const mock = github(), writer = await client(mock);
  await create(writer);
  const reader = await client(mock, '');
  assert.equal((await request(reader, '/sync/projects')).projects.length, 1);
  assert.equal((await create(reader)).status, 400);
  assert.equal((await request(writer, '/sync/projects', { projectName: 'Undisclosed', name: 'Participant' })).status, 400);
  assert.equal(Object.keys(mock.state.sessions).length, 1);
});

test('failed project creation reuses its ID after an ambiguous committed response', async () => {
  const mock = github(), fetch = mock.fetch;
  let lost = true;
  mock.fetch = async (url, options) => {
    const response = await fetch(url, options);
    if (lost && options.method === 'PUT') { lost = false; throw new Error('Simulated lost response'); }
    return response;
  };
  const service = await client(mock);
  assert.equal((await create(service)).status, 400);
  const retry = await create(service);
  assert.equal(retry.status, 201);
  assert.equal(Object.keys(mock.state.sessions).length, 1);
});

test('block deletion removes its connections and malformed operations fail without a commit', async () => {
  const mock = github(), service = await client(mock), project = await create(service);
  const a = project.idBase, b = a + 1;
  await ops(service, project, [
    { t: 'node', node: { id: a, type: 'step', title: 'First' }, layout: { x: 0, y: 0, w: 200 } },
    { t: 'node', node: { id: b, type: 'usecase', title: 'Second' }, layout: { x: 300, y: 0, w: 200 } },
    { t: 'edge', edge: { id: b + 1, from: a, to: b, label: '' } },
  ]);
  await ops(service, project, [{ t: 'nodeDel', id: a }]);
  assert.equal(mock.state.sessions[project.session].doc.edges.length, 0);
  const before = mock.state;
  assert.equal((await ops(service, project, [{ t: 'field', k: '__proto__', v: 'bad' }])).saved, undefined);
  assert.deepEqual(mock.state, before);
});

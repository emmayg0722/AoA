import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { once } from 'node:events';
import http from 'node:http';
import { applyOperation, validateBoard } from '../board.mjs';
import { createBoardServer } from '../server.mjs';

const empty = () => ({ schemaVersion: 1, id: 'discovery', title: 'Test board', revision: 0, updatedAt: null, nodes: [], edges: [], imports: [] });
const node = (id = 'test-card') => ({ id, type: 'use-case', title: 'Persistence test', description: 'Test fixture only', owner: '', status: 'idea', x: 20, y: 30, scores: { roi: null, feasibility: null, impact: null } });
const save = card => ({ type: 'save-node', create: true, node: card });
async function fixture(t) {
  const directory = await mkdtemp(join(tmpdir(), 'aoa-board-test-'));
  const dataFile = join(directory, 'board.json'); await writeFile(dataFile, JSON.stringify(empty()));
  let server;
  const start = async () => { server = await createBoardServer({ dataFile }); server.listen(0, '127.0.0.1'); await once(server, 'listening'); return `http://127.0.0.1:${server.address().port}`; };
  const stop = async () => { if (server?.listening) await server.stop(); };
  let url = await start();
  t.after(async () => { await stop(); await rm(directory, { recursive: true, force: true }); });
  return { dataFile, directory, get url() { return url; }, stop, restart: async () => { await stop(); url = await start(); },
    get: async () => (await fetch(`${url}/api/board`)).json(),
    post: async (revision, operation, headers = {}) => { const response = await fetch(`${url}/api/board`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify({ revision, operation }) }); return { status: response.status, body: await response.json() }; }
  };
}
test('durable edits survive server restart with all card and connection fields', async t => {
  const f = await fixture(t);
  assert.equal((await f.post(0, save(node()))).status, 200);
  assert.equal((await f.post(1, save(node('second')))).status, 200);
  await f.post(2, { type: 'save-edge', edge: { id: 'test-edge', source: 'test-card', target: 'second', label: 'depends on' } });
  const moved = await f.post(3, { type: 'move-node', id: 'test-card', x: -120, y: 300 });
  const disk = JSON.parse(await readFile(f.dataFile, 'utf8'));
  assert.deepEqual(disk, moved.body); assert.equal(disk.nodes[0].x, -120); assert.equal(disk.edges[0].label, 'depends on');
  await f.restart(); assert.deepEqual(await f.get(), disk);
});
test('simultaneous writes accept one revision and reject the stale writer', async t => {
  const f = await fixture(t);
  const results = await Promise.all([f.post(0, save(node('first'))), f.post(0, save(node('second')))]);
  assert.deepEqual(results.map(result => result.status).sort(), [200, 409]);
  const board = await f.get(); assert.equal(board.revision, 1); assert.equal(board.nodes.length, 1);
  assert.deepEqual(results.find(result => result.status === 409).body.board, board);
});
test('live stream sends the initial board and the exact persisted edit', async t => {
  const f = await fixture(t), controller = new AbortController();
  t.after(() => controller.abort());
  const response = await fetch(`${f.url}/api/events`, { signal: controller.signal });
  assert.match(response.headers.get('content-type'), /text\/event-stream/);
  const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = '';
  async function snapshot() {
    while (!buffer.includes('\n\n')) { const chunk = await reader.read(); assert.equal(chunk.done, false); buffer += decoder.decode(chunk.value, { stream: true }); }
    const end = buffer.indexOf('\n\n'), event = buffer.slice(0, end); buffer = buffer.slice(end + 2);
    return JSON.parse(event.split('\n').find(line => line.startsWith('data: ')).slice(6));
  }
  assert.equal((await snapshot()).revision, 0);
  const saved = await f.post(0, save(node()));
  assert.deepEqual(await snapshot(), saved.body); assert.deepEqual(saved.body, JSON.parse(await readFile(f.dataFile, 'utf8')));
  controller.abort();
});
test('invalid scores and dangling connections never change disk or revision', async t => {
  const f = await fixture(t), before = await readFile(f.dataFile, 'utf8');
  const invalid = node(); invalid.scores.roi = 6;
  assert.equal((await f.post(0, save(invalid))).status, 400);
  assert.equal((await f.post(0, { type: 'save-edge', edge: { id: 'edge', source: 'missing', target: 'also-missing', label: '' } })).status, 400);
  assert.equal(await readFile(f.dataFile, 'utf8'), before); assert.equal((await f.get()).revision, 0);
});
test('deleting a card removes its incident connections', () => {
  let board = empty();
  board = applyOperation(board, { revision: 0, operation: save(node('first')) });
  board = applyOperation(board, { revision: 1, operation: save(node('second')) });
  board = applyOperation(board, { revision: 2, operation: { type: 'save-edge', edge: { id: 'edge', source: 'first', target: 'second', label: '' } } });
  board = applyOperation(board, { revision: 3, operation: { type: 'delete-node', id: 'first' } });
  assert.equal(board.nodes.length, 1); assert.equal(board.edges.length, 0);
});
test('legacy import preserves the full source payload and creates named candidates only', () => {
  const payload = { fields: { client: 'Test fixture', draftDoc: 'Retain original notes' }, rows: [{ name: 'Test candidate', pain: 'Test pain', roi: '4', feas: '3', impact: '2' }, { name: '' }], nextId: 3, lang: 'en' };
  const board = applyOperation(empty(), { revision: 0, operation: { type: 'import-prioritization', payload } });
  assert.equal(board.nodes.length, 1); assert.equal(board.nodes[0].scores.feasibility, 3); assert.deepEqual(board.imports[0].payload, payload);
  assert.deepEqual(validateBoard(board), board);
});
test('cross-origin writes and unknown hosts are rejected', async t => {
  const f = await fixture(t);
  assert.equal((await f.post(0, save(node()), { Origin: 'http://untrusted.example' })).status, 403);
  const hostStatus = await new Promise((done, reject) => {
    const request = http.get(`${f.url}/api/board`, { headers: { Host: 'untrusted.example' } }, response => { response.resume(); done(response.statusCode); });
    request.on('error', reject);
  });
  assert.equal(hostStatus, 403);
  assert.equal((await f.get()).revision, 0);
  assert.equal((await fetch(`${f.url}/package.json`)).status, 404);
  assert.equal((await fetch(`${f.url}/use-case-discovery-board/`)).status, 200);
});
test('failed disk writes do not advance the in-memory graph', async t => {
  const f = await fixture(t);
  await rm(f.directory, { recursive: true });
  assert.equal((await f.post(0, save(node()))).status, 500);
  assert.deepEqual(await f.get(), empty());
});

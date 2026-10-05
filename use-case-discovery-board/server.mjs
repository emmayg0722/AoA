import http from 'node:http';
import { readFile, writeFile, rename, unlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { networkInterfaces, hostname } from 'node:os';
import { BoardError, applyOperation, validateBoard } from './board.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const MAX_BODY = 2 * 1024 * 1024;
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/index.html', ['index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']]
]);
async function readBody(request) {
  if (request.headers['content-type']?.split(';')[0] !== 'application/json') throw new BoardError('Use application/json.', 415);
  let size = 0; const chunks = [];
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY) throw new BoardError('Import is too large (maximum 2 MB).', 413);
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new BoardError('Invalid JSON.'); }
}
export async function createBoardServer({ dataFile = join(root, 'data/board.json'), host = '127.0.0.1' } = {}) {
  let board = validateBoard(JSON.parse(await readFile(dataFile, 'utf8')));
  let writes = Promise.resolve();
  const clients = new Set();
  const allowedHosts = new Set(['localhost', '127.0.0.1', '::1', hostname().toLowerCase(), host.toLowerCase()]);
  for (const interfaces of Object.values(networkInterfaces())) for (const item of interfaces ?? []) allowedHosts.add(item.address.toLowerCase());
  const sendSnapshot = (client, snapshot) => client.write(`event: board\ndata: ${JSON.stringify(snapshot)}\n\n`);
  const persist = async snapshot => {
    const contents = JSON.stringify(snapshot, null, 2) + '\n';
    if (Buffer.byteLength(contents) > MAX_BODY) throw new BoardError('Saved board exceeds 2 MB. Export and reduce its size first.', 413);
    const temporary = join(dirname(dataFile), `.board-${randomUUID()}.tmp`);
    try {
      await writeFile(temporary, contents, { flag: 'wx', mode: 0o600 });
      await rename(temporary, dataFile);
    } finally { await unlink(temporary).catch(() => {}); }
  };
  const server = http.createServer(async (request, response) => {
    const json = (status, value) => { response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' }); response.end(JSON.stringify(value)); };
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");
    try {
      const authority = new URL(`http://${request.headers.host}`);
      if (!allowedHosts.has(authority.hostname.replace(/^\[|\]$/g, '').toLowerCase()) || Number(authority.port || 80) !== server.address()?.port) throw new BoardError('Unrecognized server address.', 403);
      if (request.headers.origin && request.headers.origin !== authority.origin) throw new BoardError('Cross-origin access is not allowed.', 403);
      const url = new URL(request.url, authority);
      if (url.pathname === '/use-case-discovery-board') { response.writeHead(302, { Location: '/use-case-discovery-board/' }); response.end(); return; }
      const path = url.pathname.replace(/^\/use-case-discovery-board(?=\/)/, '');
      if (path === '/api/board' || path === '/data/board.json') {
        if (request.method === 'GET') return json(200, board);
        if (path === '/api/board' && request.method === 'POST') {
          const input = await readBody(request);
          const pending = writes.then(async () => {
            const next = applyOperation(board, input);
            await persist(next); board = next;
            for (const client of clients) sendSnapshot(client, board);
            return next;
          });
          writes = pending.catch(() => {});
          return json(200, await pending);
        }
        return json(405, { error: 'Method not allowed.' });
      }
      if (path === '/api/events' && request.method === 'GET') {
        if (clients.size >= 100) throw new BoardError('Too many connected browsers.', 503);
        response.writeHead(200, { 'Content-Type': 'text/event-stream', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no' });
        clients.add(response); sendSnapshot(response, board);
        const heartbeat = setInterval(() => response.write(': keepalive\n\n'), 15000);
        response.on('close', () => { clearInterval(heartbeat); clients.delete(response); });
        return;
      }
      const asset = assets.get(path);
      if (!asset || !['GET', 'HEAD'].includes(request.method)) return json(404, { error: 'Not found.' });
      const content = await readFile(join(root, asset[0]));
      response.writeHead(200, { 'Content-Type': asset[1] }); response.end(request.method === 'HEAD' ? undefined : content);
    } catch (error) {
      if (error.status === 409) return json(409, { error: error.message, board });
      if (!error.status) console.error('Board request failed:', error.message);
      if (!response.headersSent) json(error.status ?? 500, { error: error.status ? error.message : 'Could not save or load the board. Check the server and try again.' });
      else response.end();
    }
  });
  server.stop = async () => {
    for (const client of clients) client.destroy();
    await writes;
    await new Promise((done, reject) => server.close(error => error ? reject(error) : done()));
  };
  return server;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const host = process.env.HOST || '127.0.0.1';
  const port = Number(process.env.PORT || 4317);
  const server = await createBoardServer({ host });
  server.listen(port, host, () => console.log(`Discovery board: http://${host}:${server.address().port}\nData: ${join(root, 'data/board.json')}`));
  for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, async () => { await server.stop(); process.exit(0); });
}

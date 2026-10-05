// GitHub Pages can call GitHub's CORS-enabled API directly. No shared secret is published.
(() => {
  const clone = value => JSON.parse(JSON.stringify(value));
  const colours = ['#1B1474', '#c0392b', '#1a8a5c', '#d4790e', '#5348c4', '#0e7c86'];
  const integer = n => Number.isSafeInteger(n) && n > 0;
  const object = value => value && typeof value === 'object' && !Array.isArray(value);
  const blank = () => ({ fields: {}, nodes: [], layout: {}, edges: [], sopDone: [], nextId: 1, view: { x: 40, y: 40, z: 1 }, lang: 'en' });
  const json = (value, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json' } });
  const encode = value => {
    const bytes = new TextEncoder().encode(JSON.stringify(value, null, 2) + '\n');
    let binary = '';
    for (let i = 0; i < bytes.length; i += 8192) binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
    return btoa(binary);
  };
  const decode = value => JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Uint8Array.from(atob(value.replace(/\s/g, '')), c => c.charCodeAt(0))));

  function validateDoc(doc) {
    if (!object(doc)) throw new Error('Invalid saved board. Nothing was overwritten.');
    doc = Object.assign(blank(), clone(doc));
    if (!object(doc.fields) || Object.entries(doc.fields).some(([k, v]) => !['client', 'assessor', 'process', 'scope', 'draftDoc'].includes(k) || typeof v !== 'string' || v.length > 100000)) throw new Error('Invalid saved fields.');
    if (!Array.isArray(doc.nodes) || doc.nodes.length > 5000 || !Array.isArray(doc.edges) || doc.edges.length > 10000 || !object(doc.layout)) throw new Error('Invalid saved board.');
    const ids = new Set();
    for (const n of doc.nodes) {
      const p = doc.layout[n.id];
      if (!object(n) || !integer(n.id) || ids.has(n.id) || !['step', 'pain', 'system', 'usecase', 'note'].includes(n.type) || !object(p) || !['x', 'y', 'w'].every(k => Number.isFinite(p[k])) || p.w <= 0) throw new Error('Invalid saved block.');
      if (['title', 'detail', 'role', 'volume', 'pattern', 'value', 'effort'].some(k => k in n && (typeof n[k] !== 'string' || n[k].length > 100000))) throw new Error('Invalid saved block text.');
      ids.add(n.id);
    }
    const nodeIds = new Set(ids);
    for (const e of doc.edges) {
      if (!object(e) || !integer(e.id) || ids.has(e.id) || !nodeIds.has(e.from) || !nodeIds.has(e.to) || typeof (e.label || '') !== 'string') throw new Error('Invalid saved connection.');
      ids.add(e.id);
    }
    if (!integer(doc.nextId) || !Array.isArray(doc.sopDone) || doc.sopDone.length > 100 || doc.sopDone.some(v => typeof v !== 'boolean') || !object(doc.view) || !['x', 'y', 'z'].every(k => Number.isFinite(doc.view[k])) || doc.view.z <= 0 || !['en', 'da', 'sv'].includes(doc.lang)) throw new Error('Invalid saved board settings.');
    // Always allocate above every existing ID, including externally edited files.
    doc.nextId = Math.max(doc.nextId, ...Array.from(ids, id => id + 1));
    return doc;
  }
  function validateState(state) {
    if (!object(state) || state.schemaVersion !== 1 || !object(state.sessions)) throw new Error('Invalid repository data. Nothing was overwritten.');
    for (const [id, record] of Object.entries(state.sessions)) {
      if (['__proto__', 'constructor', 'prototype'].includes(id) || !object(record) || !Number.isSafeInteger(record.seq) || record.seq < 0 || !integer(record.nextSlot) || typeof record.seeded !== 'boolean') throw new Error('Invalid saved project.');
      record.doc = validateDoc(record.doc);
      if (record.project && (!object(record.project) || record.project.id !== id || typeof record.project.name !== 'string' || !Array.isArray(record.project.members) || record.project.members.some(n => typeof n !== 'string'))) throw new Error('Invalid project details.');
      if (record.githubParticipants && (!object(record.githubParticipants) || Object.values(record.githubParticipants).some(p => !object(p) || typeof p.name !== 'string' || !integer(p.slot)))) throw new Error('Invalid project participants.');
    }
    return state;
  }
  function apply(doc, op) {
    if (!object(op)) throw new Error('Invalid edit.');
    if (op.t === 'doc') return validateDoc(op.doc);
    if (op.t === 'node') {
      if (!object(op.node) || !integer(op.node.id)) throw new Error('Invalid block.');
      const index = doc.nodes.findIndex(n => n.id === op.node.id);
      if (index < 0) doc.nodes.push(clone(op.node)); else doc.nodes[index] = clone(op.node);
      doc.layout[op.node.id] = clone(op.layout);
    } else if (op.t === 'nodeDel') {
      doc.nodes = doc.nodes.filter(n => n.id !== op.id); delete doc.layout[op.id];
      doc.edges = doc.edges.filter(e => e.from !== op.id && e.to !== op.id);
    } else if (op.t === 'edge') {
      if (!object(op.edge) || !integer(op.edge.id)) throw new Error('Invalid connection.');
      const index = doc.edges.findIndex(e => e.id === op.edge.id);
      if (index < 0) doc.edges.push(clone(op.edge)); else doc.edges[index] = clone(op.edge);
    } else if (op.t === 'edgeDel') doc.edges = doc.edges.filter(e => e.id !== op.id);
    else if (op.t === 'field') {
      if (!['client', 'assessor', 'process', 'scope', 'draftDoc'].includes(op.k)) throw new Error('Invalid field.');
      doc.fields[op.k] = op.v;
    } else if (op.t === 'sop') doc.sopDone = clone(op.sopDone);
    else throw new Error('Unknown edit.');
    return doc;
  }

  class GitHubProjects {
    #token = '';
    constructor(config, options = {}) {
      if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(config.repository) || !config.branch || !config.path || config.path.split('/').some(p => !p || p === '.' || p === '..')) throw new Error('Invalid repository configuration.');
      this.repository = config.repository; this.branch = config.branch; this.path = config.path;
      this.endpoint = 'https://api.github.com/repos/' + this.repository;
      this.contents = this.endpoint + '/contents/' + this.path.split('/').map(encodeURIComponent).join('/');
      this.fetch = options.fetch || ((...args) => fetch(...args));
      this.sleep = options.sleep || (ms => new Promise(resolve => setTimeout(resolve, ms)));
      this.pollMs = options.pollMs ?? 12000;
      this.peerId = crypto.randomUUID(); this.visibility = 'public'; this.login = ''; this.memberName = '';
      this.lastCommit = null; this.writes = Promise.resolve(); this.pendingCreate = null;
    }
    get connected() { return !!this.#token && !!this.login; }
    setToken(token) { this.#token = token.trim(); this.login = ''; }
    disconnect() { this.#token = ''; this.login = ''; }
    async api(url, options = {}) {
      if (new URL(url).origin !== 'https://api.github.com') throw new Error('Invalid GitHub destination.');
      const headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2026-03-10', ...options.headers };
      if (this.#token) headers.Authorization = 'Bearer ' + this.#token;
      const response = await this.fetch(url, { ...options, headers, credentials: 'omit', redirect: 'error', cache: 'no-store', signal: options.signal || AbortSignal.timeout(20000) });
      if (!response.ok) {
        let message = response.status === 401 ? 'GitHub rejected this token. Connect with a valid repository token.' : response.status === 403 ? 'GitHub denied access or reached its request limit. Check Contents write permission and try later.' : response.status === 404 ? 'Repository, data branch, or saved project file not found.' : 'GitHub request failed (HTTP ' + response.status + '). Your browser edits are retained.';
        const error = new Error(message); error.status = response.status; throw error;
      }
      return response;
    }
    async connect() {
      if (this.#token) {
        const user = await (await this.api('https://api.github.com/user')).json();
        if (typeof user.login !== 'string') throw new Error('Cannot verify GitHub identity.');
        this.login = user.login;
      }
      const repo = await (await this.api(this.endpoint)).json();
      this.visibility = repo.private ? 'private' : 'public';
      if (this.connected && repo.permissions?.push === false) { this.login = ''; throw new Error('Your GitHub account needs write access to this repository.'); }
      return this.storage();
    }
    storage() { return { mode: 'github', transport: 'direct', repository: this.repository, url: 'https://github.com/' + this.repository, branch: this.branch, path: this.path, visibility: this.visibility, commit: this.lastCommit }; }
    async read() {
      const url = this.contents + '?ref=' + encodeURIComponent(this.branch);
      const file = await (await this.api(url)).json();
      if (!file.sha || file.type !== 'file') throw new Error('Invalid project data file.');
      const state = file.encoding === 'base64' ? decode(file.content) : await (await this.api(url, { headers: { Accept: 'application/vnd.github.raw+json' } })).json();
      return { sha: file.sha, state: validateState(state) };
    }
    async mutate(change) {
      if (!this.connected) throw new Error('Connect your GitHub token with Contents write access first.');
      const work = async () => {
        for (let attempt = 0; attempt < 4; attempt++) {
          const { sha, state } = await this.read();
          const before = JSON.stringify(state);
          const result = change(state);
          validateState(state);
          if (before === JSON.stringify(state)) return result;
          try {
            const saved = await (await this.api(this.contents, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: 'Save discovery project data', branch: this.branch, sha, content: encode(state) }) })).json();
            if (!saved.commit?.sha) throw new Error('GitHub did not confirm a commit.');
            this.lastCommit = saved.commit.sha;
            return result;
          } catch (error) {
            // Re-read and reapply operations after a competing SHA update. Never write an old snapshot.
            if (![409, 422].includes(error.status) || attempt === 3) throw error;
            await this.sleep(1000 * (attempt + 1));
          }
        }
      };
      const promise = this.writes.then(work, work);
      this.writes = promise.catch(() => {});
      return promise;
    }
    record(state, id) {
      if (!Object.hasOwn(state.sessions, id) || !state.sessions[id].project) { const error = new Error('Project not found. Check the invitation or choose an existing project.'); error.status = 404; throw error; }
      return state.sessions[id];
    }
    roster(record) {
      return record.project.members.map((name, i) => ({ id: name === this.memberName ? this.peerId : 'member-' + i, name, colour: colours[i % colours.length] }));
    }
    joined(record, id) {
      const allocation = record.githubParticipants[this.peerId];
      return { session: id, peerId: this.peerId, idBase: allocation.slot * 1000000, doc: clone(record.doc), seq: record.seq, peers: this.roster(record), project: clone(record.project), storage: this.storage(), adopted: true };
    }
    joinRecord(record, name) {
      record.githubParticipants ||= {};
      if (!record.githubParticipants[this.peerId]) {
        const slot = Math.max(record.nextSlot, Math.floor(record.doc.nextId / 1000000) + 1);
        if (slot > 1000000) throw new Error('This project has exhausted its participant ID ranges.');
        record.githubParticipants[this.peerId] = { slot, name };
        record.nextSlot = slot + 1;
      }
      if (!record.project.members.includes(name)) record.project.members.push(name);
      record.project.updatedAt = new Date().toISOString();
    }
    async request(path, options = {}) {
      try {
        const url = new URL(path, 'https://board.invalid');
        const body = options.body ? JSON.parse(options.body) : {};
        if (url.pathname === '/sync/info') return json({ storage: await this.connect(), requiresGithubToken: true });
        if (url.pathname === '/sync/projects' && options.method !== 'POST') {
          const { state } = await this.read();
          return json({ projects: Object.values(state.sessions).filter(r => r.project).map(r => r.project), storage: this.storage() });
        }
        if (url.pathname === '/sync/projects' || url.pathname === '/sync/project/join') {
          if (!body.acknowledged || typeof body.name !== 'string' || !body.name.trim() || body.name.trim().length > 80) throw new Error('Enter your display name and acknowledge repository storage.');
          this.memberName = body.name.trim();
          let id = body.projectId;
          if (url.pathname === '/sync/projects') {
            if (typeof body.projectName !== 'string' || !body.projectName.trim() || body.projectName.trim().length > 120) throw new Error('Enter a project name (up to 120 characters).');
            const key = body.projectName.trim() + '\n' + this.memberName;
            if (this.pendingCreate?.key !== key) this.pendingCreate = { key, id: crypto.randomUUID() };
            id = this.pendingCreate.id;
          }
          const record = await this.mutate(state => {
            if (url.pathname === '/sync/projects' && !Object.hasOwn(state.sessions, id)) {
              const stamp = new Date().toISOString();
              state.sessions[id] = { doc: blank(), seeded: true, seq: 0, nextSlot: 1, project: { id, name: body.projectName.trim(), createdAt: stamp, updatedAt: stamp, createdBy: this.memberName, members: [] } };
            }
            const current = this.record(state, id); this.joinRecord(current, this.memberName); return current;
          });
          this.pendingCreate = null;
          return json(this.joined(record, id), url.pathname === '/sync/projects' ? 201 : 200);
        }
        if (url.pathname === '/sync/ops') {
          if (body.peerId !== this.peerId || !Array.isArray(body.ops) || !body.ops.length || body.ops.length > 1000) throw new Error('Invalid pending edits.');
          const seq = await this.mutate(state => {
            const record = this.record(state, body.session);
            if (!record.githubParticipants?.[this.peerId]) throw new Error('Rejoin this project before saving.');
            for (const op of body.ops) record.doc = apply(record.doc, op);
            record.doc = validateDoc(record.doc); record.seq += body.ops.length;
            record.project.updatedAt = new Date().toISOString(); return record.seq;
          });
          return json({ seq, saved: true, storage: this.storage() });
        }
        if (url.pathname === '/sync/poll') {
          await this.sleep(this.pollMs);
          const { state } = await this.read();
          const record = this.record(state, url.searchParams.get('session'));
          const changed = record.seq !== Number(url.searchParams.get('since'));
          return json({ seq: record.seq, peers: this.roster(record), resync: changed, ...(changed ? { doc: record.doc } : {}) });
        }
        if (url.pathname === '/sync/leave') return json({ left: true });
        throw new Error('Use Create or Join project to collaborate on GitHub.');
      } catch (error) { return json({ error: error.message }, error.status || 400); }
    }
  }
  globalThis.AoaGithubProjects = GitHubProjects;
})();

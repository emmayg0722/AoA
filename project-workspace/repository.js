export class GithubError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

// Credentials belong to this connection only; never to a manifest or browser store.
export class Repository {
  #token = '';
  constructor(config, request = (...args) => fetch(...args)) {
    if (!/^[\w.-]+\/[\w.-]+$/.test(config.repository)) throw new Error('Invalid repository.');
    if (!/^[\w./-]+$/.test(config.branch)) throw new Error('Invalid branch.');
    this.repository = config.repository; this.branch = config.branch; this.request = request;
    this.login = ''; this.visibility = 'public';
  }
  get connected() { return !!this.#token && !!this.login; }
  disconnect() { this.#token = ''; this.login = ''; }
  async api(path, method = 'GET', body) {
    const headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2026-03-10' };
    if (this.#token) headers.Authorization = 'Bearer ' + this.#token;
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    const response = await this.request('https://api.github.com' + path, {
      method, headers, credentials: 'omit', redirect: 'error', cache: 'no-store',
      signal: AbortSignal.timeout(30000), ...(body === undefined ? {} : {body: JSON.stringify(body)})
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new GithubError(
      response.status === 401 ? 'GitHub rejected this token. Reconnect with a valid token.' :
      response.status === 403 ? 'GitHub access is denied or rate limited. Check Contents write access and try again.' :
      response.status === 404 ? 'The GitHub repository, branch, or file is unavailable.' :
      `GitHub request failed (${response.status}). ${data.message || ''}`, response.status);
    return data;
  }
  get base() { return '/repos/' + this.repository; }
  async inspect() {
    const data = await this.api(this.base);
    this.visibility = data.private ? 'private' : 'public';
    return data;
  }
  async connect(token) {
    this.disconnect(); this.#token = token.trim();
    try {
      if (!this.#token) throw new Error('Enter your GitHub token.');
      const user = await this.api('/user');
      const repo = await this.inspect();
      if (repo.permissions && repo.permissions.push === false) throw new Error('Your GitHub account needs write access to this repository.');
      this.login = user.login; await this.head();
      return this.login;
    } catch (error) { this.disconnect(); throw error; }
  }
  async head() {
    return (await this.api(this.base + '/git/ref/heads/' + this.branch)).object.sha;
  }
  async read(path, ref) {
    if (!ref) throw new Error('A snapshot commit is required.');
    try {
      const data = await this.api(this.base + '/contents/' + path.split('/').map(encodeURIComponent).join('/') + '?ref=' + encodeURIComponent(ref));
      if (data.encoding !== 'base64' || typeof data.content !== 'string') throw new Error('Project file is too large to load through GitHub.');
      const bytes = Uint8Array.from(atob(data.content.replace(/\s/g, '')), c => c.charCodeAt(0));
      return JSON.parse(new TextDecoder().decode(bytes));
    } catch (error) { if (error.status === 404) return null; throw error; }
  }
  async commit(message, prepare) {
    if (!this.connected) throw new Error('Connect your GitHub account before saving.');
    for (let attempt = 0; attempt < 4; attempt++) {
      const head = await this.head();
      const changes = await prepare(head);
      if (!changes.length) return {sha: head};
      const parent = await this.api(this.base + '/git/commits/' + head);
      const tree = await this.api(this.base + '/git/trees', 'POST', {
        base_tree: parent.tree.sha,
        tree: changes.map(({path, value}) => ({path, mode: '100644', type: 'blob', content: JSON.stringify(value, null, 2) + '\n'}))
      });
      const commit = await this.api(this.base + '/git/commits', 'POST', {message, tree: tree.sha, parents: [head]});
      try {
        await this.api(this.base + '/git/refs/heads/' + this.branch, 'PATCH', {sha: commit.sha, force: false});
        return {sha: commit.sha};
      } catch (error) {
        if (![409, 422].includes(error.status) || attempt === 3) throw error;
      }
    }
  }
}

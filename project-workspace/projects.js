export const ENGAGEMENT_KEY = 'aoa_engagement_v1';
export const INDEX_PATH = 'projects/index.json';
const copy = value => value === undefined ? undefined : structuredClone(value);
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const object = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const own = (v, key) => Object.prototype.hasOwnProperty.call(v, key);
export class Conflict extends Error {
  constructor(paths) { super('Other saved edits conflict with your changes: ' + paths.join(', ')); this.paths = paths; }
}

export function merge(base, local, remote, path = '', conflicts = []) {
  if (equal(local, base)) return copy(remote);
  if (equal(remote, base) || equal(local, remote)) return copy(local);
  // Older imports and unused tools can omit fields. A form's newly materialized
  // blank is not an intentional clear of a teammate's newly populated field.
  if (base === undefined && local === '' && typeof remote === 'string') return remote;
  if (base === undefined && remote === '' && typeof local === 'string') return local;
  if (base === undefined && Array.isArray(local) && !local.length && Array.isArray(remote)) return copy(remote);
  if (base === undefined && Array.isArray(remote) && !remote.length && Array.isArray(local)) return copy(local);
  const keyed = list => Array.isArray(list) && list.every(v => object(v) && ['string','number'].includes(typeof v.id)) && new Set(list.map(v => String(v.id))).size === list.length;
  if (keyed(base) && keyed(local) && keyed(remote)) {
    const byId = list => new Map(list.map(v => [String(v.id),v]));
    const before=byId(base), mine=byId(local), theirs=byId(remote), result=[];
    for (const id of new Set([...theirs.keys(),...mine.keys()])) {
      const itemPath=`${path}[id=${id}]`;
      // Concurrent additions with the same numeric ID are distinct records.
      if (!before.has(id) && mine.has(id) && theirs.has(id) && !equal(mine.get(id),theirs.get(id))) {
        conflicts.push(itemPath);result.push(copy(mine.get(id)));continue;
      }
      const item=merge(before.get(id),mine.get(id),theirs.get(id),itemPath,conflicts);
      if (item!==undefined) result.push(item);
    }
    return result;
  }
  if (object(local) && object(remote) && (object(base) || base == null)) {
    const result = {}; base = object(base) ? base : {};
    for (const key of new Set([...Object.keys(base), ...Object.keys(local), ...Object.keys(remote)])) {
      // Avoid inherited keys and prototype mutations when importing arbitrary JSON.
      const value = merge(own(base,key) ? base[key] : undefined, own(local,key) ? local[key] : undefined,
        own(remote,key) ? remote[key] : undefined, path ? path + '.' + key : key, conflicts);
      if (value !== undefined) Object.defineProperty(result, key, {value, enumerable: true, configurable: true, writable: true});
    }
    return result;
  }
  conflicts.push(path || 'state'); return copy(local);
}

export function keyPaths(registry, id) {
  if (!/^[a-z0-9-]+$/.test(id)) throw new Error('Invalid project ID.');
  const paths = new Map([[ENGAGEMENT_KEY, `projects/${id}/engagement.json`]]);
  for (const phase of registry) for (const tool of phase.tools)
    paths.set(tool.key, `projects/${id}/${phase.folder}/${tool.folder}/state.json`);
  return paths;
}

async function concurrent(items, action) {
  const results = []; let cursor = 0;
  await Promise.all(Array.from({length: Math.min(6, items.length)}, async () => {
    while (cursor < items.length) { const i = cursor++; results[i] = await action(items[i]); }
  }));
  return results;
}

export class Projects {
  constructor(repository, registry) { this.repository = repository; this.registry = registry; }
  async list() {
    const head = await this.repository.head();
    const index = await this.repository.read(INDEX_PATH, head);
    if (!index || index.schemaVersion !== 1 || !Array.isArray(index.projects)) throw new Error('The project index has not been prepared yet.');
    return index.projects;
  }
  async create({id, client, title, name, initialValues = {}, example = null}) {
    if (![client,title,name].every(v => typeof v === 'string' && v.trim() && v.length <= 160)) throw new Error('Enter a client, project name, and your name (up to 160 characters).');
    const paths = keyPaths(this.registry, id);
    if (!object(initialValues) || Object.keys(initialValues).some(key => !paths.has(key))) throw new Error('The starting project contains an unsupported tool.');
    if (example !== null && (typeof example !== 'string' || !/^[a-z0-9-]+$/.test(example))) throw new Error('The starting example ID is invalid.');
    const now = new Date().toISOString();
    const summary = {id, client: client.trim(), title: title.trim(), createdAt: now};
    const manifest = {schemaVersion: 1, ...summary, members: {[this.repository.login]: {name: name.trim(), joinedAt: now}}};
    if (example) manifest.sourceExampleId=example;
    return this.repository.commit('Create client project ' + id, async head => {
      const index = await this.repository.read(INDEX_PATH, head);
      if (!index || index.schemaVersion !== 1) throw new Error('Project data branch is not initialized.');
      if (index.projects.some(p => p.id === id)) {
        const existing = await this.repository.read(`projects/${id}/project.json`, head);
        if (existing?.client === summary.client && existing?.title === summary.title && existing?.members?.[this.repository.login]) return [];
        throw new Error('This project ID already exists.');
      }
      return [{path: INDEX_PATH, value: {...index, projects: [...index.projects, summary]}},
        {path: `projects/${id}/project.json`, value: manifest},
        ...Array.from(paths, ([key,path]) => {
          const data=key===ENGAGEMENT_KEY ? {client:summary.client,assessor:name.trim(),useCase:summary.title} : copy(initialValues[key]) ?? null;
          // Update identity headers only. Example narratives remain visibly fictional
          // and must be replaced by the participants before treating them as client work.
          if (object(data)) {
            for (const fields of [data,data.fields].filter(object)) {
              if (own(fields,'client')) fields.client=summary.client;
              if (own(fields,'company')) fields.company=summary.client;
              if (own(fields,'assessor')) fields.assessor=name.trim();
            }
          }
          return {path,value:{schemaVersion:1,key,data}};
        })];
    });
  }
  async join(id, name) {
    if (!name.trim() || name.length > 160) throw new Error('Enter your name (up to 160 characters).');
    keyPaths(this.registry, id);
    return this.repository.commit('Join client project ' + id, async head => {
      const path = `projects/${id}/project.json`;
      const manifest = await this.repository.read(path, head);
      if (!manifest) throw new Error('This project does not exist.');
      const member = manifest.members?.[this.repository.login];
      if (member?.name === name.trim()) return [];
      return [{path, value:{...manifest, members:{...manifest.members, [this.repository.login]:{name:name.trim(), joinedAt:member?.joinedAt || new Date().toISOString()}}}}];
    });
  }
  async load(id) {
    const paths = keyPaths(this.registry, id); const head = await this.repository.head();
    const manifest = await this.repository.read(`projects/${id}/project.json`, head);
    if (!manifest || manifest.schemaVersion !== 1) throw new Error('This project does not exist or uses an unsupported format.');
    const values = Object.fromEntries(await concurrent([...paths], async ([key,path]) => {
      const state = await this.repository.read(path, head);
      if (!state || state.schemaVersion !== 1 || state.key !== key) throw new Error('Project file is missing or invalid: ' + path);
      return [key, state.data];
    }));
    return {id, head, manifest, values};
  }
  async save(id, baseline, desired) {
    const paths = keyPaths(this.registry, id); let accepted;
    const result = await this.repository.commit('Save client project ' + id, async head => {
      const changed = Object.keys(desired).filter(key => paths.has(key) && !equal(desired[key],baseline[key]));
      const conflicts = []; accepted = {};
      const files = await concurrent(changed, async key => {
        const state = await this.repository.read(paths.get(key), head);
        if (!state || state.key !== key || state.schemaVersion !== 1) throw new Error('Project state is unavailable: ' + key);
        const data = merge(baseline[key], desired[key], state.data, key, conflicts);
        accepted[key] = data;
        return equal(data,state.data) ? null : {path:paths.get(key), value:{schemaVersion:1, key, data}};
      });
      if (conflicts.length) throw new Conflict(conflicts);
      return files.filter(Boolean);
    });
    return {...result, accepted};
  }
}

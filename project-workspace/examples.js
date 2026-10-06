import {ENGAGEMENT_KEY} from './projects.js';

export function coverage(example, registry) {
  const populated = new Set(Object.keys(example.sources));
  return {
    tools: registry.flatMap(phase => phase.tools).filter(tool => populated.has(tool.key)).length,
    phases: registry.filter(phase => phase.tools.some(tool => populated.has(tool.key))).length
  };
}

export async function loadExample(example, registry, root, request = fetch) {
  const tools = registry.flatMap(phase => phase.tools);
  const allowed = new Set(tools.map(tool => tool.key));
  if (!example || !/^[a-z0-9-]+$/.test(example.id) || !example.client || !example.title || !example.sources || example.engagement?.client !== example.client)
    throw new Error('This example project is invalid.');
  const files = await Promise.all(Object.entries(example.sources).map(async ([key,path]) => {
    const url = new URL(path,root);
    const sampleRoot = new URL('Phase 1 - Discovery & Assessment/sample-data/',root);
    if (!allowed.has(key) || url.origin !== sampleRoot.origin || !url.pathname.startsWith(sampleRoot.pathname) || url.search || url.hash)
      throw new Error('This example contains an unsupported source.');
    const response = await request(url);
    if (!response.ok) throw new Error('Example source could not load: '+path);
    const data = await response.json();
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Example source is invalid: '+path);
    return [key,data];
  }));
  return {
    id: example.id, example: true, coverage: coverage(example,registry),
    manifest: {client:example.client,title:example.title},
    values: {...Object.fromEntries(tools.map(tool => [tool.key,null])), [ENGAGEMENT_KEY]:structuredClone(example.engagement), ...Object.fromEntries(files)}
  };
}

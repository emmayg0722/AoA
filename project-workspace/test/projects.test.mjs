import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Repository} from '../repository.js';
import {Projects,Conflict,merge,keyPaths,ENGAGEMENT_KEY} from '../projects.js';
import {FakeGithub} from './fake-github.mjs';
import {loadExample} from '../examples.js';
const registry=JSON.parse(await readFile(new URL('../registry.json',import.meta.url)));
const key=registry[1].tools[0].key;
async function setup() {
  const api=new FakeGithub();const repo=new Repository({repository:'test/toolkit',branch:'codex/project-data'},api.request.bind(api));
  await repo.connect('test-valid');return {api,repo,projects:new Projects(repo,registry)};
}
const details=id => ({id,client:'Test client Å',title:'Fixture engagement',name:'Test architect'});

test('registry covers all ten phases, every unique tool, and valid integrated original pages',async () => {
  assert.equal(registry.length,10);const tools=registry.flatMap(p=>p.tools);assert.equal(tools.length,45);
  assert.equal(new Set(tools.map(t=>t.key)).size,45);assert.equal(keyPaths(registry,'test-project').size,46);
  for (const t of tools) {
    const href=decodeURIComponent(t.href)+(t.href.endsWith('/') ? 'index.html' : '');
    const html=await readFile(new URL('../../'+href,import.meta.url),'utf8');
    assert.match(html,/project-workspace\/tool-storage.js/);assert.ok(html.indexOf('tool-storage.js')<html.indexOf('<style>'));
  }
});
test('atomic creation initializes one client folder, shared header and all 45 tool files',async () => {
  const {api,projects}=await setup();await projects.create(details('test-project'));
  const files=api.snapshots.get(api.head);assert.equal(Object.keys(files).length,48);
  assert.equal(files['projects/index.json'].projects.length,1);
  const loaded=await projects.load('test-project');assert.equal(loaded.manifest.client,'Test client Å');assert.equal(loaded.values[ENGAGEMENT_KEY].client,'Test client Å');
  assert.equal(loaded.values[key],null);assert.equal(api.calls.filter(c=>c.method==='PATCH').length,1);
  assert.ok(!JSON.stringify(files).includes('test-valid'));
});
test('anonymous project IDs load every saved tool without credentials, membership changes or per-file REST calls',async () => {
  const {api,projects,repo}=await setup();await projects.create(details('public-project'));
  const original=JSON.stringify(api.snapshots.get(api.head));repo.disconnect();api.calls=[];
  const listed=await projects.list();const loaded=await projects.load(listed[0].id);
  assert.equal(loaded.manifest.client,'Test client Å');assert.equal(Object.keys(loaded.values).length,46);
  assert.ok(api.calls.every(call=>call.method==='GET' && !call.headers?.Authorization));
  assert.equal(api.calls.filter(call=>call.path.includes('/contents/')).length,0);
  assert.equal(JSON.stringify(api.snapshots.get(api.head)),original);
  await assert.rejects(projects.save(loaded.id,loaded.values,{...loaded.values,[key]:{fields:{vision:'Denied'}}}),/Connect your GitHub/);
  await assert.rejects(projects.load('../private'),/Invalid project ID/);
  await assert.rejects(projects.load('missing-public-project'),/does not exist/);
});
test('failed branch update never acknowledges or exposes partial project data',async () => {
  const {api,projects}=await setup();api.failUpdate=true;
  await assert.rejects(projects.create(details('test-project')),/access is denied/);
  assert.deepEqual(api.snapshots.get(api.head)['projects/index.json'].projects,[]);
});
test('copying an example creates separate phase folders atomically and updates only identity headers',async () => {
  const catalog=JSON.parse(await readFile(new URL('../examples/catalog.json',import.meta.url)));
  const example=await loadExample(catalog.projects[0],registry,new URL('../../',import.meta.url),async url=>({ok:true,json:async()=>JSON.parse(await readFile(url,'utf8'))}));
  const before=JSON.stringify(example.values);const {api,projects}=await setup();
  await projects.create({...details('example-copy'),initialValues:example.values,example:example.id});
  const loaded=await projects.load('example-copy');
  assert.equal(loaded.manifest.sourceExampleId,'nordkap');
  assert.equal(loaded.values.aoa_usecase_board_v1.fields.client,'Test client Å');
  assert.equal(loaded.values.aoa_ai_strategy_v1.fields.assessor,'Test architect');
  assert.equal(loaded.values[ENGAGEMENT_KEY].useCase,'Fixture engagement');
  assert.equal(loaded.values.aoa_ai_strategy_v1.fields.vision,example.values.aoa_ai_strategy_v1.fields.vision);
  assert.ok(loaded.values.aoa_roi_analysis_v1);
  assert.equal(loaded.values.dra_arch_builder_v1,null);
  assert.equal(JSON.stringify(example.values),before);
  assert.equal(api.calls.filter(c=>c.method==='PATCH').length,1);
  await projects.create(details('empty-project'));
  assert.equal((await projects.load('empty-project')).values.aoa_ai_strategy_v1,null);
  await assert.rejects(projects.create({...details('bad-seed'),initialValues:{unknown:{}}}),/unsupported tool/);
});
test('creation retry with the same request ID does not duplicate the project',async () => {
  const {projects}=await setup();await projects.create(details('test-project'));await projects.create(details('test-project'));
  assert.equal((await projects.list()).length,1);
});
test('competing project creation is rebased onto the current tree without dropping either client',async () => {
  const {api,projects}=await setup();api.beforeUpdate=()=>api.external(files=>files['projects/index.json'].projects.push({id:'other-project',client:'Other fixture',title:'Other test'}));
  await projects.create(details('test-project'));
  assert.deepEqual((await projects.list()).map(p=>p.id),['other-project','test-project']);
  assert.equal(api.calls.filter(c=>c.method==='PATCH').length,2);
});
test('same tool, independent fields from two participants merge without losing work',async () => {
  const {projects}=await setup();await projects.create(details('test-project'));
  const initial=await projects.load('test-project');const first=structuredClone(initial.values);first[key]={fields:{vision:'Initial vision',objective:'Initial objective'},rows:[]};
  await projects.save('test-project',initial.values,first);const a=await projects.load('test-project');const b=await projects.load('test-project');
  const av=structuredClone(a.values),bv=structuredClone(b.values);av[key].fields.vision='Participant A';bv[key].fields.objective='Participant B';
  await projects.save(a.id,a.values,av);await projects.save(b.id,b.values,bv);
  assert.deepEqual((await projects.load(a.id)).values[key].fields,{vision:'Participant A',objective:'Participant B'});
});
test('same-field and array edits conflict instead of overwriting saved work',async () => {
  const {projects}=await setup();await projects.create(details('test-project'));const initial=await projects.load('test-project');
  const first=structuredClone(initial.values);first[key]={fields:{vision:'Original'},rows:[{id:1,text:'Original'}]};await projects.save(initial.id,initial.values,first);
  const baseline=(await projects.load(initial.id)).values;const a=structuredClone(baseline),b=structuredClone(baseline);
  a[key].fields.vision='A';a[key].rows.push({id:2,text:'A'});b[key].fields.vision='B';b[key].rows.push({id:2,text:'B'});
  await projects.save(initial.id,baseline,a);
  await assert.rejects(projects.save(initial.id,baseline,b),error=>error instanceof Conflict && error.paths.length===2);
  assert.equal((await projects.load(initial.id)).values[key].fields.vision,'A');assert.equal(b[key].fields.vision,'B');
});
test('tool saves and shared header stay isolated across client projects',async () => {
  const {projects}=await setup();await projects.create(details('first-project'));await projects.create({...details('second-project'),client:'Second fixture'});
  const a=await projects.load('first-project');const changed=structuredClone(a.values);changed[key]={fields:{vision:'Only first client'}};changed[ENGAGEMENT_KEY].useCase='First project scope';
  await projects.save(a.id,a.values,changed);const b=await projects.load('second-project');
  assert.equal(b.values[key],null);assert.equal(b.values[ENGAGEMENT_KEY].client,'Second fixture');assert.equal(b.values[ENGAGEMENT_KEY].useCase,'Fixture engagement');
});
test('join missing project never creates a project and members preserve each other',async () => {
  const {projects,api,repo}=await setup();await assert.rejects(projects.join('missing-project','Test person'),/does not exist/);
  await projects.create(details('test-project'));api.external(files=>files['projects/test-project/project.json'].members.other={name:'Other fixture',joinedAt:'test'});
  await projects.join('test-project','Renamed fixture');const loaded=await projects.load('test-project');
  assert.equal(loaded.manifest.members.other.name,'Other fixture');assert.equal(loaded.manifest.members[repo.login].name,'Renamed fixture');
});
test('invalid connection discards its credential and cannot write',async () => {
  const {repo}=await setup();await assert.rejects(repo.connect('invalid-test'),/rejected this token/);assert.equal(repo.connected,false);
  await assert.rejects(repo.commit('test',async()=>[]),/Connect your GitHub/);
});
test('JSON imports cannot poison object prototypes while independent deletions merge',() => {
  const conflicts=[];const merged=merge({a:1,b:1},{b:1},{a:1,b:2},'',conflicts);assert.deepEqual(merged,{b:2});assert.deepEqual(conflicts,[]);
  const evil=JSON.parse('{"__proto__":{"polluted":true}}');const safe=merge({},evil,{other:true});assert.equal({}.polluted,undefined);assert.equal(Object.getPrototypeOf(safe),Object.prototype);
});
test('independent edits to existing table rows and board blocks merge by record ID',() => {
  const base=[{id:1,title:'First',detail:'Original'},{id:2,title:'Second',detail:'Original'}];
  const local=structuredClone(base),remote=structuredClone(base);local[0].title='Local title';remote[1].detail='Remote detail';
  const conflicts=[];const result=merge(base,local,remote,'nodes',conflicts);
  assert.deepEqual(conflicts,[]);assert.equal(result[0].title,'Local title');assert.equal(result[1].detail,'Remote detail');
  const collision=[];merge([], [{id:1,title:'Local new'}], [{id:1,title:'Remote new'}],'nodes',collision);assert.deepEqual(collision,['nodes[id=1]']);
});
test('materializing an omitted blank form field cannot clear a teammate’s new value',() => {
  const conflicts=[];const data=merge({fields:{vision:'Imported'}},{fields:{vision:'Local vision',metrics:''}},{fields:{vision:'Imported',metrics:'Teammate metric'}},'tool',conflicts);
  assert.deepEqual(conflicts,[]);assert.deepEqual(data.fields,{vision:'Local vision',metrics:'Teammate metric'});
  const clearing=[];merge('Known value','','Changed by teammate','field',clearing);assert.deepEqual(clearing,['field']);
});

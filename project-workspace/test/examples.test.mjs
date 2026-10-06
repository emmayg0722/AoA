import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {loadExample,coverage} from '../examples.js';
import {ENGAGEMENT_KEY} from '../projects.js';

const registry=JSON.parse(await readFile(new URL('../registry.json',import.meta.url)));
const catalog=JSON.parse(await readFile(new URL('../examples/catalog.json',import.meta.url)));
const root=new URL('../../',import.meta.url);
const request=async url => ({ok:true,json:async()=>JSON.parse(await readFile(url,'utf8'))});

test('Nordkap project reuses every existing engagement sample across all ten phases',async () => {
  assert.equal(catalog.schemaVersion,1);assert.equal(new Set(catalog.projects.map(p=>p.id)).size,catalog.projects.length);
  const nordkap=catalog.projects.find(p=>p.id==='nordkap');
  const existing=await readdir(new URL('Phase 1 - Discovery & Assessment/sample-data/engagement-nordkap/',root));
  assert.deepEqual(Object.values(nordkap.sources).map(path=>path.split('/').at(-1)).sort(),existing.filter(name=>name.endsWith('.json')).sort());
  assert.deepEqual(coverage(nordkap,registry),{tools:42,phases:10});
  const loaded=await loadExample(nordkap,registry,root,request);
  assert.equal(Object.keys(loaded.values).length,46);
  assert.equal(loaded.values[ENGAGEMENT_KEY].client,'Nordkap Insurance');
  assert.equal(loaded.values.aoa_usecase_board_v1.nodes[0].title,'Loss reported (FNOL)');
  assert.match(loaded.values.aoa_ai_strategy_v1.fields.vision,/Nordkap/);
  assert.ok(loaded.values.aoa_roi_analysis_v1);
  assert.equal(loaded.values.aoa_ai_maturity_v1,null);
  assert.equal(loaded.values.dra5c_engagement_v1,null);
  assert.equal(loaded.values.dra_arch_builder_v1,null);
  for (const state of Object.values(loaded.values)) if (state?.fields?.client) assert.equal(state.fields.client,nordkap.client);
});
test('discovery examples disclose their limited coverage and remain isolated on reload',async () => {
  const furniture=catalog.projects.find(p=>p.id==='nordvik');
  const a=await loadExample(furniture,registry,root,request);
  assert.deepEqual(a.coverage,{tools:1,phases:1});assert.equal(a.values.aoa_ai_strategy_v1,null);
  a.values.aoa_usecase_board_v1.nodes[0].title='Temporary edit';
  a.values[ENGAGEMENT_KEY].client='Temporary header';
  const reset=await loadExample(furniture,registry,root,request);
  assert.equal(reset.values.aoa_usecase_board_v1.nodes[0].title,'Range and demand plan');
  assert.equal(reset.values[ENGAGEMENT_KEY].client,'Nordvik Furniture');
  const food=await loadExample(catalog.projects.find(p=>p.id==='gronhoj'),registry,root,request);
  assert.equal(food.values[ENGAGEMENT_KEY].client,'Grønhøj Foods');
  assert.equal(food.values.aoa_usecase_board_v1.nodes[0].title,'Grower contracts and crop plan');
});
test('failed example source rejects the entire load without mutating the catalog',async () => {
  const source=catalog.projects[0],before=JSON.stringify(source);
  await assert.rejects(loadExample(source,registry,root,async url=>url.pathname.endsWith('roi-analysis.json') ? {ok:false} : request(url)),/could not load/);
  assert.equal(JSON.stringify(source),before);
});
test('example sources cannot load credentials, arbitrary pages or unknown tool states',async () => {
  for (const path of ['https://other.example/secret.json','../config.json','Phase 1 - Discovery & Assessment/sample-data/../outside.json','Phase 1 - Discovery & Assessment/sample-data/x.json?token=secret']) {
    await assert.rejects(loadExample({...catalog.projects[0],sources:{aoa_usecase_board_v1:path}},registry,new URL('https://example.test/AoA/'),()=>{throw new Error('Unexpected fetch');}),/unsupported source/);
  }
  await assert.rejects(loadExample({...catalog.projects[0],sources:{unknown:'x'}},registry,root,request),/unsupported source/);
});

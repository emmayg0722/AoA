import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {runInNewContext} from 'node:vm';
import {merge} from '../projects.js';
const source=await readFile(new URL('../tool-storage.js',import.meta.url),'utf8');
test('a SOP double-save after merging remote fields cannot erase unseen teammate edits',() => {
  let shared={fields:{vision:'Original',alignment:''},sopDone:[]};const native=new Map([['legacy','old draft']]);
  const window={localStorage:{getItem:key=>native.get(key) ?? null,setItem:(key,value)=>native.set(key,value),removeItem:key=>native.delete(key)},addEventListener(){}};
  const parent={ToolkitWorkspace:{bridge:{active:true,keys:['tool'],get:()=>JSON.stringify(shared),set:(key,raw,base)=>{shared=merge(JSON.parse(base),JSON.parse(raw),shared);}}}};
  runInNewContext(source,{window,parent,document:{addEventListener(){}},JSON,Object,MutationObserver:class{}});
  const storage=window.localStorage;
  let form={fields:{vision:'Local first',alignment:''},sopDone:[]};storage.setItem('tool',JSON.stringify(form));
  shared.fields.alignment='Remote merged field';
  let wrapper=JSON.parse(storage.getItem('tool'));wrapper.sopDone=[true];storage.setItem('tool',JSON.stringify(wrapper));
  form.fields.vision='Local second';storage.setItem('tool',JSON.stringify(form));
  wrapper=JSON.parse(storage.getItem('tool'));wrapper.sopDone=[true];storage.setItem('tool',JSON.stringify(wrapper));
  assert.equal(shared.fields.alignment,'Remote merged field');assert.equal(shared.fields.vision,'Local second');
  assert.equal(native.get('legacy'),'old draft');assert.equal(native.has('tool'),false);
});
test('standalone browsing uses its original browser storage without a project',() => {
  const original={getItem(){}};const window={localStorage:original};
  runInNewContext(source,{window,parent:window});assert.equal(window.localStorage,original);
});
test('view-only tool storage rejects writes, deletes and clears without changing saved state or browser drafts',() => {
  const native=new Map([['legacy','original draft']]);let writes=0;
  const window={localStorage:{getItem:key=>native.get(key)??null,setItem:(key,value)=>native.set(key,value),removeItem:key=>native.delete(key)},addEventListener(){}};
  const parent={ToolkitWorkspace:{bridge:{active:true,viewOnly:true,keys:['tool'],get:()=>'{"saved":"Original"}',set:()=>writes++}}};
  runInNewContext(source,{window,parent,document:{addEventListener(){}},JSON,Object,MutationObserver:class{}});
  const storage=window.localStorage;storage.setItem('tool','{"saved":"Changed"}');storage.removeItem('tool');storage.clear();
  assert.equal(storage.getItem('tool'),'{"saved":"Original"}');assert.equal(writes,0);
  assert.equal(native.get('legacy'),'original draft');assert.equal(native.has('tool'),false);
});

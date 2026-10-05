import {Repository} from './repository.js';
import {Projects, ENGAGEMENT_KEY, Conflict, merge} from './projects.js';

const $ = id => document.getElementById(id);
const clone = value => structuredClone(value);
const equal = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const root = new URL('../',location.href);
const [config, registry] = await Promise.all(['config.json','registry.json'].map(async path => {
  const response = await fetch(path,{cache:'no-store'}); if (!response.ok) throw new Error('Workspace configuration could not load.'); return response.json();
}));
const repo = new Repository(config), projects = new Projects(repo,registry);
const tools = registry.flatMap(phase => phase.tools.map(tool => ({...tool,phase})));
const keys = [ENGAGEMENT_KEY,...tools.map(tool => tool.key)];
let active = null, baseline = {}, values = {}, currentPhase = registry[0], currentTool = null;
let saveTimer, saving = null, busy = false, remoteHead = null, conflictsPending = false;
let connectedName = '', createId = null;
let recoveryAvailable = true;
let tabId;
try { tabId = sessionStorage.getItem('aoa_workspace_tab'); if (!tabId) {tabId=crypto.randomUUID();sessionStorage.setItem('aoa_workspace_tab',tabId);} }
catch (_) {tabId=crypto.randomUUID();}
const journalKey = id => `aoa_workspace_pending:${config.repository}:${id}:${tabId}`;
function message(id,text,error=false) { $(id).textContent=text; $(id).classList.toggle('error',error); }
function dirty() { return active && keys.some(key => !equal(baseline[key],values[key])); }
function journal() {
  if (!active) return;
  try {
    if (dirty()) localStorage.setItem(journalKey(active.id),JSON.stringify({schemaVersion:1,id:active.id,baseline,values}));
    else localStorage.removeItem(journalKey(active.id));
    recoveryAvailable=true;
  } catch (_) { recoveryAvailable=false;message('saveStatus','Browser recovery storage is full. Keep this tab open and save to GitHub.',true); }
}
function queue() {
  journal(); clearTimeout(saveTimer);
  if (conflictsPending) return;
  message('saveStatus','Pending changes · saving to GitHub in 8 seconds'+(recoveryAvailable ? '' : ' · browser recovery storage is full'),!recoveryAvailable);
  saveTimer=setTimeout(() => save().catch(showSaveError),8000);
}
function showSaveError(error) {
  message('saveStatus',error.message + (recoveryAvailable ? ' Your pending work is retained in this browser.' : ' Keep this tab open or download pending work; browser recovery storage is full.'),true);
  if (error instanceof Conflict) showConflicts(error.paths);
}
function showConflicts(paths) {
  conflictsPending=true;clearTimeout(saveTimer);$('conflicts').hidden=false;
  $('conflictText').textContent='Your changes and GitHub both changed: ' + paths.join(', ') + '. Review or download your pending work, then choose which version to keep.';
}
function commitStatus(sha) {
  $('commitLink').href=`https://github.com/${config.repository}/commit/${sha}`;
  $('commitLink').hidden=false;
}
function showUpdates(text) { $('updates').hidden=false; $('updatesText').textContent=text; }
async function save() {
  clearTimeout(saveTimer);
  if (saving) {await saving; if (dirty()) return save(); return;}
  if (!active || !dirty()) return;
  if (conflictsPending) throw new Error('Resolve the conflicting edits before saving.');
  const id=active.id, sent=clone(values), old=clone(baseline);
  message('saveStatus','Saving project changes to GitHub…');
  saving=(async () => {
    const result=await projects.save(id,old,sent);
    for (const [key,accepted] of Object.entries(result.accepted)) {
      const conflicts=[];
      const newer=merge(sent[key],values[key],accepted,key,conflicts);
      if (!equal(sent[key],accepted)) showUpdates('Other saved edits were merged. Reload the tool to display them.');
      baseline[key]=clone(accepted); values[key]=newer;
      if (conflicts.length) showConflicts(conflicts);
    }
    active.head=result.sha;remoteHead=null;commitStatus(result.sha);journal();
    message('saveStatus',dirty() ? 'Newer changes are pending.' : 'Saved to GitHub · '+new Date().toLocaleTimeString());
    renderToolList();
  })();
  try { await saving; } finally {saving=null;}
  if (dirty() && !conflictsPending) queue();
}

window.ToolkitWorkspace={bridge:{
  get active() {return !!active;},keys,
  get(key) {return values[key] == null ? null : JSON.stringify(values[key]);},
  set(key, raw, frameBase) {
    if (!active || !keys.includes(key)) return;
    const value=raw===null ? null : JSON.parse(raw);
    const base=frameBase===null ? null : JSON.parse(frameBase);
    const conflicts=[];values[key]=merge(base,value,values[key],key,conflicts);
    if (conflicts.length) showConflicts(conflicts);
    queue();
  },
  navigate(href) {
    const url=new URL(href);const tool=tools.find(tool => new URL(tool.href,root).pathname===url.pathname);
    if (tool) {openTool(tool).catch(showSaveError);return true;}
    if (url.pathname===new URL('engagement-report.html',root).pathname) {openReport().catch(showSaveError);return true;}
    if (url.pathname===root.pathname || url.pathname===new URL('index.html',root).pathname) {showPhase(currentPhase).catch(showSaveError);return true;}
    return false;
  }
}};

function phaseNavigation() {
  $('phaseNav').replaceChildren();
  for (const phase of registry) {
    const button=document.createElement('button');button.type='button';
    button.textContent=phase.title;button.setAttribute('aria-current',currentPhase.number===phase.number ? 'step' : 'false');
    const count=document.createElement('span');count.textContent=phase.tools.length+' tools';button.append(count);
    button.addEventListener('click',() => showPhase(phase).catch(showSaveError));$('phaseNav').append(button);
  }
}
function renderToolList() {
  $('toolList').replaceChildren();
  for (const tool of currentPhase.tools) {
    const button=document.createElement('button');button.type='button';button.className='tool-card';button.textContent=tool.title;
    const status=document.createElement('small');status.textContent=values[tool.key] == null ? 'Open tool →' : 'Project work available →';button.append(status);
    button.addEventListener('click',() => openTool({...tool,phase:currentPhase}).catch(showSaveError));$('toolList').append(button);
  }
}
async function showPhase(phase) {
  if (busy) return;await save();currentPhase=phase;currentTool=null;
  $('toolFrame').removeAttribute('src');$('toolView').hidden=true;$('overview').hidden=false;
  $('phaseTitle').textContent=phase.title;phaseNavigation();renderToolList();
}
async function openTool(tool) {
  if (busy) return;await save();currentPhase=tool.phase;currentTool=tool;
  phaseNavigation();$('overview').hidden=true;$('toolView').hidden=false;$('toolTitle').textContent=tool.title;
  $('toolFrame').title=tool.title+' · '+active.manifest.title;$('toolFrame').src=new URL(tool.href,root).href;
}
async function openReport() {
  await save();currentTool={title:'Master project report',href:'engagement-report.html',phase:currentPhase};
  $('overview').hidden=true;$('toolView').hidden=false;$('toolTitle').textContent=currentTool.title;
  $('toolFrame').title=currentTool.title;$('toolFrame').src=new URL(currentTool.href,root).href;
}
async function listProjects() {
  const list=await projects.list();const selected=$('projectList').value;$('projectList').replaceChildren(new Option('Choose a project',''));
  for (const project of list) $('projectList').append(new Option(`${project.client} · ${project.title}`,project.id));
  $('projectList').value=selected;
  return list;
}
function mode() {
  const join=new FormData($('projectForm')).get('mode')==='join';
  $('createFields').hidden=join;$('joinFields').hidden=!join;$('enterProject').textContent=join ? 'Join project' : 'Create project';
  $('client').required=!join;$('projectTitle').required=!join;
}
function drawManifest() {
  $('activeClient').textContent=active.manifest.client;$('activeTitle').textContent=active.manifest.title;
  $('members').textContent='Project members: '+Object.values(active.manifest.members || {}).map(member => member.name).join(', ');
  $('folderLink').href=`https://github.com/${config.repository}/tree/${config.branch}/projects/${active.id}`;
}
async function enter(id) {
  message('entryStatus','Loading project folders and tool state…');
  const loaded=await projects.load(id);active=loaded;baseline=clone(loaded.values);values=clone(loaded.values);
  conflictsPending=false;remoteHead=null;$('conflicts').hidden=true;$('updates').hidden=true;
  try {
    const draft=JSON.parse(localStorage.getItem(journalKey(id)) || 'null');
    if (draft?.schemaVersion===1 && draft.id===id) {
      const conflicts=[];values=merge(draft.baseline,draft.values,values,'',conflicts);
      if (conflicts.length) showConflicts(conflicts);
      showUpdates('Recovered pending work from this browser. Review it and save when ready.');
    }
  } catch (_) {showUpdates('A browser recovery copy could not be read. Original browser drafts are available under Project options.');}
  drawManifest();$('entry').hidden=true;$('workspace').hidden=false;
  history.replaceState(null,'','?project='+encodeURIComponent(id));
  commitStatus(active.head);message('saveStatus',dirty() ? 'Recovered changes are pending. Save when ready.' : 'Loaded saved project from GitHub');
  currentPhase=registry[0];await showPhaseWithoutSave(currentPhase);journal();
}
async function showPhaseWithoutSave(phase) {
  currentPhase=phase;currentTool=null;$('toolFrame').removeAttribute('src');$('toolView').hidden=true;$('overview').hidden=false;
  $('phaseTitle').textContent=phase.title;phaseNavigation();renderToolList();
}
function download(name,value) {
  const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(() => URL.revokeObjectURL(url),1000);
}

$('connectionForm').addEventListener('submit',async event => {
  event.preventDefault();const token=$('token').value;$('token').value='';$('connect').disabled=true;
  message('connectionStatus','Connecting to GitHub…');
  try {
    connectedName=await repo.connect(token);await listProjects();
    $('storageNotice').textContent=`Projects are stored in ${config.repository}, a ${repo.visibility} GitHub repository. `+(repo.visibility==='public' ? 'Anyone can read saved client names and tool contents. Use only information you can publish.' : 'Repository collaborators can read the saved project contents.');
    message('connectionStatus','Connected as '+connectedName+'.');$('enterProject').disabled=false;
    if (active) {$('entry').hidden=true;$('workspace').hidden=false;$('projectForm').inert=false;message('saveStatus','GitHub reconnected. Pending work is retained.');}
  } catch (error) {message('connectionStatus',error.message,true);$('enterProject').disabled=true;}
  finally {$('connect').disabled=false;}
});
$('projectForm').addEventListener('change',mode);
$('projectList').addEventListener('change',() => {$('projectId').value=$('projectList').value;});
$('projectForm').addEventListener('submit',async event => {
  event.preventDefault();if (!repo.connected || busy) return;busy=true;$('enterProject').disabled=true;
  try {
    const joining=new FormData($('projectForm')).get('mode')==='join';const name=$('participant').value.trim();let id;
    message('entryStatus',joining ? 'Joining project…' : 'Creating the client project and all phase/tool folders…');
    if (joining) {id=$('projectId').value.trim() || $('projectList').value;await projects.join(id,name);}
    else {
      // Retain the request ID across ambiguous network failures; retries cannot create duplicates.
      const request={client:$('client').value.trim(),title:$('projectTitle').value.trim(),name};
      let pending;try {pending=JSON.parse(sessionStorage.getItem('aoa_workspace_create') || 'null');} catch (_) {}
      if (!pending || !equal(pending.request,request)) {pending={id:crypto.randomUUID(),request};try {sessionStorage.setItem('aoa_workspace_create',JSON.stringify(pending));} catch (_) {}}
      createId=pending.id;id=createId;await projects.create({id,...request});
    }
    await enter(id);try {sessionStorage.removeItem('aoa_workspace_create');} catch (_) {}createId=null;message('entryStatus','');
  } catch (error) {message('entryStatus',error.message,true);}
  finally {busy=false;$('enterProject').disabled=!repo.connected;}
});
$('save').addEventListener('click',() => save().catch(showSaveError));
$('backToPhase').addEventListener('click',() => showPhase(currentPhase).catch(showSaveError));
$('report').addEventListener('click',() => openReport().catch(showSaveError));
$('invite').addEventListener('click',async () => {
  try {await navigator.clipboard.writeText(new URL('?project='+active.id,location.href).href);message('saveStatus','Invitation copied. Teammates need their own GitHub write access.');}
  catch (_) {message('saveStatus','Invitation: '+new URL('?project='+active.id,location.href).href);}
});
$('switchProject').addEventListener('click',async () => {
  try {await save();active=null;baseline={};values={};$('toolFrame').removeAttribute('src');$('workspace').hidden=true;$('entry').hidden=false;history.replaceState(null,'',location.pathname);await listProjects();}
  catch (error) {showSaveError(error);}
});
$('reconnect').addEventListener('click',() => {$('workspace').hidden=true;$('entry').hidden=false;$('projectForm').inert=true;$('token').focus();message('entryStatus','Reconnect to resume your current project. Pending edits remain available.');});
$('forget').addEventListener('click',async () => {
  journal();repo.disconnect();$('enterProject').disabled=true;
  if (dirty() && !recoveryAvailable) {message('saveStatus','Token forgotten. Browser recovery storage is full; download your pending work before leaving.',true);return;}
  clearTimeout(saveTimer);active=null;baseline={};values={};$('toolFrame').removeAttribute('src');$('workspace').hidden=true;$('entry').hidden=false;$('projectForm').inert=false;
  message('connectionStatus','Token forgotten. Connect again to join a project. Pending work has a browser recovery copy.');
});
$('refresh').addEventListener('click',async () => {
  try {
    await save();const tool=currentTool,phase=currentPhase;
    const loaded=await projects.load(active.id);active=loaded;baseline=clone(loaded.values);values=clone(loaded.values);remoteHead=null;drawManifest();journal();
    $('updates').hidden=true;commitStatus(active.head);message('saveStatus','Loaded latest saved project from GitHub');
    if (tool) {if (tool.href==='engagement-report.html') await openReport();else await openTool(tool);} else await showPhase(phase);
  } catch (error) {showSaveError(error);}
});
$('downloadPending').addEventListener('click',() => download(active.id+'-pending.json',{schemaVersion:1,project:active.manifest,baseline,values}));
$('exportProject').addEventListener('click',() => download(active.id+'.json',{schemaVersion:1,project:active.manifest,values}));
$('keepMine').addEventListener('click',async () => {
  try {
    const latest=await projects.load(active.id);const unresolved=[];
    values=merge(baseline,values,latest.values,'',unresolved);baseline=clone(latest.values);active.head=latest.head;
    conflictsPending=false;$('conflicts').hidden=true;journal();await save();
    showUpdates('Conflict choice saved. Reload the tool to display the combined project state.');
  } catch (error) {showSaveError(error);}
});
$('useRemote').addEventListener('click',async () => {
  try {
    const latest=await projects.load(active.id);active=latest;baseline=clone(latest.values);values=clone(latest.values);conflictsPending=false;
    $('conflicts').hidden=true;$('updates').hidden=true;journal();drawManifest();message('saveStatus','Using the latest saved GitHub version');
    if (currentTool) {if (currentTool.href==='engagement-report.html') await openReport();else await openTool(currentTool);} else await showPhase(currentPhase);
  } catch (error) {showSaveError(error);}
});
let drafts=[];
$('importDrafts').addEventListener('click',() => {
  drafts=[];$('draftList').replaceChildren();
  for (const tool of [{key:ENGAGEMENT_KEY,title:'Shared client header'},...tools]) {
    try {
      const raw=localStorage.getItem(tool.key);if (!raw) continue;const data=JSON.parse(raw);if (data===null) continue;
      drafts.push({key:tool.key,data});const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=tool.key;
      label.append(input,document.createTextNode(' '+tool.title));$('draftList').append(label);
    } catch (_) {}
  }
  if (!drafts.length) $('draftList').textContent='No existing saved drafts were found in this browser.';
  $('confirmImport').disabled=!drafts.length;$('importDialog').showModal();
});
$('importDialog').addEventListener('close',() => {
  if ($('importDialog').returnValue!=='import') return;
  const selected=[...$('draftList').querySelectorAll('input:checked')].map(input => input.value);
  for (const draft of drafts) if (selected.includes(draft.key)) values[draft.key]=clone(draft.data);
  if (selected.length) {queue();showUpdates('Selected browser drafts imported. Reload the tool to display them.');renderToolList();}
});
window.addEventListener('beforeunload',event => {if (dirty()) {event.preventDefault();event.returnValue='';}});
setInterval(async () => {
  if (!active || saving || busy) return;
  try {const head=await repo.head();if (head!==active.head && head!==remoteHead) {remoteHead=head;showUpdates('Newer project work is saved on GitHub. Your open tool has not been reloaded.');}}
  catch (error) {message('saveStatus','GitHub refresh failed. '+error.message+' Pending edits remain in this browser.',true);}
},15000);
mode();
const invited=new URLSearchParams(location.search).get('project');
if (invited) {document.querySelector('input[name=mode][value=join]').checked=true;$('projectId').value=invited;mode();}
try {await repo.inspect();const list=await listProjects();message('connectionStatus',`${list.length} project${list.length===1?'':'s'} available. Connect to create or join.`);}
catch (error) {message('connectionStatus',error.message,true);}

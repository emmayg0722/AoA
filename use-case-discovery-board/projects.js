// Project entry wraps the original workshop; names are display names, not accounts.
const PROJECT = { mode: 'create', storage: null, ready: false, busy: false };
const byId = id => document.getElementById(id);
let journalId;
try {
  journalId = sessionStorage.getItem('aoa_project_journal') || crypto.randomUUID();
  sessionStorage.setItem('aoa_project_journal', journalId);
} catch (_) { journalId = crypto.randomUUID(); }
const pendingKey = () => KEY + '_' + journalId + '_pending';

function persistProjectPending() {
  if (!SY.project) return;
  try { localStorage.setItem(pendingKey(), JSON.stringify([...(SY.inflight || []), ...SY.queue])); } catch (_) {}
}

function projectMessage(message) { byId('projectMessage').textContent = message; }
function storageDescription(storage) {
  if (storage.mode === 'github') {
    return `Project boards, engagement fields, checklist, project details and participant names are committed to ${storage.repository} on GitHub. ${storage.visibility === 'public' ? 'This repository is public: anyone can read this data and its commit history.' : 'The repository is private: people with repository access can read this data and its commit history.'} Display names do not create private accounts.`;
  }
  return 'This server saves project boards, engagement fields, checklist, project details and participant names to its repository folder. Automatic GitHub saving is not configured on this server. Display names do not create private accounts.';
}

function chooseProjectMode(mode) {
  PROJECT.mode = mode;
  byId('createProjectTab').setAttribute('aria-pressed', String(mode === 'create'));
  byId('joinProjectTab').setAttribute('aria-pressed', String(mode === 'join'));
  byId('createProjectFields').hidden = mode !== 'create';
  byId('joinProjectFields').hidden = mode !== 'join';
  byId('projectName').required = mode === 'create';
  byId('projectName').disabled = mode !== 'create';
  byId('projectSubmit').textContent = mode === 'create' ? 'Create project & open board' : 'Join project & open board';
  projectMessage('');
}

async function projectRequest(path, body) {
  const response = await syncFetch(path, { method: body ? 'POST' : 'GET',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined, signal: AbortSignal.timeout(30000) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Connection failed (HTTP ${response.status})`);
  return data;
}

async function refreshProjects() {
  PROJECT.ready = false;
  byId('projectSubmit').disabled = true;
  byId('projectAcknowledged').checked = false;
  projectMessage('Checking the collaboration service…');
  try {
    byId('syncUrl').value = byId('projectRelayUrl').value;
    byId('syncToken').value = byId('projectAccessCode').value;
    configureSync();
    const response = await syncFetch('/sync/info', { signal: AbortSignal.timeout(6500) });
    if (!response.ok) throw new Error('The collaboration service is unavailable.');
    const info = await response.json();
    PROJECT.storage = info.storage;
    byId('projectStorageNotice').textContent = storageDescription(info.storage);
    const data = await projectRequest('/sync/projects');
    const list = byId('projectList');
    list.replaceChildren(new Option('Choose an existing project', ''));
    data.projects.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).forEach(project => {
      list.add(new Option(`${project.name} · ${project.members.length} participant name${project.members.length === 1 ? '' : 's'}`, project.id));
    });
    const requested = byId('joinProjectId').value.trim();
    if (Array.from(list.options).some(option => option.value === requested)) list.value = requested;
    PROJECT.ready = true;
    byId('projectSubmit').disabled = false;
    projectMessage(data.projects.length ? `${data.projects.length} project${data.projects.length === 1 ? '' : 's'} available.` : 'No projects yet. Create the first project on this service.');
  } catch (error) {
    projectMessage(error.message.includes('access code') ? error.message : 'Online collaboration is not connected. Use Connection settings to connect a running service, or open your browser-only board.');
    byId('projectConnection').open = true;
  }
}

function replaceProjectBoard(doc) {
  // Clear every field and undo history so nothing leaks from a different project.
  fieldEls().forEach(el => { el.value = ''; });
  nodes = []; layout = {}; edges = []; sopDone = []; nextId = 1;
  sel = null; linkFrom = null; undoStack = []; redoStack = [];
  view = Object.assign({ x: 40, y: 40, z: 1 }, doc.view || {});
  restoreFields(doc.fields || {});
  applyRemoteOp({ t: 'doc', doc });
  syncUndoButtons();
}

function showProjectBoard(data, name) {
  KEY = 'aoa_project_' + encodeURIComponent(SY.base || location.origin) + '_' + data.project.id;
  SY.project = data.project; SY.storage = data.storage;
  SY.session = data.session; SY.peerId = data.peerId; SY.seq = data.seq;
  SY.peers = data.peers || []; SY.on = true; SY.generation++; SY.errs = 0;
  replaceProjectBoard(data.doc);
  let pending = [];
  try { pending = JSON.parse(localStorage.getItem(pendingKey()) || '[]'); } catch (_) {}
  SY.queue = Array.isArray(pending) ? pending : [];
  SY.queue.forEach(applyRemoteOp);
  nextId = Math.max(nextId, data.idBase, ...nodes.map(node => node.id + 1), ...edges.map(edge => edge.id + 1));
  byId('syncName').value = name;
  byId('syncSession').value = data.session;
  byId('syncSession').disabled = true;
  byId('activeProjectName').textContent = data.project.name;
  byId('activeProjectStorage').textContent = storageDescription(data.storage);
  byId('projectEntry').hidden = true;
  byId('workshopMain').hidden = false;
  byId('projectBar').hidden = false;
  byId('projectShareControls').hidden = false;
  byId('liveInvite').hidden = true;
  const url = new URL(location.href);
  url.searchParams.delete('session'); url.searchParams.set('project', data.project.id);
  if (SY.base) url.searchParams.set('relay', SY.base); else url.searchParams.delete('relay');
  history.replaceState(null, '', url);
  byId('projectShareLink').value = url.href;
  renderBoard(); renderPreview(); renderPeers(); save(); syncBtnLabel(); updateProjectLabels();
  setSaveStatus(SY.queue.length ? 'syncSaving' : 'syncSaved');
  setSyncStatus(t('syncLive')(SY.peers.length));
  window.scrollTo({ top: 0, behavior: 'smooth' });
  requestAnimationFrame(() => { renderEdges(); if (nodes.length) fitBoard(); });
  pollLoop();
  if (SY.queue.length) flushSync();
}

async function submitProject(event) {
  event.preventDefault();
  if (!PROJECT.ready || PROJECT.busy || !byId('projectAcknowledged').checked) return;
  const name = byId('projectDisplayName').value.trim();
  const projectId = byId('joinProjectId').value.trim() || byId('projectList').value;
  if (!name || (PROJECT.mode === 'join' && !projectId)) return projectMessage('Enter your name and choose a project or paste its project ID.');
  PROJECT.busy = true; byId('projectSubmit').disabled = true;
  projectMessage(PROJECT.mode === 'create' ? 'Creating and saving the project…' : 'Joining the saved project…');
  try {
    const body = { name, acknowledged: true };
    if (PROJECT.mode === 'create') body.projectName = byId('projectName').value.trim();
    else body.projectId = projectId;
    const data = await projectRequest(PROJECT.mode === 'create' ? '/sync/projects' : '/sync/project/join', body);
    showProjectBoard(data, name);
  } catch (error) { projectMessage(error.message); }
  finally { PROJECT.busy = false; byId('projectSubmit').disabled = !PROJECT.ready; }
}

async function reconnectProject() {
  setSyncStatus(t('syncConnecting'));
  try {
    configureSync();
    const data = await projectRequest('/sync/project/join', { projectId: SY.project.id, name: byId('syncName').value.trim(), acknowledged: true });
    showProjectBoard(data, byId('syncName').value.trim());
  } catch (error) { setSyncStatus(error.message); }
}

async function changeProject() {
  if (SY.on && !(await leaveSync())) return;
  save();
  SY.project = null; SY.storage = null; SY.inflight = []; SY.queue = [];
  byId('workshopMain').hidden = true; byId('projectBar').hidden = true;
  byId('projectEntry').hidden = false;
  byId('syncSession').disabled = false;
  byId('projectDisplayName').value = byId('syncName').value;
  byId('joinProjectId').value = '';
  const url = new URL(location.href); url.searchParams.delete('project');
  history.replaceState(null, '', url);
  byId('projectShareControls').hidden = false;
  await refreshProjects();
}

function updateProjectLabels() {
  if (!SY.project) return;
  document.querySelector('[data-i18n="syncHint"]').textContent = 'Collaborators in this project share this board. Accepted changes appear for everyone connected to the same service and project.';
  document.querySelector('[data-i18n="syncPrivacy"]').textContent = storageDescription(SY.storage);
}

function openBrowserBoard() {
  KEY = 'aoa_usecase_board_v1';
  replaceProjectBoard({}); loadSaved(); prefillEngagement();
  byId('projectEntry').hidden = true; byId('workshopMain').hidden = false;
  byId('projectBar').hidden = false; byId('projectShareControls').hidden = true;
  byId('activeProjectName').textContent = 'Browser-only board';
  byId('activeProjectStorage').textContent = 'Changes stay in this browser. They are not shared with a project or saved to GitHub.';
  renderBoard(); renderSop(); renderPreview();
  requestAnimationFrame(() => { renderEdges(); if (nodes.length) fitBoard(); });
}

async function copyProjectLink() {
  try { await navigator.clipboard.writeText(byId('projectShareLink').value); byId('projectCopyStatus').textContent = 'Link copied. Share it with your collaborators.'; }
  catch (_) { byId('projectShareLink').select(); byId('projectCopyStatus').textContent = 'Select and copy this link to invite collaborators.'; }
}

async function initProjects() {
  byId('projectForm').addEventListener('submit', submitProject);
  byId('projectList').addEventListener('change', () => { byId('joinProjectId').value = byId('projectList').value; });
  const query = new URLSearchParams(location.search);
  if (query.has('project')) { chooseProjectMode('join'); byId('joinProjectId').value = query.get('project'); }
  let configured = '';
  try {
    const response = await fetch('./config.json', { cache: 'no-store', signal: AbortSignal.timeout(5000) });
    if (response.ok) configured = (await response.json()).relayUrl || '';
  } catch (_) {}
  byId('projectRelayUrl').value = query.get('relay') || configured || byId('syncUrl').value;
  await refreshProjects();
}
initProjects();

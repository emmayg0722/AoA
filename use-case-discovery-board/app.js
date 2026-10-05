const $ = id => document.getElementById(id);
const assetBase = new URL('./', import.meta.url);
const api = new URL('api/board', assetBase);
let board = null, writable = false, busy = false, selected = null;
let draft = null, draftBase = null, draftRevision = 0, dirty = false, stale = false;
let pan = { x: 40, y: 40, scale: 1 }, gesture = null, stream;
const statuses = { idea: 'Idea', review: 'In review', approved: 'Approved' };
const uid = () => crypto.randomUUID();
const svgNS = 'http://www.w3.org/2000/svg';
for (const name of ['scoreRoi', 'scoreFeasibility', 'scoreImpact']) {
  $(name).append(new Option('—', ''));
  for (let value = 1; value <= 5; value++) $(name).append(new Option(String(value), String(value)));
}
function notice(message, error = false) {
  $('notice').textContent = message; $('notice').hidden = !message; $('notice').classList.toggle('error', error);
}
function syncControls() {
  document.querySelectorAll('[data-write]').forEach(button => button.disabled = !writable || busy);
  $('saveNode').disabled = !writable || busy || stale;
  $('nodeFields').disabled = !writable || busy;
  $('edgeTarget').disabled = !writable || busy;
  $('edgeLabel').disabled = !writable || busy;
  $('titleInput').disabled = !writable || busy;
  $('staleDraft').hidden = !stale;
  $('connection').classList.toggle('live', writable);
}
function average(node) {
  const values = Object.values(node.scores);
  return values.every(value => value !== null) ? (values.reduce((sum, value) => sum + value, 0) / 3).toFixed(1) : null;
}
function confirmation(message, initialValue = null) {
  const dialog = $('confirmation');
  $('confirmationMessage').textContent = message;
  $('confirmationText').hidden = initialValue === null;
  $('confirmationInput').value = initialValue ?? '';
  dialog.returnValue = 'cancel';
  return new Promise(resolve => {
    dialog.addEventListener('close', () => resolve(dialog.returnValue === 'continue' ? (initialValue === null ? true : $('confirmationInput').value) : (initialValue === null ? false : null)), { once: true });
    dialog.showModal();
  });
}
async function canLeave() {
  return !busy && (!dirty || await confirmation('Discard the unsaved card draft?'));
}
async function selectNode(id, focus = false) {
  if (id === selected && draft && dirty) { if (focus) focusNode(board.nodes.find(node => node.id === id)); return; }
  if (id !== selected && !await canLeave()) return;
  selected = id; draft = null; dirty = false; stale = false;
  const node = board?.nodes.find(item => item.id === id);
  if (node) openDraft(node, false);
  render();
  if (focus && node) focusNode(node);
}
function openDraft(node, isNew) {
  draft = { ...structuredClone(node), isNew };
  draftBase = isNew ? null : JSON.stringify(node);
  draftRevision = board.revision; dirty = isNew; stale = false;
  $('nodeForm').hidden = false; $('emptyEditor').hidden = true; $('closeEditor').hidden = false;
  $('editorHeading').textContent = isNew ? 'New card' : 'Card details';
  $('nodeTitle').value = node.title; $('nodeDescription').value = node.description; $('nodeOwner').value = node.owner;
  $('nodeType').value = node.type; $('nodeStatus').value = node.status;
  $('nodeX').value = node.x; $('nodeY').value = node.y;
  $('scoreRoi').value = node.scores.roi ?? ''; $('scoreFeasibility').value = node.scores.feasibility ?? ''; $('scoreImpact').value = node.scores.impact ?? '';
  $('deleteNode').hidden = isNew;
  $('scoreFields').hidden = node.type === 'note';
  renderConnections(); syncControls();
}
async function newCard(type = 'use-case') {
  if (!writable || !await canLeave()) return;
  selected = null;
  const bounds = $('viewport').getBoundingClientRect();
  openDraft({ id: uid(), title: '', description: '', owner: '', type, status: 'idea',
    x: Math.round((bounds.width / 2 - pan.x) / pan.scale - 126), y: Math.round((bounds.height / 2 - pan.y) / pan.scale - 80),
    scores: { roi: null, feasibility: null, impact: null } }, true);
  renderGraph(); renderList();
  $('nodeTitle').focus();
}
function formNode() {
  const score = id => $(id).value === '' ? null : Number($(id).value);
  return { id: draft.id, title: $('nodeTitle').value.trim(), description: $('nodeDescription').value,
    owner: $('nodeOwner').value, type: $('nodeType').value, status: $('nodeStatus').value,
    x: Number($('nodeX').value), y: Number($('nodeY').value),
    scores: { roi: score('scoreRoi'), feasibility: score('scoreFeasibility'), impact: score('scoreImpact') } };
}
function adopt(snapshot) {
  if (board && snapshot.revision < board.revision) return;
  const changed = board && snapshot.revision !== board.revision;
  board = snapshot;
  if (changed && draft) {
    const saved = board.nodes.find(node => node.id === draft.id);
    if (!dirty && !draft.isNew) {
      if (saved) openDraft(saved, false); else { draft = null; selected = null; }
    } else if (draft.isNew || (saved && JSON.stringify(saved) === draftBase)) {
      draftRevision = board.revision;
    } else { stale = true; }
  }
  render();
}
async function mutate(operation, revision = board.revision) {
  if (!writable || busy) return false;
  busy = true; syncControls(); $('saveState').textContent = 'Saving…';
  try {
    const response = await fetch(api, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ revision, operation }) });
    const result = await response.json();
    if (!response.ok) { if (result.board) adopt(result.board); throw new Error(result.error || 'Save failed.'); }
    adopt(result); notice(''); return true;
  } catch (error) {
    notice(error.message || 'The server is unavailable. Your draft has not been saved.', true);
    $('saveState').textContent = 'Not saved · review the message above';
    return false;
  } finally { busy = false; syncControls(); }
}
function render() {
  if (!board) return;
  $('boardTitle').textContent = board.title; document.title = `${board.title} · AoA`;
  if (document.activeElement !== $('titleInput')) $('titleInput').value = board.title;
  $('cardCount').textContent = `${board.nodes.length} ${board.nodes.length === 1 ? 'card' : 'cards'}`;
  $('graphSummary').textContent = `${board.edges.length} ${board.edges.length === 1 ? 'connection' : 'connections'}`;
  $('saveState').textContent = writable ? (board.updatedAt ? `Saved ${new Date(board.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · revision ${board.revision}` : 'Ready · no cards saved yet') : 'Repository snapshot · read-only';
  $('canvasHint').textContent = writable ? 'Drag cards · Connect in the editor' : 'Pan and zoom · Saved snapshot';
  renderList(); if (!gesture) renderGraph(); renderConnections();
  if (!draft) {
    $('nodeForm').hidden = true; $('emptyEditor').hidden = false; $('closeEditor').hidden = true;
    $('connectionsPanel').hidden = true; $('editorHeading').textContent = 'Card details';
  }
  syncControls();
}
function renderList() {
  const query = $('search').value.toLowerCase();
  const nodes = board.nodes.filter(node => `${node.title} ${node.description} ${node.owner}`.toLowerCase().includes(query));
  const activeId = document.activeElement?.dataset.listId;
  $('cardList').replaceChildren();
  if (!nodes.length) {
    const text = document.createElement('p'); text.className = 'list-empty';
    text.textContent = query ? 'No cards match this search.' : 'Your saved cards will appear here.';
    $('cardList').append(text);
  }
  for (const node of nodes) {
    const button = document.createElement('button'); button.dataset.listId = node.id; button.classList.toggle('selected', node.id === selected);
    button.textContent = node.title; button.setAttribute('aria-pressed', String(node.id === selected));
    const meta = document.createElement('small'); meta.textContent = `${node.type === 'note' ? 'Note' : statuses[node.status]}${node.owner ? ` · ${node.owner}` : ''}`;
    button.append(meta); button.addEventListener('click', () => selectNode(node.id, true)); $('cardList').append(button);
    if (activeId === node.id) button.focus({ preventScroll: true });
  }
}
function renderGraph() {
  const activeId = document.activeElement?.dataset.nodeId;
  $('nodes').replaceChildren();
  for (const node of board.nodes) {
    const button = document.createElement('button'); button.className = 'graph-node'; button.dataset.nodeId = node.id;
    button.classList.toggle('selected', node.id === selected); button.classList.toggle('note', node.type === 'note');
    button.style.left = `${node.x}px`; button.style.top = `${node.y}px`;
    button.setAttribute('aria-label', `${node.title}, ${statuses[node.status]}. Select to edit.`); button.setAttribute('aria-pressed', String(node.id === selected));
    const meta = document.createElement('div'); meta.className = 'node-meta';
    const type = document.createElement('span'); type.textContent = node.type === 'note' ? 'Note' : 'Use case';
    const status = document.createElement('span'); status.textContent = statuses[node.status]; meta.append(type, status);
    const title = document.createElement('strong'); title.textContent = node.title;
    const description = document.createElement('p'); description.textContent = node.description || 'Add the problem and context in the editor.';
    const bottom = document.createElement('div'); bottom.className = 'node-bottom';
    const owner = document.createElement('span'); owner.textContent = node.owner || 'No owner assigned';
    const score = document.createElement('span'); score.textContent = node.type === 'note' ? '' : average(node) ? `Score ${average(node)} / 5` : 'Unscored';
    bottom.append(owner, score); button.append(meta, title, description, bottom);
    button.addEventListener('click', event => { if (event.detail === 0) selectNode(node.id); });
    $('nodes').append(button); if (activeId === node.id) button.focus({ preventScroll: true });
  }
  $('emptyCanvas').hidden = board.nodes.length > 0; renderEdges(); applyPan();
}
function renderEdges() {
  $('edgePaths').replaceChildren();
  for (const edge of board.edges) {
    const source = board.nodes.find(node => node.id === edge.source), target = board.nodes.find(node => node.id === edge.target);
    if (!source || !target) continue;
    const sourceElement = Array.from($('nodes').children).find(element => element.dataset.nodeId === source.id);
    const targetElement = Array.from($('nodes').children).find(element => element.dataset.nodeId === target.id);
    const toRight = target.x >= source.x;
    const sx = source.x + (toRight ? 252 : 0), sy = source.y + (sourceElement?.offsetHeight || 145) / 2;
    const tx = target.x + (toRight ? 0 : 252), ty = target.y + (targetElement?.offsetHeight || 145) / 2;
    const bend = Math.max(60, Math.abs(tx - sx) * .45) * (toRight ? 1 : -1);
    const path = document.createElementNS(svgNS, 'path'); path.setAttribute('d', `M ${sx} ${sy} C ${sx + bend} ${sy}, ${tx - bend} ${ty}, ${tx} ${ty}`); path.setAttribute('marker-end', 'url(#arrow)'); $('edgePaths').append(path);
    if (edge.label) { const label = document.createElementNS(svgNS, 'text'); label.setAttribute('x', String((sx + tx) / 2)); label.setAttribute('y', String((sy + ty) / 2 - 10)); label.setAttribute('text-anchor', 'middle'); label.textContent = edge.label; $('edgePaths').append(label); }
  }
}
function renderConnections() {
  const saved = board?.nodes.find(node => node.id === selected);
  $('connectionsPanel').hidden = !saved || !!draft?.isNew;
  if (!saved) return;
  const target = $('edgeTarget').value; $('edgeTarget').replaceChildren(new Option('Choose a card', ''));
  for (const node of board.nodes.filter(node => node.id !== selected)) $('edgeTarget').append(new Option(node.title, node.id));
  $('edgeTarget').value = target;
  $('connectionList').replaceChildren();
  const edges = board.edges.filter(edge => edge.source === selected || edge.target === selected);
  if (!edges.length) { const p = document.createElement('p'); p.textContent = 'No connections yet.'; $('connectionList').append(p); }
  for (const edge of edges) {
    const otherId = edge.source === selected ? edge.target : edge.source;
    const other = board.nodes.find(node => node.id === otherId);
    const row = document.createElement('div'); row.className = 'connection-row';
    const label = document.createElement('p'); label.textContent = `${edge.source === selected ? '→' : '←'} ${other.title}${edge.label ? ` · ${edge.label}` : ''}`;
    const actions = document.createElement('div'); actions.className = 'connection-actions';
    const edit = document.createElement('button'); edit.textContent = 'Edit label'; edit.dataset.write = '';
    edit.addEventListener('click', async () => { const revision = board.revision; const value = await confirmation('Edit connection label', edge.label); if (value !== null) await mutate({ type: 'save-edge', edge: { ...edge, label: value } }, revision); });
    const remove = document.createElement('button'); remove.textContent = 'Remove'; remove.dataset.write = '';
    remove.addEventListener('click', () => mutate({ type: 'delete-edge', id: edge.id }));
    actions.append(edit, remove); row.append(label, actions); $('connectionList').append(row);
  }
}
function applyPan() {
  $('world').style.transform = `translate(${pan.x}px,${pan.y}px) scale(${pan.scale})`;
  $('zoomLevel').value = `${Math.round(pan.scale * 100)}%`;
}
function zoom(factor) {
  const bounds = $('viewport').getBoundingClientRect(), next = Math.min(2, Math.max(.25, pan.scale * factor));
  const ratio = next / pan.scale;
  pan.x = bounds.width / 2 - (bounds.width / 2 - pan.x) * ratio;
  pan.y = bounds.height / 2 - (bounds.height / 2 - pan.y) * ratio;
  pan.scale = next; applyPan();
}
function focusNode(node) {
  const bounds = $('viewport').getBoundingClientRect();
  pan.x = bounds.width / 2 - (node.x + 126) * pan.scale; pan.y = bounds.height / 2 - (node.y + 80) * pan.scale; applyPan();
}
function fitBoard() {
  if (!board?.nodes.length) { pan = { x: 40, y: 40, scale: 1 }; applyPan(); return; }
  const bounds = $('viewport').getBoundingClientRect();
  const minX = Math.min(...board.nodes.map(node => node.x)), minY = Math.min(...board.nodes.map(node => node.y));
  const width = Math.max(...board.nodes.map(node => node.x + 252)) - minX;
  const height = Math.max(...board.nodes.map(node => node.y + 240)) - minY;
  pan.scale = Math.min(1, Math.max(.25, Math.min((bounds.width - 80) / width, (bounds.height - 80) / height)));
  pan.x = (bounds.width - width * pan.scale) / 2 - minX * pan.scale; pan.y = (bounds.height - height * pan.scale) / 2 - minY * pan.scale; applyPan();
}
$('viewport').addEventListener('pointerdown', async event => {
  if (event.button !== 0 || event.target.closest('#emptyCanvas')) return;
  const button = event.target.closest('[data-node-id]');
  if (button) {
    if (busy) return;
    if (dirty) { if (await canLeave()) { dirty = false; await selectNode(button.dataset.nodeId); } return; }
    selected = button.dataset.nodeId; dirty = false; stale = false;
    const node = board.nodes.find(item => item.id === selected); openDraft(node, false); renderList();
    Array.from($('nodes').children).forEach(element => { element.classList.toggle('selected', element.dataset.nodeId === selected); element.setAttribute('aria-pressed', String(element.dataset.nodeId === selected)); });
    if (!writable || busy) return;
    gesture = { type: 'node', id: selected, startX: event.clientX, startY: event.clientY, x: node.x, y: node.y, revision: board.revision, element: button, moved: false };
    button.classList.add('dragging');
  } else {
    gesture = { type: 'pan', startX: event.clientX, startY: event.clientY, x: pan.x, y: pan.y };
    $('viewport').classList.add('panning');
  }
  $('viewport').setPointerCapture(event.pointerId);
});
$('viewport').addEventListener('pointermove', event => {
  if (!gesture) return;
  const dx = event.clientX - gesture.startX, dy = event.clientY - gesture.startY;
  if (gesture.type === 'pan') { pan.x = gesture.x + dx; pan.y = gesture.y + dy; applyPan(); }
  else {
    if (Math.abs(dx) + Math.abs(dy) > 4) gesture.moved = true;
    const x = Math.round(gesture.x + dx / pan.scale), y = Math.round(gesture.y + dy / pan.scale);
    gesture.element.style.left = `${x}px`; gesture.element.style.top = `${y}px`;
    $('nodeX').value = x; $('nodeY').value = y;
    // Only the transient render copy moves; the authoritative board is unchanged until the save succeeds.
    const saved = board.nodes.find(node => node.id === gesture.id);
    if (saved) { const original = { x: saved.x, y: saved.y }; Object.assign(saved, { x, y }); renderEdges(); Object.assign(saved, original); }
  }
});
async function endGesture(cancelled = false) {
  if (!gesture) return;
  const previous = gesture; gesture = null; $('viewport').classList.remove('panning');
  if (previous.type === 'node') {
    previous.element.classList.remove('dragging');
    if (!cancelled && previous.moved) await mutate({ type: 'move-node', id: previous.id, x: Number($('nodeX').value), y: Number($('nodeY').value) }, previous.revision);
    const saved = board.nodes.find(node => node.id === selected);
    if (saved) openDraft(saved, false);
    renderGraph();
  }
}
$('viewport').addEventListener('pointerup', () => endGesture());
$('viewport').addEventListener('pointercancel', () => endGesture(true));
$('viewport').addEventListener('keydown', event => {
  if (event.target !== $('viewport')) return;
  const moves = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] };
  if (moves[event.key]) { event.preventDefault(); pan.x += moves[event.key][0]; pan.y += moves[event.key][1]; applyPan(); }
});
$('addCase').addEventListener('click', () => newCard()); $('firstCase').addEventListener('click', () => newCard());
$('addNote').addEventListener('click', () => newCard('note'));
$('closeEditor').addEventListener('click', async () => { if (await canLeave()) { selected = null; draft = null; dirty = false; stale = false; render(); } });
$('nodeForm').addEventListener('input', () => { dirty = true; $('scoreFields').hidden = $('nodeType').value === 'note'; });
$('nodeForm').addEventListener('submit', async event => {
  event.preventDefault(); if (!draft || stale) return;
  const node = formNode();
  if (await mutate({ type: 'save-node', node, create: draft.isNew }, draftRevision)) {
    selected = node.id; dirty = false; openDraft(board.nodes.find(item => item.id === node.id), false); render();
  }
});
$('deleteNode').addEventListener('click', async () => {
  if (!selected || !await confirmation('Delete this card and its connections?')) return;
  if (await mutate({ type: 'delete-node', id: selected }, draftRevision)) { selected = null; draft = null; dirty = false; stale = false; render(); }
});
$('reloadDraft').addEventListener('click', async () => {
  if (!await canLeave()) return;
  const node = board.nodes.find(item => item.id === draft?.id);
  dirty = false; stale = false;
  if (node) openDraft(node, false); else { draft = null; selected = null; }
  render();
});
$('edgeForm').addEventListener('submit', async event => {
  event.preventDefault(); if (!selected) return;
  if (await mutate({ type: 'save-edge', edge: { id: uid(), source: selected, target: $('edgeTarget').value, label: $('edgeLabel').value } })) $('edgeLabel').value = '';
});
let titleRevision = 0;
$('titleInput').addEventListener('focus', () => { titleRevision = board.revision; });
$('renameForm').addEventListener('submit', async event => { event.preventDefault(); await mutate({ type: 'rename', title: $('titleInput').value.trim() }, titleRevision); titleRevision = board.revision; });
$('search').addEventListener('input', renderList);
$('zoomIn').addEventListener('click', () => zoom(1.2)); $('zoomOut').addEventListener('click', () => zoom(1 / 1.2)); $('fit').addEventListener('click', fitBoard);
$('export').addEventListener('click', () => {
  if (!board) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(board, null, 2) + '\n'], { type: 'application/json' }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'discovery-board.json'; anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$('import').addEventListener('click', async () => { if (await canLeave()) $('importFile').click(); });
$('importFile').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = ''; if (!file) return;
  try {
    if (file.size > 2 * 1024 * 1024) throw new Error('Import must be smaller than 2 MB.');
    const payload = JSON.parse(await file.text());
    const replace = payload.schemaVersion === 1;
    if (!replace && !Array.isArray(payload.rows)) throw new Error('Choose a board JSON or a prioritization JSON export.');
    const revision = board.revision;
    if (!await confirmation(replace ? 'Replace the entire board with this JSON? Export the current board first if you want a backup.' : 'Append the use cases from this prioritization export?')) return;
    const operation = replace ? { type: 'replace', board: payload } : { type: 'import-prioritization', payload };
    if (await mutate(operation, revision)) { selected = null; draft = null; dirty = false; stale = false; render(); fitBoard(); }
  } catch (error) { notice(`Import failed: ${error.message}`, true); }
});
window.addEventListener('beforeunload', event => { if (dirty || busy) { event.preventDefault(); event.returnValue = ''; } });
async function initialize() {
  try {
    const response = await fetch(api); if (!response.ok) throw new Error('No writable server');
    const snapshot = await response.json(); if (snapshot.schemaVersion !== 1) throw new Error('No writable server');
    writable = true; $('connection').textContent = 'Live · repository saves'; adopt(snapshot);
    stream = new EventSource(new URL('api/events', assetBase));
    stream.addEventListener('board', event => { const value = JSON.parse(event.data); writable = true; $('connection').textContent = 'Live · repository saves'; adopt(value); });
    stream.onopen = () => { writable = true; $('connection').textContent = 'Live · repository saves'; syncControls(); };
    stream.onerror = () => { writable = false; $('connection').textContent = 'Reconnecting…'; syncControls(); $('saveState').textContent = 'Connection lost · draft kept'; };
  } catch {
    try {
      const response = await fetch(new URL('data/board.json', assetBase)); if (!response.ok) throw new Error('Board file unavailable');
      board = await response.json(); if (board.schemaVersion !== 1 || !Array.isArray(board.nodes)) throw new Error('Invalid board file');
      writable = false; $('connection').textContent = 'Saved snapshot'; render();
      notice('Read-only snapshot. To edit and save into the repo, run “npm start” in use-case-discovery-board, then open http://127.0.0.1:4317.');
    } catch { $('connection').textContent = 'Unavailable'; $('saveState').textContent = 'Board could not load'; notice('Could not load the board. Start its server with “npm start” and open http://127.0.0.1:4317.', true); }
  }
  if (board) fitBoard();
}
initialize();

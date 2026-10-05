import { randomUUID } from 'node:crypto';

export class BoardError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
const requireValue = (condition, message) => { if (!condition) throw new BoardError(message); };
const text = (value, name, max = 4000, required = false) => {
  requireValue(typeof value === 'string' && value.length <= max, `${name} must be text (maximum ${max} characters).`);
  requireValue(!required || value.trim().length > 0, `${name} is required.`);
  return value;
};
const id = value => {
  requireValue(typeof value === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(value), 'Invalid identifier.');
  return value;
};
const coordinate = value => {
  requireValue(Number.isFinite(value) && Math.abs(value) <= 50000, 'Positions must be numbers between -50000 and 50000.');
  return Math.round(value);
};
const score = value => {
  requireValue(value === null || (Number.isInteger(value) && value >= 1 && value <= 5), 'Scores must be 1–5 or unscored.');
  return value;
};
function validateNode(node) {
  requireValue(node && typeof node === 'object', 'Invalid card.');
  requireValue(['use-case', 'note'].includes(node.type), 'Invalid card type.');
  requireValue(['idea', 'review', 'approved'].includes(node.status), 'Invalid status.');
  return {
    id: id(node.id), type: node.type, title: text(node.title, 'Card title', 160, true),
    description: text(node.description, 'Problem / notes'), owner: text(node.owner, 'Owner', 160),
    status: node.status, x: coordinate(node.x), y: coordinate(node.y),
    scores: { roi: score(node.scores?.roi), feasibility: score(node.scores?.feasibility), impact: score(node.scores?.impact) }
  };
}
export function validateBoard(board) {
  requireValue(board && board.schemaVersion === 1, 'Unsupported board format. Expected schemaVersion 1.');
  requireValue(Number.isSafeInteger(board.revision) && board.revision >= 0, 'Invalid revision.');
  requireValue(board.updatedAt === null || (typeof board.updatedAt === 'string' && Number.isFinite(Date.parse(board.updatedAt))), 'Invalid saved time.');
  requireValue(Array.isArray(board.nodes) && board.nodes.length <= 500, 'A board supports up to 500 cards.');
  requireValue(Array.isArray(board.edges) && board.edges.length <= 2000, 'A board supports up to 2000 connections.');
  requireValue(Array.isArray(board.imports) && board.imports.length <= 50, 'A board supports up to 50 source imports.');
  const nodes = board.nodes.map(validateNode), nodeIds = new Set(nodes.map(node => node.id));
  requireValue(nodeIds.size === nodes.length, 'Duplicate card identifiers.');
  const edgeIds = new Set(), pairs = new Set();
  const edges = board.edges.map(edge => {
    requireValue(edge && typeof edge === 'object', 'Invalid connection.');
    const edgeId = id(edge.id), source = id(edge.source), target = id(edge.target);
    requireValue(nodeIds.has(source) && nodeIds.has(target), 'Connections must reference existing cards.');
    requireValue(source !== target, 'A card cannot connect to itself.');
    requireValue(!edgeIds.has(edgeId) && !pairs.has(`${source}:${target}`), 'Duplicate connection.');
    edgeIds.add(edgeId); pairs.add(`${source}:${target}`);
    return { id: edgeId, source, target, label: text(edge.label, 'Connection label', 160) };
  });
  for (const entry of board.imports) {
    requireValue(entry && entry.format === 'aoa_usecase_priority_v1' && typeof entry.importedAt === 'string' && Number.isFinite(Date.parse(entry.importedAt)), 'Invalid source import.');
    requireValue(entry.payload && typeof entry.payload === 'object' && !Array.isArray(entry.payload), 'Invalid imported payload.');
  }
  return {
    schemaVersion: 1, id: id(board.id), title: text(board.title, 'Board title', 160, true),
    revision: board.revision, updatedAt: board.updatedAt, nodes, edges, imports: structuredClone(board.imports)
  };
}
export function applyOperation(current, request) {
  requireValue(request && Number.isSafeInteger(request.revision), 'A saved revision is required.');
  if (request.revision !== current.revision) throw new BoardError('The board changed. Review the latest version, then save again.', 409);
  const operation = request.operation;
  requireValue(operation && typeof operation === 'object', 'An operation is required.');
  let board = structuredClone(current);
  const findNode = nodeId => {
    const node = board.nodes.find(item => item.id === nodeId);
    if (!node) throw new BoardError('This card no longer exists.', 409);
    return node;
  };
  switch (operation.type) {
    case 'rename': board.title = operation.title; break;
    case 'save-node': {
      const node = validateNode(operation.node);
      const index = board.nodes.findIndex(item => item.id === node.id);
      if (operation.create) {
        requireValue(index === -1, 'This card already exists.'); board.nodes.push(node);
      } else {
        findNode(node.id); board.nodes[index] = node;
      }
      break;
    }
    case 'move-node': Object.assign(findNode(operation.id), { x: coordinate(operation.x), y: coordinate(operation.y) }); break;
    case 'delete-node':
      findNode(operation.id);
      board.nodes = board.nodes.filter(node => node.id !== operation.id);
      board.edges = board.edges.filter(edge => edge.source !== operation.id && edge.target !== operation.id);
      break;
    case 'save-edge': {
      const index = board.edges.findIndex(edge => edge.id === operation.edge?.id);
      if (index === -1) board.edges.push(operation.edge); else board.edges[index] = operation.edge;
      break;
    }
    case 'delete-edge':
      requireValue(board.edges.some(edge => edge.id === operation.id), 'Connection no longer exists.');
      board.edges = board.edges.filter(edge => edge.id !== operation.id); break;
    case 'replace': board = validateBoard(operation.board); board.id = current.id; break;
    case 'import-prioritization': {
      const payload = operation.payload;
      requireValue(payload && Array.isArray(payload.rows) && payload.rows.length <= 500, 'Expected a prioritization JSON export with rows.');
      const candidates = payload.rows.filter(row => row && typeof row.name === 'string' && row.name.trim());
      requireValue(candidates.length > 0, 'The import contains no named use cases.');
      const importedScore = value => value === null || value === undefined || value === '' ? null : score(Number(value));
      const offset = Math.ceil(board.nodes.length / 3) * 200;
      candidates.forEach((row, index) => board.nodes.push({
        id: randomUUID(), type: 'use-case', title: row.name, description: row.pain ?? '', owner: '', status: 'idea',
        x: 80 + (index % 3) * 300, y: 80 + Math.floor(index / 3) * 200 + offset,
        scores: { roi: importedScore(row.roi), feasibility: importedScore(row.feas), impact: importedScore(row.impact) }
      }));
      board.imports.push({ format: 'aoa_usecase_priority_v1', importedAt: new Date().toISOString(), payload: structuredClone(payload) });
      break;
    }
    default: throw new BoardError('Unknown board operation.');
  }
  board.revision = current.revision + 1;
  board.updatedAt = new Date().toISOString();
  return validateBoard(board);
}

(function () {
  'use strict';
  let bridge;
  try { bridge = parent !== window && parent.ToolkitWorkspace?.bridge; } catch (_) { return; }
  if (!bridge?.active) return;
  window.AoaProjectTool = true;
  const native = window.localStorage;
  const keys = bridge.keys;
  const frameValues = Object.fromEntries(keys.map(key => [key, bridge.get(key)]));
  const storage = {
    // Keep a coherent form snapshot. Existing tools often read/write again inside
    // a SOP wrapper; exposing unseen remote values there makes stale form fields
    // look like intentional changes on the next input event.
    getItem(key) { key = String(key); return keys.includes(key) ? frameValues[key] : native.getItem(key); },
    setItem(key, value) {
      key = String(key); value = String(value);
      if (!keys.includes(key)) return native.setItem(key,value);
      bridge.set(key, value, frameValues[key]); frameValues[key] = value;
    },
    removeItem(key) { key = String(key); if (!keys.includes(key)) return native.removeItem(key); bridge.set(key,null,frameValues[key]); frameValues[key] = null; },
    clear() { keys.forEach(key => this.removeItem(key)); },
    key(i) { return [...new Set([...keys, ...Object.keys(native)])][i] ?? null; },
    get length() { return new Set([...keys, ...Object.keys(native)]).size; }
  };
  Object.defineProperty(window, 'localStorage', {value:storage, configurable:true});
  window.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link || link.target === '_blank' || link.hasAttribute('download') || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname === location.pathname) return;
    if (bridge.navigate(url.href)) event.preventDefault();
  });
  // The original tool's local-storage note must not contradict project saving.
  const updateNotices = () => {
    for (const node of document.querySelectorAll('[data-i18n="noteBody"], [data-i18n="savedFlag"], #savedFlag')) {
      const text = node.textContent;
      const replacement = bridge.example ? (node.id === 'savedFlag' || node.dataset.i18n === 'savedFlag' ? 'Temporary example edits · reset in workspace' : 'This is a fictional example project. Edits stay in this tab; reset or reload restores the repository examples. Raw profiler uploads stay in this browser.') : node.id === 'savedFlag' || node.dataset.i18n === 'savedFlag' ? 'Changes captured · see GitHub status above' :
        'This tool is part of your client project. Changes queue for GitHub saving; check the shared status above. Raw profiler uploads stay in this browser.';
      if (/locally|browser|API|lokalt|webbläs|browseren|lokal/i.test(text) && text !== replacement) node.textContent = replacement;
    }
    const reportNotes = bridge.example ? {statPrivacy:'Reads this fictional example project. Edits stay in this tab.',manageHint:'Export this example’s tool state, or import a backup into the temporary example. Reset or reload restores the original examples.',importDone:'Example backup imported into this tab. Changes are temporary.',emptyReport:'No example data for this tool. Open a phase tool to explore.'} : {statPrivacy:'Reads this project’s saved work from GitHub.',manageHint:'Export this project’s tool state as one JSON backup, or import a backup into this project. Imported changes queue for GitHub saving.',importDone:'Project backup imported. Check the GitHub save status above.',emptyReport:'No saved tool work in this project yet. Open a phase tool to start.'};
    for (const [key,text] of Object.entries(reportNotes)) for (const node of document.querySelectorAll(`[data-i18n="${key}"]`)) if (node.textContent!==text) node.textContent=text;
  };
  document.addEventListener('DOMContentLoaded', () => {
    updateNotices(); new MutationObserver(updateNotices).observe(document.body,{subtree:true,childList:true,characterData:true});
  });
})();

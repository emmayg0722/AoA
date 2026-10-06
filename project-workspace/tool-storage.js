(function () {
  'use strict';
  let bridge;
  try { bridge = parent !== window && parent.ToolkitWorkspace?.bridge; } catch (_) { return; }
  if (!bridge?.active) return;
  window.AoaProjectTool = true;
  const native = window.localStorage;
  const viewActions=new Set(['zoomStep(1.2)','zoomStep(1/1.2)','fitBoard()','toggleFocus()',
    'currentDimIdx--;renderDimension();','currentDimIdx++;renderDimension();','showResults();']);
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
      if (bridge.viewOnly) return;
      bridge.set(key, value, frameValues[key]); frameValues[key] = value;
    },
    removeItem(key) { key = String(key); if (!keys.includes(key)) return native.removeItem(key); if (bridge.viewOnly) return; bridge.set(key,null,frameValues[key]); frameValues[key] = null; },
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
    if (bridge.viewOnly) {
      // Preserve selectable text and readable content for assistive technology.
      // The parent also rejects mutations, including initialization autosaves.
      for (const node of document.querySelectorAll('input, textarea, select, button, [contenteditable]')) {
        if (node.tagName==='BUTTON' && viewActions.has(node.getAttribute('onclick'))) continue;
        if (node.matches('textarea, input:not([type="checkbox"]):not([type="radio"]):not([type="file"]):not([type="range"]):not([type="color"]):not([type="button"]):not([type="submit"]):not([type="reset"])')) {
          if (!node.readOnly) node.readOnly=true;
        } else if (node.matches('input, select, button')) {
          if (!node.disabled) node.disabled=true;
        } else if (node.contentEditable!=='false') node.contentEditable='false';
      }
    }
    for (const node of document.querySelectorAll('[data-i18n="noteBody"], [data-i18n="savedFlag"], #savedFlag')) {
      const text = node.textContent;
      const replacement = bridge.viewOnly ? 'Viewing saved project work · editing disabled' : bridge.example ? (node.id === 'savedFlag' || node.dataset.i18n === 'savedFlag' ? 'Temporary example edits · reset in workspace' : 'This is a fictional example project. Edits stay in this tab; reset or reload restores the repository examples. Raw profiler uploads stay in this browser.') : node.id === 'savedFlag' || node.dataset.i18n === 'savedFlag' ? 'Changes captured · see GitHub status above' :
        'This tool is part of your client project. Changes queue for GitHub saving; check the shared status above. Raw profiler uploads stay in this browser.';
      if (/locally|browser|API|lokalt|webbläs|browseren|lokal/i.test(text) && text !== replacement) node.textContent = replacement;
    }
    const reportNotes = bridge.viewOnly ? {statPrivacy:'Reads this project’s saved work from GitHub. View-only access.',manageHint:'Viewing the saved project report. Editing and importing are disabled.',importDone:'Viewing saved work; imports are disabled.',emptyReport:'No saved tool work in this project yet.'} : bridge.example ? {statPrivacy:'Reads this fictional example project. Edits stay in this tab.',manageHint:'Export this example’s tool state, or import a backup into the temporary example. Reset or reload restores the original examples.',importDone:'Example backup imported into this tab. Changes are temporary.',emptyReport:'No example data for this tool. Open a phase tool to explore.'} : {statPrivacy:'Reads this project’s saved work from GitHub.',manageHint:'Export this project’s tool state as one JSON backup, or import a backup into this project. Imported changes queue for GitHub saving.',importDone:'Project backup imported. Check the GitHub save status above.',emptyReport:'No saved tool work in this project yet. Open a phase tool to start.'};
    for (const [key,text] of Object.entries(reportNotes)) for (const node of document.querySelectorAll(`[data-i18n="${key}"]`)) if (node.textContent!==text) node.textContent=text;
  };
  document.addEventListener('DOMContentLoaded', () => {
    updateNotices(); new MutationObserver(updateNotices).observe(document.body,{subtree:true,childList:true,characterData:true,...(bridge.viewOnly ? {attributes:true,attributeFilter:['disabled','readonly','contenteditable']} : {})});
  });
  for (const type of ['pointerdown','mousedown']) document.addEventListener(type,event => {
    if (bridge.viewOnly && event.target.closest?.('svg, canvas, [draggable="true"], #boardView .node')) event.stopImmediatePropagation();
  },true);
  document.addEventListener('click',event => {
    if (bridge.viewOnly && event.target.closest?.('li[onclick^="selectOption"]')) {event.preventDefault();event.stopImmediatePropagation();}
  },true);
  document.addEventListener('keydown',event => {
    if (!bridge.viewOnly) return;
    if (['Delete','Backspace'].includes(event.key) || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase()==='z')) {event.preventDefault();event.stopImmediatePropagation();}
    else if (event.key.startsWith('Arrow') && document.querySelector('#boardView')) event.stopImmediatePropagation();
  },true);
})();

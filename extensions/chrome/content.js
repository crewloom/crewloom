/**
 * Crewloom Computer Use - Content Script
 * Manual Page Visual Grounding, DOM Indexing, Element Labeling, and Action Simulation.
 */

const MAX_INDEXED_ELEMENTS = 400;
const INTERACTIVE_SELECTOR =
  'button, a, input, select, textarea, [role="button"], [role="link"], [role="tab"], [role="checkbox"], [tabindex="0"]';

let isInspectorActive = false;
let inspectorBox = null;
let hudElement = null;
let trackedTags = [];
let repositionFrame = null;
let indexGeneration = 0;

// Ensure HUD banner exists
function showHud(statusText = 'Active') {
  if (hudElement) {
    const statusTextNode = hudElement.querySelector('.crewloom-hud-text');
    if (statusTextNode) statusTextNode.textContent = statusText;
    hudElement.style.display = 'flex';
    return;
  }

  hudElement = document.createElement('div');
  hudElement.className = 'crewloom-agent-hud';
  const logoUrl = chrome.runtime.getURL('icons/icon-32.png');

  hudElement.innerHTML = `
    <img src="${logoUrl}" alt="Logo" class="crewloom-hud-logo">
    <span class="crewloom-hud-title">Crewloom Computer Use</span>
    <div class="crewloom-hud-status">
      <span class="crewloom-hud-dot"></span>
      <span class="crewloom-hud-text"></span>
    </div>
    <button class="crewloom-hud-close" title="Hide Overlay">✕</button>
  `;

  hudElement.querySelector('.crewloom-hud-text').textContent = statusText;

  hudElement.querySelector('.crewloom-hud-close').addEventListener('click', () => {
    clearAllIndexTags();
    hudElement.style.display = 'none';
  });

  document.body.appendChild(hudElement);
}

// Overlay container for index tags
function getGroundingOverlay() {
  let overlay = document.getElementById('crewloom-grounding-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'crewloom-grounding-overlay';
    document.body.appendChild(overlay);
  }
  return overlay;
}

function placeTag(entry) {
  const rect = entry.element.getBoundingClientRect();
  const left = Math.round(rect.left + window.scrollX);
  const top = Math.max(0, Math.round(rect.top + window.scrollY - 16));
  entry.tag.style.left = `${left}px`;
  entry.tag.style.top = `${top}px`;
  entry.tag.style.display = rect.bottom < 0 || rect.top > window.innerHeight ? 'none' : '';
}

function repositionTags() {
  repositionFrame = null;
  const overlay = document.getElementById('crewloom-grounding-overlay');
  if (!overlay || !trackedTags.length) return;
  overlay.style.width = `${Math.max(document.documentElement.scrollWidth, window.innerWidth)}px`;
  overlay.style.height = `${Math.max(document.documentElement.scrollHeight, window.innerHeight)}px`;
  trackedTags.forEach(placeTag);
}

function scheduleReposition() {
  if (repositionFrame !== null) return;
  repositionFrame = window.requestAnimationFrame(repositionTags);
}

// Index all interactive elements with numbered labels [1], [2], [3]
function indexInteractiveElements() {
  clearAllIndexTags();
  const overlay = getGroundingOverlay();
  overlay.style.display = 'block';
  overlay.style.width = `${Math.max(document.documentElement.scrollWidth, window.innerWidth)}px`;
  overlay.style.height = `${Math.max(document.documentElement.scrollHeight, window.innerHeight)}px`;

  const elements = Array.from(document.querySelectorAll(INTERACTIVE_SELECTOR));
  const items = [];
  let total = 0;

  for (const el of elements) {
    // Skip our own overlay chrome
    if (el.closest('.crewloom-agent-hud') || el.closest('#crewloom-grounding-overlay')) continue;

    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    if (
      rect.width <= 8 ||
      rect.height <= 8 ||
      style.visibility === 'hidden' ||
      style.display === 'none' ||
      style.opacity === '0'
    ) {
      continue;
    }

    total += 1;

    // Bound the overlay so dense pages cannot flood the DOM
    if (items.length >= MAX_INDEXED_ELEMENTS) continue;

    const index = items.length + 1;
    el.classList.add('crewloom-indexed-element');
    el.dataset.crewloomIndex = index;

    const tag = document.createElement('div');
    tag.className = 'crewloom-indexed-tag';
    tag.textContent = `[${index}]`;
    tag.dataset.targetIndex = index;
    overlay.appendChild(tag);

    const entry = { element: el, tag };
    trackedTags.push(entry);
    placeTag(entry);

    items.push({
      index,
      tag: el.tagName.toLowerCase(),
      type: el.getAttribute('type') || null,
      id: el.id || null,
      text: (el.textContent || el.value || el.placeholder || el.getAttribute('aria-label') || '')
        .trim()
        .slice(0, 40),
      rect: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height)
      }
    });
  }

  trackedTags.forEach(placeTag);
  window.addEventListener('scroll', scheduleReposition, { passive: true });
  window.addEventListener('resize', scheduleReposition, { passive: true });

  const status =
    items.length < total
      ? `Indexed ${items.length} of ${total} (limit ${MAX_INDEXED_ELEMENTS})`
      : `${total} elements indexed`;
  showHud(status);

  return { generation: indexGeneration, items, total, truncated: items.length < total, limit: MAX_INDEXED_ELEMENTS };
}

// Clear all indexed tags
function clearAllIndexTags() {
  indexGeneration += 1;
  if (repositionFrame !== null) {
    window.cancelAnimationFrame(repositionFrame);
    repositionFrame = null;
  }
  window.removeEventListener('scroll', scheduleReposition);
  window.removeEventListener('resize', scheduleReposition);

  document.querySelectorAll('.crewloom-indexed-element').forEach((el) => {
    el.classList.remove('crewloom-indexed-element');
    delete el.dataset.crewloomIndex;
  });
  const overlay = document.getElementById('crewloom-grounding-overlay');
  if (overlay) {
    overlay.innerHTML = '';
    overlay.style.display = 'none';
  }
  trackedTags = [];
}

// Trigger simulated agent click with visual wave
function clickElementByIndex(index, generation = indexGeneration) {
  if (!Number.isInteger(index) || index < 1 || generation !== indexGeneration) {
    return { ok: false, error: 'Stale or invalid element index; re-index the page' };
  }
  const el = trackedTags[index - 1]?.element;
  if (!el?.isConnected) return { ok: false, error: 'Indexed element was removed; re-index the page' };
  const style = window.getComputedStyle(el);
  const size = el.getBoundingClientRect();
  if (el.disabled || el.getAttribute('aria-disabled') === 'true' || size.width <= 8 || size.height <= 8 ||
      style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
    return { ok: false, error: 'Indexed element is hidden or disabled; re-index the page' };
  }

  const rect = el.getBoundingClientRect();
  const clickX = rect.left + rect.width / 2;
  const clickY = rect.top + rect.height / 2;

  // Render expanding click wave
  const wave = document.createElement('div');
  wave.className = 'crewloom-click-wave';
  wave.style.left = `${clickX}px`;
  wave.style.top = `${clickY}px`;
  document.body.appendChild(wave);
  setTimeout(() => wave.remove(), 500);

  // Trigger real click
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  el.focus();
  el.click();

  showHud(`Clicked [${index}]`);
  return { ok: true, x: clickX, y: clickY, tag: el.tagName.toLowerCase() };
}

// Mouse Inspector functionality
function toggleInspector(forceState) {
  isInspectorActive = forceState !== undefined ? forceState : !isInspectorActive;

  if (isInspectorActive) {
    if (!inspectorBox) {
      inspectorBox = document.createElement('div');
      inspectorBox.className = 'crewloom-inspector-box';
      inspectorBox.innerHTML = '<span class="crewloom-inspector-label"></span>';
      document.body.appendChild(inspectorBox);
    }
    document.addEventListener('mousemove', onInspectorMouseMove, { passive: true });
    showHud('Inspector active');
  } else {
    if (inspectorBox) inspectorBox.remove();
    inspectorBox = null;
    document.removeEventListener('mousemove', onInspectorMouseMove);
  }
}

function onInspectorMouseMove(e) {
  if (!isInspectorActive || !inspectorBox) return;
  const target = document.elementFromPoint(e.clientX, e.clientY);
  if (!target || target.closest('.crewloom-agent-hud') || target === inspectorBox) return;

  const rect = target.getBoundingClientRect();
  inspectorBox.style.left = `${rect.left}px`;
  inspectorBox.style.top = `${rect.top}px`;
  inspectorBox.style.width = `${rect.width}px`;
  inspectorBox.style.height = `${rect.height}px`;

  const label = inspectorBox.querySelector('.crewloom-inspector-label');
  const tagDesc = `${target.tagName.toLowerCase()}${target.id ? '#' + target.id : ''}`;
  label.textContent = `<${tagDesc}> (${Math.round(rect.width)}×${Math.round(rect.height)})`;
}

// Message Listener from Sidepanel & Background
function handleMessage(message, sender, sendResponse) {
  if (message.type === 'INDEX_PAGE') {
    const result = indexInteractiveElements();
    sendResponse({
      ok: true,
      generation: result.generation,
      count: result.items.length,
      total: result.total,
      truncated: result.truncated,
      limit: result.limit,
      items: result.items
    });
    return false;
  }

  if (message.type === 'CLEAR_INDEX') {
    clearAllIndexTags();
    sendResponse({ ok: true });
    return false;
  }

  if (message.type === 'CLICK_INDEX') {
    sendResponse(clickElementByIndex(message.index, message.generation));
    return false;
  }

  if (message.type === 'TOGGLE_INSPECTOR') {
    toggleInspector();
    sendResponse({ ok: true, active: isInspectorActive });
    return false;
  }

  if (message.type === 'GET_PAGE_SUMMARY') {
    sendResponse({
      ok: true,
      title: document.title,
      url: window.location.href,
      elementsCount: document.querySelectorAll('*').length
    });
    return false;
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CLEAR_INDEX') { handleMessage(message, sender, sendResponse); return false; }
  chrome.storage.local.get({ 'crewloom.enabled': false }, (stored) => {
    if (!stored['crewloom.enabled']) return sendResponse({ ok: false, error: 'Browser companion is disabled' });
    handleMessage(message, sender, sendResponse);
  });
  return true;
});
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes['crewloom.enabled']?.newValue === false) {
    clearAllIndexTags();
    isInspectorActive = false;
    document.removeEventListener('mousemove', onInspectorMouseMove);
    inspectorBox?.remove(); inspectorBox = null;
    hudElement?.remove(); hudElement = null;
  }
});

// Only the operator's local dashboard can request a state change. Other pages cannot.
const dashboardPage = location.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) && location.port === '4317';
if (dashboardPage) {
  window.addEventListener('message', (event) => {
    if (event.source !== window || event.origin !== location.origin) return;
    const type = event.data?.type;
    if (!['CREWLOOM_GET_CONTROL', 'CREWLOOM_SET_CONTROL'].includes(type)) return;
    if (type === 'CREWLOOM_SET_CONTROL' && typeof event.data.enabled !== 'boolean') return;
    chrome.runtime.sendMessage({ type: type === 'CREWLOOM_SET_CONTROL' ? 'SET_CONTROL' : 'GET_CONTROL', enabled: event.data.enabled }, (result) => {
      if (chrome.runtime.lastError || !result?.ok) return;
      window.postMessage({ type: 'CREWLOOM_CONTROL_STATE', enabled: result.enabled, version: result.version }, location.origin);
    });
  });
}

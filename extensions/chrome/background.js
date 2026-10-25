/**
 * Crewloom Computer Use - Background Service Worker (Manifest V3)
 * Manual browser companion: persistent activation, visible-tab capture and local dashboard status.
 */

// Open the side panel immediately when the action icon is clicked
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error('Error setting panel behavior:', error));

// Create Context Menus (recreate on install/update so entries never duplicate)
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: 'crewloom-inspect',
      title: 'Inspect with Crewloom Computer Use',
      contexts: ['all']
    });
    chrome.contextMenus.create({
      id: 'crewloom-capture',
      title: 'Capture Visual Frame for Agent',
      contexts: ['all']
    });
  });
});

const captureKey = (windowId) => `crewloom.pendingCapture.${windowId}`;

// Handle Context Menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (!tab?.id || !Number.isInteger(tab.windowId) || tab.windowId < 0) return;
  const windowId = tab.windowId;

  // Open the side panel for this window
  chrome.sidePanel.open({ windowId }).catch((error) => {
    console.error('Error opening side panel:', error);
  });

  if (info.menuItemId === 'crewloom-inspect') {
    chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_INSPECTOR' }, () => {
      void chrome.runtime.lastError;
    });
  } else if (info.menuItemId === 'crewloom-capture') {
    // Persist before notifying: a newly opened panel consumes this on readiness.
    chrome.storage.session.set({ [captureKey(windowId)]: { tabId: tab.id, createdAt: Date.now() } }, () => {
      chrome.runtime.sendMessage({ type: 'CAPTURE_REQUEST', windowId }).catch(() => {});
    });
  }
});

const CHAT_GROUPS_KEY = 'crewloom.chatGroups';

function getChatGroupInfo(chatId, callback) {
  chrome.storage.local.get(CHAT_GROUPS_KEY, (res) => {
    const map = res[CHAT_GROUPS_KEY] || {};
    const entry = map[chatId];
    if (!entry || !entry.groupId) return callback(null);
    if (!chrome.tabGroups?.get) return callback(entry);
    chrome.tabGroups.get(entry.groupId, (group) => {
      if (chrome.runtime.lastError || !group) {
        delete map[chatId];
        chrome.storage.local.set({ [CHAT_GROUPS_KEY]: map }, () => callback(null));
      } else {
        callback(entry);
      }
    });
  });
}

function saveChatGroup(chatId, groupId, title, color, callback) {
  chrome.storage.local.get(CHAT_GROUPS_KEY, (res) => {
    const map = res[CHAT_GROUPS_KEY] || {};
    map[chatId] = { groupId, title, color, updatedAt: Date.now() };
    chrome.storage.local.set({ [CHAT_GROUPS_KEY]: map }, () => {
      callback({ ok: true, groupId, title });
    });
  });
}

function finalizeChatGroup(chatId, chatTitle, groupId, color, callback) {
  const title = `Crewloom: ${chatTitle || chatId || 'Chat'}`;
  if (chrome.tabGroups?.update) {
    chrome.tabGroups.update(groupId, { title, color }, () => {
      void chrome.runtime.lastError;
      saveChatGroup(chatId, groupId, title, color, callback);
    });
  } else {
    saveChatGroup(chatId, groupId, title, color, callback);
  }
}

function getOrCreateChatGroup(chatId, chatTitle, tabId, color, callback) {
  if (typeof color === 'function') {
    callback = color;
    color = 'purple';
  }
  if (!chrome.tabs?.group) {
    return callback({ ok: false, error: 'Tab group operation failed' });
  }
  const groupTitle = `Crewloom: ${chatTitle || chatId || 'Chat'}`;
  getChatGroupInfo(chatId, (entry) => {
    if (entry?.groupId) {
      chrome.tabs.group({ tabIds: [tabId], groupId: entry.groupId }, (groupId) => {
        if (chrome.runtime.lastError) {
          createNewOrFindGroup(chatId, chatTitle, tabId, color, groupTitle, callback);
        } else {
          callback({ ok: true, groupId });
        }
      });
    } else {
      createNewOrFindGroup(chatId, chatTitle, tabId, color, groupTitle, callback);
    }
  });
}

function createNewOrFindGroup(chatId, chatTitle, tabId, color, groupTitle, callback) {
  if (chrome.tabGroups?.query) {
    chrome.tabGroups.query({ title: groupTitle }, (groups) => {
      if (!chrome.runtime.lastError && groups && groups.length > 0) {
        chrome.tabs.group({ tabIds: [tabId], groupId: groups[0].id }, (gid) => {
          if (!chrome.runtime.lastError && gid) {
            saveChatGroup(chatId, gid, groupTitle, color, callback);
            return;
          }
          createBrandNewGroup(chatId, chatTitle, tabId, color, callback);
        });
      } else {
        createBrandNewGroup(chatId, chatTitle, tabId, color, callback);
      }
    });
  } else {
    createBrandNewGroup(chatId, chatTitle, tabId, color, callback);
  }
}

function createBrandNewGroup(chatId, chatTitle, tabId, color, callback) {
  chrome.tabs.group({ tabIds: [tabId] }, (newGroupId) => {
    if (chrome.runtime.lastError || !newGroupId) return callback({ ok: false, error: 'Tab group operation failed' });
    finalizeChatGroup(chatId, chatTitle, newGroupId, color, callback);
  });
}

// Central Message Routing
function handleMessage(message, sender, sendResponse) {
  // Capture the visible tab. windowId comes from the caller so the right window is captured.
  if (message.type === 'CAPTURE_TAB') {
    const windowId = message.windowId;
    if (!Number.isInteger(windowId) || windowId < 0) { sendResponse({ ok: false, error: 'Explicit panel window required' }); return false; }
    chrome.tabs.captureVisibleTab(windowId, { format: 'png' }, (dataUrl) => {
      if (chrome.runtime.lastError) {
        sendResponse({ ok: false, error: chrome.runtime.lastError.message });
      } else {
        chrome.storage.local.get({ 'crewloom.enabled': false }, (value) => sendResponse(value['crewloom.enabled'] ? { ok: true, dataUrl } : { ok: false, error: 'Browser companion was disabled during capture' }));
      }
    });
    return true; // Keep channel open for async response
  }

  if (message.type === 'PANEL_READY') {
    if (!Number.isInteger(message.windowId) || message.windowId < 0) { sendResponse({ ok: false, error: 'Explicit panel window required' }); return false; }
    const key = captureKey(message.windowId);
    chrome.storage.session.get(key, (value) => {
      const pending = value[key];
      chrome.storage.session.remove(key, () => sendResponse({ ok: true, pending: pending && Date.now() - pending.createdAt < 30000 ? pending : null }));
    });
    return true;
  }

  // Get active tab info
  if (message.type === 'GET_ACTIVE_TAB') {
    if (!Number.isInteger(message.windowId) || message.windowId < 0) { sendResponse({ ok: false, error: 'Explicit panel window required' }); return false; }
    chrome.tabs.query({ active: true, windowId: message.windowId }, (tabs) => {
      if (tabs && tabs[0]) {
        sendResponse({ ok: true, tab: tabs[0] });
      } else {
        sendResponse({ ok: false, error: 'No active tab' });
      }
    });
    return true;
  }

  // Get target tab info (active tab or specific tab in group)
  if (message.type === 'GET_TARGET_TAB') {
    if (Number.isInteger(message.tabId) && message.tabId > 0) {
      chrome.tabs.get(message.tabId, (tab) => {
        if (chrome.runtime.lastError || !tab) {
          sendResponse({ ok: false, error: 'Tab not found' });
        } else {
          sendResponse({ ok: true, tab });
        }
      });
      return true;
    }
    if (!Number.isInteger(message.windowId) || message.windowId < 0) { sendResponse({ ok: false, error: 'Explicit panel window required' }); return false; }
    chrome.tabs.query({ active: true, windowId: message.windowId }, (tabs) => {
      if (tabs && tabs[0]) {
        sendResponse({ ok: true, tab: tabs[0] });
      } else {
        sendResponse({ ok: false, error: 'No active tab' });
      }
    });
    return true;
  }

  // Create background tab belonging to a chat's tab group without stealing focus
  if (message.type === 'CREATE_CHAT_TAB') {
    const url = message.url || 'about:blank';
    const active = Boolean(message.active);
    const chatId = String(message.chatId || 'default');
    const chatTitle = String(message.chatTitle || chatId || 'Chat');
    chrome.tabs.create({ url, active }, (tab) => {
      if (chrome.runtime.lastError || !tab?.id) {
        sendResponse({ ok: false, error: 'Tab not found' });
        return;
      }
      getOrCreateChatGroup(chatId, chatTitle, tab.id, 'purple', (groupRes) => {
        sendResponse({ ok: true, tab, groupId: groupRes?.groupId ?? null });
      });
    });
    return true;
  }

  // Group existing tab into a chat's tab group
  if (message.type === 'GROUP_CHAT_TAB') {
    const tabId = message.tabId;
    if (!Number.isInteger(tabId) || tabId <= 0) { sendResponse({ ok: false, error: 'Tab not found' }); return false; }
    const chatId = String(message.chatId || 'default');
    const chatTitle = String(message.chatTitle || chatId || 'Chat');
    const color = message.color || 'purple';
    getOrCreateChatGroup(chatId, chatTitle, tabId, color, (groupRes) => {
      if (!groupRes.ok) { sendResponse({ ok: false, error: 'Tab group operation failed' }); return; }
      sendResponse({ ok: true, groupId: groupRes.groupId, title: groupRes.title });
    });
    return true;
  }

  // List all tabs belonging to a chat's tab group
  if (message.type === 'GET_CHAT_TABS') {
    const chatId = String(message.chatId || 'default');
    getChatGroupInfo(chatId, (info) => {
      if (!info?.groupId) {
        sendResponse({ ok: true, tabs: [], groupId: null });
        return;
      }
      chrome.tabs.query({ groupId: info.groupId }, (tabs) => {
        if (chrome.runtime.lastError) {
          sendResponse({ ok: true, tabs: [], groupId: info.groupId });
        } else {
          sendResponse({ ok: true, tabs: tabs || [], groupId: info.groupId, title: info.title });
        }
      });
    });
    return true;
  }

  // List all open tabs in window
  if (message.type === 'GET_ALL_TABS') {
    const query = Number.isInteger(message.windowId) && message.windowId >= 0
      ? { windowId: message.windowId }
      : {};
    chrome.tabs.query(query, (tabs) => {
      if (chrome.runtime.lastError) {
        sendResponse({ ok: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ ok: true, tabs: tabs || [] });
      }
    });
    return true;
  }

  // Navigate a chat tab in the background without stealing focus
  if (message.type === 'NAVIGATE_CHAT_TAB') {
    const tabId = message.tabId;
    const url = message.url;
    if (!Number.isInteger(tabId) || tabId <= 0) { sendResponse({ ok: false, error: 'Tab not found' }); return false; }
    if (!url || typeof url !== 'string') { sendResponse({ ok: false, error: 'Invalid tab URL' }); return false; }
    const active = Boolean(message.active);
    chrome.tabs.update(tabId, { url, active }, (tab) => {
      if (chrome.runtime.lastError || !tab) {
        sendResponse({ ok: false, error: 'Tab not found' });
        return;
      }
      sendResponse({ ok: true, tab });
    });
    return true;
  }

  // Close a chat tab
  if (message.type === 'CLOSE_CHAT_TAB') {
    const tabId = message.tabId;
    if (!Number.isInteger(tabId) || tabId <= 0) { sendResponse({ ok: false, error: 'Tab not found' }); return false; }
    chrome.tabs.remove(tabId, () => {
      if (chrome.runtime.lastError) { sendResponse({ ok: false, error: 'Tab not found' }); return; }
      sendResponse({ ok: true });
    });
    return true;
  }

  // Central Claude-compatible Computer Use Action Gateway
  if (message.type === 'COMPUTER_ACTION') {
    const action = message.action;
    // 1. Tab lifecycle actions
    if (action === 'create_tab') {
      const url = message.url || 'about:blank';
      const active = Boolean(message.active);
      const chatId = String(message.chatId || 'default');
      const chatTitle = String(message.chatTitle || chatId || 'Chat');
      chrome.tabs.create({ url, active }, (tab) => {
        if (chrome.runtime.lastError || !tab?.id) {
          sendResponse({ ok: false, error: 'Tab not found' });
          return;
        }
        getOrCreateChatGroup(chatId, chatTitle, tab.id, 'purple', (groupRes) => {
          sendResponse({ ok: true, action: 'create_tab', tab, groupId: groupRes?.groupId ?? null });
        });
      });
      return true;
    }
    if (action === 'list_tabs') {
      const chatId = String(message.chatId || 'default');
      getChatGroupInfo(chatId, (info) => {
        if (!info?.groupId) {
          chrome.tabs.query({}, (tabs) => sendResponse({ ok: true, action: 'list_tabs', tabs: tabs || [] }));
          return;
        }
        chrome.tabs.query({ groupId: info.groupId }, (tabs) => {
          sendResponse({ ok: true, action: 'list_tabs', tabs: tabs || [], groupId: info.groupId, title: info.title });
        });
      });
      return true;
    }
    if (action === 'navigate') {
      const tabId = message.tabId;
      const url = message.url;
      if (!Number.isInteger(tabId) || tabId <= 0) { sendResponse({ ok: false, error: 'Tab not found' }); return false; }
      if (!url || typeof url !== 'string') { sendResponse({ ok: false, error: 'Invalid tab URL' }); return false; }
      chrome.tabs.update(tabId, { url, active: Boolean(message.active) }, (tab) => {
        if (chrome.runtime.lastError || !tab) { sendResponse({ ok: false, error: 'Tab not found' }); return; }
        sendResponse({ ok: true, action: 'navigate', tab });
      });
      return true;
    }
    if (action === 'close_tab') {
      const tabId = message.tabId;
      if (!Number.isInteger(tabId) || tabId <= 0) { sendResponse({ ok: false, error: 'Tab not found' }); return false; }
      chrome.tabs.remove(tabId, () => {
        if (chrome.runtime.lastError) { sendResponse({ ok: false, error: 'Tab not found' }); return; }
        sendResponse({ ok: true, action: 'close_tab' });
      });
      return true;
    }
    if (action === 'screenshot') {
      const windowId = message.windowId;
      if (!Number.isInteger(windowId) || windowId < 0) {
        chrome.windows?.getCurrent((w) => {
          if (!w?.id) { sendResponse({ ok: false, error: 'Explicit panel window required' }); return; }
          chrome.tabs.captureVisibleTab(w.id, { format: 'png' }, (dataUrl) => {
            if (chrome.runtime.lastError) sendResponse({ ok: false, error: chrome.runtime.lastError.message });
            else sendResponse({ ok: true, action: 'screenshot', dataUrl });
          });
        });
        return true;
      }
      chrome.tabs.captureVisibleTab(windowId, { format: 'png' }, (dataUrl) => {
        if (chrome.runtime.lastError) sendResponse({ ok: false, error: chrome.runtime.lastError.message });
        else sendResponse({ ok: true, action: 'screenshot', dataUrl });
      });
      return true;
    }

    // 2. In-page DOM / input / coordinate actions -> forward to target tab
    const forwardToTab = (targetTabId) => {
      chrome.tabs.sendMessage(targetTabId, message, (res) => {
        if (chrome.runtime.lastError) {
          sendResponse({ ok: false, error: 'connection refused' });
        } else {
          sendResponse(res || { ok: false, error: 'unknown error' });
        }
      });
    };

    if (Number.isInteger(message.tabId) && message.tabId > 0) {
      forwardToTab(message.tabId);
      return true;
    }
    if (Number.isInteger(message.windowId) && message.windowId >= 0) {
      chrome.tabs.query({ active: true, windowId: message.windowId }, (tabs) => {
        if (tabs && tabs[0]?.id) forwardToTab(tabs[0].id);
        else sendResponse({ ok: false, error: 'No active tab' });
      });
      return true;
    }
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs[0]?.id) forwardToTab(tabs[0].id);
      else sendResponse({ ok: false, error: 'No active tab' });
    });
    return true;
  }

  // Helper for resilient localhost / 127.0.0.1 fetch
  const fetchWithFallback = async (path, options = {}) => {
    try {
      const res = await fetch(`http://localhost:4317${path}`, { ...options, signal: AbortSignal.timeout(5000) });
      if (res.ok) return res.json();
      throw new Error(`HTTP ${res.status}`);
    } catch {
      const fallbackRes = await fetch(`http://127.0.0.1:4317${path}`, { ...options, signal: AbortSignal.timeout(5000) });
      if (fallbackRes.ok) return fallbackRes.json();
      throw new Error(`HTTP ${fallbackRes.status}`);
    }
  };

  // Check Local Crewloom Daemon
  if (message.type === 'CHECK_LOCAL_DAEMON') {
    fetchWithFallback('/api/extension')
      .then((data) => { if (data.daemon !== 'crewloom' || data.browserCompanion !== 'manual') throw new Error('Unsupported dashboard handshake'); sendResponse({ ok: true, connected: true, data }); })
      .catch((err) => sendResponse({ ok: false, connected: false, error: err.message }));
    return true;
  }

  // Read current macOS permission state from the dashboard API
  if (message.type === 'GET_SYSTEM_PERMISSIONS') {
    fetchWithFallback('/api/system-permissions')
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }

  if (message.type === 'OPEN_MACOS_SETTINGS') {
    chrome.tabs.create({ url: 'http://127.0.0.1:4317/' }, () => sendResponse(chrome.runtime.lastError
      ? {ok:false,error:chrome.runtime.lastError.message}
      : { ok: true, instruction: 'Open Settings from the authenticated dashboard' }));
    return true;
  }

  sendResponse({ ok: false, error: 'unknown error' });
  return false;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const ownPanel = sender.id === chrome.runtime.id && sender.url === chrome.runtime.getURL('sidepanel.html');
  let dashboard = false;
  try { const url = new URL(sender.url); dashboard = url.protocol === 'http:' && ['localhost','127.0.0.1','[::1]'].includes(url.hostname) && url.port === '4317'; } catch {}
  if (['GET_CONTROL','SET_CONTROL'].includes(message.type)) {
    if (!ownPanel && !dashboard) { sendResponse({ ok: false, error: 'Untrusted control sender' }); return false; }
    if (message.type === 'SET_CONTROL') {
      if (typeof message.enabled !== 'boolean') { sendResponse({ ok: false, error: 'Invalid enabled state' }); return false; }
      chrome.storage.local.set({ 'crewloom.enabled': message.enabled }, () => sendResponse({ ok: true, enabled: message.enabled, version: chrome.runtime.getManifest().version }));
    } else chrome.storage.local.get({ 'crewloom.enabled': false }, (value) => sendResponse({ ok: true, enabled: value['crewloom.enabled'], version: chrome.runtime.getManifest().version }));
    return true;
  }
  if (!ownPanel) { sendResponse({ ok: false, error: 'Only the companion panel may request this action' }); return false; }
  chrome.storage.local.get({ 'crewloom.enabled': false }, (value) => {
    if (message.type === 'CAPTURE_TAB' && !value['crewloom.enabled']) return sendResponse({ ok: false, error: 'Browser companion is disabled' });
    handleMessage(message, sender, sendResponse);
  });
  return true;
});

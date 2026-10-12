/**
 * Crewloom Computer Use - Side Panel Controller
 * Manual tab management, DOM indexing, visual capture & execution.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const tabTitle = document.getElementById('tabTitle');
  const tabUrl = document.getElementById('tabUrl');
  const refreshTabBtn = document.getElementById('refreshTabBtn');
  const indexBtn = document.getElementById('indexBtn');
  let currentGeneration = null;
  let panelWindowId = null;
  const captureBtn = document.getElementById('captureBtn');
  const inspectBtn = document.getElementById('inspectBtn');
  const clearBtn = document.getElementById('clearBtn');
  const visionImg = document.getElementById('visionImg');
  const visionEmpty = document.getElementById('visionEmpty');
  const frameMeta = document.getElementById('frameMeta');
  const elementInput = document.getElementById('elementInput');
  const clickElementBtn = document.getElementById('clickElementBtn');
  const directoryList = document.getElementById('directoryList');
  const elemCountBadge = document.getElementById('elemCountBadge');
  const terminalLogs = document.getElementById('terminalLogs');
  const clearConsoleBtn = document.getElementById('clearConsoleBtn');
  const openMacSettingsBtn = document.getElementById('openMacSettingsBtn');
  const langToggle = document.getElementById('langToggle');
  const daemonLabel = document.getElementById('daemonLabel');

  const LANG_KEY = 'crewloom.lang';
  const MAX_DIRECTORY_ROWS = 50;
  const RESTRICTED_URL = /^(chrome|edge|brave|about|chrome-extension|devtools|view-source):/i;

  let currentTab = null;
  let language = 'en';
  let directoryEmptyKey = 'dirIdle';
  let lastDirectoryNote = null;
  let lastCaptureTime = null;

  const i18n = {
    en: {
      indexName: 'Auto-Index Page',
      indexSub: 'Number buttons [1], [2]...',
      captureName: 'Vision Capture',
      captureSub: 'Capture tab screenshot',
      inspectName: 'Hover Inspector',
      inspectSub: 'Inspect DOM elements',
      clearName: 'Clear Overlays',
      clearSub: 'Remove in-page tags',
      visionTitle: 'Visual Vision Frame',
      visionEmpty: 'Click "Vision Capture" to stream the visual tab state for the AI agent.',
      noCapture: 'No capture yet',
      captureMeta: 'Captured {time}',
      inputPlaceholder: 'Element # (e.g. 1)',
      clickBtn: 'Execute Click',
      interactiveTitle: 'Interactive Elements',
      terminalTitle: 'Agent Execution Stream',
      clearConsole: 'Clear',
      permAcc: '🖥️ Accessibility',
      permScreen: '📸 Screen Capture',
      macSettings: 'macOS Settings ↗',
      daemonOnline: 'Online :4317',
      daemonStandalone: 'Standalone',
      dirIdle: 'Click "Auto-Index Page" to detect interactive elements.',
      dirEmpty: 'No interactive elements detected.',
      dirCleared: 'Overlays cleared.',
      dirShowing: 'Showing first {shown} of {total} elements.',
      dirTruncated: 'Page limit reached: {shown} of {total} indexed (limit {limit}).',
      logInit: 'Panel ready. Extension version {version}.',
      logTab: 'Focused tab: {title}',
      logNoTab: 'No readable tab.',
      logIndexing: 'Indexing interactive elements on page...',
      logIndexed: 'Indexed {count} interactive elements.',
      logIndexLimited: 'Indexed {shown} of {total} elements; page limit {limit} reached.',
      logIndexFailed: 'Index failed: {error}',
      logRestricted: 'This page blocks extensions (browser settings page).',
      logCleared: 'In-page grounding tags cleared.',
      logClearFailed: 'Clear failed: {error}',
      logInspecting: 'Inspector activated: hover over page elements.',
      logInspectorOff: 'Inspector deactivated.',
      logInspectorFailed: 'Inspector failed: {error}',
      logCapture: 'Capturing high-resolution visual tab frame...',
      logCaptured: 'Visual frame captured at {time}.',
      logCaptureFailed: 'Vision capture failed: {error}',
      logClick: 'Executing browser click on element [{index}]...',
      logClicked: 'Click dispatched on <{tag}> at ({x}, {y}).',
      logClickFailed: 'Click failed: {error}',
      logMacOpening: 'Opening macOS Accessibility settings...',
      logMacOpened: 'macOS settings request sent to the dashboard.',
      logMacFailed: 'Could not reach the dashboard API: {error}',
      logDaemon: 'Local Crewloom daemon handshake verified.',
      logDaemonOffline: 'Dashboard API offline on :4317 ({error}).',
      logLang: 'Language switched to {language}.'
    },
    ar: {
      indexName: 'ترقيم الصفحة',
      indexSub: 'ترقيم العناصر التفاعلية [1]، [2]...',
      captureName: 'التقاط الرؤية',
      captureSub: 'أخذ لقطة فورية للتبويب',
      inspectName: 'الفاحص المباشر',
      inspectSub: 'فحص شجرة DOM للويب',
      clearName: 'مسح الإشارات',
      clearSub: 'إزالة أرقام العناصر',
      visionTitle: 'إطار الرؤية البصرية',
      visionEmpty: 'اضغط "التقاط الرؤية" لبث لقطة التبويب لوكيل الذكاء الاصطناعي.',
      noCapture: 'لا يوجد التقاط بعد',
      captureMeta: 'تم الالتقاط {time}',
      inputPlaceholder: 'رقم العنصر (مثال: 1)',
      clickBtn: 'تنفيذ النقر',
      interactiveTitle: 'العناصر التفاعلية',
      terminalTitle: 'سجل تنفيذ الوكيل',
      clearConsole: 'مسح',
      permAcc: '🖥️ إمكانية الوصول',
      permScreen: '📸 تسجيل الشاشة',
      macSettings: 'إعدادات الماك ↗',
      daemonOnline: 'متصل :4317',
      daemonStandalone: 'مستقل',
      dirIdle: 'اضغط "ترقيم الصفحة" لاكتشاف العناصر التفاعلية.',
      dirEmpty: 'لم يتم العثور على عناصر تفاعلية.',
      dirCleared: 'تم مسح الإشارات.',
      dirShowing: 'عرض أول {shown} من {total} عنصر.',
      dirTruncated: 'بلغت حدود الصفحة: تم ترقيم {shown} من {total} (الحد {limit}).',
      logInit: 'اللوحة جاهزة. إصدار الإضافة {version}.',
      logTab: 'التبويب النشط: {title}',
      logNoTab: 'لا يوجد تبويب قابل للقراءة.',
      logIndexing: 'جارٍ ترقيم العناصر التفاعلية في الصفحة...',
      logIndexed: 'تم ترقيم {count} عنصر تفاعلي.',
      logIndexLimited: 'تم ترقيم {shown} من {total} عنصر؛ تم بلوغ حد الصفحة {limit}.',
      logIndexFailed: 'فشل الترقيم: {error}',
      logRestricted: 'هذه الصفحة تمنع الإضافات (صفحة إعدادات المتصفح).',
      logCleared: 'تم مسح أرقام العناصر من الصفحة.',
      logClearFailed: 'فشل المسح: {error}',
      logInspecting: 'تم تفعيل الفاحص: مرّر المؤشر فوق عناصر الصفحة.',
      logInspectorOff: 'تم إيقاف الفاحص.',
      logInspectorFailed: 'فشل الفاحص: {error}',
      logCapture: 'جارٍ التقاط إطار الرؤية بدقة عالية...',
      logCaptured: 'تم التقاط الإطار البصري في {time}.',
      logCaptureFailed: 'فشل التقاط الرؤية: {error}',
      logClick: 'جارٍ تنفيذ نقرة الوكيل على العنصر [{index}]...',
      logClicked: 'تم إرسال نقرة إلى <{tag}> عند ({x}، {y}).',
      logClickFailed: 'فشلت النقرة: {error}',
      logMacOpening: 'جارٍ فتح إعدادات الوصول في macOS...',
      logMacOpened: 'تم إرسال طلب الإعدادات إلى الداشبورد.',
      logMacFailed: 'تعذر الوصول إلى واجهة الداشبورد: {error}',
      logDaemon: 'تم التحقق من الاتصال بالداشبورد المحلي.',
      logDaemonOffline: 'واجهة الداشبورد غير متاحة على :4317 ({error}).',
      logLang: 'تم تبديل اللغة إلى {language}.'
    }
  };

  const languageNames = { en: 'English', ar: 'Arabic' };

  function t(key, vars) {
    const template = i18n[language][key] ?? i18n.en[key] ?? key;
    if (!vars) return template;
    return template.replace(/\{(\w+)\}/g, (match, name) =>
      Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : match
    );
  }

  function getTime() {
    return new Date().toLocaleTimeString('en-US', { hour12: false });
  }

  function log(key, type = 'info', vars) {
    const line = document.createElement('div');
    line.className = `log-line log-${type}`;
    line.textContent = `[${getTime()}] ${t(key, vars)}`;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  function describeError(error, key = 'logIndexFailed') {
    const message = chrome.runtime.lastError?.message || error || 'unknown error';
    if (RESTRICTED_URL.test(currentTab?.url || '')) {
      return log('logRestricted', 'warn');
    }
    return log(key, 'warn', { error: message });
  }

  function setDirectoryText(textKey) {
    directoryEmptyKey = textKey;
    lastDirectoryNote = null;
    directoryList.innerHTML = '';
    const empty = document.createElement('div');
    empty.className = 'directory-empty';
    empty.textContent = t(textKey);
    directoryList.appendChild(empty);
  }

  function setDirectoryNote(key, vars) {
    lastDirectoryNote = { key, vars };
    const note = document.createElement('div');
    note.className = 'directory-note';
    note.textContent = t(key, vars);
    directoryList.insertBefore(note, directoryList.firstChild);
  }

  function resetIndexState() {
    currentGeneration = null;
    elemCountBadge.textContent = '0';
    setDirectoryText('dirIdle');
  }

  // Refresh active tab info
  function refreshActiveTab(onReady) {
    chrome.runtime.sendMessage({ type: 'GET_ACTIVE_TAB', windowId: panelWindowId }, (res) => {
      const tabId = res?.tab?.id;
      const previousId = currentTab?.id;
      currentTab = res?.tab ?? null;

      if (!currentTab?.id) {
        tabTitle.textContent = t('logNoTab');
        tabUrl.textContent = '—';
        return;
      }

      tabTitle.textContent = currentTab.title || 'Untitled';
      tabUrl.textContent = currentTab.url ? new URL(currentTab.url).hostname : '—';
      log('logTab', 'info', { title: tabTitle.textContent });

      if (previousId && previousId !== currentTab.id) {
        // Indices from the previous page no longer describe this tab
        chrome.tabs.sendMessage(previousId, { type: 'CLEAR_INDEX' }, () => {
          void chrome.runtime.lastError;
        });
        resetIndexState();
      }
      if (typeof onReady === 'function') onReady();
    });
  }

  // Auto-Index Page
  indexBtn.addEventListener('click', () => {
    if (!currentTab?.id) return refreshActiveTab();
    log('logIndexing', 'action');
    chrome.tabs.sendMessage(currentTab.id, { type: 'INDEX_PAGE' }, (res) => {
      if (chrome.runtime.lastError || !res?.ok) {
        currentGeneration = null;
    elemCountBadge.textContent = '0';
        setDirectoryText('dirIdle');
        return describeError(res?.error);
      }
      currentGeneration = res.generation;
      elemCountBadge.textContent = res.count;
      if (res.truncated) {
        log('logIndexLimited', 'warn', {
          shown: res.count,
          total: res.total,
          limit: res.limit
        });
      } else {
        log('logIndexed', 'success', { count: res.count });
      }
      renderDirectory(res);
    });
  });

  // Render directory list
  function renderDirectory(res) {
    const items = res.items || [];
    directoryList.innerHTML = '';
    if (!items.length) {
      setDirectoryText('dirEmpty');
      return;
    }

    const shown = Math.min(items.length, MAX_DIRECTORY_ROWS);
    setDirectoryNote(res.truncated ? 'dirTruncated' : 'dirShowing', {
      shown: res.truncated ? items.length : shown,
      total: res.total ?? items.length,
      limit: res.limit ?? items.length
    });

    items.slice(0, shown).forEach((item) => {
      const row = document.createElement('div');
      row.className = 'directory-item';

      const idx = document.createElement('span');
      idx.className = 'elem-idx';
      idx.textContent = `[${item.index}]`;

      const desc = document.createElement('span');
      desc.className = 'elem-desc';
      desc.textContent = `<${item.tag}> ${item.text || '—'}`;
      desc.title = `<${item.tag}> ${item.text || ''}`;

      const click = document.createElement('button');
      click.className = 'btn-item-click';
      click.dataset.index = item.index;
      click.textContent = 'Click';
      click.addEventListener('click', () => executeClick(item.index));

      row.append(idx, desc, click);
      directoryList.appendChild(row);
    });
  }

  // Execute Click on Element Index
  function executeClick(index) {
    if (!currentTab?.id) return;
    log('logClick', 'action', { index });
    chrome.tabs.sendMessage(currentTab.id, { type: 'CLICK_INDEX', index, generation: currentGeneration }, (res) => {
      if (res?.ok) {
        log('logClicked', 'success', {
          tag: res.tag,
          x: Math.round(res.x),
          y: Math.round(res.y)
        });
      } else {
        log('logClickFailed', 'warn', { error: res?.error || 'element not found' });
      }
    });
  }

  clickElementBtn.addEventListener('click', () => {
    const value = parseInt(elementInput.value, 10);
    if (Number.isFinite(value) && value > 0) {
      executeClick(value);
      elementInput.value = '';
    }
  });

  elementInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') clickElementBtn.click();
  });

  // Vision Capture
  function captureFrame() {
    log('logCapture', 'action');
    chrome.runtime.sendMessage(
      { type: 'CAPTURE_TAB', windowId: panelWindowId },
      (res) => {
        if (res?.ok && res.dataUrl) {
          visionImg.src = res.dataUrl;
          visionImg.classList.remove('hidden');
          visionEmpty.classList.add('hidden');
          const time = getTime();
          lastCaptureTime = time;
          frameMeta.textContent = t('captureMeta', { time });
          log('logCaptured', 'success', { time });
        } else {
          log('logCaptureFailed', 'warn', { error: res?.error || 'unknown error' });
        }
      }
    );
  }

  captureBtn.addEventListener('click', captureFrame);

  let consumingCapture = false;
  function consumePendingCapture() {
    if (consumingCapture || !Number.isInteger(panelWindowId)) return;
    consumingCapture = true;
    chrome.runtime.sendMessage({ type: 'PANEL_READY', windowId: panelWindowId }, (res) => {
      consumingCapture = false;
      if (!res?.ok || !res.pending) return;
      refreshActiveTab(() => {
        // Refuse if the clicked tab changed while the panel was opening.
        if (currentTab?.id === res.pending.tabId && currentTab.windowId === panelWindowId) captureFrame();
      });
    });
  }
  chrome.runtime.onMessage.addListener((message) => {
    if (message?.type === 'CAPTURE_REQUEST' && message.windowId === panelWindowId) consumePendingCapture();
  });

  // Hover Inspector
  inspectBtn.addEventListener('click', () => {
    if (!currentTab?.id) return;
    chrome.tabs.sendMessage(currentTab.id, { type: 'TOGGLE_INSPECTOR' }, (res) => {
      if (chrome.runtime.lastError || !res?.ok) {
        return describeError(res?.error, 'logInspectorFailed');
      }
      log(res.active ? 'logInspecting' : 'logInspectorOff', 'info');
    });
  });

  // Clear Overlays
  clearBtn.addEventListener('click', () => {
    if (!currentTab?.id) return;
    chrome.tabs.sendMessage(currentTab.id, { type: 'CLEAR_INDEX' }, (res) => {
      if (chrome.runtime.lastError || !res?.ok) {
        return describeError(res?.error, 'logClearFailed');
      }
      currentGeneration = null;
    elemCountBadge.textContent = '0';
      setDirectoryText('dirCleared');
      log('logCleared', 'info');
    });
  });

  // Refresh tab
  refreshTabBtn.addEventListener('click', refreshActiveTab);

  // Clear console
  clearConsoleBtn.addEventListener('click', () => {
    terminalLogs.innerHTML = '';
  });

  // macOS Settings Deep Link
  openMacSettingsBtn.addEventListener('click', () => {
    log('logMacOpening', 'action');
    chrome.runtime.sendMessage(
      { type: 'OPEN_MACOS_SETTINGS', pane: 'Privacy_Accessibility' },
      (res) => {
        if (res?.ok) log('logMacOpened', 'success');
        else log('logMacFailed', 'warn', { error: res?.error || 'unknown error' });
      }
    );
  });

  function applyLanguage(lang) {
    language = lang === 'ar' ? 'ar' : 'en';
    const isRtl = language === 'ar';
    document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', language);
    langToggle.textContent = isRtl ? 'English' : 'العربية';

    document.querySelector('#indexBtn .tool-name').textContent = t('indexName');
    document.querySelector('#indexBtn .tool-sub').textContent = t('indexSub');
    document.querySelector('#captureBtn .tool-name').textContent = t('captureName');
    document.querySelector('#captureBtn .tool-sub').textContent = t('captureSub');
    document.querySelector('#inspectBtn .tool-name').textContent = t('inspectName');
    document.querySelector('#inspectBtn .tool-sub').textContent = t('inspectSub');
    document.querySelector('#clearBtn .tool-name').textContent = t('clearName');
    document.querySelector('#clearBtn .tool-sub').textContent = t('clearSub');
    document.querySelector('#visionSection .section-title').textContent = t('visionTitle');
    document.querySelector('#visionEmpty span').textContent = t('visionEmpty');
    elementInput.placeholder = t('inputPlaceholder');
    clickElementBtn.textContent = t('clickBtn');
    document.querySelector('.directory-section .section-title').textContent = t('interactiveTitle');
    document.querySelector('.terminal-section .section-title').textContent = t('terminalTitle');
    clearConsoleBtn.textContent = t('clearConsole');
    document.getElementById('permAcc').textContent = t('permAcc');
    document.getElementById('permScreen').textContent = t('permScreen');
    openMacSettingsBtn.textContent = t('macSettings');
    if (lastCaptureTime) frameMeta.textContent = t('captureMeta', { time: lastCaptureTime });

    const empty = directoryList.querySelector('.directory-empty');
    if (empty) empty.textContent = t(directoryEmptyKey);
    const note = directoryList.querySelector('.directory-note');
    if (note && lastDirectoryNote) note.textContent = t(lastDirectoryNote.key, lastDirectoryNote.vars);
  }

  // Language Toggle (English <-> Arabic) persisted across panel sessions
  function setLanguage(lang, announce) {
    applyLanguage(lang);
    chrome.storage.local.set({ [LANG_KEY]: language });
    if (announce) log('logLang', 'info', { language: languageNames[language] });
  }

  langToggle.addEventListener('click', () => {
    setLanguage(language === 'ar' ? 'en' : 'ar', true);
  });

  chrome.storage.local.get(LANG_KEY, (stored) => {
    applyLanguage(stored?.[LANG_KEY]);
    log('logInit', 'info', { version: chrome.runtime.getManifest().version });
    refreshActiveTab();
  });

  const control = document.getElementById('companionEnabled');
  function showControl(enabled) {
    control.checked = enabled;
    for (const id of ['indexBtn','captureBtn','inspectBtn','clickElementBtn']) document.getElementById(id).disabled = !enabled;
  }
  chrome.runtime.sendMessage({ type: 'GET_CONTROL' }, (res) => showControl(res?.ok && res.enabled));
  control.addEventListener('change', () => chrome.runtime.sendMessage({ type: 'SET_CONTROL', enabled: control.checked }, (res) => showControl(res?.ok && res.enabled)));
  chrome.storage.onChanged.addListener((changes, area) => { if (area === 'local' && changes['crewloom.enabled']) showControl(changes['crewloom.enabled'].newValue); });

  // Check Local Daemon status
  chrome.runtime.sendMessage({ type: 'CHECK_LOCAL_DAEMON' }, (res) => {
    if (res?.connected) {
      daemonLabel.textContent = t('daemonOnline');
      log('logDaemon', 'success');
    } else {
      daemonLabel.textContent = t('daemonStandalone');
      daemonLabel.style.color = 'var(--warn)';
      log('logDaemonOffline', 'warn', { error: res?.error || 'connection refused' });
    }
  });

  chrome.windows?.getCurrent((w) => { panelWindowId = w.id; refreshActiveTab(consumePendingCapture); });

  // Dynamic tab tracking like Claude/Codex
  if (chrome.tabs?.onActivated) {
    chrome.tabs.onActivated.addListener(() => refreshActiveTab());
  }
  if (chrome.tabs?.onUpdated) {
    chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
      if (currentTab && tabId === currentTab.id && changeInfo.status === 'complete') {
        resetIndexState();
        refreshActiveTab();
      }
    });
  }
});
'use client';
import { useEffect, useState } from 'react';
export default function ComputerUsePanel({ language }: { language: 'en' | 'ar' }) {
  const ar = language === 'ar';
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [version, setVersion] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [permissions, setPermissions] = useState<{ id: string; granted: boolean | null; error?: string }[]>([]);
  const [deviceKind, setDeviceKind] = useState<'windows' | 'macos' | 'linux'>('macos');

  useEffect(() => {
    if (typeof window === 'undefined' || !navigator) return;
    const ua = navigator.userAgent || '';
    const platform = (navigator as unknown as { userAgentData?: { platform?: string } }).userAgentData?.platform || navigator.platform || '';
    if (/Win/i.test(platform) || /Windows/i.test(ua)) setDeviceKind('windows');
    else if (/Linux/i.test(platform) || /Linux/i.test(ua)) setDeviceKind('linux');
    else setDeviceKind('macos');
  }, []);
  useEffect(() => {
    let lastSeen = 0;
    function receive(event: MessageEvent) {
      if (event.source !== window || event.origin !== location.origin || event.data?.type !== 'CREWLOOM_CONTROL_STATE') return;
      if (typeof event.data.enabled !== 'boolean' || typeof event.data.version !== 'string') return;
      lastSeen = Date.now(); setEnabled(event.data.enabled); setVersion(event.data.version); setPending(false); setError('');
    }
    window.addEventListener('message', receive);
    const poll = () => { if (Date.now() - lastSeen > 10000) { setEnabled(null); setPending(false); } window.postMessage({ type: 'CREWLOOM_GET_CONTROL' }, location.origin); };
    poll(); const timer = setInterval(poll, 5000);
    return () => { window.removeEventListener('message', receive); clearInterval(timer); };
  }, []);
  async function inspect() {
    try {
      const response = await fetch('/api/system-permissions', { cache: 'no-store' });
      const value = await response.json(); if (!response.ok) throw new Error(value.error);
      setPermissions(value.permissions);
    } catch (e) { setError(String(e)); }
  }
  async function open(pane: string) {
    try {
      const response = await fetch('/api/system-permissions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pane }) });
      if (!response.ok) throw new Error((await response.json()).error);
    } catch (e) { setError(String(e)); }
  }
  return <section className="computer-use-panel" aria-label="Crewloom Browser Companion">
    <div className="computer-use-row">
      <img src="/assets/crewloom-computer-use-icon.svg" alt="" width="40" height="40" />
      <div><strong>{ar ? 'إضافة متصفح Crewloom' : 'Crewloom Browser Companion'}</strong>
        <p>{enabled === null ? (ar ? 'الاتصال غير متحقق — حمّل الإضافة وأعد تحميل الصفحة' : 'Connection unverified — load the extension and reload this page') : `${version} · ${ar ? 'تحكم يدوي بالمتصفح' : 'Manual browser controls'}`}</p>
      </div>
      <button role="switch" aria-checked={enabled === true} disabled={enabled === null || pending}
        aria-label={ar ? 'تفعيل إضافة المتصفح' : 'Enable browser companion'}
        className={`companion-switch ${enabled ? 'on' : ''}`}
        onClick={() => { setPending(true); window.postMessage({ type: 'CREWLOOM_SET_CONTROL', enabled: !enabled }, location.origin); }}>
        <span />
      </button>
    </div>
    <div style={{ margin: '10px 0', padding: '8px 12px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--line)', fontSize: '12px' }}>
      <strong>{ar ? 'الترشيح التلقائي عبر المتصفح للجهاز الحالي:' : 'Browser-recommended host adapter for your device:'}</strong>{' '}
      {deviceKind === 'windows' ? (
        <span>{ar ? 'ويندوز (Win32) — أتمتة الـ DOM والتقاط الشاشة عبر محول Windows Adapter المدمج' : 'Windows (Win32) — DOM automation & native capture via built-in Windows Adapter'}</span>
      ) : deviceKind === 'linux' ? (
        <span>{ar ? 'لينكس (X11/Wayland) — متوافق مع إضافة المتصفح' : 'Linux (X11/Wayland) — compatible with Browser Companion'}</span>
      ) : (
        <span>{ar ? 'ماك macOS — يحتاج إذن تسجيل الشاشة والوصولية للأتمتة الكاملة' : 'macOS — requires Screen Recording & Accessibility for full automation'}</span>
      )}
    </div>
    <p>{ar ? 'التفعيل عام للإضافة في هذا المتصفح. التحكم عبر DOM لا يحتاج صلاحية Accessibility.' : 'Activation applies to this browser extension. DOM controls do not require macOS Accessibility.'}</p>
    <p><a href="/api/extension/download">{ar ? 'تحميل إضافة المتصفح' : 'Download browser extension'}</a></p>
    <button onClick={inspect}>{ar ? (deviceKind === 'windows' ? 'فحص جاهزية التقاط الشاشة على Windows' : 'فحص التقاط الشاشة على macOS') : (deviceKind === 'windows' ? 'Check Windows screen capture' : 'Check macOS screen capture')}</button>{' '}
    <button onClick={() => open(deviceKind === 'windows' ? 'ms-settings:privacy' : 'Privacy_ScreenCapture')}>{ar ? 'فتح إعدادات الشاشة' : 'Open screen settings'}</button>
    {permissions.map(p => <p key={p.id}>{p.id}: {p.granted === null ? (ar ? 'غير متحقق' : 'Unknown') : p.granted ? (ar ? 'تم التحقق من الفحص' : 'Probe verified') : (ar ? 'الفحص لم ينجح' : 'Probe failed')}{p.error ? ` — ${p.error}` : ''}</p>)}
    {error && <p role="alert">{error}</p>}
  </section>;
}

'use client';
import ActivityPanel, { type Activity, type Controls } from './activity-panel';
import ProjectsPanel from './projects-panel';
import ComputerUsePanel from './computer-use-panel';
import { parseToolArguments } from '../lib/tool-arguments';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { LogoLoader } from './logo-loader';

type Skill = { id: string; description: string; lastActivity: string | null; openTasks: number; doneEntries: number; openChallenges: number; ideas: number; tools: string[]; runs: number; failedRuns: number; status: 'healthy' | 'attention' | 'idle' };
type Tool = { id: string; skill: string; description: string; example_args: string; effect: string; dashboard?: 'cli' | 'project' };
type Run = { ts: string; tool: string; skill: string; exit_code: number; duration_ms: number; source: string; output?: string };
type Overview = { activity?: Activity; controls?: Controls; projectRoot: string; toolkitRoot: string; generatedAt: string; totals: Record<string, number>; skills: Skill[]; tools: Tool[]; runs: Run[] };
type Detail = { id: string; skill: string; brain: Record<string, string> };

const T = {
  en: { skills: 'Roles', tools: 'Tools', attention: 'Need attention', tasks: 'Open tasks', challenges: 'Open challenges', failed: 'Failed runs (last 50)', live: 'Live', offline: 'Reconnecting', search: 'Search roles', all: 'All', run: 'Run', runs: 'Recent runs', checks: 'Run repository checks', args: 'Arguments (quoted text or JSON array, project-relative)', none: 'No runs recorded yet. Run a tool here or with the CLI.', role: 'Role', status: 'Status', activity: 'Last memory update', done: 'Done', open: 'Open', ideas: 'Ideas', lang: 'العربية', signIn: 'Sign in', signOut: 'Sign out', token: 'Dashboard access token', unauthorized: 'Sign in to view this project.', download: 'Download App', downloadAria: 'Download Crewloom Desktop & CLI' },
  ar: { skills: 'الأدوار', tools: 'الأدوات', attention: 'تحتاج متابعة', tasks: 'مهام مفتوحة', challenges: 'تحديات مفتوحة', failed: 'تشغيل فاشل (آخر 50)', live: 'مباشر', offline: 'إعادة اتصال', search: 'ابحث في الأدوار', all: 'الكل', run: 'تشغيل', runs: 'آخر التشغيلات', checks: 'شغّل فحوص الريبو', args: 'المعاملات (نص مقتبس أو مصفوفة JSON، مسارات نسبية للمشروع)', none: 'لا توجد تشغيلات بعد. شغّل أداة من هنا أو من الـ CLI.', role: 'الدور', status: 'الحالة', activity: 'آخر تحديث للذاكرة', done: 'منجز', open: 'مفتوح', ideas: 'أفكار', lang: 'English', signIn: 'تسجيل الدخول', signOut: 'تسجيل الخروج', token: 'رمز دخول لوحة المعلومات', unauthorized: 'سجّل الدخول لعرض هذا المشروع.', download: 'تحميل التطبيق', downloadAria: 'تحميل تطبيق كرو لوم المكتبي والطرفية' },
} as const;

const ago = (iso: string | null) => {
  if (!iso) return '—';
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  return s < 60 ? `${Math.floor(s)}s` : s < 3600 ? `${Math.floor(s / 60)}m` : s < 86400 ? `${Math.floor(s / 3600)}h` : `${Math.floor(s / 86400)}d`;
};

export default function Dashboard() {
  const [lang, setLang] = useState<'en' | 'ar'>('en');
  const t = T[lang];
  const [data, setData] = useState<Overview | null>(null);
  const [live, setLive] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'all' | Skill['status']>('all');
  const [detail, setDetail] = useState<Detail | null>(null);
  const [tab, setTab] = useState('skill');
  const [toolId, setToolId] = useState('');
  const [args, setArgs] = useState('');
  const [busy, setBusy] = useState(false);
  const [output, setOutput] = useState<{ ok: boolean; text: string } | null>(null);
  const [local, setLocal] = useState(false);
  const [token, setToken] = useState('');
  const [auth, setAuth] = useState<'unknown' | 'in' | 'out' | 'error'>('unknown');
  const openId = useRef<string | null>(null);

  const [device, setDevice] = useState<{ os: 'windows' | 'macos-arm' | 'macos-intel' | 'linux' | 'unknown'; nameEn: string; nameAr: string; downloadUrl: string; command: string }>({
    os: 'unknown',
    nameEn: 'App & CLI',
    nameAr: 'التطبيق والطرفية',
    downloadUrl: 'https://crewloom.org/#install',
    command: 'curl -fsSL https://crewloom.org/install.sh | bash',
  });

  useEffect(() => {
    if (typeof window === 'undefined' || !navigator) return;
    const ua = navigator.userAgent || '';
    const platform = (navigator as unknown as { userAgentData?: { platform?: string } }).userAgentData?.platform || navigator.platform || '';

    if (/Win/i.test(platform) || /Windows/i.test(ua)) {
      setDevice({
        os: 'windows',
        nameEn: 'Windows (Recommended)',
        nameAr: 'ويندوز (موصى به لجهازك)',
        downloadUrl: 'https://crewloom.org/install.ps1',
        command: 'irm https://crewloom.org/install.ps1 | iex',
      });
      return;
    }
    if (/Mac/i.test(platform) || /Macintosh|MacIntel/i.test(ua)) {
      let isAppleSilicon = true;
      try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl && 'getExtension' in gl) {
          const debugInfo = (gl as WebGLRenderingContext).getExtension('WEBGL_debug_renderer_info');
          if (debugInfo) {
            const renderer = (gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || '';
            if (/Intel/i.test(renderer)) isAppleSilicon = false;
          }
        }
      } catch {}

      setDevice({
        os: isAppleSilicon ? 'macos-arm' : 'macos-intel',
        nameEn: isAppleSilicon ? 'macOS Apple Silicon (Recommended)' : 'macOS Intel (Recommended)',
        nameAr: isAppleSilicon ? 'ماك Apple Silicon (موصى به)' : 'ماك معالجات إنتل (موصى به)',
        downloadUrl: 'https://crewloom.org/Crewloom.dmg',
        command: 'curl -fsSL https://crewloom.org/install.sh | bash',
      });
      return;
    }
    if (/Linux/i.test(platform) || /Linux/i.test(ua)) {
      setDevice({
        os: 'linux',
        nameEn: 'Linux CLI (Recommended)',
        nameAr: 'لينكس الطرفية (موصى به)',
        downloadUrl: 'https://crewloom.org/#install',
        command: 'curl -fsSL https://crewloom.org/install.sh | bash',
      });
      return;
    }
  }, []);

  const session = useCallback(async () => {
    try {
      const res = await fetch('/api/auth/session', { cache: 'no-store' });
      const body = await res.json();
      setLocal(body.method === 'local');
      setAuth(res.ok && body.authenticated ? 'in' : 'out');
    } catch { setAuth('error'); }
  }, []);

  const signIn = async () => {
    const res = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }) });
    if (res.ok) { setToken(''); setAuth('in'); } else setAuth('error');
  };

  const signOut = async () => {
    await fetch('/api/auth/login', { method: 'DELETE' });
    setData(null); setDetail(null); setLive(false); setAuth('out');
  };

  const load = useCallback(async () => {
    try {
      const res = await fetch('/api/overview', { cache: 'no-store' });
      if (res.status === 401 || res.status === 403) { setAuth('out'); return; }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json()); setError('');
    } catch (e) { setError(String(e)); }
  }, []);

  const loadDetail = useCallback(async (id: string) => {
    const res = await fetch(`/api/skills/${id}`, { cache: 'no-store' });
    if (res.ok) {
      const value = await res.json();
      if (openId.current === id) setDetail(value);
    }
  }, []);

  useEffect(() => { document.documentElement.lang = lang; document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'; }, [lang]);
  useEffect(() => { void session(); }, [session]);
  useEffect(() => { if (auth === 'in') void load(); }, [auth, load]);
  useEffect(() => {
    if (auth !== 'in') return;
    const source = new EventSource('/api/events');
    source.addEventListener('ready', () => setLive(true));
    source.addEventListener('change', () => { void load(); if (openId.current) void loadDetail(openId.current); });
    source.onerror = () => setLive(false);
    return () => source.close();
  }, [auth, load, loadDetail]);
  useEffect(() => { if (auth !== 'in') return; const id = setInterval(() => { void load(); }, 15000); return () => clearInterval(id); }, [auth, load]);
  useEffect(() => { if (data && !toolId && data.tools[0]) { setToolId(data.tools[0].id); setArgs(data.tools[0].example_args.replace('{input}', '')); } }, [data, toolId]);

  const skills = useMemo(() => (data?.skills ?? []).filter((s) => (filter === 'all' || s.status === filter) && (`${s.id} ${s.description}`.toLowerCase().includes(query.toLowerCase()))), [data, filter, query]);

  const pickSkill = (id: string) => { openId.current = id; setTab('skill'); void loadDetail(id); };
  const runTool = async () => {
    setBusy(true); setOutput(null);
    try {
      const res = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tool: toolId, args: parseToolArguments(args) }) });
      const body = await res.json();
      if (res.status === 401 || res.status === 403) { setAuth('out'); return; }
      setOutput({ ok: res.ok && body.exit_code === 0, text: body.error ?? body.output ?? '' });
    } catch (e) { setOutput({ ok: false, text: String(e) }); } finally { setBusy(false); }
  };
  const runChecks = async () => {
    setBusy(true); setOutput(null);
    try { const res = await fetch('/api/check', { method: 'POST' });
      if (res.status === 401 || res.status === 403) { setAuth('out'); return; }
      const body = await res.json(); setOutput({ ok: body.exit_code === 0, text: body.output }); }
    catch (e) { setOutput({ ok: false, text: String(e) }); } finally { setBusy(false); }
  };

  const totals = data?.totals ?? {};
  if (auth === 'unknown') {
    const opening = lang === 'ar' ? 'جارٍ فتح اللوحة…' : 'Opening dashboard…';
    return <main className="wrap boot"><LogoLoader label={opening} size={112} /><p>{opening}</p></main>;
  }
  if (auth !== 'in') {
    return (
      <main className="wrap">
        <header className="top">
          <h1>Crewloom</h1>
          <div className="toolbar">
            <a
              href={device.downloadUrl}
              download={device.os === 'windows' ? 'install.ps1' : device.os.startsWith('macos') ? 'Crewloom.dmg' : undefined}
              target={device.os === 'linux' || device.os === 'unknown' ? '_blank' : undefined}
              rel="noopener noreferrer"
              aria-label={`${t.downloadAria} - ${lang === 'ar' ? device.nameAr : device.nameEn}`}
              title={`${t.downloadAria} - ${lang === 'ar' ? device.nameAr : device.nameEn}`}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                borderRadius: '8px',
                background: 'var(--accent)',
                color: '#fff',
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '13px',
              }}
            >
              {device.os === 'windows' ? (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
                </svg>
              ) : device.os.startsWith('macos') ? (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 4.13c.63-.77 1.06-1.84.94-2.91-.91.04-2.02.61-2.67 1.38-.58.67-1.09 1.76-.95 2.81 1.02.08 2.05-.51 2.68-1.28z"/>
                </svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
              )}
              <span>{lang === 'ar' ? device.nameAr : device.nameEn}</span>
            </a>
            <button className="ghost" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>{t.lang}</button>
          </div>
        </header>
        <section className="card">
          <h2>{t.signIn}</h2>
          <p>{t.unauthorized}</p>
          <div className="toolbar">
            <input type="password" value={token} onChange={(e) => setToken(e.target.value)} placeholder={t.token} aria-label={t.token} autoComplete="off" />
            <button onClick={signIn} disabled={!token}>{t.signIn}</button>
          </div>
          {auth === 'error' && <div className="card" role="alert">401</div>}
        </section>
      </main>
    );
  }
  return (
    <main className="wrap">
      <header className="top">
        <h1>Crewloom</h1>
        <div className="toolbar">
          <span className="live" role="status"><i className={`dot ${live ? 'on' : ''}`} />{live ? t.live : t.offline}</span>
          <a
            href={device.downloadUrl}
            download={device.os === 'windows' ? 'install.ps1' : device.os.startsWith('macos') ? 'Crewloom.dmg' : undefined}
            target={device.os === 'linux' || device.os === 'unknown' ? '_blank' : undefined}
            rel="noopener noreferrer"
            aria-label={`${t.downloadAria} - ${lang === 'ar' ? device.nameAr : device.nameEn}`}
            title={`${t.downloadAria} - ${lang === 'ar' ? device.nameAr : device.nameEn}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '8px',
              background: 'var(--accent)',
              color: '#fff',
              textDecoration: 'none',
              fontWeight: 600,
              fontSize: '13px',
            }}
          >
            {device.os === 'windows' ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
              </svg>
            ) : device.os.startsWith('macos') ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 4.13c.63-.77 1.06-1.84.94-2.91-.91.04-2.02.61-2.67 1.38-.58.67-1.09 1.76-.95 2.81 1.02.08 2.05-.51 2.68-1.28z"/>
              </svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            )}
            <span>{lang === 'ar' ? device.nameAr : device.nameEn}</span>
          </a>
          {!local && <button className="ghost" onClick={signOut}>{t.signOut}</button>}
          <button className="ghost" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>{t.lang}</button>
        </div>
      </header>
      <section
        className="card"
        aria-label={lang === 'ar' ? 'النسخة الموصى بها للجهاز' : 'Recommended device build'}
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          padding: '12px 16px',
          marginBottom: '16px',
          background: 'var(--panel)',
          border: '1px solid var(--accent)',
          borderRadius: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '20px' }}>
            {device.os === 'windows' ? '🪟' : device.os.startsWith('macos') ? '🍏' : '🐧'}
          </span>
          <div>
            <strong style={{ fontSize: '13px' }}>
              {lang === 'ar' ? 'الترشيح التلقائي عبر المتصفح للجهاز الحالي:' : 'Browser-recommended build for your device:'}
            </strong>
            <div style={{ fontSize: '12px', color: 'var(--mute)' }}>
              {lang === 'ar' ? device.nameAr : device.nameEn}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px' }}>
          <code style={{ fontSize: '11px', padding: '5px 10px', background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: '6px' }} dir="ltr">
            {device.command}
          </code>
          <a
            href={device.downloadUrl}
            download={device.os === 'windows' ? 'install.ps1' : device.os.startsWith('macos') ? 'Crewloom.dmg' : undefined}
            target={device.os === 'linux' || device.os === 'unknown' ? '_blank' : undefined}
            rel="noopener noreferrer"
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              background: 'var(--accent)',
              color: '#fff',
              textDecoration: 'none',
              fontSize: '12px',
              fontWeight: 600,
            }}
          >
            {lang === 'ar' ? 'تحميل مباشر' : 'Download Now'}
          </a>
          <a
            href="https://crewloom.org/#install"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: '12px', color: 'var(--mute)', textDecoration: 'underline' }}
          >
            {lang === 'ar' ? 'كافة الأنظمة' : 'All Platforms'}
          </a>
        </div>
      </section>
      <p>{lang === "ar" ? "المشروع الحالي" : "Current project"}: <code dir="ltr">{data?.projectRoot ?? "…"}</code></p>
      {data?.toolkitRoot && <details><summary>{lang === 'ar' ? 'مصدر تشغيل اللوحة' : 'Dashboard runtime source'}</summary>
        <code dir="ltr">{data.toolkitRoot}</code>
      </details>}
      {error && <div className="card" role="alert">API: {error}</div>}
      <ComputerUsePanel language={lang} />
      <ProjectsPanel language={lang} />
      <ActivityPanel activity={data?.activity} controls={data?.controls} language={lang} />
      <section className="tiles" aria-label="Totals">
        <div className="tile"><b>{totals.skills ?? '—'}</b><span>{t.skills}</span></div>
        <div className="tile"><b>{totals.tools ?? '—'}</b><span>{t.tools}</span></div>
        <div className={`tile ${totals.attention ? 'warn' : ''}`}><b>{totals.attention ?? '—'}</b><span>{t.attention}</span></div>
        <div className="tile"><b>{totals.openTasks ?? '—'}</b><span>{t.tasks}</span></div>
        <div className={`tile ${totals.openChallenges ? 'warn' : ''}`}><b>{totals.openChallenges ?? '—'}</b><span>{t.challenges}</span></div>
        <div className={`tile ${totals.failedRuns ? 'bad' : ''}`}><b>{totals.failedRuns ?? '—'}</b><span>{t.failed}</span></div>
      </section>
      <div className="grid">
        <div>
          <section className="card">
            <h2>{t.skills}</h2>
            <div className="toolbar">
              <input type="search" placeholder={t.search} value={query} onChange={(e) => setQuery(e.target.value)} aria-label={t.search} />
              <select value={filter} onChange={(e) => setFilter(e.target.value as typeof filter)} aria-label={t.status}>
                <option value="all">{t.all}</option><option value="healthy">healthy</option><option value="attention">attention</option><option value="idle">idle</option>
              </select>
            </div>
            <div className="scroll">
              <table>
                <thead><tr><th scope="col">{t.role}</th><th scope="col">{t.status}</th><th scope="col">{t.tasks}</th><th scope="col">{t.done}</th><th scope="col">{t.challenges}</th><th scope="col">{t.runs}</th><th scope="col">{t.activity}</th></tr></thead>
                <tbody>
                  {skills.map((s) => (
                    <tr key={s.id} className="row" tabIndex={0} onClick={() => pickSkill(s.id)} onKeyDown={(e) => e.key === 'Enter' && pickSkill(s.id)}>
                      <td><b>{s.id}</b></td>
                      <td><span className={`badge ${s.status}`}>{s.status}</span></td>
                      <td>{s.openTasks}</td><td>{s.doneEntries}</td><td>{s.openChallenges}</td>
                      <td>{s.runs}{s.failedRuns ? <span className="badge fail"> {s.failedRuns}✕</span> : null}</td>
                      <td>{ago(s.lastActivity)}</td>
                    </tr>
                  ))}
                  {!skills.length && <tr><td colSpan={7} className="empty">—</td></tr>}
                </tbody>
              </table>
            </div>
          </section>
          {detail && (
            <section className="card" aria-live="polite">
              <h2>{detail.id}</h2>
              <div className="tabs">
                {['skill', ...Object.keys(detail.brain)].map((k) => <button key={k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)}>{k}</button>)}
                <button className="ghost" aria-label="Close detail view" onClick={() => { setDetail(null); openId.current = null; }}>✕</button>
              </div>
              <pre>{tab === 'skill' ? detail.skill : detail.brain[tab]}</pre>
            </section>
          )}
        </div>
        <div>
          <section className="card">
            <h2>{t.tools}</h2>
            <div className="toolbar">
              <select value={toolId} onChange={(e) => { const tool = data?.tools.find((x) => x.id === e.target.value); setToolId(e.target.value); setArgs(tool?.example_args.replace('{input}', '') ?? ''); }} aria-label={t.tools}>
                {data?.tools.map((x) => <option key={x.id} value={x.id}>{x.id}</option>)}
              </select>
              <button onClick={runTool} disabled={busy || !toolId || data?.tools.find((tool) => tool.id === toolId)?.dashboard === 'cli'}>{t.run}</button>
            </div>
            <input style={{ width: '100%' }} value={args} onChange={(e) => setArgs(e.target.value)} placeholder={t.args} aria-label={t.args} />
            <p className="empty">{data?.tools.find((x) => x.id === toolId)?.description}</p>
            {data?.tools.find((tool) => tool.id === toolId)?.dashboard === 'cli' && <p>
              {lang === 'ar' ? 'الأداة تحتاج مدخلات مشاريع صريحة عبر CLI؛ راجع دليل الأدوات.' : 'This tool requires explicit project inputs through the CLI; see the tool guide.'}
            </p>}
            <button className="ghost" onClick={runChecks} disabled={busy}>{t.checks}</button>
            {output && <pre style={{ borderColor: output.ok ? 'var(--ok)' : 'var(--bad)' }}>{output.text || (output.ok ? 'PASS' : 'FAIL')}</pre>}
          </section>
          <section className="card">
            <h2>{t.runs}</h2>
            <ul className="feed">
              {data?.runs.map((r, i) => (
                <li key={`${r.ts}-${i}`}>
                  <span><span className={`badge ${r.exit_code === 0 ? 'healthy' : 'fail'}`}>{r.exit_code === 0 ? 'PASS' : `EXIT ${r.exit_code}`}</span> <b>{r.tool}</b></span>
                  <small>{r.source} · {r.duration_ms}ms · {ago(r.ts)}</small>
                </li>
              ))}
              {data && !data.runs.length && <li className="empty">{t.none}</li>}
            </ul>
          </section>
        </div>
      </div>
    </main>
  );
}

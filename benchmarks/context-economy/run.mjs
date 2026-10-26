#!/usr/bin/env node
// Runs read-only tasks through an agent CLI and records context and cost metrics per run.
// Usage: node run.mjs --label <name> [--only <taskId>] [--repeat 1] [--max-budget 2] [--repo <dir>] [-- <extra agent flags>]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const opts = { label: '', only: null, repeat: 1, maxBudget: '2', repo: path.resolve(here, '../../..'), extra: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--') { opts.extra = argv.slice(i + 1); break; }
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`${arg} needs a value`);
      i += 1;
      return argv[i];
    };
    if (arg === '--label') opts.label = next();
    else if (arg === '--only') opts.only = next();
    else if (arg === '--repeat') opts.repeat = Number(next());
    else if (arg === '--max-budget') opts.maxBudget = next();
    else if (arg === '--repo') opts.repo = path.resolve(next());
    else throw new Error(`Unknown argument ${arg}`);
  }
  if (!opts.label) throw new Error('--label is required');
  if (!Number.isInteger(opts.repeat) || opts.repeat < 1) throw new Error('--repeat must be a positive integer');
  return opts;
}

function runClaude(prompt, opts) {
  const args = [
    '-p', prompt, '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
    '--disallowedTools', 'Edit', 'Write', 'NotebookEdit', 'Bash',
    '--max-budget-usd', opts.maxBudget, ...opts.extra,
  ];
  return new Promise((resolve, reject) => {
    const child = spawn('claude', args, { cwd: opts.repo, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    child.stdout.on('data', (d) => { out += d; });
    child.stderr.on('data', (d) => { err += d; });
    child.on('error', reject);
    child.on('close', (code) => (code === 0 ? resolve(out) : reject(new Error(`claude exited ${code}: ${err.slice(-300)}`))));
  });
}

/** Fold a stream-json transcript into per-run metrics. One API turn is one distinct assistant message id. */
export function measure(stream) {
  const turns = new Map();
  const tools = {};
  let result = null;
  for (const line of stream.split('\n').filter(Boolean)) {
    const event = JSON.parse(line);
    if (event.type === 'assistant') {
      const { id, usage, content } = event.message;
      turns.set(id, usage ?? turns.get(id) ?? {});
      for (const block of content) if (block.type === 'tool_use') tools[block.name] = (tools[block.name] ?? 0) + 1;
    } else if (event.type === 'result') result = event;
  }
  if (!result) throw new Error('transcript has no result event');
  const usages = [...turns.values()];
  const ctx = (u) => (u.input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0) + (u.cache_read_input_tokens ?? 0);
  const sum = (key) => usages.reduce((n, u) => n + (u[key] ?? 0), 0);
  return {
    apiTurns: usages.length,
    tools,
    baseContext: usages.length ? ctx(usages[0]) : 0,
    finalContext: usages.length ? ctx(usages[usages.length - 1]) : 0,
    billed: {
      input: sum('input_tokens'),
      cacheWrite: sum('cache_creation_input_tokens'),
      cacheRead: sum('cache_read_input_tokens'),
      output: sum('output_tokens'),
    },
    costUsd: result.total_cost_usd,
    durationMs: result.duration_ms,
    isError: Boolean(result.is_error),
    answer: result.result ?? '',
  };
}

/** null means "no automatic grader": the answer needs a human read. */
export function grade(answer, mustMatch) {
  if (mustMatch === null) return null;
  return mustMatch.every((pattern) => new RegExp(pattern, 'i').test(answer));
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const tasks = JSON.parse(fs.readFileSync(path.join(here, 'tasks.json'), 'utf8'))
    .filter((task) => !opts.only || task.id === opts.only);
  if (tasks.length === 0) throw new Error(`No task matches --only ${opts.only}`);
  fs.mkdirSync(path.join(here, 'results'), { recursive: true });
  const file = path.join(here, 'results', `${opts.label}-${new Date().toISOString().replace(/[:.]/g, '-')}.jsonl`);
  for (const task of tasks) {
    for (let run = 1; run <= opts.repeat; run += 1) {
      const metrics = measure(await runClaude(task.prompt, opts));
      const record = { label: opts.label, task: task.id, kind: task.kind, run, extra: opts.extra, correct: grade(metrics.answer, task.mustMatch), ...metrics };
      fs.appendFileSync(file, `${JSON.stringify(record)}\n`);
      console.log(`${task.id} #${run}: turns=${record.apiTurns} base=${record.baseContext} final=${record.finalContext} cost=$${record.costUsd.toFixed(3)} correct=${record.correct}`);
    }
  }
  console.log(`results: ${file}`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((error) => { console.error(error.message); process.exit(1); });
}

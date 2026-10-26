#!/usr/bin/env node
// Compares two result files per task kind. Usage: node compare.mjs <baseline.jsonl> <candidate.jsonl>
import fs from 'node:fs';

const load = (file) => fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((line) => JSON.parse(line));
const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

function summarize(records) {
  const processed = (r) => r.billed.input + r.billed.cacheWrite + r.billed.cacheRead;
  const graded = records.filter((r) => r.correct !== null);
  return {
    runs: records.length,
    baseContext: median(records.map((r) => r.baseContext)),
    processedTokens: median(records.map(processed)),
    costUsd: median(records.map((r) => r.costUsd)),
    apiTurns: median(records.map((r) => r.apiTurns)),
    correct: graded.length ? `${graded.filter((r) => r.correct).length}/${graded.length}` : 'n/a',
  };
}

const [basePath, candPath] = process.argv.slice(2);
if (!basePath || !candPath) { console.error('usage: compare.mjs <baseline.jsonl> <candidate.jsonl>'); process.exit(1); }
const base = load(basePath);
const cand = load(candPath);
const delta = (a, b) => (a === 0 ? 'n/a' : `${(((b - a) / a) * 100).toFixed(0)}%`);
for (const kind of ['specific', 'vague']) {
  const a = summarize(base.filter((r) => r.kind === kind));
  const b = summarize(cand.filter((r) => r.kind === kind));
  if (a.runs === 0 || b.runs === 0) { console.log(`${kind}: missing runs (baseline ${a.runs}, candidate ${b.runs})`); continue; }
  console.log(`\n${kind} (median per run; baseline ${a.runs} runs, candidate ${b.runs} runs)`);
  for (const key of ['baseContext', 'processedTokens', 'apiTurns', 'costUsd']) {
    console.log(`  ${key.padEnd(16)} ${String(a[key]).padStart(10)} -> ${String(b[key]).padStart(10)}  ${delta(a[key], b[key])}`);
  }
  console.log(`  correct (graded)   ${a.correct} -> ${b.correct}`);
}
console.log('\nA reduction only counts if "correct" did not drop. Ungraded tasks need a manual read of the stored answers.');

import assert from 'node:assert/strict';
import test from 'node:test';
import { grade, measure } from './run.mjs';

const line = (value) => JSON.stringify(value);
const stream = [
  line({ type: 'assistant', message: { id: 'a', usage: { input_tokens: 2, cache_creation_input_tokens: 1000, cache_read_input_tokens: 0, output_tokens: 5 }, content: [{ type: 'tool_use', name: 'Grep' }] } }),
  // Same message id streamed again with final usage and a second tool call: still one API turn.
  line({ type: 'assistant', message: { id: 'a', usage: { input_tokens: 2, cache_creation_input_tokens: 1000, cache_read_input_tokens: 0, output_tokens: 9 }, content: [{ type: 'tool_use', name: 'Read' }] } }),
  line({ type: 'assistant', message: { id: 'b', usage: { input_tokens: 2, cache_creation_input_tokens: 100, cache_read_input_tokens: 1000, output_tokens: 20 }, content: [{ type: 'text', text: 'done' }] } }),
  line({ type: 'result', total_cost_usd: 0.12, duration_ms: 900, is_error: false, result: 'usage-tracker.ts 5000' }),
].join('\n');

test('measure counts one API turn per message id and sums billed tokens', () => {
  const m = measure(stream);
  assert.equal(m.apiTurns, 2);
  assert.deepEqual(m.tools, { Grep: 1, Read: 1 });
  assert.equal(m.baseContext, 1002);
  assert.equal(m.finalContext, 1102);
  assert.deepEqual(m.billed, { input: 4, cacheWrite: 1100, cacheRead: 1000, output: 29 });
  assert.equal(m.costUsd, 0.12);
});

test('measure rejects a transcript without a result instead of inventing numbers', () => {
  assert.throws(() => measure(line({ type: 'assistant', message: { id: 'a', usage: {}, content: [] } })), /no result/);
});

test('grade requires every pattern, and null means ungraded', () => {
  assert.equal(grade('usage-tracker.ts has 5000', ['usage-tracker\\.ts', '5000']), true);
  assert.equal(grade('usage-tracker.ts', ['usage-tracker\\.ts', '5000']), false);
  assert.equal(grade('anything', null), null);
});

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { aggregate } from './aggregate-plus.mjs';

const base = { mutate: ['a.ts', 'b.ts'], thresholds: { high: 80, low: 60, break: 15.3 } };
const report = (file, statuses) => ({ schemaVersion: '1', files: { [file]: {
  source: 'source', mutants: statuses.map((status, id) => ({ id: String(id), status, static: id === 0 })),
} } });
test('weighted global score includes static mutants and no-coverage mutants', () => {
  const result = aggregate(base, [report('a.ts', ['Killed']), report('b.ts', ['Survived', 'NoCoverage', 'Timeout'])]);
  assert.equal(result.summary.score, 50);
  assert.equal(result.thresholds.break, 15.3);
  assert.equal(result.files['a.ts'].mutants[0].static, true);
  assert.notEqual(result.files['a.ts'].mutants[0].id, result.files['b.ts'].mutants[0].id);
});
test('missing, empty, unexpected and unresolved shards fail closed', () => {
  assert.throws(() => aggregate(base, [report('a.ts', ['Killed'])]), /Missing/);
  assert.throws(() => aggregate(base, [report('a.ts', []), report('b.ts', ['Killed'])]), /No mutants/);
  assert.throws(() => aggregate(base, [report('c.ts', ['Killed']), report('b.ts', ['Killed'])]), /scope/);
  for (const status of ['Pending', 'Ignored']) {
    assert.throws(() => aggregate(base, [report('a.ts', [status]), report('b.ts', ['Killed'])]), /Unresolved/);
  }
});
test('resolved mutant errors use the standard Stryker denominator', () => {
  const result = aggregate(base, [report('a.ts', ['Killed', 'RuntimeError']),
    report('b.ts', ['Survived', 'CompileError'])]);
  assert.equal(result.summary.score, 50);
  assert.equal(result.summary.counts.RuntimeError, 1);
  assert.equal(result.summary.counts.CompileError, 1);
});
test('global score below the original threshold fails', () => {
  assert.throws(() => aggregate(base, [report('a.ts', ['Survived']), report('b.ts', ['NoCoverage'])]), /Mutation score/);
});
test('a survivor with zero executed tests invalidates the report', () => {
  const survivor = report('b.ts', ['Survived']);
  survivor.files['b.ts'].mutants[0].testsCompleted = 0;
  assert.throws(() => aggregate(base, [report('a.ts', ['Killed']), survivor]), /zero tests/);
  survivor.files['b.ts'].mutants[0].testsCompleted = 1;
  assert.equal(aggregate(base, [report('a.ts', ['Killed']), survivor]).summary.score, 50);
});

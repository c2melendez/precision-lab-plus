import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';

const script = new URL('./patch-vitest5-runner.mjs', import.meta.url);
function fixture(version = '10.0.0') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 's19-runner-'));
  for (const [name, packageVersion] of [['vitest', '5.0.1'], ['@stryker-mutator/vitest-runner', version]]) {
    const dir = path.join(root, 'node_modules', name);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'package.json'), JSON.stringify({ version: packageVersion, type: 'module' }));
  }
  const dir = path.join(root, 'node_modules/@stryker-mutator/vitest-runner/dist/src');
  fs.mkdirSync(dir, { recursive: true });
  for (const name of ['test-helpers.js', 'stryker-setup.js']) {
    fs.writeFileSync(path.join(dir, name), "export function collectTestName({ name, suite, }) { return name; }\n");
  }
  return { root, dir };
}
test('both helpers preserve native nested test names and patch idempotently', async () => {
  const { root, dir } = fixture();
  try {
    execFileSync(process.execPath, [script.pathname, root]);
    execFileSync(process.execPath, [script.pathname, root]);
    for (const name of ['test-helpers.js', 'stryker-setup.js']) {
      const { collectTestName } = await import(pathToFileURL(path.join(dir, name)));
      assert.equal(collectTestName({ name: 'case', fullTestName: 'suite > case' }), 'suite > case');
      assert.equal(collectTestName({ name: 'legacy' }), 'legacy');
    }
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
test('an unreviewed runner version fails without modifying its helpers', () => {
  const { root, dir } = fixture('11.0.0');
  try {
    const before = fs.readFileSync(path.join(dir, 'test-helpers.js'), 'utf8');
    assert.throws(() => execFileSync(process.execPath, [script.pathname, root], { stdio: 'pipe' }));
    assert.equal(fs.readFileSync(path.join(dir, 'test-helpers.js'), 'utf8'), before);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

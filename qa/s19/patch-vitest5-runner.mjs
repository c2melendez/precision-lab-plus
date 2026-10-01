import fs from 'node:fs';
import path from 'node:path';

// Stryker 10 reconstructs names with spaces. Vitest 5 filters fullTestName,
// whose nested-suite separator is " > ". Keep coverage IDs and filters equal.
const root = path.resolve(process.argv[2] ?? '.');
const readPackage = name => JSON.parse(fs.readFileSync(path.join(root, 'node_modules', name, 'package.json'), 'utf8'));
const vitest = readPackage('vitest');
if (Number(vitest.version.split('.')[0]) < 5) {
  console.log(`S19 runner patch unnecessary for Vitest ${vitest.version}`);
  process.exit(0);
}
const runner = readPackage('@stryker-mutator/vitest-runner');
if (runner.version !== '10.0.0') throw new Error(`Review compatibility patch for runner ${runner.version}`);
const original = 'function collectTestName({ name, suite, }) {';
const replacement = 'function collectTestName({ name, suite, fullTestName, }) {\n    if (typeof fullTestName === "string") return fullTestName;';
for (const file of ['test-helpers.js', 'stryker-setup.js']) {
  const target = path.join(root, 'node_modules/@stryker-mutator/vitest-runner/dist/src', file);
  const source = fs.readFileSync(target, 'utf8');
  if (source.includes(replacement)) continue;
  if (source.split(original).length !== 2) throw new Error(`Unexpected Stryker helper source in ${file}`);
  fs.writeFileSync(target, source.replace(original, replacement));
}
console.log(`S19 runner uses native fullTestName for Vitest ${vitest.version}`);

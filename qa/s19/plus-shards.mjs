import fs from 'node:fs';
import path from 'node:path';

const base = JSON.parse(fs.readFileSync('stryker.config.json', 'utf8'));
if (base.mutate.some(file => /[*?!:]/.test(file))) {
  throw new Error('S19 shards require an explicit list of source files');
}
const shards = base.mutate.map((file, index) => ({ id: String(index), file }));
if (process.argv[2] === 'matrix') {
  console.log(JSON.stringify({ include: shards }));
} else {
  const shard = shards.find(item => item.id === process.argv[2]);
  if (!shard) throw new Error('Unknown S19 shard');
  const config = {
    ...base,
    mutate: [shard.file],
    // Recycle the Vitest parent before hundreds of worker contexts accumulate.
    maxTestRunnerReuse: 25,
    ignoreStatic: false,
    // The complete baseline is enforced once by aggregate-plus.mjs.
    thresholds: { ...base.thresholds, break: 0 },
    jsonReporter: { fileName: `reports/mutation/${shard.id}/mutation.json` },
    htmlReporter: { fileName: `reports/mutation/${shard.id}/mutation.html` },
  };
  fs.mkdirSync(path.join('reports/mutation', shard.id), { recursive: true });
  fs.writeFileSync('stryker.shard.json', JSON.stringify(config, null, 2));
  fs.writeFileSync(`reports/mutation/${shard.id}/shard.json`, JSON.stringify(shard));
}

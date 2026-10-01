import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function aggregate(base, reports) {
  if (reports.length !== base.mutate.length) throw new Error('Missing S19 shard');
  const files = {};
  const counts = {};
  for (let index = 0; index < base.mutate.length; index++) {
    const report = reports[index];
    const expected = base.mutate[index];
    const entries = Object.entries(report.files ?? {});
    if (entries.length !== 1 || entries[0][0].replaceAll('\\', '/') !== expected) {
      throw new Error(`Incomplete or unexpected mutation scope for ${expected}`);
    }
    const [file, result] = entries[0];
    if (!result.mutants?.length) throw new Error(`No mutants reported for ${file}`);
    files[file] = { ...result, mutants: result.mutants.map(m => ({ ...m, id: `${index}:${m.id}` })) };
    for (const mutant of result.mutants) {
      // Incomplete runs and infrastructure crashes cannot count as a green gate.
      if (!['Killed', 'Timeout', 'Survived', 'NoCoverage', 'CompileError'].includes(mutant.status)) {
        throw new Error(`Unresolved mutant ${file}:${mutant.id} (${mutant.status})`);
      }
      counts[mutant.status] = (counts[mutant.status] ?? 0) + 1;
    }
  }
  const detected = (counts.Killed ?? 0) + (counts.Timeout ?? 0);
  const valid = detected + (counts.Survived ?? 0) + (counts.NoCoverage ?? 0);
  if (!valid) throw new Error('No valid mutants evaluated');
  const score = 100 * detected / valid;
  if (score < base.thresholds.break) throw new Error(`Mutation score ${score} < ${base.thresholds.break}`);
  return { schemaVersion: reports[0].schemaVersion, thresholds: base.thresholds, files,
    summary: { score, counts, sourceFiles: base.mutate.length } };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const base = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const root = process.argv[3];
  const reports = base.mutate.map((file, index) => {
    const dir = path.join(root, String(index));
    const shard = JSON.parse(fs.readFileSync(path.join(dir, 'shard.json'), 'utf8'));
    if (shard.id !== String(index) || shard.file !== file) throw new Error('Shard manifest mismatch');
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'mutation.json'), 'utf8'));
    if (report.files?.[file]?.source !== fs.readFileSync(path.join('frontend', file), 'utf8')) {
      throw new Error(`Source mismatch for ${file}`);
    }
    return report;
  });
  const report = aggregate(base, reports);
  fs.writeFileSync(path.join(root, 'mutation.json'), JSON.stringify(report, null, 2));
  console.log(`S19_PLUS_AGGREGATE ${JSON.stringify(report.summary)}`);
}

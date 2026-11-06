import { readFileSync } from "node:fs";

function fail(message, details = undefined) {
  process.stderr.write(message + "\n");
  if (details !== undefined) process.stderr.write(JSON.stringify(details, null, 2) + "\n");
  process.exit(1);
}

let audit;
let lock;
try {
  audit = JSON.parse(readFileSync("npm-audit.json", "utf8"));
  lock = JSON.parse(readFileSync("package-lock.json", "utf8"));
} catch (error) {
  fail("Cannot read the complete npm audit report or package lock.", String(error));
}

if (
  audit.auditReportVersion !== 2 ||
  !audit.metadata?.vulnerabilities ||
  !audit.metadata?.dependencies ||
  !audit.vulnerabilities ||
  typeof audit.vulnerabilities !== "object" ||
  audit.error
) {
  fail("npm audit did not produce a complete v2 report; an incomplete or failed audit cannot pass CI.");
}

const vulnerabilities = audit.vulnerabilities;
const names = Object.keys(vulnerabilities).sort();
const metadata = audit.metadata.vulnerabilities;
const total = metadata.total;

if (!Number.isInteger(total) || total < 0) {
  fail("npm audit returned an invalid vulnerability total.", metadata);
}

if (total === 0 && names.length === 0) {
  process.stdout.write("Full dependency audit: no vulnerabilities reported.\n");
  process.exit(0);
}

const expected = {
  "@rollup/plugin-node-resolve": {
    version: "16.0.3",
    severity: "low",
    node: "node_modules/@rollup/plugin-node-resolve",
    via: ["deepmerge"],
  },
  "@typescript-eslint/eslint-plugin": {
    version: "8.67.0",
    severity: "moderate",
    node: "node_modules/@typescript-eslint/eslint-plugin",
    via: ["@typescript-eslint/parser", "@typescript-eslint/type-utils", "@typescript-eslint/utils"],
  },
  "@typescript-eslint/parser": {
    version: "8.67.0",
    severity: "moderate",
    node: "node_modules/@typescript-eslint/parser",
    via: ["@typescript-eslint/typescript-estree"],
  },
  "@typescript-eslint/type-utils": {
    version: "8.67.0",
    severity: "moderate",
    node: "node_modules/@typescript-eslint/type-utils",
    via: ["@typescript-eslint/typescript-estree", "@typescript-eslint/utils"],
  },
  "@typescript-eslint/typescript-estree": {
    version: "8.67.0",
    severity: "moderate",
    node: "node_modules/@typescript-eslint/typescript-estree",
    via: ["minimatch"],
  },
  "@typescript-eslint/utils": {
    version: "8.67.0",
    severity: "moderate",
    node: "node_modules/@typescript-eslint/utils",
    via: ["@typescript-eslint/typescript-estree"],
  },
  deepmerge: {
    version: "4.3.1",
    severity: "low",
    node: "node_modules/deepmerge",
    via: [],
  },
  glob: {
    version: "11.1.0",
    severity: "moderate",
    node: "node_modules/workbox-build/node_modules/glob",
    via: ["minimatch"],
  },
  minimatch: {
    version: "10.2.6",
    severity: "moderate",
    node: "node_modules/minimatch",
    via: [],
  },
  "vite-plugin-pwa": {
    version: "1.3.0",
    severity: "moderate",
    node: "node_modules/vite-plugin-pwa",
    via: ["workbox-build"],
  },
  "workbox-build": {
    version: "7.4.1",
    severity: "moderate",
    node: "node_modules/workbox-build",
    via: ["@rollup/plugin-node-resolve", "glob"],
  },
};

const allowedAdvisories = {
  "https://github.com/advisories/GHSA-gcqx-w48m-w2h4": {
    package: "deepmerge",
    severity: "low",
    range: ">=4.2.0 <=4.3.1",
  },
  "https://github.com/advisories/GHSA-3g3m-2fjr-6pw4": {
    package: "glob",
    severity: "moderate",
    range: ">=9.0.0 <=14.0.1",
  },
  "https://github.com/advisories/GHSA-g3hv-75wg-m249": {
    package: "minimatch",
    severity: "moderate",
    range: ">=7.0.0 <11.0.1",
  },
};

const expectedNames = Object.keys(expected).sort();
const namesMatch =
  names.length === expectedNames.length &&
  names.every((name, index) => name === expectedNames[index]);

if (!namesMatch || total !== 11 || metadata.low !== 2 || metadata.moderate !== 9 ||
    metadata.high !== 0 || metadata.critical !== 0 || metadata.info !== 0) {
  fail("Unexpected dependency audit findings; the full audit remains a hard CI gate.", {
    names,
    total,
    counts: metadata,
  });
}

const foundAdvisories = new Set();

for (const [name, rule] of Object.entries(expected)) {
  const item = vulnerabilities[name];
  const lockEntry = lock.packages?.[rule.node];

  if (!item || item.severity !== rule.severity || lockEntry?.version !== rule.version || lockEntry.dev !== true) {
    fail("A reviewed package changed version, severity, lockfile location, or development/runtime classification.", {
      package: name,
      expected: rule,
      audit: item,
      lockEntry,
    });
  }

  if (!Array.isArray(item.nodes) || item.nodes.length !== 1 || item.nodes[0] !== rule.node) {
    fail("The vulnerable dependency moved to an unreviewed lockfile location.", {
      package: name,
      expectedNode: rule.node,
      actualNodes: item.nodes,
    });
  }

  const stringVia = [];
  for (const via of item.via ?? []) {
    if (typeof via === "string") {
      stringVia.push(via);
      continue;
    }
    if (!via || typeof via !== "object" || !allowedAdvisories[via.url]) {
      fail("An unreviewed advisory appeared in the full audit report.", { package: name, via });
    }
    const allowed = allowedAdvisories[via.url];
    if (allowed.package !== name || allowed.severity !== via.severity || allowed.range !== via.range) {
      fail("An allowed advisory's package, severity, or affected range changed.", { package: name, via });
    }
    foundAdvisories.add(via.url);
  }

  const expectedVia = [...rule.via].sort();
  const actualVia = stringVia.sort();
  if (
    expectedVia.length !== actualVia.length ||
    expectedVia.some((value, index) => value !== actualVia[index])
  ) {
    fail("The reviewed transitive vulnerability chain changed.", {
      package: name,
      expectedVia,
      actualVia,
    });
  }
}

const expectedAdvisories = Object.keys(allowedAdvisories).sort();
const actualAdvisories = [...foundAdvisories].sort();
if (
  actualAdvisories.length !== expectedAdvisories.length ||
  expectedAdvisories.some((value, index) => value !== actualAdvisories[index])
) {
  fail("The full audit advisory set differs from the three reviewed findings.", {
    expectedAdvisories,
    actualAdvisories,
  });
}

process.stdout.write(
  "Accepted only the three reviewed dev-tooling advisories for the exact 11-package " +
  "dependency chain and versions. The complete audit report is retained; " +
  "the production dependency audit remains a blocking step.\n",
);

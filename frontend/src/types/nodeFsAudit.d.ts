// Minimal Node fs declaration for the Vitest-only structural audit.
// Browser components do not import this module.
declare module "node:fs" {
  export function readFileSync(path: string, encoding: "utf8"): string;
}

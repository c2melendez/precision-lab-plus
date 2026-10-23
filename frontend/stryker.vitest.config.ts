import { defineConfig } from "vitest/config";

/**
 * Vitest surface used only by Stryker (S19).
 * Restricts to pure-logic unit tests so coverageAnalysis "all" stays tractable
 * and every mutant is exercised by asserts that can actually kill it.
 */
export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: [
      "src/__tests__/fractionDisplay.test.ts",
      "src/__tests__/systemSplit.test.ts",
      "src/__tests__/unitConversion.mutation.test.ts",
      "src/exhaustive-module08-units.test.ts",
    ],
  },
});

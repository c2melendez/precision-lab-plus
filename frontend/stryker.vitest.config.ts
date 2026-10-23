import { defineConfig } from "vitest/config";

/**
 * Vitest surface used only by Stryker (S19).
 * Pure-logic unit tests for the current mutate list.
 * calculusIntent remains deferred until dedicated kill rate is raised.
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

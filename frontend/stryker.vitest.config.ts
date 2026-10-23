import { defineConfig } from "vitest/config";

/**
 * Vitest surface used only by Stryker (S19).
 * Restricted to pure-logic unit tests matching the current mutate list
 * (fractionDisplay + unitConversion). systemSplit stays out of mutate until
 * its kill rate is raised; calculusIntent likewise deferred.
 */
export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: [
      "src/__tests__/fractionDisplay.test.ts",
      "src/__tests__/unitConversion.mutation.test.ts",
      "src/exhaustive-module08-units.test.ts",
    ],
  },
});

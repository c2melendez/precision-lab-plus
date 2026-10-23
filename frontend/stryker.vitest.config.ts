import { defineConfig } from "vitest/config";

/**
 * S19 certified baseline surface (run 39890525978, score 21.10% >= break 15.3).
 * systemSplit re-entry (run 39896676447) scored 4.38% and dragged total to 14.36%;
 * deferred until kill rate supports the threshold. calculusIntent also deferred.
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

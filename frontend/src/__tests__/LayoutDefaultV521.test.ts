import { beforeEach, describe, expect, it, vi } from "vitest";

describe("layout inicial V5.2.1", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("una instalación nueva inicia en split", async () => {
    const mod = await import("../store/useLayoutModeStore");
    expect(mod.useLayoutModeStore.getState().layoutMode).toBe("split");
  });

  it("respeta una preferencia guardada válida", async () => {
    localStorage.setItem("precision-lab-layout-mode", "focus");
    const mod = await import("../store/useLayoutModeStore");
    expect(mod.useLayoutModeStore.getState().layoutMode).toBe("focus");
  });
});

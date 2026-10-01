import { beforeEach, describe, expect, it, vi } from "vitest";

describe("layout inicial B7", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("una instalación nueva inicia en Balanceada", async () => {
    const mod = await import("../store/useLayoutModeStore");
    expect(mod.useLayoutModeStore.getState().layoutMode).toBe("fused");
  });

  it("conserva presets B7 vigentes y migra solo layouts retirados", async () => {
    localStorage.setItem("precision-lab-layout-mode", "focus");
    let mod = await import("../store/useLayoutModeStore");
    expect(mod.useLayoutModeStore.getState().layoutMode).toBe("focus");

    vi.resetModules();
    localStorage.setItem("precision-lab-layout-mode", "stacked");
    mod = await import("../store/useLayoutModeStore");
    expect(mod.useLayoutModeStore.getState().layoutMode).toBe("fused");
    expect(localStorage.getItem("precision-lab-layout-mode")).toBe("fused");
  });
});

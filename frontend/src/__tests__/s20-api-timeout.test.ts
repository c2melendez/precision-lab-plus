import { afterEach, describe, expect, it, vi } from "vitest";

import { callApi } from "../api/client";

describe("S20 — timeout y recuperación del cliente API", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("aborta a los 15s y una solicitud posterior vuelve a funcionar", async () => {
    vi.useFakeTimers();

    globalThis.fetch = vi.fn().mockImplementation((_url: string, init?: RequestInit) => {
      return new Promise((_resolve, reject) => {
        const signal = init?.signal;
        if (!signal) {
          reject(new Error("La solicitud S20 debe incluir AbortSignal"));
          return;
        }
        signal.addEventListener(
          "abort",
          () => reject(new DOMException("Aborted", "AbortError")),
          { once: true },
        );
      });
    });

    const pending = callApi("/evaluate", { expression: "1+1" });
    await vi.advanceTimersByTimeAsync(15_001);
    const timedOut = await pending;

    expect(timedOut.success).toBe(false);
    expect(timedOut.error_code).toBe("INTERNAL_ERROR");
    expect(timedOut.error_message).toMatch(/15s/);

    const recoveryBody = {
      success: true,
      operation: "evaluate",
      request_id: "s20-recovery",
      steps: [],
      has_detailed_steps: false,
      warnings: [],
      duration_ms: 1,
      result_approx: 15,
    };
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: () => Promise.resolve(recoveryBody),
    } as unknown as Response);

    const recovered = await callApi("/evaluate", { expression: "7+8" });
    expect(recovered).toEqual(recoveryBody);
  });
});

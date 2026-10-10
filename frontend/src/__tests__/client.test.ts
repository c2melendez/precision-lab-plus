import { afterEach, describe, expect, it, vi } from "vitest";

import { callApi, UnknownEndpointError } from "../api/client";

describe("callApi", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("sintetiza un MathResponse de error ante un fallo de red", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

    const result = await callApi("/evaluate", { expression: "1+1" });

    expect(result.success).toBe(false);
    expect(result.error_code).toBe("INTERNAL_ERROR");
    expect(result.operation).toBe("evaluate");
    expect(result.request_id).toBeTruthy();
    expect(typeof result.duration_ms).toBe("number");
  });

  it("sintetiza un MathResponse de error ante un AbortError sin timeout vencido", async () => {
    globalThis.fetch = vi.fn().mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          reject(new DOMException("Aborted", "AbortError"));
        }),
    );

    const result = await callApi("/derivative", { expression: "x**2", variable: "x", order: 1 });

    expect(result.success).toBe(false);
    expect(result.error_code).toBe("INTERNAL_ERROR");
    expect(result.operation).toBe("derivative");
    expect(result.error_message).toMatch(/fallo de red/);
  });

  it("SG28: cancelar desde el usuario aborta fetch y permite recuperar", async () => {
    const caller = new AbortController();
    globalThis.fetch = vi.fn().mockImplementation((_url: string, init: RequestInit) =>
      new Promise<Response>((_resolve, reject) => {
        (init.signal as AbortSignal).addEventListener("abort", () =>
          reject(new DOMException("Aborted", "AbortError")), { once: true });
      }));
    const pending = callApi("/evaluate", { expression: "2+3" }, { signal: caller.signal });
    caller.abort();
    const cancelled = await pending;
    expect(cancelled.success).toBe(false);
    expect(cancelled.error_message).toMatch(/cancelado por el usuario/);
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200, json: async () => ({
        success: true, operation: "evaluate", request_id: "sg28-next",
        result_text: "5", steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
      }),
    } as Response);
    const recovered = await callApi("/evaluate", { expression: "2+3" });
    expect(recovered.success).toBe(true);
  });

  it("SG28: señal previamente cancelada no hace la petición", async () => {
    const caller = new AbortController();
    caller.abort();
    globalThis.fetch = vi.fn();
    const result = await callApi("/evaluate", { expression: "2+3" }, { signal: caller.signal });
    expect(result.error_message).toMatch(/cancelado por el usuario/);
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("SG28: tras una cancelación AbortError la siguiente evaluación se recupera", async () => {
    const successfulResponse = {
      success: true,
      operation: "evaluate",
      request_id: "sg28-recovered",
      result_text: "42",
      result_latex: "42",
      steps: [],
      has_detailed_steps: false,
      warnings: [],
      duration_ms: 1,
    };
    globalThis.fetch = vi.fn()
      .mockRejectedValueOnce(new DOMException("Aborted", "AbortError"))
      .mockResolvedValueOnce({
        status: 200,
        json: () => Promise.resolve(successfulResponse),
      } as unknown as Response);

    const cancelled = await callApi("/evaluate", { expression: "1+1" });
    expect(cancelled.success).toBe(false);
    expect(cancelled.error_message).toMatch(/fallo de red/);

    const recovered = await callApi("/evaluate", { expression: "6*7" });
    expect(recovered).toEqual(successfulResponse);
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    const firstSignal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal;
    const secondSignal = (vi.mocked(globalThis.fetch).mock.calls[1][1] as RequestInit).signal;
    expect(firstSignal).toBeInstanceOf(AbortSignal);
    expect(secondSignal).toBeInstanceOf(AbortSignal);
    expect(secondSignal).not.toBe(firstSignal);
  });

  it("SG28: el timeout de 15 segundos aborta fetch y permite recuperación", async () => {
    vi.useFakeTimers();
    try {
      let aborted = false;
      const successResponse = {
        success: true,
        operation: "evaluate",
        request_id: "sg28-timeout-recovered",
        result_text: "42",
        steps: [],
        has_detailed_steps: false,
        warnings: [],
        duration_ms: 1,
      };
      globalThis.fetch = vi.fn()
        .mockImplementationOnce((_url: string, options: RequestInit) => new Promise((_resolve, reject) => {
          const signal = options.signal as AbortSignal;
          signal.addEventListener("abort", () => {
            aborted = true;
            reject(new DOMException("Aborted", "AbortError"));
          }, { once: true });
        }))
        .mockResolvedValueOnce({
          status: 200,
          json: () => Promise.resolve(successResponse),
        } as unknown as Response);

      const pending = callApi("/evaluate", { expression: "1+1" });
      await vi.advanceTimersByTimeAsync(15_000);
      const timedOut = await pending;
      expect(aborted).toBe(true);
      expect(timedOut.success).toBe(false);
      expect(timedOut.error_message).toMatch(/tiempo máximo/);
      const recovered = await callApi("/evaluate", { expression: "6*7" });
      expect(recovered).toEqual(successResponse);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: antes del umbral de 15 segundos la petición sigue activa", async () => {
    vi.useFakeTimers();
    try {
      let resolveFetch!: (value: Response) => void;
      globalThis.fetch = vi.fn().mockImplementation(
        () => new Promise<Response>((resolve) => { resolveFetch = resolve; }),
      );

      const pending = callApi("/evaluate", { expression: "1+1" });
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      await vi.advanceTimersByTimeAsync(14_999);
      expect(signal.aborted).toBe(false);

      resolveFetch({
        status: 200,
        json: () => Promise.resolve({
          success: true, operation: "evaluate", request_id: "sg28-before-limit",
          result_text: "2", steps: [], has_detailed_steps: false,
          warnings: [], duration_ms: 1,
        }),
      } as Response);
      expect((await pending).success).toBe(true);
      await vi.advanceTimersByTimeAsync(1);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: una petición completada limpia su temporizador y no se aborta después", async () => {
    vi.useFakeTimers();
    try {
      const response = {
        success: true,
        operation: "evaluate",
        request_id: "sg28-no-late-abort",
        result_text: "4",
        steps: [],
        has_detailed_steps: false,
        warnings: [],
        duration_ms: 1,
      };
      globalThis.fetch = vi.fn().mockResolvedValue({
        status: 200,
        json: () => Promise.resolve(response),
      } as unknown as Response);

      const result = await callApi("/evaluate", { expression: "2+2" });
      expect(result).toEqual(response);
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      expect(signal.aborted).toBe(false);
      await vi.advanceTimersByTimeAsync(30_000);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: solicitudes paralelas usan AbortSignal independientes", async () => {
    const response = { success: true, operation: "evaluate", request_id: "sg28-parallel", steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1 };
    globalThis.fetch = vi.fn().mockResolvedValue({ status: 200, json: () => Promise.resolve(response) } as Response);
    await Promise.all([callApi("/evaluate", { expression: "1+1" }), callApi("/evaluate", { expression: "2+2" })]);
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    const first = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal;
    const second = (vi.mocked(globalThis.fetch).mock.calls[1][1] as RequestInit).signal;
    expect(first).toBeInstanceOf(AbortSignal);
    expect(second).toBeInstanceOf(AbortSignal);
    expect(first).not.toBe(second);
  });

  it("SG28: timeout de una solicitud no cancela otra iniciada más tarde", async () => {
    vi.useFakeTimers();
    try {
      let resolveRecent!: (value: Response) => void;
      const firstFetch = vi.fn((_url: string, options: RequestInit) => new Promise<Response>((_resolve, reject) => {
        (options.signal as AbortSignal).addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")), { once: true });
      }));
      const secondFetch = vi.fn((_url: string, _options: RequestInit) => new Promise<Response>((resolve) => { resolveRecent = resolve; }));
      globalThis.fetch = vi.fn().mockImplementationOnce(firstFetch).mockImplementationOnce(secondFetch);
      const oldRequest = callApi("/evaluate", { expression: "1+1" });
      await vi.advanceTimersByTimeAsync(5_000);
      const newRequest = callApi("/evaluate", { expression: "2+2" });
      await vi.advanceTimersByTimeAsync(10_000);
      const oldResponse = await oldRequest;
      expect(oldResponse.success).toBe(false);
      const newerSignal = (vi.mocked(globalThis.fetch).mock.calls[1][1] as RequestInit).signal as AbortSignal;
      expect(newerSignal.aborted).toBe(false);
      resolveRecent({ status: 200, json: () => Promise.resolve({
        success: true, operation: "evaluate", request_id: "sg28-overlap",
        result_text: "4", steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
      }) } as Response);
      expect((await newRequest).success).toBe(true);
      await vi.advanceTimersByTimeAsync(10_000);
      expect(newerSignal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: un fallo de red libera el timeout sin aborto tardío", async () => {
    vi.useFakeTimers();
    try {
      globalThis.fetch = vi.fn().mockRejectedValue(new TypeError("Offline"));
      const response = await callApi("/evaluate", { expression: "1+1" });
      expect(response.success).toBe(false);
      expect(response.error_message).toMatch(/servidor/);
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      expect(signal.aborted).toBe(false);
      await vi.advanceTimersByTimeAsync(30_000);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: la respuesta no-JSON deja el temporizador cancelado", async () => {
    vi.useFakeTimers();
    try {
      globalThis.fetch = vi.fn().mockResolvedValue({
        status: 502,
        json: () => Promise.reject(new SyntaxError("Invalid JSON")),
      } as unknown as Response);
      const failed = await callApi("/evaluate", { expression: "2+2" });
      expect(failed.success).toBe(false);
      expect(failed.error_message).toMatch(/no-JSON/);
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      await vi.advanceTimersByTimeAsync(30_000);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: timeout sigue activo durante lectura del cuerpo JSON", async () => {
    vi.useFakeTimers();
    try {
      let bodyAborted = false;
      globalThis.fetch = vi.fn().mockImplementation((_url: string, options: RequestInit) => Promise.resolve({
        status: 200,
        json: () => new Promise((_resolve, reject) => {
          (options.signal as AbortSignal).addEventListener("abort", () => {
            bodyAborted = true;
            reject(new DOMException("Aborted", "AbortError"));
          }, { once: true });
        }),
      } as Response));
      const pending = callApi("/evaluate", { expression: "2+2" });
      await vi.advanceTimersByTimeAsync(15_000);
      const result = await pending;
      expect(bodyAborted).toBe(true);
      expect(result.success).toBe(false);
      expect(result.error_message).toMatch(/tiempo máximo/);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: lectura JSON completada antes del timeout conserva el resultado", async () => {
    vi.useFakeTimers();
    try {
      let resolveBody!: (value: unknown) => void;
      globalThis.fetch = vi.fn().mockResolvedValue({
        status: 200,
        json: () => new Promise((resolve) => { resolveBody = resolve; }),
      } as unknown as Response);
      const pending = callApi("/evaluate", { expression: "2+2" });
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      await vi.advanceTimersByTimeAsync(14_999);
      expect(signal.aborted).toBe(false);
      resolveBody({
        success: true, operation: "evaluate", request_id: "sg28-body-before-limit",
        result_text: "4", steps: [], has_detailed_steps: false, warnings: [], duration_ms: 1,
      });
      expect((await pending).success).toBe(true);
      await vi.advanceTimersByTimeAsync(1);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: JSON tardío no se acepta tras un timeout ya vencido", async () => {
    vi.useFakeTimers();
    try {
      let finishBody!: (body: unknown) => void;
      globalThis.fetch = vi.fn().mockResolvedValue({
        status: 200,
        // Adaptador no cooperativo: el Promise no escucha AbortSignal.
        json: () => new Promise((resolve) => { finishBody = resolve; }),
      } as unknown as Response);
      const pending = callApi("/evaluate", { expression: "2+2" });
      await vi.advanceTimersByTimeAsync(15_000);
      finishBody({
        success: true, operation: "evaluate", request_id: "sg28-late-json",
        result_text: "4", steps: [], has_detailed_steps: false,
        warnings: [], duration_ms: 1,
      });
      const result = await pending;
      expect(result.success).toBe(false);
      expect(result.error_message).toMatch(/tiempo máximo/);
    } finally {
      vi.useRealTimers();
    }
  });

  it("SG28: fetch tardío no convierte un timeout en éxito", async () => {
    vi.useFakeTimers();
    try {
      let resolveFetch!: (value: Response) => void;
      globalThis.fetch = vi.fn().mockImplementation(() => new Promise<Response>((resolve) => {
        resolveFetch = resolve;
      }));
      const pending = callApi("/evaluate", { expression: "2+2" });
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      await vi.advanceTimersByTimeAsync(15_000);
      expect(signal.aborted).toBe(true);
      resolveFetch({ status: 200, json: () => Promise.resolve({
        success: true, operation: "evaluate", request_id: "sg28-late-fetch",
        result_text: "4", steps: [], has_detailed_steps: false,
        warnings: [], duration_ms: 1,
      }) } as Response);
      const result = await pending;
      expect(result.success).toBe(false);
      expect(result.error_message).toMatch(/tiempo máximo/);
    } finally {
      vi.useRealTimers();
    }
  });

  it("sintetiza un MathResponse de error ante una respuesta no-JSON", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 502,
      json: () => Promise.reject(new SyntaxError("Unexpected token <")),
    } as unknown as Response);

    const result = await callApi("/evaluate", { expression: "1+1" });

    expect(result.success).toBe(false);
    expect(result.error_code).toBe("INTERNAL_ERROR");
    expect(result.error_message).toMatch(/no-JSON/);
  });

  it("SG28: respuesta JSON inválida tampoco deja un aborto tardío", async () => {
    vi.useFakeTimers();
    try {
      globalThis.fetch = vi.fn().mockResolvedValue({
        status: 200, json: () => Promise.resolve({ foo: "bar" }),
      } as unknown as Response);
      const result = await callApi("/evaluate", { expression: "1+1" });
      expect(result.success).toBe(false);
      expect(result.error_message).toMatch(/contrato MathResponse/);
      const signal = (vi.mocked(globalThis.fetch).mock.calls[0][1] as RequestInit).signal as AbortSignal;
      await vi.advanceTimersByTimeAsync(30_000);
      expect(signal.aborted).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it("sintetiza un MathResponse de error si el JSON no cumple el contrato mínimo", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: () => Promise.resolve({ foo: "bar" }),
    } as unknown as Response);

    const result = await callApi("/evaluate", { expression: "1+1" });

    expect(result.success).toBe(false);
    expect(result.error_code).toBe("INTERNAL_ERROR");
    expect(result.error_message).toMatch(/contrato MathResponse/);
  });

  it("devuelve la respuesta real cuando el backend responde correctamente", async () => {
    const realResponse = {
      success: true,
      operation: "evaluate",
      request_id: "abc-123",
      steps: [],
      has_detailed_steps: false,
      warnings: [],
      duration_ms: 5.2,
      result_approx: 2,
    };
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: () => Promise.resolve(realResponse),
    } as unknown as Response);

    const result = await callApi("/evaluate", { expression: "1+1" });

    expect(result).toEqual(realResponse);
  });

  it("lanza UnknownEndpointError para un endpoint fuera de la whitelist", async () => {
    await expect(callApi("/no-existe", {})).rejects.toBeInstanceOf(UnknownEndpointError);
  });
});

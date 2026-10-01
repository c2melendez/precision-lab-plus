import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { HistoryEntry } from "../store/useHistoryStore";

const recentStorageKey = "precision-lab-recent-keys";
const historyStorageKey = "calculadora-cientifica-history";
const key = (value: string) => ({ glyph: value, insertLatex: value, ariaLabel: value });
const input = {
  sourceModule: "scientific", operation: "integral", endpointUrl: "/integral",
  requestPayload: { expression: "x", variable: "x", lower: "0", upper: "1" },
  inputText: "\\int_0^1 x\\,dx", label: "Integral", resultLatex: "\\frac{1}{2}",
  hasDetailedSteps: true, warnings: [],
};
const persisted = { ...input, id: "saved", timestamp: 100 } satisfies HistoryEntry;
async function recent() {
  vi.resetModules();
  return (await import("../store/useRecentKeysStore")).useRecentKeysStore;
}
async function history() {
  vi.resetModules();
  return (await import("../store/useHistoryStore")).useHistoryStore;
}

beforeEach(() => localStorage.clear());
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("recent keys across reloads", () => {
  it("reloads both docks and keeps independent module histories", async () => {
    const store = await recent();
    store.getState().recordKey("scientific", key("x"), "variable");
    store.getState().recordKey("scientific", key("sin"), "operation");
    store.getState().recordKey("matrices", key("det"), "operation");
    const restored = await recent();
    expect(restored.getState().getRecents("scientific")).toEqual({ variables: [key("x")], operations: [key("sin")] });
    expect(restored.getState().getRecents("matrices")).toEqual({ variables: [], operations: [key("det")] });
    expect(restored.getState().getRecents("unknown")).toEqual({ variables: [], operations: [] });
  });

  it("trims persisted docks to seven entries without changing their order", async () => {
    const keys = Array.from({ length: 9 }, (_, i) => key(String(i)));
    localStorage.setItem(recentStorageKey, JSON.stringify({ scientific: { operations: keys, variables: keys } }));
    const store = await recent();
    expect(store.getState().getRecents("scientific")).toEqual({ operations: keys.slice(0, 7), variables: keys.slice(0, 7) });
  });

  it.each(["{broken", "null", "7", '"text"'])("recovers from invalid storage %s", async raw => {
    localStorage.setItem(recentStorageKey, raw);
    expect((await recent()).getState().recentByMode).toEqual({});
  });

  it.each([
    null, 1, { operations: null, variables: [] }, { operations: [], variables: {} },
    { operations: [null], variables: [] }, { operations: ["x"], variables: [] },
    { operations: [{ glyph: "x", ariaLabel: "x" }], variables: [] },
    { operations: [{ glyph: "x", insertLatex: "x" }], variables: [] },
    { operations: [{ insertLatex: "x", ariaLabel: "x" }], variables: [] },
    { operations: [], variables: [{ glyph: "x", insertLatex: 1, ariaLabel: "x" }] },
    { operations: [], variables: [{ glyph: "x", insertLatex: "x", ariaLabel: 1 }] },
  ])("discards malformed mode entries but preserves valid ones: %j", async invalid => {
    localStorage.setItem(recentStorageKey, JSON.stringify({ invalid, valid: { operations: [key("sin")], variables: [] } }));
    expect((await recent()).getState().recentByMode).toEqual({ valid: { operations: [key("sin")], variables: [] } });
  });

  it("promotes a variable by insertion identity and persists the new label", async () => {
    const store = await recent();
    for (let i = 0; i < 9; i++) store.getState().recordKey("scientific", key(String(i)), "variable");
    const updated = { ...key("4"), ariaLabel: "updated" };
    store.getState().recordKey("scientific", updated, "variable");
    expect((await recent()).getState().getRecents("scientific")).toEqual({
      operations: [], variables: [updated, ...[8, 7, 6, 5, 3, 2].map(i => key(String(i)))],
    });
  });

  it("keeps session state when reads or writes are denied", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("denied"); });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("quota"); });
    const store = await recent();
    expect(store.getState().recentByMode).toEqual({});
    store.getState().recordKey("scientific", key("x"), "variable");
    expect(store.getState().getRecents("scientific").variables).toEqual([key("x")]);
  });

  it("starts safely without browser storage", async () => {
    vi.stubGlobal("localStorage", undefined);
    expect((await recent()).getState().recentByMode).toEqual({});
  });
});

describe("history across reloads and reuse", () => {
  it("preserves the natural integral input, request and result across reloads", async () => {
    const store = await history();
    store.getState().addEntry(input);
    const entry = store.getState().entries[0];
    expect(entry).toMatchObject(input);
    expect(entry.id).toEqual(expect.any(String));
    expect(entry.id.length).toBeGreaterThan(0);
    expect(entry.timestamp).toBeGreaterThan(0);
    const restored = await history();
    expect(restored.getState().entries).toEqual([entry]);
    expect(restored.getState().reuseEntry(entry.id)).toEqual(entry);
    expect(restored.getState().reuseEntry("missing")).toBeNull();
  });

  it("keeps only the fifty newest entries, in order, with distinct ids", async () => {
    const store = await history();
    for (let i = 0; i < 52; i++) store.getState().addEntry({ ...input, label: String(i) });
    const entries = (await history()).getState().entries;
    expect(entries.map(entry => entry.label)).toEqual(Array.from({ length: 50 }, (_, i) => String(51 - i)));
    expect(new Set(entries.map(entry => entry.id)).size).toBe(50);
  });

  it("clears memory and persisted history", async () => {
    const store = await history();
    store.getState().addEntry(input);
    store.getState().clearHistory();
    expect(store.getState().entries).toEqual([]);
    expect(JSON.parse(localStorage.getItem(historyStorageKey)!)).toEqual({ schemaVersion: 1, entries: [] });
    expect((await history()).getState().entries).toEqual([]);
  });

  it.each(["{broken", "null", '{}', '{"schemaVersion":2,"entries":[]}', '{"schemaVersion":1,"entries":{}}'])
  ("safely discards invalid or incompatible storage %s", async raw => {
    localStorage.setItem(historyStorageKey, raw);
    expect((await history()).getState().entries).toEqual([]);
  });

  it("rejects reuse through an unrecognized endpoint", async () => {
    localStorage.setItem(historyStorageKey, JSON.stringify({ schemaVersion: 1, entries: [{ ...persisted, endpointUrl: "https://example.com/steal" }] }));
    expect((await history()).getState().reuseEntry("saved")).toBeNull();
  });

  it("keeps adding and clearing when storage is unavailable", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("denied"); });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("quota"); });
    const store = await history();
    expect(store.getState().entries).toEqual([]);
    store.getState().addEntry(input);
    expect(store.getState().entries).toHaveLength(1);
    store.getState().clearHistory();
    expect(store.getState().entries).toEqual([]);
  });

  it("uses distinct fallback ids when randomUUID is unavailable", async () => {
    vi.stubGlobal("crypto", {});
    const store = await history();
    store.getState().addEntry(input);
    store.getState().addEntry(input);
    const [a, b] = store.getState().entries;
    expect(a.id).toMatch(/^entry-\d+-[a-z0-9]+$/);
    expect(a.id).not.toBe(b.id);
  });

  it("starts safely outside the browser", async () => {
    vi.stubGlobal("window", undefined);
    expect((await history()).getState().entries).toEqual([]);
  });
});

/**
 * src/api/submitWithHistory.ts — envuelve `callApi` registrando cada
 * intento en `useHistoryStore` (spec, sección 11: History conectado,
 * `reuseEntry` valida `endpointUrl` contra `KNOWN_ENDPOINTS` antes de
 * reejecutar — la validación vive en el propio store, esto solo alimenta
 * las entradas).
 */

import { useHistoryStore } from "../store/useHistoryStore";
import { callApi, type MathResponse } from "./client";
import type { KnownEndpoint } from "./endpoints";

function inferSourceModule(endpoint: KnownEndpoint): string {
  if (endpoint.startsWith("/matrix/")) return "Matrices";
  if (endpoint.startsWith("/statistics/")) return "Estadística";
  if (endpoint.startsWith("/graph/")) return "Gráficas";
  if (endpoint.startsWith("/geometry/")) return "Geometría";
  if (endpoint.startsWith("/units/")) return "Unidades";
  return "Científica";
}

export async function submitAndRecord(
  endpoint: KnownEndpoint,
  payload: Record<string, unknown>,
  label: string,
  sourceModule?: string,
  historyInputText?: string,
): Promise<MathResponse> {
  const result = await callApi(endpoint, payload);

  useHistoryStore.getState().addEntry({
    sourceModule: sourceModule ?? inferSourceModule(endpoint),
    operation: result.operation,
    endpointUrl: endpoint,
    requestPayload: payload,
    // requestPayload conserva la sintaxis del backend; inputText conserva
    // la expresión visual original cuando el llamador la conoce. No deben
    // mezclarse: Historial/Reusar necesitan la segunda para reconstruir
    // exactamente lo que el usuario escribió en MathLive.
    inputText: historyInputText ?? label,
    label,
    resultLatex: result.success ? (result.result_latex ?? undefined) : undefined,
    resultText: result.success ? (result.result_text ?? undefined) : undefined,
    resultApprox: result.success && result.result_approx != null ? String(result.result_approx) : undefined,
    resultType: result.success ? (result.result_type ?? undefined) : undefined,
    resultData: result.success ? (result.result_data ?? undefined) : undefined,
    hasDetailedSteps: result.has_detailed_steps,
    warnings: result.warnings,
  });

  return result;
}

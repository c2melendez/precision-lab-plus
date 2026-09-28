import type { components } from "../types/api";

type GraphData = components["schemas"]["GraphData"];

const WIDTH = 320;
const HEIGHT = 120;
const PAD = 12;

/** Curvas SVG compactas a partir de los puntos ya calculados por el motor. */
export function graphPreviewGeometry(data: GraphData): {
  paths: string[];
  zeroX: number | null;
  zeroY: number | null;
} | null {
  const [xMin, xMax] = data.x_range;
  const [yMin, yMax] = data.y_range ?? [];
  if (![xMin, xMax, yMin, yMax].every((value) => Number.isFinite(value)) || xMax <= xMin || yMax <= yMin) {
    return null;
  }

  const xPixel = (x: number) => PAD + ((x - xMin) / (xMax - xMin)) * (WIDTH - 2 * PAD);
  const yPixel = (y: number) => HEIGHT - PAD - ((y - yMin) / (yMax - yMin)) * (HEIGHT - 2 * PAD);
  const paths = data.traces.filter((trace) => trace.type === "line").map((trace) => {
    let connected = false;
    return trace.x.map((x, index) => {
      const y = trace.y[index];
      if (!Number.isFinite(x) || y == null || !Number.isFinite(y)) {
        connected = false;
        return "";
      }
      const command = connected ? "L" : "M";
      connected = true;
      return `${command}${xPixel(x).toFixed(2)} ${yPixel(y).toFixed(2)}`;
    }).filter(Boolean).join(" ");
  }).filter(Boolean);

  if (paths.length === 0) return null;
  return {
    paths,
    zeroX: xMin <= 0 && xMax >= 0 ? xPixel(0) : null,
    zeroY: yMin <= 0 && yMax >= 0 ? yPixel(0) : null,
  };
}

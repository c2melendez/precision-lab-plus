import type { components } from "../types/api";

type GraphData = components["schemas"]["GraphData"];

const WIDTH = 320;
const HEIGHT = 120;
const PAD = 12;

/** Curvas SVG compactas a partir de los puntos ya calculados por el motor. */
export function graphPreviewGeometry(data: GraphData, includeZero = false): {
  paths: string[];
  zeroX: number | null;
  zeroY: number | null;
  projectX: (x: number) => number;
  projectY: (y: number) => number;
} | null {
  const [xMin, xMax] = data.x_range;
  const [rawYMin, rawYMax] = data.y_range ?? [];
  const yMin = includeZero ? Math.min(rawYMin, 0) : rawYMin;
  const yMax = includeZero ? Math.max(rawYMax, 0) : rawYMax;
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
    projectX: xPixel,
    projectY: yPixel,
  };
}

/** Área con signo: cada tramo se recorta a los límites y se parte en sus cruces por cero. */
export function integralRegionGeometry(
  data: GraphData,
  lower: number,
  upper: number,
  geometry: NonNullable<ReturnType<typeof graphPreviewGeometry>>,
): { positivePath: string; negativePath: string; lowerX: number; upperX: number } | null {
  const trace = data.traces.find((item) => item.type === "line");
  if (!trace || !Number.isFinite(lower) || !Number.isFinite(upper)) return null;
  const start = Math.max(Math.min(lower, upper), data.x_range[0]);
  const end = Math.min(Math.max(lower, upper), data.x_range[1]);
  if (end < start || geometry.zeroY === null) return null;
  const positive: string[] = [];
  const negative: string[] = [];
  const orientation = upper >= lower ? 1 : -1;
  const baseline = geometry.zeroY.toFixed(2);

  for (let index = 1; index < trace.x.length; index++) {
    const x0 = trace.x[index - 1], x1 = trace.x[index];
    const y0 = trace.y[index - 1], y1 = trace.y[index];
    if (!Number.isFinite(x0) || !Number.isFinite(x1) || y0 == null || y1 == null
      || !Number.isFinite(y0) || !Number.isFinite(y1) || x1 <= x0) continue;
    const left = Math.max(start, x0), right = Math.min(end, x1);
    if (left >= right) continue;
    const valueAt = (x: number) => y0 + ((x - x0) / (x1 - x0)) * (y1 - y0);
    const leftY = valueAt(left), rightY = valueAt(right);
    const crossing = leftY * rightY < 0 ? left + (right - left) * -leftY / (rightY - leftY) : null;
    const knots = crossing === null ? [left, right] : [left, crossing, right];
    for (let part = 1; part < knots.length; part++) {
      const a = knots[part - 1], b = knots[part];
      const ya = valueAt(a), yb = valueAt(b);
      if (ya === 0 && yb === 0) continue;
      const ax = geometry.projectX(a).toFixed(2), bx = geometry.projectX(b).toFixed(2);
      const path = `M${ax} ${baseline} L${ax} ${geometry.projectY(ya).toFixed(2)} L${bx} ${geometry.projectY(yb).toFixed(2)} L${bx} ${baseline} Z`;
      (orientation * (ya + yb) >= 0 ? positive : negative).push(path);
    }
  }
  return { positivePath: positive.join(" "), negativePath: negative.join(" "),
    lowerX: geometry.projectX(lower), upperX: geometry.projectX(upper) };
}

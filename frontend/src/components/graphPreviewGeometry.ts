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
export function integralRegionSegments(data: GraphData, lower: number, upper: number): {
  positive: Array<[number, number, number, number]>;
  negative: Array<[number, number, number, number]>;
} {
  const positive: Array<[number, number, number, number]> = [];
  const negative: Array<[number, number, number, number]> = [];
  const trace = data.traces.find((item) => item.type === "line");
  if (!trace || !Number.isFinite(lower) || !Number.isFinite(upper)) return { positive, negative };
  const start = Math.max(Math.min(lower, upper), data.x_range[0]);
  const end = Math.min(Math.max(lower, upper), data.x_range[1]);
  const orientation = upper >= lower ? 1 : -1;
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
      (orientation * (ya + yb) >= 0 ? positive : negative).push([a, ya, b, yb]);
    }
  }
  return { positive, negative };
}

export function integralRegionGeometry(
  data: GraphData,
  lower: number,
  upper: number,
  geometry: NonNullable<ReturnType<typeof graphPreviewGeometry>>,
): { positivePath: string; negativePath: string; lowerX: number; upperX: number } | null {
  if (!Number.isFinite(lower) || !Number.isFinite(upper) || geometry.zeroY === null) return null;
  const segments = integralRegionSegments(data, lower, upper);
  const baseline = geometry.zeroY.toFixed(2);
  const draw = ([a, ya, b, yb]: [number, number, number, number]) => {
      const ax = geometry.projectX(a).toFixed(2), bx = geometry.projectX(b).toFixed(2);
      return `M${ax} ${baseline} L${ax} ${geometry.projectY(ya).toFixed(2)} L${bx} ${geometry.projectY(yb).toFixed(2)} L${bx} ${baseline} Z`;
  };
  return { positivePath: segments.positive.map(draw).join(" "), negativePath: segments.negative.map(draw).join(" "),
    lowerX: geometry.projectX(lower), upperX: geometry.projectX(upper) };
}

/** Resalta únicamente las muestras que se acercan al punto desde cada lado. */
export function limitApproachGeometry(
  data: GraphData,
  point: string,
  direction: "both" | "left" | "right",
  geometry: NonNullable<ReturnType<typeof graphPreviewGeometry>>,
): { leftPath: string; rightPath: string; pointX: number | null } {
  const trace = data.traces.find((item) => item.type === "line");
  const [xMin, xMax] = data.x_range;
  const finite = point !== "oo" && point !== "-oo" && Number.isFinite(Number(point));
  const target = Number(point);
  const radius = (xMax - xMin) * 0.35;
  const draw = (side: "left" | "right") => {
    if (!trace || (direction !== "both" && direction !== side)) return "";
    let connected = false;
    return trace.x.map((x, index) => {
      const y = trace.y[index];
      const selected = finite
        ? side === "left" ? x < target && x >= target - radius : x > target && x <= target + radius
        : point === "oo" ? side === "right" && x >= xMax - radius
          : side === "left" && x <= xMin + radius;
      if (!selected || !Number.isFinite(x) || y == null || !Number.isFinite(y)) {
        connected = false;
        return "";
      }
      const command = connected ? "L" : "M";
      connected = true;
      return `${command}${geometry.projectX(x).toFixed(2)} ${geometry.projectY(y).toFixed(2)}`;
    }).filter(Boolean).join(" ");
  };
  return { leftPath: draw("left"), rightPath: draw("right"),
    pointX: finite && target >= xMin && target <= xMax ? geometry.projectX(target) : null };
}

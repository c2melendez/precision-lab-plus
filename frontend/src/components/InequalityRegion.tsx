import type { components } from "../types/api";

type Boundary = components["schemas"]["InequalityBoundary"];

export function InequalityRegion({ boundaries, polygon, viewport, kind }: {
  boundaries: Boundary[]; polygon: number[][]; viewport: number[]; kind: string;
}) {
  const [xMin, xMax, yMin, yMax] = viewport;
  const px = (x: number) => 12 + (x - xMin) / (xMax - xMin) * 296;
  const py = (y: number) => 148 - (y - yMin) / (yMax - yMin) * 136;
  const atFrame = ([x, y]: number[]) => Math.abs(x - xMin) < 1e-7 || Math.abs(x - xMax) < 1e-7
    || Math.abs(y - yMin) < 1e-7 || Math.abs(y - yMax) < 1e-7;
  const included = ([x, y]: number[]) => boundaries.every(({ a, b, c, operator }) => {
    const delta = a * x + b * y - c;
    return operator === "<" ? delta < -1e-7 : operator === ">" ? delta > 1e-7
      : operator === "<=" ? delta <= 1e-7 : delta >= -1e-7;
  });
  const clip = ({ a, b, c }: Boundary): number[][] => {
    const candidates = [
      ...(b !== 0 ? [[xMin, (c - a * xMin) / b], [xMax, (c - a * xMax) / b]] : []),
      ...(a !== 0 ? [[(c - b * yMin) / a, yMin], [(c - b * yMax) / a, yMax]] : []),
    ].filter(([x, y]) => x >= xMin - 1e-7 && x <= xMax + 1e-7
      && y >= yMin - 1e-7 && y <= yMax + 1e-7);
    const unique = candidates.filter(([x, y], i) => !candidates.slice(0, i)
      .some(([u, v]) => Math.abs(x - u) + Math.abs(y - v) < 1e-7));
    return unique.slice(0, 2);
  };
  return <div data-testid="inequality-region" role="img"
    aria-label={`Región ${kind === "empty" ? "vacía" : kind === "bounded" ? "acotada" : "no acotada"}; fronteras discontinuas excluidas y continuas incluidas`}
    className="w-full max-w-xl rounded-lg border border-paper-line bg-paper/50 p-2">
    <svg viewBox="0 0 320 160" className="h-40 w-full" aria-hidden="true">
      {xMin <= 0 && xMax >= 0 && <line x1={px(0)} x2={px(0)} y1="8" y2="152" stroke="currentColor" opacity="0.2" />}
      {yMin <= 0 && yMax >= 0 && <line x1="8" x2="312" y1={py(0)} y2={py(0)} stroke="currentColor" opacity="0.2" />}
      {polygon.length >= 3 && <polygon data-testid="feasible-region"
        points={polygon.map(([x, y]) => `${px(x)},${py(y)}`).join(" ")}
        fill="#2862b8" fillOpacity="0.24" />}
      {boundaries.map((boundary, index) => {
        const segment = clip(boundary);
        return segment.length === 2 ? <line key={index} data-testid="inequality-boundary"
          x1={px(segment[0][0])} y1={py(segment[0][1])}
          x2={px(segment[1][0])} y2={py(segment[1][1])}
          stroke={["#2862b8", "#b65d20", "#16865d"][index % 3]}
          strokeWidth="2.5" strokeDasharray={boundary.operator.length === 1 ? "6 5" : undefined} /> : null;
      })}
      {kind !== "empty" && polygon.length === 2 && <line data-testid="feasible-line"
        x1={px(polygon[0][0])} y1={py(polygon[0][1])}
        x2={px(polygon[1][0])} y2={py(polygon[1][1])}
        stroke="#174a9c" strokeWidth="5" />}
      {kind !== "empty" && polygon.length <= 2 && polygon.map((point, index) =>
        atFrame(point) ? <circle key={index} data-testid="feasible-continuation"
          cx={px(point[0])} cy={py(point[1])} r="4" fill="#174a9c" />
          : <circle key={index} data-testid="feasible-endpoint"
            cx={px(point[0])} cy={py(point[1])} r="5" stroke="#174a9c" strokeWidth="2"
            fill={included(point) ? "#174a9c" : "white"} />)}
      {kind === "empty" && <text x="160" y="83" textAnchor="middle" fill="currentColor" fontSize="13">Región vacía ∅</text>}
    </svg>
  </div>;
}

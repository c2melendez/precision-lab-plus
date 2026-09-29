import type { components } from "../types/api";

type Point = components["schemas"]["ComplexGraphPoint"];
type GraphData = components["schemas"]["GraphData"];

export function argandGraphData(points: Point[]): GraphData {
  const bound = Math.max(1, ...points.flatMap(({ re, im }) => [Math.abs(re), Math.abs(im)])) * 1.4;
  return {
    traces: points.map(({ re, im, label }) => ({ type: "point", name: label, x: [re], y: [im] })),
    x_range: [-bound, bound], y_range: [-bound, bound],
    x_axis_label: "Re", y_axis_label: "Im", points_truncated: false,
  };
}

export function ArgandPlane({ points }: { points: Point[] }) {
  const data = argandGraphData(points);
  const bound = data.x_range[1];
  const px = (re: number) => 160 + re / bound * 135;
  const py = (im: number) => 80 - im / bound * 65;
  return <div data-testid="complex-argand" role="img"
    aria-label={`Plano de Argand con ${points.length} ${points.length === 1 ? "punto" : "puntos"}; ejes Re e Im`}
    className="w-full max-w-xl rounded-lg border border-paper-line bg-paper/50 p-2">
    <svg viewBox="0 0 320 160" className="h-40 w-full" aria-hidden="true">
      <line x1="12" x2="308" y1="80" y2="80" stroke="currentColor" opacity="0.35" />
      <line x1="160" x2="160" y1="8" y2="152" stroke="currentColor" opacity="0.35" />
      <text x="291" y="75" fill="currentColor" fontSize="11">Re</text>
      <text x="165" y="19" fill="currentColor" fontSize="11">Im</text>
      {points.map(({ re, im, label }, index) => <g key={index}>
        <circle data-testid="complex-point" cx={px(re)} cy={py(im)} r="5"
          fill={["#2862b8", "#b65d20", "#16865d"][index % 3]} stroke="white" strokeWidth="1.5" />
        <text x={px(re) + 7} y={py(im) - 7} fill="currentColor" fontSize="10">{label}</text>
      </g>)}
    </svg>
  </div>;
}

import type { MathResponse } from "../api/client";

type Circle = NonNullable<MathResponse["inequality_circle"]>;

export function CircleInequality({ circle }: { circle: Circle }) {
  const xAxis = 160 - circle.center_x / circle.radius * 54;
  const yAxis = 80 + circle.center_y / circle.radius * 54;
  return <div data-testid="circle-inequality" role="img"
    aria-label={`${circle.inside ? "Interior" : "Exterior"} del círculo con centro (${circle.center_x_exact}, ${circle.center_y_exact}) y radio ${circle.radius_exact}; frontera ${circle.boundary_included ? "incluida" : "excluida"}`}
    className="w-full max-w-xl rounded-lg border border-paper-line bg-paper/50 p-2">
    <svg viewBox="0 0 320 160" className="h-40 w-full" aria-hidden="true">
      {xAxis >= 8 && xAxis <= 312 && <line x1={xAxis} x2={xAxis} y1="8" y2="152" stroke="currentColor" opacity="0.2" />}
      {yAxis >= 8 && yAxis <= 152 && <line x1="8" x2="312" y1={yAxis} y2={yAxis} stroke="currentColor" opacity="0.2" />}
      {circle.inside ? <circle data-testid="circle-interior-region" cx="160" cy="80" r="54" fill="#2862b8" fillOpacity="0.24" />
        : <path data-testid="circle-exterior-region" fill="#2862b8" fillOpacity="0.24" fillRule="evenodd"
          d="M 8 8 H 312 V 152 H 8 Z M 214 80 A 54 54 0 1 0 106 80 A 54 54 0 1 0 214 80 Z" />}
      <circle data-testid="circle-boundary" cx="160" cy="80" r="54" fill="none" stroke="#2862b8"
        strokeWidth="2.5" strokeDasharray={circle.boundary_included ? undefined : "6 5"} />
      <circle cx="160" cy="80" r="2" fill="currentColor" opacity="0.5" />
    </svg>
  </div>;
}

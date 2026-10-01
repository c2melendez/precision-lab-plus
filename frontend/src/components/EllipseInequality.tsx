import type { MathResponse } from "../api/client";

type Ellipse = NonNullable<MathResponse["inequality_ellipse"]>;

export function EllipseInequality({ ellipse }: { ellipse: Ellipse }) {
  const scale = Math.min(78 / ellipse.radius_x, 54 / ellipse.radius_y);
  const rx = ellipse.radius_x * scale;
  const ry = ellipse.radius_y * scale;
  const xAxis = 160 - ellipse.center_x * scale;
  const yAxis = 80 + ellipse.center_y * scale;
  return <div data-testid="ellipse-inequality" role="img"
    aria-label={`${ellipse.inside ? "Interior" : "Exterior"} de la elipse con centro (${ellipse.center_x_exact}, ${ellipse.center_y_exact}), radios ${ellipse.radius_x_exact} y ${ellipse.radius_y_exact}; frontera ${ellipse.boundary_included ? "incluida" : "excluida"}`}
    className="w-full max-w-xl rounded-lg border border-paper-line bg-paper/50 p-2">
    <svg viewBox="0 0 320 160" className="h-40 w-full" aria-hidden="true">
      {xAxis >= 8 && xAxis <= 312 && <line x1={xAxis} x2={xAxis} y1="8" y2="152" stroke="currentColor" opacity="0.2" />}
      {yAxis >= 8 && yAxis <= 152 && <line x1="8" x2="312" y1={yAxis} y2={yAxis} stroke="currentColor" opacity="0.2" />}
      {ellipse.inside ? <ellipse data-testid="ellipse-interior-region" cx="160" cy="80" rx={rx} ry={ry} fill="#2862b8" fillOpacity="0.24" />
        : <path data-testid="ellipse-exterior-region" fill="#2862b8" fillOpacity="0.24" fillRule="evenodd"
          d={`M 8 8 H 312 V 152 H 8 Z M ${160 + rx} 80 A ${rx} ${ry} 0 1 0 ${160 - rx} 80 A ${rx} ${ry} 0 1 0 ${160 + rx} 80 Z`} />}
      <ellipse data-testid="ellipse-boundary" cx="160" cy="80" rx={rx} ry={ry} fill="none" stroke="#2862b8"
        strokeWidth="2.5" strokeDasharray={ellipse.boundary_included ? undefined : "6 5"} />
      <circle cx="160" cy="80" r="2" fill="currentColor" opacity="0.5" />
    </svg>
  </div>;
}

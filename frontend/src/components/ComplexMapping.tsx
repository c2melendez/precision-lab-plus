import type { components } from "../types/api";
import { ArgandPlane } from "./ArgandPlane";

type Sample = components["schemas"]["ComplexGraphSample"];

export function ComplexMapping({ samples, detailed = false }: { samples: Sample[]; detailed?: boolean }) {
  return <div data-testid="complex-mapping" className="w-full max-w-3xl space-y-3">
    <div className="grid gap-3 sm:grid-cols-2">
      <div>
        <p className="mb-1 text-xs font-medium">Dominio · z</p>
        <ArgandPlane points={samples.map((sample) => sample.source)} />
      </div>
      <div>
        <p className="mb-1 text-xs font-medium">Imagen · f(z)</p>
        <ArgandPlane points={samples.map((sample) => sample.target)} />
      </div>
    </div>
    <p className="text-xs text-muted">Muestras puntuales del mapeo complejo; cada color une una entrada con su imagen. Las escalas de ambos planos son independientes.</p>
    {detailed && <ul className="grid gap-1 text-sm sm:grid-cols-2">
      {samples.map((sample) => <li key={sample.source.label}>
        f({sample.source.label}) = {sample.target.re} {sample.target.im < 0 ? "−" : "+"} {Math.abs(sample.target.im)}i
      </li>)}
    </ul>}
  </div>;
}

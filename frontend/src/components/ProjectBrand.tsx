export function ProjectBrand() {
  return (
    <div className="flex min-w-0 items-center gap-2.5" aria-label="Precision Lab Plus">
      <span
        aria-hidden="true"
        className="relative grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-marker/40 bg-marker-soft text-sm font-bold tracking-tight text-marker-text"
      >
        PL
        <span className="absolute -bottom-1 -right-1 grid h-4 w-4 place-items-center rounded-full bg-marker text-[10px] font-bold text-white">+</span>
      </span>
      <span className="min-w-0 truncate text-lg font-semibold text-ink">
        Precision Lab <span className="text-marker-text">Plus</span>
      </span>
    </div>
  );
}

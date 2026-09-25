export function ProjectBrand() {
  const brandIcon = `${import.meta.env.BASE_URL}precision-lab-plus.svg`;
  return (
    <div className="flex min-w-0 items-center gap-2.5" aria-label="Precision Lab Plus">
      <img
        src={brandIcon}
        alt=""
        aria-hidden="true"
        className="h-10 w-10 shrink-0 rounded-xl shadow-sm"
      />
      <h1 className="min-w-0 truncate text-lg font-semibold text-ink">
        Precision Lab <span className="text-marker-text">Plus</span>
      </h1>
    </div>
  );
}

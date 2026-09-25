interface ProjectBrandProps {
  showName?: boolean;
}

export function ProjectBrand({ showName = true }: ProjectBrandProps) {
  const brandIcon = new URL("precision-lab-plus.svg", document.baseURI).toString();
  return (
    <div className="flex min-w-0 flex-col items-start gap-1.5" aria-label="Precision Lab Plus">
      <img
        src={brandIcon}
        alt=""
        aria-hidden="true"
        className="h-10 w-10 shrink-0 rounded-xl shadow-sm"
      />
      {showName && (
        <h1 className="hidden whitespace-nowrap text-[15px] font-semibold leading-tight text-white md:block">
          Precision Lab <span className="text-sky-300">Plus</span>
        </h1>
      )}
    </div>
  );
}

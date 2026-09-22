import { useEffect, useRef, type ReactNode } from "react";

// P2 (spec v2 §3): drawer unificado de Historial. Mismo componente
// conceptual que HistoryDrawer.tsx de Precision Lab Lite, adaptado a los
// tokens de fondo claro de este repo (bg-paper/border-paper-line en vez
// de bg-chrome/border-chrome-soft). No reescribe History.tsx — solo lo
// envuelve vía `children`.

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export function HistoryDrawer({ isOpen, onClose, children }: HistoryDrawerProps) {
  const drawerRef = useRef<HTMLElement | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    previousFocusRef.current = document.activeElement as HTMLElement | null;

    const closeButton = drawerRef.current?.querySelector<HTMLElement>("[data-history-close]");
    if (window.matchMedia("(max-width: 1023px)").matches) {
      requestAnimationFrame(() => closeButton?.focus());
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      event.preventDefault();
      onClose();
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      requestAnimationFrame(() => previousFocusRef.current?.focus());
    };
  }, [isOpen]);

  return (
    <>
      {isOpen && (
        <div
          onClick={onClose}
          aria-hidden="true"
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
        />
      )}

      <aside
        id="history-panel"
        aria-label="Historial de operaciones"
        className={
          isOpen
            ? "fixed inset-0 z-50 flex flex-col bg-paper md:inset-y-0 md:left-auto md:right-0 md:w-[78%] lg:static lg:inset-auto lg:z-auto lg:w-[260px] lg:shrink-0 lg:border-l lg:border-paper-line dt:w-[280px]"
            : "hidden lg:block lg:w-0 lg:shrink-0 lg:overflow-hidden lg:transition-[width] lg:duration-200"
        }
      >
        <div className="flex items-center justify-between border-b border-paper-line p-3 lg:hidden">
          <span className="text-sm font-medium text-ink">Historial</span>
          <button
            type="button"
            data-history-close
            onClick={onClose}
            aria-label="Cerrar historial"
            className="rounded p-1 text-muted hover:text-ink"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 lg:w-[260px] dt:w-[280px]">{children}</div>
      </aside>
    </>
  );
}

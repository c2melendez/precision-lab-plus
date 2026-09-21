import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../components/BasicMode", () => ({ BasicMode: () => <div>Basic mode</div> }));
vi.mock("../components/SimpleBasicMode", () => ({ SimpleBasicMode: () => null }));
vi.mock("../components/DerivativeMode", () => ({ DerivativeMode: () => null }));
vi.mock("../components/EquationMode", () => ({ EquationMode: () => null }));
vi.mock("../components/GraphMode", () => ({ GraphMode: () => null }));
vi.mock("../components/History", () => ({ History: () => null }));
vi.mock("../components/HistoryDrawer", () => ({ HistoryDrawer: ({ children }: { children: React.ReactNode }) => <>{children}</> }));
vi.mock("../components/IntegralMode", () => ({ IntegralMode: () => null }));
vi.mock("../components/LimitMode", () => ({ LimitMode: () => null }));
vi.mock("../components/MatrixMode", () => ({ MatrixMode: () => null }));
vi.mock("../components/StatisticsMode", () => ({ StatisticsMode: () => null }));
vi.mock("../components/SystemMode", () => ({ SystemMode: () => null }));
vi.mock("../components/UnitsMode", () => ({ UnitsMode: () => null }));
vi.mock("../components/AjustesPopover", () => ({ AjustesPopover: () => <button>Ajustes</button> }));
vi.mock("../components/KeyboardDock", () => ({ KeyboardDock: () => null }));
vi.mock("../hooks/useMinWidthMediaQuery", () => ({
  FLOATING_MIN_WIDTH_PX: 1024,
  useMinWidthMediaQuery: () => true,
}));

import App from "../App";

describe("branding V5.2.1", () => {
  it("muestra Precision Lab Plus en la cabecera", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Precision Lab Plus" })).toBeInTheDocument();
  });
});

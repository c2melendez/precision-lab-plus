# Validación local y CI — Precision Lab Plus

## Backend

```bash
cd backend
pip install -r requirements.txt pytest pytest-cov
pytest -q
```

## Frontend

```bash
cd frontend
npm ci
npm run typecheck
npm test
npm run build
```

## E2E integrado con Playwright

Desde `frontend/`:

```bash
npm install --no-save --package-lock=false @playwright/test@1.55.0
npx playwright install chromium
npx playwright test
```

Playwright levanta automáticamente FastAPI en `127.0.0.1:8000` y Vite en `127.0.0.1:4174`. Se prueban Desktop 1440, tablet y móvil, además del contrato HTTP de operaciones críticas como `log(100)` y `ln(e)`.

## Quality gate recomendado

No publicar si falla pytest, typecheck, Vitest/paridad del teclado, build de producción o Playwright E2E.

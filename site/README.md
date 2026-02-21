# A7 Documentation Site

React + TypeScript + Vite docs frontend for the A7 compiler repository.

## Local Development

```bash
cd site
npm install
npm run dev
```

The site uses `HashRouter`, so routes resolve as `#/path` locally and on GitHub Pages.

## Build

```bash
cd site
npm run build
npm run preview
```

## Quality Checks

```bash
cd site
npm run lint
```

Repository-level docs style checks:

```bash
uv run python scripts/check_docs_style.py
```

## Styling System

Design tokens and shared interface styles live in:

- `site/src/styles/tokens.css`
- `site/src/index.css`

Primary shared UI primitives live in `site/src/components/`.

## Deployment

GitHub Pages deploy runs from `.github/workflows/deploy-docs.yml` when docs-related files change on `main`/`master`.

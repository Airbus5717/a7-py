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

The current site direction is:

- warm monochrome, paper-toned surfaces
- editorial serif display type with a restrained sans body
- 1px border discipline and flat panels
- top navigation plus drawer-based full route navigation
- image-led home page with framed media and minimal motion via reveal-on-scroll
- built-in `light` / `dark` / `system` theme modes with persistence
- dark-extension detection to avoid double-dark styling when browser extensions inject their own theme layer

## Deployment

GitHub Pages deploy runs from `.github/workflows/deploy-docs.yml` when docs-related files change on `main`/`master`.

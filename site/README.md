# A7 Documentation Site

This site is a custom Astro static site.

It does not use a docs template.

Routes are flat and direct.

## Local development

```bash
cd site
npm install
npm run dev
```

## Build

```bash
cd site
npm run build
```

## Check

```bash
cd site
npm run check
```

## Deployment

GitHub Actions deploys `site/dist` to GitHub Pages.

Workflow file: `.github/workflows/deploy-docs.yml`

Production URL: `https://airbus5717.github.io/a7-py/`

const BASE = import.meta.env.BASE_URL || '/';

export const SITE_TITLE = 'A7 Compiler Docs';
export const SITE_TAGLINE = 'Plain docs for the A7 language and compiler.';

export function withBase(path: string): string {
  const base = BASE.endsWith('/') ? BASE : `${BASE}/`;
  const cleaned = path.replace(/^\/+|\/+$/g, '');
  return cleaned ? `${base}${cleaned}/` : base;
}

export function stripBase(pathname: string): string {
  const baseNoSlash = BASE.replace(/\/$/, '');
  const cleanPath = pathname.replace(/\/$/, '') || '/';

  if (!baseNoSlash || baseNoSlash === '/') {
    return cleanPath;
  }

  if (cleanPath === baseNoSlash) {
    return '/';
  }

  if (cleanPath.startsWith(`${baseNoSlash}/`)) {
    return cleanPath.slice(baseNoSlash.length) || '/';
  }

  return cleanPath;
}

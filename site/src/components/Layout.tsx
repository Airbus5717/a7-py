import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import { useTheme } from '../hooks/useTheme'

type PrimaryNavItem =
  | { kind: 'route'; to: string; label: string; end?: boolean }
  | { kind: 'link'; href: string; label: string }

const PRIMARY_NAV: PrimaryNavItem[] = [
  { kind: 'route', to: '/', label: 'Docs', end: true },
  { kind: 'route', to: '/start', label: 'Guide' },
  { kind: 'route', to: '/language', label: 'Reference' },
  { kind: 'route', to: '/examples', label: 'Examples' },
  { kind: 'route', to: '/testing', label: 'Playground' },
  { kind: 'route', to: '/changelog', label: 'Blog' },
  { kind: 'link', href: 'https://github.com/Airbus5717/a7-py', label: 'GitHub ↗' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { pathname } = useLocation()
  const { preference, resolvedTheme, darkExtensionActive, cycleTheme } = useTheme()

  useEffect(() => {
    if (!sidebarOpen) {
      return
    }

    const previousOverflow = document.body.style.overflow
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setSidebarOpen(false)
      }
    }

    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [sidebarOpen])

  useEffect(() => {
    document.documentElement.classList.add('reveal-ready')

    const elements = Array.from(document.querySelectorAll<HTMLElement>('[data-reveal]'))
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            observer.unobserve(entry.target)
          }
        })
      },
      {
        threshold: 0.14,
        rootMargin: '0px 0px -8% 0px',
      },
    )

    elements.forEach((element, index) => {
      element.classList.remove('is-visible')
      element.style.setProperty('--reveal-delay', `${(index % 6) * 80}ms`)
      observer.observe(element)
    })

    return () => observer.disconnect()
  }, [pathname])

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>

      {sidebarOpen && <div className="mobile-overlay" onClick={() => setSidebarOpen(false)} />}

      <aside className={`app-sidebar${sidebarOpen ? ' open' : ''}`} aria-hidden={!sidebarOpen}>
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </aside>

      <div className="app-main">
        <header className="site-header">
          <div className="site-header-inner">
            <NavLink to="/" className="site-brand">
              <span className="site-brand-mark">A7</span>
            </NavLink>

            <nav className="site-nav" aria-label="Primary">
              {PRIMARY_NAV.map((item) => (
                item.kind === 'route' ? (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) => `site-nav-link${isActive ? ' active' : ''}`}
                  >
                    {item.label}
                  </NavLink>
                ) : (
                  <a
                    key={item.href}
                    className="site-nav-link"
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {item.label}
                  </a>
                )
              ))}
            </nav>

            <div className="site-header-tools">
              <button type="button" className="site-search" aria-label="Search documentation">
                <span className="site-search-label">
                  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <circle cx="11" cy="11" r="6.5" />
                    <path strokeLinecap="round" d="M16 16l4 4" />
                  </svg>
                  Search docs
                </span>
                <span className="site-search-kbd">/</span>
              </button>

              <button
                type="button"
                onClick={cycleTheme}
                className="theme-toggle"
                aria-label={`Theme: ${preference}. Click to cycle theme mode.`}
                title={darkExtensionActive ? 'Dark extension detected. Site theme will avoid double-dark styling.' : undefined}
              >
                <span className="theme-toggle-icon" aria-hidden="true">
                  {resolvedTheme === 'dark' ? (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" />
                    </svg>
                  ) : preference === 'system' ? (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                      <rect x="3.5" y="4.5" width="17" height="12" rx="2" />
                      <path strokeLinecap="round" d="M8 19.5h8M12 16.5v3" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                      <circle cx="12" cy="12" r="4.5" />
                      <path strokeLinecap="round" d="M12 2.5v2.5M12 19v2.5M21.5 12H19M5 12H2.5M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8M18.7 18.7l-1.8-1.8M7.1 7.1L5.3 5.3" />
                    </svg>
                  )}
                </span>
                <span className="theme-toggle-label">{preference}</span>
                {darkExtensionActive ? <span className="theme-toggle-badge">ext</span> : null}
              </button>

              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="site-menu-button"
                aria-label="Open site navigation"
              >
                <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 7h16M4 12h16M4 17h16" />
                </svg>
                <span className="site-menu-button-text">Menu</span>
              </button>
            </div>
          </div>
        </header>

        <header className="mobile-header">
          <div className="mobile-header-row">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="icon-button"
              aria-label="Open docs navigation"
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <strong className="nav-brand-mark">A7</strong>
            <span className="nav-brand-text">Documentation</span>
          </div>
        </header>

        <main id="main-content" className="app-main-inner" tabIndex={-1}>
          <Outlet />
        </main>

        {pathname !== '/' ? (
          <footer className="app-footer">
            <div className="app-footer-inner">
              <span>A7 Programming Language</span>
              <a href="https://github.com/Airbus5717/a7-py" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
            </div>
          </footer>
        ) : null}
      </div>
    </div>
  )
}

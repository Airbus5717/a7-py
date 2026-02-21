import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  summary: string
  eyebrow?: string
  actions?: ReactNode
}

export default function PageHeader({ title, summary, eyebrow, actions }: PageHeaderProps) {
  return (
    <header className="page-header">
      {eyebrow && <span className="page-header-eyebrow">{eyebrow}</span>}
      <h1 className="page-header-title">{title}</h1>
      <p className="page-header-summary">{summary}</p>
      {actions ? <div style={{ marginTop: 'var(--space-3)' }}>{actions}</div> : null}
    </header>
  )
}

import type { ReactNode } from 'react'

interface SectionPanelProps {
  title?: string
  subtitle?: string
  children: ReactNode
  className?: string
}

export default function SectionPanel({ title, subtitle, children, className = '' }: SectionPanelProps) {
  return (
    <section className={`section-panel ${className}`.trim()}>
      {title && <h2 className="section-title">{title}</h2>}
      {subtitle && <p className="section-subtitle">{subtitle}</p>}
      {children}
    </section>
  )
}

import type { ReactNode } from 'react'

interface DocCalloutProps {
  tone?: 'info' | 'warning' | 'success'
  children: ReactNode
}

export default function DocCallout({ tone = 'info', children }: DocCalloutProps) {
  return <div className={`doc-callout ${tone}`}>{children}</div>
}

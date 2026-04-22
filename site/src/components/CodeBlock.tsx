import { useHighlight } from '../hooks/useHighlight'

interface CodeBlockProps {
  code: string
  lang?: string
  title?: string
}

export default function CodeBlock({ code, lang, title }: CodeBlockProps) {
  const html = useHighlight(code, lang)

  return (
    <figure className="code-shell" data-reveal>
      {(title || lang) && (
        <figcaption className="code-head">
          <span className="code-head-dots" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span className="code-head-title">{title || lang}</span>
          <span className="code-head-meta">{lang ? 'A7' : ''}</span>
        </figcaption>
      )}
      {html ? (
        <div className="code-pre code-highlighted" dangerouslySetInnerHTML={{ __html: html }} />
      ) : (
        <pre className="code-pre">
          <code>{code}</code>
        </pre>
      )}
    </figure>
  )
}

import { Link } from 'react-router-dom'
import CodeBlock from '../components/CodeBlock'
import MetricTile from '../components/MetricTile'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const HELLO = `io :: import "std/io"

main :: fn() {
    io.println("Hello, World!")
}`

const STATS = [
  { label: 'Tests', value: 'Run pytest', note: 'status depends on current branch' },
  { label: 'Examples', value: '36 programs' },
  { label: 'Pipeline stages', value: '5' },
  { label: 'Recursion limit', value: '100' },
]

const LINKS = [
  { to: '/start', label: 'Get Started', desc: 'Install, compile, run' },
  { to: '/language', label: 'Language', desc: 'Types, syntax, control flow' },
  { to: '/examples', label: 'Examples', desc: 'All 36 programs' },
  { to: '/pipeline', label: 'Pipeline', desc: 'Compiler stages' },
  { to: '/cli', label: 'CLI', desc: 'Modes and flags' },
  { to: '/status', label: 'Status', desc: 'What works, what doesn\'t' },
]

export default function Home() {
  return (
    <div className="page">
      <PageHeader
        title="A7"
        summary="A statically typed language that compiles to Zig. Generics, manual memory, no recursive AST walks."
      />

      <SectionPanel>
        <CodeBlock code={HELLO} lang="a7" title="examples/001_hello.a7" />
      </SectionPanel>

      <section className="metric-grid">
        {STATS.map((s) => (
          <MetricTile key={s.label} label={s.label} value={s.value} note={s.note} />
        ))}
      </section>

      <SectionPanel title="What's different">
        <ul className="doc-list">
          <li>Pointer syntax is property-based: <code className="doc-inline-code">.adr</code> for address-of, <code className="doc-inline-code">.val</code> for dereference.</li>
          <li>Logical operators are <code className="doc-inline-code">and</code>, <code className="doc-inline-code">or</code>, and unary-not (<code className="doc-inline-code">not</code> or <code className="doc-inline-code">!</code>).</li>
          <li>Constants use <code className="doc-inline-code">::</code>, variables use <code className="doc-inline-code">:=</code>.</li>
          <li>Generics declared with <code className="doc-inline-code">$T</code> prefix.</li>
          <li>Every compiler pass uses explicit stacks, not recursion.</li>
        </ul>
      </SectionPanel>

      <section className="link-card-grid">
        {LINKS.map((link) => (
          <Link key={link.to} to={link.to} className="link-card">
            <span className="link-card-title">{link.label}</span>
            <span className="link-card-desc">{link.desc}</span>
          </Link>
        ))}
      </section>
    </div>
  )
}

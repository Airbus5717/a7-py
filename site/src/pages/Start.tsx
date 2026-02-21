import { Link } from 'react-router-dom'
import CodeBlock from '../components/CodeBlock'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const HELLO = `io :: import "std/io"

main :: fn() {
    io.println("Hello, World!")
}`

export default function Start() {
  return (
    <div className="page">
      <PageHeader
        title="Getting Started"
        summary="Clone, install, compile your first file."
      />

      <SectionPanel title="Requirements">
        <ul className="doc-list">
          <li>Python 3.13+</li>
          <li><a href="https://docs.astral.sh/uv/" target="_blank" rel="noopener noreferrer">uv</a> package manager</li>
          <li>Zig compiler (to run generated output)</li>
        </ul>
      </SectionPanel>

      <SectionPanel title="Install">
        <CodeBlock
          lang="bash"
          code={`git clone https://github.com/Airbus5717/a7-py.git
cd a7-py
uv sync`}
        />
      </SectionPanel>

      <SectionPanel title="Write a program">
        <CodeBlock code={HELLO} lang="a7" title="hello.a7" />
      </SectionPanel>

      <SectionPanel title="Compile and run">
        <CodeBlock
          lang="bash"
          code={`# Compile to Zig
uv run python main.py hello.a7

# Run it
zig run hello.zig

# Other modes
uv run python main.py --mode tokens hello.a7   # just tokens
uv run python main.py --mode ast hello.a7       # parse tree
uv run python main.py --format json hello.a7    # JSON output`}
        />
      </SectionPanel>

      <SectionPanel title="Next">
        <ul className="doc-list">
          <li><Link to="/language">Language Reference</Link> — full syntax</li>
          <li><Link to="/examples">Examples</Link> — 36 programs to read</li>
          <li><Link to="/cli">CLI</Link> — all flags and modes</li>
        </ul>
      </SectionPanel>
    </div>
  )
}

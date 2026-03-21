import MetricTile from '../components/MetricTile'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const done = [
  { name: 'Parser', desc: 'All constructs: functions, structs, enums, unions, generics, match, imports, labeled loops.' },
  { name: 'Semantic analysis', desc: 'Name resolution, type checking with inference, control flow and memory checks, slice/index validation.' },
  { name: 'Preprocessing', desc: 'Nine sub-passes: lowering, resolution, mutation, usage, shadowing, hoisting, folding.' },
  { name: 'Zig backend', desc: 'Full translation with type mapping, pointer handling, hoisting, annotations, labeled loops.' },
  { name: 'C backend', desc: 'C11 output validated with zig cc. Labeled loops, slices, defer, match statements.' },
]

const missing = [
  { name: 'fall statement semantics', desc: 'fall is parsed but not yet validated or lowered in semantic/codegen passes.' },
  { name: 'Advanced match diagnostics', desc: 'No overlap/redundancy or unreachable-branch detection for case patterns.' },
  { name: 'Generic constraint internals', desc: 'Inline type-set constraint resolution in generics.py is still placeholder-level.' },
  { name: 'Recursive generic instantiation', desc: 'Recursive generic structs need cycle-safe substitution and field resolution.' },
  { name: 'Memory/lifetime model', desc: 'Only basic del reference checks. No ownership/borrow-style lifetime analysis.' },
]

export default function Status() {
  return (
    <div className="page">
      <PageHeader
        title="Status"
        summary="What works and what doesn't yet."
      />

      <section className="metric-grid">
        <MetricTile label="Pipeline" value="Working" />
        <MetricTile label="Tests" value="Run pytest" note="PYTHONPATH=. uv run pytest --tb=no -q" />
        <MetricTile label="Examples" value="Run verifier" note="scripts/verify_examples_e2e.py" />
      </section>

      <SectionPanel title="Done">
        <div className="stack-2">
          {done.map((item) => (
            <article key={item.name} className="doc-callout success">
              <p style={{ margin: 0 }}><strong>{item.name}</strong></p>
              <p className="text-secondary" style={{ margin: '4px 0 0' }}>{item.desc}</p>
            </article>
          ))}
        </div>
      </SectionPanel>

      <SectionPanel title="Open gaps (unskipped tests)">
        <div className="stack-2">
          {missing.map((item) => (
            <article key={item.name} className="doc-callout warning">
              <p style={{ margin: 0 }}><strong>{item.name}</strong></p>
              <p className="text-secondary" style={{ margin: '4px 0 0' }}>{item.desc}</p>
            </article>
          ))}
        </div>
      </SectionPanel>

      <SectionPanel title="Next priorities">
        <ol className="doc-list">
          <li>Implement fall statement validation and backend lowering.</li>
          <li>Add match pattern overlap/redundancy and exhaustiveness diagnostics.</li>
          <li>Improve type checker: control-flow narrowing, return consistency, dead code detection.</li>
          <li>Add optimization passes: constant folding, dead code elimination, constant propagation.</li>
        </ol>
      </SectionPanel>
    </div>
  )
}

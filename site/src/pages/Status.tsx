import MetricTile from '../components/MetricTile'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const done = [
  { name: 'Parser', desc: 'All constructs: functions, structs, enums, unions, generics, match, imports.' },
  { name: 'Semantic analysis', desc: 'Name resolution, type checking with inference, control flow and memory checks.' },
  { name: 'Preprocessing', desc: 'Nine sub-passes: lowering, resolution, mutation, usage, shadowing, hoisting, folding.' },
  { name: 'Zig backend', desc: 'Full translation with type mapping, pointer handling, hoisting, annotations.' },
]

const missing = [
  { name: 'Match expression typing', desc: 'MATCH_EXPR is parsed, but semantic type checking does not handle it yet.' },
  { name: '@type_set declaration parsing', desc: 'Top-level @type_set(...) in const declarations still fails in expression path.' },
  { name: 'Generic arithmetic constraints', desc: 'Arithmetic over $T is rejected when constraint/type information is required.' },
  { name: 'Generic struct literal substitution', desc: 'Field checks compare against unresolved $T/$U in instantiated literals.' },
  { name: 'Field access on Box(i32)', desc: 'GenericInstanceType is not resolved to concrete StructType before field access checks.' },
  { name: 'Generic local literal init', desc: 'Patterns like total: $T = 0 need inference/coercion in generic numeric contexts.' },
  { name: 'Recursive generic instantiation', desc: 'Recursive generic structs need cycle-safe substitution and field resolution.' },
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
        <MetricTile label="Tests" value="1039 pass / 7 fail" note="pytest on 2026-02-21 after unskipping 9 semantic tests" />
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
          <li>Add MATCH_EXPR support to semantic type checking and branch type unification.</li>
          <li>Fix generic type substitution for instantiated structs and field access.</li>
          <li>Implement constraint-aware generic arithmetic and type-set declaration parsing.</li>
        </ol>
      </SectionPanel>
    </div>
  )
}

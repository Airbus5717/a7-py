import CodeBlock from '../components/CodeBlock'
import DataTable from '../components/DataTable'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const ioFunctions = [
  ['io.println(s: string)', 'Print with newline'],
  ['io.print(s: string)', 'Print without newline'],
  ['io.eprintln(s: string)', 'Print to stderr'],
]

const mathFunctions = [
  ['sqrt_f32(x: f32) f32', 'Square root'],
  ['sqrt_f64(x: f64) f64', 'Square root (f64)'],
  ['abs_f32(x: f32) f32', 'Absolute value (float)'],
  ['abs_i32(x: i32) i32', 'Absolute value (int)'],
  ['floor_f32(x: f32) f32', 'Floor'],
  ['ceil_f32(x: f32) f32', 'Ceiling'],
  ['sin_f64(x: f64) f64', 'Sine'],
  ['cos_f64(x: f64) f64', 'Cosine'],
  ['pow_f64(x: f64, y: f64) f64', 'Power'],
  ['min_i32(a: i32, b: i32) i32', 'Minimum'],
  ['max_i32(a: i32, b: i32) i32', 'Maximum'],
]

const intrinsics = [
  ['@size_of(T)', 'Size of type in bytes'],
  ['@align_of(T)', 'Alignment of type'],
  ['@type_id(T)', 'Unique numeric type identifier'],
  ['@type_name(T)', 'Type name as string'],
  ['@type_set(...)', 'Define type set constraints'],
  ['@unreachable()', 'Mark code as unreachable'],
  ['@likely(cond)', 'Branch hint'],
  ['@unlikely(cond)', 'Branch hint'],
]

export default function Stdlib() {
  return (
    <div className="page">
      <PageHeader
        title="Standard Library"
        summary="Built-in modules and compiler intrinsics."
      />

      <SectionPanel title="io">
        <DataTable
          caption="Standard io module functions."
          headers={['Function', 'Description']}
          rows={ioFunctions.map(([sig, desc]) => [
            <code className="doc-inline-code" key={sig}>{sig}</code>,
            desc,
          ])}
        />
        <CodeBlock
          lang="a7"
          code={`io :: import "std/io"

main :: fn() {
    io.println("Hello, World!")
    io.print("no newline")
}`}
        />
      </SectionPanel>

      <SectionPanel title="math">
        <DataTable
          caption="Standard math module functions."
          headers={['Function', 'Description']}
          rows={mathFunctions.map(([sig, desc]) => [
            <code className="doc-inline-code" key={sig}>{sig}</code>,
            desc,
          ])}
        />
        <CodeBlock
          lang="a7"
          code={`math :: import "std/math"

main :: fn() {
    x := sqrt_f32(16.0)
    y := abs_i32(-42)
    z := pow_f64(2.0, 10.0)
}`}
        />
      </SectionPanel>

      <SectionPanel title="mem and string">
        <ul className="doc-list">
          <li><strong>mem</strong> — byte-copy, fill, zero, compare, raw alloc/free.</li>
          <li><strong>string</strong> — length, compare, find, contains, starts_with, ends_with.</li>
        </ul>
      </SectionPanel>

      <SectionPanel title="Intrinsics">
        <DataTable
          caption="Compiler intrinsics available in A7."
          headers={['Intrinsic', 'Description']}
          rows={intrinsics.map(([name, desc]) => [
            <code className="doc-inline-code" key={name}>{name}</code>,
            desc,
          ])}
        />
      </SectionPanel>
    </div>
  )
}

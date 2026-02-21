import { useCallback, useMemo, useState } from 'react'
import CodeModal from '../components/CodeModal'
import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const exampleModules = import.meta.glob<string>('../../../examples/*.a7', {
  query: '?raw',
  import: 'default',
})

const EXAMPLES = [
  { file: '000_empty.a7', title: 'Empty Program', category: 'Basics', desc: 'Minimal valid A7 program' },
  { file: '001_hello.a7', title: 'Hello World', category: 'Basics', desc: 'Print to stdout with io module' },
  { file: '002_var.a7', title: 'Variables', category: 'Basics', desc: 'Variable and constant declarations' },
  { file: '003_comments.a7', title: 'Comments', category: 'Basics', desc: 'Single-line and nested block comments' },
  { file: '004_func.a7', title: 'Functions', category: 'Basics', desc: 'Function declarations and calls' },
  { file: '005_for_loop.a7', title: 'For Loops', category: 'Control Flow', desc: 'C-style and range-based loops' },
  { file: '006_if.a7', title: 'Conditionals', category: 'Control Flow', desc: 'If-else statements and expressions' },
  { file: '007_while.a7', title: 'While Loops', category: 'Control Flow', desc: 'While loop patterns' },
  { file: '008_switch.a7', title: 'Match', category: 'Control Flow', desc: 'Pattern matching with ranges and fallthrough' },
  { file: '009_struct.a7', title: 'Structs', category: 'Types', desc: 'Struct declarations and initialization' },
  { file: '010_enum.a7', title: 'Enums', category: 'Types', desc: 'Enumerations with explicit values' },
  { file: '011_memory.a7', title: 'Memory', category: 'Memory', desc: 'Heap allocation with new/del' },
  { file: '012_arrays.a7', title: 'Arrays', category: 'Types', desc: 'Fixed-size arrays and slices' },
  { file: '013_pointers.a7', title: 'Pointers', category: 'Memory', desc: 'Pointer operations with .adr/.val' },
  { file: '014_generics.a7', title: 'Generics', category: 'Types', desc: 'Generic functions and structs with $T' },
  { file: '015_types.a7', title: 'Type System', category: 'Types', desc: 'Type aliases and composite types' },
  { file: '016_unions.a7', title: 'Unions', category: 'Types', desc: 'Union and tagged union types' },
  { file: '017_methods.a7', title: 'Methods', category: 'Types', desc: 'Methods with self receiver' },
  { file: '018_modules.a7', title: 'Modules', category: 'Basics', desc: 'Import system and visibility' },
  { file: '019_literals.a7', title: 'Literals', category: 'Basics', desc: 'All literal formats: hex, octal, binary, escapes' },
  { file: '020_operators.a7', title: 'Operators', category: 'Basics', desc: 'Arithmetic, logical, bitwise, assignment' },
  { file: '021_control_flow.a7', title: 'Control Flow', category: 'Control Flow', desc: 'Combined control flow patterns' },
  { file: '022_function_pointers.a7', title: 'Function Pointers', category: 'Functions', desc: 'Higher-order functions and callbacks' },
  { file: '023_inline_structs.a7', title: 'Inline Structs', category: 'Types', desc: 'Anonymous struct types' },
  { file: '024_defer.a7', title: 'Defer', category: 'Memory', desc: 'Resource management with defer' },
  { file: '025_linked_list.a7', title: 'Linked List', category: 'Data Structures', desc: 'Generic linked list implementation' },
  { file: '026_binary_tree.a7', title: 'Binary Tree', category: 'Data Structures', desc: 'Binary search tree with traversal' },
  { file: '027_callbacks.a7', title: 'Callbacks', category: 'Functions', desc: 'Event handling and dispatcher pattern' },
  { file: '028_state_machine.a7', title: 'State Machine', category: 'Patterns', desc: 'State machines with function pointers' },
  { file: '029_sorting.a7', title: 'Sorting', category: 'Algorithms', desc: 'Sorting with custom comparators' },
  { file: '030_calculator.a7', title: 'Calculator', category: 'Applications', desc: 'Math operations including sqrt, power' },
  { file: '031_number_guessing.a7', title: 'Number Guessing', category: 'Applications', desc: 'Interactive game with RNG' },
  { file: '032_prime_numbers.a7', title: 'Primes', category: 'Algorithms', desc: 'Sieve of Eratosthenes, factorization' },
  { file: '033_fibonacci.a7', title: 'Fibonacci', category: 'Algorithms', desc: 'Multiple implementations with memoization' },
  { file: '034_string_utils.a7', title: 'String Utils', category: 'Applications', desc: 'Text processing utilities' },
  { file: '035_matrix.a7', title: 'Matrix Ops', category: 'Applications', desc: 'Matrix operations and linear algebra' },
]

const CATEGORIES = ['All', ...new Set(EXAMPLES.map((example) => example.category))]

export default function Examples() {
  const [category, setCategory] = useState('All')
  const [query, setQuery] = useState('')
  const [modal, setModal] = useState<{ title: string; code: string } | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  const filtered = useMemo(
    () =>
      EXAMPLES.filter((example) => {
        const matchesCategory = category === 'All' || example.category === category
        const search = query.trim().toLowerCase()
        const matchesQuery =
          search.length === 0 ||
          example.file.toLowerCase().includes(search) ||
          example.title.toLowerCase().includes(search) ||
          example.desc.toLowerCase().includes(search)

        return matchesCategory && matchesQuery
      }),
    [category, query],
  )

  const openExample = useCallback((example: (typeof EXAMPLES)[number]) => {
    setLoadError(null)

    const key = `../../../examples/${example.file}`
    const loader = exampleModules[key]
    if (!loader) {
      setLoadError(`Source for ${example.file} is not available in this build.`)
      return
    }
    loader()
      .then((code) => {
        setModal({ title: example.file, code })
      })
      .catch(() => {
        setLoadError(`Could not load ${example.file}.`)
      })
  }, [])

  return (
    <div className="page">
      <PageHeader
        eyebrow="Learn by Running"
        title="Examples"
        summary="Thirty-six example programs spanning basics, language features, data structures, and full applications."
      />

      <SectionPanel title="Browse the Library" subtitle="Filter by category and search by filename, title, or description.">
        <div className="filters stack-2">
          <input
            className="doc-input"
            placeholder="Search examples..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            aria-label="Search examples"
          />

          <div className="chip-row">
            {CATEGORIES.map((item) => (
              <button
                key={item}
                type="button"
                className={`doc-chip-button ${item === category ? 'active' : ''}`}
                onClick={() => setCategory(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <p className="text-tertiary">
            Showing <strong>{filtered.length}</strong> of <strong>{EXAMPLES.length}</strong> examples.
          </p>

          {loadError && (
            <p className="doc-callout warning" role="status" aria-live="polite" style={{ margin: 0 }}>
              {loadError}
            </p>
          )}
        </div>
      </SectionPanel>

      <section className="link-card-grid">
        {filtered.map((example) => (
          <article
            key={example.file}
            className="example-card"
            onClick={() => openExample(example)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                openExample(example)
              }
            }}
          >
            <div className="example-card-top">
              <code className="doc-inline-code">{example.file}</code>
              <span className="doc-chip">{example.category}</span>
            </div>
            <h2 className="example-card-title">{example.title}</h2>
            <p className="example-card-desc">{example.desc}</p>
          </article>
        ))}
      </section>

      {modal && <CodeModal title={modal.title} code={modal.code} onClose={() => setModal(null)} />}
    </div>
  )
}

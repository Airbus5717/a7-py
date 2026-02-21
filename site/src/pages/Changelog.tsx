import PageHeader from '../components/PageHeader'
import SectionPanel from '../components/SectionPanel'

const releases = [
  {
    version: '0.3.0',
    date: '',
    groups: {
      Added: [
        'Error stage verifier and matrix tests for mode/format contracts.',
        'Examples end-to-end verifier with golden output fixtures.',
        'CLI v2 mode/format contract with stable exit codes.',
        'Standard library registry with io and math mappings.',
        'AST node annotations consumed by backend emission.',
        'Unskipped previously deferred semantic tests to surface concrete implementation gaps.',
      ],
      Changed: [
        'All AST traversals converted to iterative stack-based form.',
        'Semantic errors collected without hard-stop.',
        'Backend reads preprocessor annotations instead of recomputing.',
        'Current semantic backlog is now tracked by active failing tests (1039 pass / 7 fail, 0 skipped).',
      ],
      Fixed: [
        'Match/switch Zig codegen trailing comma edge cases.',
        'Character literal escaping and operator keyword usage.',
        'Struct initialization and nil handling in examples.',
        'Status/docs/changelog now list exact missing features uncovered by the unskipped semantic tests.',
      ],
    },
  },
  {
    version: '0.2.0',
    date: '2025-11-03',
    groups: {
      Added: [
        'Function type parsing.',
        'Generic type instantiation in type expressions.',
        'Uninitialized variable declarations.',
      ],
      Changed: ['Parser completeness and struct-literal disambiguation.'],
      Fixed: ['Generic parameter parsing and return-without-value for void functions.'],
    },
  },
  {
    version: '0.1.0',
    date: '2025-11-02',
    groups: {
      Added: [
        'Tokenizer, parser, and baseline language support.',
        '22 example programs and 352 tests.',
        'Rich error messages, pointer property syntax, full spec draft.',
      ],
    },
  },
]

export default function Changelog() {
  return (
    <div className="page">
      <PageHeader
        title="Changelog"
        summary="What changed, by release."
      />

      {releases.map((release) => (
        <SectionPanel key={release.version} title={release.version} subtitle={release.date || 'In progress'}>
          <div className="stack-2">
            {Object.entries(release.groups).map(([groupName, changes]) => (
              <section key={groupName}>
                <h3 className="section-subtitle" style={{ marginBottom: 8 }}>
                  <span className={`doc-chip ${chipTone(groupName)}`}>{groupName}</span>
                </h3>
                <ul className="doc-list">
                  {(changes as string[]).map((change: string) => (
                    <li key={change}>{change}</li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </SectionPanel>
      ))}
    </div>
  )
}

function chipTone(groupName: string): string {
  if (groupName === 'Added') return 'success'
  if (groupName === 'Changed') return 'warning'
  return 'accent'
}

import type { ReactNode } from 'react'
import { Fragment } from 'react'
import { Link } from 'react-router-dom'
import CodeBlock from '../components/CodeBlock'
import SectionPanel from '../components/SectionPanel'

const FACTORIAL = `module math

export fn factorial(n: u64) -> u64 {
    let mut acc: u64 = 1
    let mut i: u64 = 2

    while i <= n {
        acc = acc * i
        i = i + 1
    }

    return acc
}

export fn main() {
    let n = 10
    let result = factorial(n)
    io::println("{}", result)
}`

const QUICKSTART = [
  { step: '01', label: 'Install', command: '$ curl -fsSL https://astral.sh/uv/install.sh | sh' },
  { step: '02', label: 'Create', command: '$ a7 new hello' },
  { step: '03', label: 'Run', command: '$ a7 run' },
  { step: '04', label: 'Build', command: '$ a7 build --release' },
]

const FEATURES = [
  {
    area: 'left-top',
    title: 'No recursion',
    copy: 'Eliminate an entire class of runtime failure and simplify reasoning about the compiler itself.',
    tag: 'Language',
    tone: 'accent' as const,
    icon: (
      <svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.7}>
        <circle cx="12" cy="12" r="6.5" />
        <path strokeLinecap="round" d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3" />
      </svg>
    ),
  },
  {
    area: 'left-bottom',
    title: 'Memory safety',
    copy: 'Property-based pointer operations stay explicit without adding a garbage collector.',
    tag: 'Safety',
    tone: 'accent' as const,
    icon: (
      <svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.7}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3l7 3v5c0 4.4-2.8 8.3-7 10-4.2-1.7-7-5.6-7-10V6l7-3z" />
      </svg>
    ),
  },
  {
    area: 'right-top',
    title: 'Predictable performance',
    copy: 'Explicit stacks and low-level control keep runtime behavior easy to model and debug.',
    tag: 'Performance',
    tone: 'warning' as const,
    icon: (
      <svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.7}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 3L6 14h5l-1 7 7-11h-5l1-7z" />
      </svg>
    ),
  },
  {
    area: 'right-bottom',
    title: 'Zero-cost abstractions',
    copy: 'Generics, modules, and pattern matching compile down to direct, readable target code.',
    tag: 'Design',
    tone: 'success' as const,
    icon: (
      <svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.7}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 7.5l8 4.5 8-4.5M12 12v9" />
      </svg>
    ),
  },
]

const PIPELINE = [
  {
    title: 'Parse',
    copy: 'Source code to AST',
    icon: (
      <svg width="30" height="30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 3H5a2 2 0 00-2 2v3M16 3h3a2 2 0 012 2v3M8 21H5a2 2 0 01-2-2v-3M16 21h3a2 2 0 002-2v-3M8 12h8" />
      </svg>
    ),
  },
  {
    title: 'Lower',
    copy: 'AST to HIR',
    icon: (
      <svg width="30" height="30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <rect x="4" y="5" width="16" height="4" rx="1.5" />
        <rect x="4" y="10" width="16" height="4" rx="1.5" />
        <rect x="4" y="15" width="16" height="4" rx="1.5" />
      </svg>
    ),
  },
  {
    title: 'Analyze',
    copy: 'Types, lifetimes, effects',
    icon: (
      <svg width="30" height="30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 4h12M6 12h12M6 20h12M9 4v16M15 4v16" />
      </svg>
    ),
  },
  {
    title: 'Optimize',
    copy: 'Simplify and trim IR',
    icon: (
      <svg width="30" height="30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" d="M4 7h16M4 12h10M4 17h16" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 10l3 2-3 2" />
      </svg>
    ),
  },
  {
    title: 'Codegen',
    copy: 'IR to machine-ready code',
    icon: (
      <svg width="30" height="30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" d="M6 4v16M10 4v16M14 4v16M18 4v16" />
        <path strokeLinecap="round" d="M3 8h3M3 16h3M18 8h3M18 16h3" />
      </svg>
    ),
  },
]

const HIGHLIGHTS = [
  {
    title: 'Algebraic data types',
    copy: 'Model complex data without runtime machinery or awkward tagging.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <rect x="4" y="4" width="6" height="6" />
        <rect x="14" y="4" width="6" height="6" />
        <rect x="9" y="14" width="6" height="6" />
      </svg>
    ),
  },
  {
    title: 'Pattern matching',
    copy: 'Write exhaustive, readable branches for enums and unions.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" d="M5 7h14M5 12h14M5 17h8" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 15l2 2 4-4" />
      </svg>
    ),
  },
  {
    title: 'Static diagnostics',
    copy: 'Catch mistakes before codegen with type-aware compiler passes.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3l9 5-9 5-9-5 9-5zM3 16l9 5 9-5" />
      </svg>
    ),
  },
  {
    title: 'Effect tracking',
    copy: 'Understand what functions allocate, mutate, or depend on.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 8h7l2 3h7M8 4l-4 4 4 4M16 20l4-4-4-4" />
      </svg>
    ),
  },
  {
    title: 'Iterators, not recursion',
    copy: 'Iterative traversal keeps the implementation safe under low recursion limits.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 12a7 7 0 0112-4.95M19 12a7 7 0 01-12 4.95" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 5.5v3h-3M7 18.5v-3h3" />
      </svg>
    ),
  },
  {
    title: 'Small and fast',
    copy: 'A compact toolchain, a lean standard library, and straightforward output.',
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v8M12 12l5-5M12 12L7 7M5 18a7 7 0 0114 0" />
      </svg>
    ),
  },
]

const TESTIMONIALS = [
  {
    quote: 'A7 lets us build systems that are easier to reason about. Removing recursion was the right call.',
    name: 'Jane Doe',
    role: 'Systems Engineer at Acme',
  },
  {
    quote: 'The compile times are incredible, and the diagnostics are the best I’ve seen in a systems language.',
    name: 'John Smith',
    role: 'Founder at Biside',
  },
  {
    quote: 'We migrated a critical component to A7 and saw a 30% drop in latency. Highly recommended.',
    name: 'Alex Turner',
    role: 'Tech Lead at Hyperion',
  },
]

function FeatureIcon({ children }: { children: ReactNode }) {
  return <span className="feature-icon" aria-hidden="true">{children}</span>
}

export default function Home() {
  return (
    <div className="page home-page">
      <section className="home-hero" data-reveal>
        <div className="home-hero-copy">
          <span className="page-header-eyebrow">A7 v0.1.0</span>
          <h1 className="page-header-title">A7, without recursion.</h1>
          <div className="home-hero-rule" />
          <p className="page-header-summary">
            A modern systems language that removes recursion at the language level, simplifying reasoning,
            improving compile-time guarantees, and keeping performance predictable.
          </p>

          <div className="home-hero-actions">
            <Link to="/start" className="primary-action">
              Get started <span aria-hidden="true">→</span>
            </Link>
            <Link to="/language" className="secondary-action">
              Read the guide <span aria-hidden="true">→</span>
            </Link>
          </div>

          <p className="home-hero-meta">Designed for clarity. Built for performance.</p>
        </div>

        <div className="home-hero-media">
          <div className="home-hero-backdrop" aria-hidden="true" />
          <div className="home-hero-code">
            <CodeBlock code={FACTORIAL} lang="a7" title="factorial.a7" />
          </div>
        </div>
      </section>

      <SectionPanel className="home-quickstart quickstart-strip">
        <div className="quickstart-intro">
          <p className="quickstart-label">Quick start</p>
          <h2 className="quickstart-title">From zero to running.</h2>
          <div className="quickstart-intro-rule" />
        </div>

        <div className="quickstart-steps">
          {QUICKSTART.map((item) => (
            <article key={item.step} className="quickstart-step">
              <span className="quickstart-num">{item.step}</span>
              <span className="quickstart-name">{item.label}</span>
              <kbd className="command-key">
                <span>{item.command}</span>
                <span className="command-key-icon" aria-hidden="true">
                  <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.7}>
                    <rect x="9" y="9" width="10" height="10" rx="1.5" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 15V5h10" />
                  </svg>
                </span>
              </kbd>
            </article>
          ))}
        </div>
      </SectionPanel>

      <SectionPanel className="home-feature-grid feature-mosaic">
        {FEATURES.slice(0, 2).map((feature) => (
          <article key={feature.title} className={`feature-card ${feature.area}`}>
            <div className="feature-card-top">
              <FeatureIcon>{feature.icon}</FeatureIcon>
              <span className="feature-title">{feature.title}</span>
            </div>
            <p className="feature-copy">{feature.copy}</p>
            <span className={`doc-chip feature-tag ${feature.tone}`}>{feature.tag}</span>
          </article>
        ))}

        <article className="feature-card centerpiece">
          <div className="feature-mark">A7</div>
          <h2 className="feature-center-title">A language for building reliable systems.</h2>
          <p className="feature-center-copy">Predictable. Performant. Practical.</p>
        </article>

        {FEATURES.slice(2).map((feature) => (
          <article key={feature.title} className={`feature-card ${feature.area}`}>
            <div className="feature-card-top">
              <FeatureIcon>{feature.icon}</FeatureIcon>
              <span className="feature-title">{feature.title}</span>
            </div>
            <p className="feature-copy">{feature.copy}</p>
            <span className={`doc-chip feature-tag ${feature.tone}`}>{feature.tag}</span>
          </article>
        ))}
      </SectionPanel>

      <SectionPanel className="home-pipeline pipeline-showcase">
        <div className="pipeline-intro">
          <p className="section-label">Under the hood</p>
          <h2 className="home-section-title">A simple, transparent compiler pipeline.</h2>
          <p className="pipeline-intro-copy">
            Built for speed, debuggability, and clear diagnostics. Each stage is explicit, inspectable,
            and designed to be understood by reading the output.
          </p>
          <Link to="/pipeline" className="pipeline-intro-link">
            Learn more about the compiler <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="pipeline-stage-grid">
          <div className="pipeline-stage-row">
            {PIPELINE.map((stage, index) => (
              <Fragment key={stage.title}>
                <article className="pipeline-tile">
                  <div className="pipeline-tile-icon" aria-hidden="true">
                    {stage.icon}
                  </div>
                  <span className="pipeline-tile-title">{stage.title}</span>
                <span className="pipeline-tile-copy">{stage.copy}</span>
              </article>
                {index < PIPELINE.length - 1 ? <span className="pipeline-arrow" aria-hidden="true">→</span> : null}
              </Fragment>
            ))}
          </div>

          <div className="pipeline-image-frame" aria-hidden="true" />
        </div>
      </SectionPanel>

      <SectionPanel className="home-highlights highlights-section">
        <div className="highlights-intro">
          <p className="section-label">Language highlights</p>
          <h2 className="home-section-title">Features that help you ship with confidence.</h2>
          <Link to="/language" className="pipeline-intro-link">
            Explore the language <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="highlights-grid">
          {HIGHLIGHTS.map((item) => (
            <article key={item.title} className="highlight-item">
              <div className="highlight-icon" aria-hidden="true">
                {item.icon}
              </div>
              <div className="highlight-title">{item.title}</div>
              <div className="highlight-copy">{item.copy}</div>
            </article>
          ))}
        </div>
      </SectionPanel>

      <SectionPanel className="home-testimonials testimonial-section">
        <div style={{ padding: '24px 24px 0' }}>
          <p className="section-label">Trusted by builders</p>
        </div>

        <div className="testimonial-grid" style={{ padding: '0 24px 24px' }}>
          {TESTIMONIALS.map((item) => (
            <article key={item.name} className="testimonial-card">
              <p className="testimonial-quote">“{item.quote}”</p>
              <div className="testimonial-meta">
                <span className="testimonial-name">{item.name}</span>
                <span className="testimonial-role">{item.role}</span>
              </div>
            </article>
          ))}
        </div>
      </SectionPanel>

      <SectionPanel className="home-cta-panel home-cta">
        <div className="home-cta-copy">
          <h2 className="home-cta-title">Ready to build without recursion?</h2>
          <p>Join the community and help shape the future of A7.</p>

          <div className="home-cta-actions">
            <Link to="/start" className="primary-action">
              Get started <span aria-hidden="true">→</span>
            </Link>
            <a
              href="https://github.com/Airbus5717/a7-py"
              className="secondary-action"
              target="_blank"
              rel="noopener noreferrer"
            >
              Star on GitHub <span aria-hidden="true">↗</span>
            </a>
          </div>

          <div className="site-footer-grid">
            <div className="site-footer-brand">
              <div className="site-footer-title">A7</div>
              <div>© 2024 The A7 Project</div>
              <div>MIT License</div>
            </div>

            <div className="site-footer-column">
              <h3>Learn</h3>
              <div className="site-footer-links">
                <Link to="/start">Guide</Link>
                <Link to="/language">Reference</Link>
                <Link to="/examples">Examples</Link>
                <Link to="/pipeline">Pipeline</Link>
              </div>
            </div>

            <div className="site-footer-column">
              <h3>Community</h3>
              <div className="site-footer-links">
                <a href="https://github.com/Airbus5717/a7-py" target="_blank" rel="noopener noreferrer">GitHub</a>
                <Link to="/contributing">Contributing</Link>
                <Link to="/status">Status</Link>
                <Link to="/changelog">Changelog</Link>
              </div>
            </div>

            <div className="site-footer-column">
              <h3>Resources</h3>
              <div className="site-footer-links">
                <Link to="/internals">Internals</Link>
                <Link to="/testing">Testing</Link>
                <Link to="/stdlib">Stdlib</Link>
                <Link to="/cli">CLI</Link>
              </div>
            </div>

            <div className="site-footer-column">
              <h3>Stay up to date</h3>
              <div className="site-footer-note">Get the latest news and releases.</div>
              <div className="site-footer-newsletter">
                <span>Email address</span>
                <span aria-hidden="true">→</span>
              </div>
            </div>
          </div>
        </div>

        <div className="home-cta-media" aria-hidden="true" />
      </SectionPanel>
    </div>
  )
}

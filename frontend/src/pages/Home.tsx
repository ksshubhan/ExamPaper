import { Link } from 'react-router-dom'
import { FORMATS } from '../data/catalog'

export default function Home() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-12">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        ExamPaper
      </h1>
      <p className="mt-3 max-w-xl text-lg text-[var(--muted)]">
        Original past papers and worksheets, generated for your exam board.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {FORMATS.map((f) => (
          <Link
            key={f.slug}
            to={`/${f.slug}`}
            className="flex min-h-28 items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)] text-xl font-semibold text-[var(--text)] shadow-sm transition hover:border-[var(--muted)] active:scale-[0.99]"
          >
            {f.featureTitle}
          </Link>
        ))}
      </div>
    </div>
  )
}

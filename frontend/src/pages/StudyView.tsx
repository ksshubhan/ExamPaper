import { useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import {
  FORMATS,
  getBoard,
  getFormat,
  getQualification,
  getSubject,
} from '../data/catalog'
import Breadcrumb from '../components/Breadcrumb'
import GeneratedQuestion from '../components/GeneratedQuestion'
import { generateItem } from '../lib/api'
import type { Item } from '../lib/types'

export default function StudyView() {
  const { feature, qualification, board, subject } = useParams()
  const format = getFormat(feature)
  const qual = getQualification(qualification)
  const examBoard = getBoard(qualification, board)
  const subj = getSubject(subject)

  const [item, setItem] = useState<Item | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Any unknown / mismatched slug -> back to the front door.
  if (!format || !qual || !examBoard || !subj) {
    return <Navigate to="/" replace />
  }

  // Everything except the format segment stays pinned.
  const context = `${qual.slug}/${examBoard.slug}/${subj.slug}`

  async function handleGenerate() {
    if (!format || !qual || !examBoard || !subj) return
    setLoading(true)
    setError(null)
    try {
      const generated = await generateItem({
        format: format.slug,
        qualification: qual.slug,
        board: examBoard.slug,
        subject: subj.slug,
      })
      setItem(generated)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-8">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: format.featureTitle, to: `/${format.slug}` },
          { label: qual.name, to: `/${format.slug}/${qual.slug}` },
          {
            label: examBoard.name,
            to: `/${format.slug}/${qual.slug}/${examBoard.slug}`,
          },
          { label: subj.name },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">{subj.name}</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        {examBoard.name} · {qual.name}
      </p>

      <Link
        to={`/${format.slug}/${context}/build`}
        className="mt-4 inline-flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-semibold transition hover:border-[var(--muted)]"
      >
        Build a full paper from topics →
      </Link>

      {/* Format tabs: only the :feature segment changes, never the rest. */}
      <div className="mt-5 flex gap-2" role="tablist" aria-label="Format">
        {FORMATS.map((f) => {
          const active = f.slug === format.slug
          return (
            <Link
              key={f.slug}
              to={`/${f.slug}/${context}`}
              role="tab"
              aria-selected={active}
              className={
                'rounded-full px-5 py-2.5 text-sm font-medium transition ' +
                (active
                  ? 'bg-[var(--accent)] text-[var(--accent-text)]'
                  : 'border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] hover:border-[var(--muted)]')
              }
            >
              {f.label}
            </Link>
          )
        })}
      </div>

      <div className="mt-5 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm">
        <h2 className="text-lg font-semibold">
          {format.label} · {subj.name}
        </h2>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Generate an original {examBoard.name} {qual.name}{' '}
          {format.label.toLowerCase()} for {subj.name}.
        </p>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={loading}
          className="mt-5 rounded-xl bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-[var(--accent-text)] transition active:scale-[0.99] disabled:opacity-60"
        >
          {loading ? 'Generating…' : item ? 'Generate another' : 'Generate'}
        </button>
        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      </div>

      {item && (
        <div className="mt-6">
          <GeneratedQuestion item={item} />
        </div>
      )}
    </div>
  )
}

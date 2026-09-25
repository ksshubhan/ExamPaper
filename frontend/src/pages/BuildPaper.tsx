import { useEffect, useMemo, useState } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { Navigate, useParams } from 'react-router-dom'
import { getBoard, getFormat, getQualification, getSubject } from '../data/catalog'
import Breadcrumb from '../components/Breadcrumb'
import PaperPreview, {
  MarkSchemeDocument,
  PaperDocument,
  PaperSheet,
} from '../components/PaperPreview'
import { generatePaper, getTopics, renderPdf } from '../lib/api'
import type { Paper, TopicGroup } from '../lib/types'

const MARK_PRESETS = [25, 40, 60, 80]

/** Serialize every same-origin stylesheet so the PDF renderer has our CSS. */
function collectCss(): string {
  let css = ''
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      for (const rule of Array.from(sheet.cssRules)) css += rule.cssText + '\n'
    } catch {
      // A cross-origin stylesheet we can't read — not ours, skip it.
    }
  }
  return css
}

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function BuildPaper() {
  const { feature, qualification, board, subject } = useParams()
  const format = getFormat(feature)
  const qual = getQualification(qualification)
  const examBoard = getBoard(qualification, board)
  const subj = getSubject(subject)

  const [groups, setGroups] = useState<TopicGroup[]>([])
  const [topicsError, setTopicsError] = useState<string | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [calculator, setCalculator] = useState(false)
  const [tier, setTier] = useState<'foundation' | 'higher'>('higher')
  const [targetMarks, setTargetMarks] = useState(80)
  const [includeAnswers, setIncludeAnswers] = useState(true)

  const [paper, setPaper] = useState<Paper | null>(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTopics()
      .then(setGroups)
      .catch((e) =>
        setTopicsError(e instanceof Error ? e.message : 'Could not load topics.'),
      )
  }, [])

  // A non-calculator paper can't use calculator-only topics.
  const visibleGroups = useMemo(() => {
    if (calculator) return groups
    return groups
      .map((g) => ({
        ...g,
        topics: g.topics.filter((t) => !t.requires_calculator),
      }))
      .filter((g) => g.topics.length > 0)
  }, [groups, calculator])

  if (!format || !qual || !examBoard || !subj) {
    return <Navigate to="/" replace />
  }

  const context = `${format.slug}/${qual.slug}/${examBoard.slug}/${subj.slug}`

  function toggle(slug: string) {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(slug) ? next.delete(slug) : next.add(slug)
      return next
    })
  }

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      const result = await generatePaper({
        format: format!.slug,
        qualification: qual!.slug,
        board: examBoard!.slug,
        subject: subj!.slug,
        calculator,
        tier,
        topics: [...selected],
        target_marks: targetMarks,
        include_answers: includeAnswers,
      })
      setPaper(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  async function handleDownload() {
    if (!paper) return
    setDownloading(true)
    setError(null)
    try {
      const css = collectCss()
      // The question paper — never contains answers.
      const paperHtml = renderToStaticMarkup(
        <PaperSheet>
          <PaperDocument paper={paper} />
        </PaperSheet>,
      )
      saveBlob(await renderPdf(paperHtml, css, 'paper.pdf'), 'paper.pdf')
      // The mark scheme ships as its own separate PDF.
      if (paper.include_answers) {
        const schemeHtml = renderToStaticMarkup(
          <PaperSheet>
            <MarkSchemeDocument paper={paper} />
          </PaperSheet>,
        )
        saveBlob(
          await renderPdf(schemeHtml, css, 'mark-scheme.pdf'),
          'mark-scheme.pdf',
        )
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not build the PDF.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-8">
      <div className="no-print">
        <Breadcrumb
          items={[
            { label: 'Home', to: '/' },
            { label: format.featureTitle, to: `/${format.slug}` },
            { label: qual.name, to: `/${format.slug}/${qual.slug}` },
            {
              label: examBoard.name,
              to: `/${format.slug}/${qual.slug}/${examBoard.slug}`,
            },
            { label: subj.name, to: `/${context}` },
            { label: 'Build a paper' },
          ]}
        />

        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          Build a custom paper
        </h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Pick the topics you want to practise. We assemble an original{' '}
          {examBoard.name} {qual.name} {subj.name} paper, ramped easy to hard.
        </p>

        {/* Options */}
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Segmented
            label="Tier"
            value={tier}
            options={[
              { value: 'foundation', label: 'Foundation' },
              { value: 'higher', label: 'Higher' },
            ]}
            onChange={(v) => setTier(v as 'foundation' | 'higher')}
          />
          <Segmented
            label="Paper type"
            value={calculator ? 'calc' : 'noncalc'}
            options={[
              { value: 'noncalc', label: 'Non-calculator' },
              { value: 'calc', label: 'Calculator' },
            ]}
            onChange={(v) => setCalculator(v === 'calc')}
          />
          <Segmented
            label="Length"
            value={String(targetMarks)}
            options={MARK_PRESETS.map((m) => ({
              value: String(m),
              label: `${m} marks`,
            }))}
            onChange={(v) => setTargetMarks(Number(v))}
          />
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={includeAnswers}
              onChange={(e) => setIncludeAnswers(e.target.checked)}
              className="h-4 w-4 accent-[var(--accent)]"
            />
            Include answers &amp; mark scheme
          </label>
        </div>

        {/* Topic picker */}
        {topicsError && (
          <p className="mt-6 text-sm text-red-500">{topicsError}</p>
        )}
        <div className="mt-6 space-y-5">
          {visibleGroups.map((g) => (
            <div key={g.strand}>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                {g.strand}
              </h2>
              <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {g.topics.map((t) => {
                  const on = selected.has(t.slug)
                  return (
                    <button
                      key={t.slug}
                      type="button"
                      onClick={() => toggle(t.slug)}
                      aria-pressed={on}
                      className={
                        'flex items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition ' +
                        (on
                          ? 'border-[var(--accent)] bg-[var(--hover)]'
                          : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--muted)]')
                      }
                    >
                      <span>
                        <span className="font-medium">{t.name}</span>
                        <span className="ml-2 text-xs text-[var(--muted)]">
                          {t.spec_ref} · grade {t.grade_band}
                        </span>
                      </span>
                      <span
                        className={
                          'ml-3 grid h-5 w-5 shrink-0 place-items-center rounded-md border text-xs ' +
                          (on
                            ? 'border-[var(--accent)] bg-[var(--accent)] text-[var(--accent-text)]'
                            : 'border-[var(--border)]')
                        }
                      >
                        {on ? '✓' : ''}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-7 flex items-center gap-4">
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading || selected.size === 0}
            className="rounded-xl bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-[var(--accent-text)] transition active:scale-[0.99] disabled:opacity-50"
          >
            {loading
              ? 'Assembling…'
              : paper
                ? 'Regenerate paper'
                : 'Generate paper'}
          </button>
          <span className="text-sm text-[var(--muted)]">
            {selected.size === 0
              ? 'Select at least one topic'
              : `${selected.size} topic${selected.size === 1 ? '' : 's'} selected`}
          </span>
        </div>
        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}

        {paper && paper.notes.length > 0 && (
          <div className="mt-5 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
            {paper.notes.map((n, i) => (
              <p key={i}>{n}</p>
            ))}
          </div>
        )}

        {paper && paper.questions.length > 0 && (
          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-[var(--muted)]">
              {paper.questions.length} questions · {paper.total_marks} marks ·{' '}
              {paper.duration_minutes} min
            </p>
            <button
              type="button"
              onClick={handleDownload}
              disabled={downloading}
              className="rounded-xl bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-[var(--accent-text)] transition hover:opacity-90 disabled:opacity-50"
            >
              {downloading
                ? 'Preparing PDF…'
                : paper.include_answers
                  ? 'Download paper + mark scheme'
                  : 'Download paper PDF'}
            </button>
          </div>
        )}
      </div>

      {paper && paper.questions.length > 0 && (
        <div className="mt-6">
          <PaperPreview paper={paper} />
        </div>
      )}
    </div>
  )
}

function Segmented({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-[var(--muted)]">{label}:</span>
      <div className="flex gap-1 rounded-full border border-[var(--border)] bg-[var(--surface)] p-1">
        {options.map((o) => {
          const active = o.value === value
          return (
            <button
              key={o.value}
              type="button"
              onClick={() => onChange(o.value)}
              aria-pressed={active}
              className={
                'rounded-full px-3 py-1.5 text-sm font-medium transition ' +
                (active
                  ? 'bg-[var(--accent)] text-[var(--accent-text)]'
                  : 'text-[var(--text)] hover:bg-[var(--hover)]')
              }
            >
              {o.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

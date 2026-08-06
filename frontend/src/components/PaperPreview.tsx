import type { ReactNode } from 'react'
import type { Item, Paper } from '../lib/types'
import { BracketsIcon } from './icons'

/**
 * Renders a Paper as an exam-style sheet. The sheet is always white/black so it
 * matches what prints (the print stylesheet shows only `.printable`). Page
 * breaks and break-avoidance are driven by the `.page-break` / `.avoid-break`
 * classes defined in index.css.
 *
 * The cover mirrors a real Edexcel front page (layout + wording), with the
 * Pearson logo / paper code / barcode replaced by Learnify's own versions.
 */
export default function PaperPreview({ paper }: { paper: Paper }) {
  return (
    <div className="printable paper-sheet mx-auto max-w-[820px] bg-white text-black shadow-sm">
      <Cover paper={paper} />

      {/* Questions start on a fresh page, after the cover's "Turn over". */}
      <section className="page-break px-12 py-10">
        {paper.questions.map((q, i) => (
          <QuestionBlock key={q.id} item={q} number={i + 1} />
        ))}
      </section>

      {paper.include_answers && paper.questions.length > 0 && (
        <Answers paper={paper} />
      )}
    </div>
  )
}

// --------------------------------------------------------------------------- #
// Cover page
// --------------------------------------------------------------------------- #
function subjectName(slug: string): string {
  if (slug === 'maths') return 'Mathematics'
  return slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDuration(min: number): string {
  const h = Math.floor(min / 60)
  const m = min % 60
  const parts: string[] = []
  if (h) parts.push(`${h} hour${h === 1 ? '' : 's'}`)
  if (m) parts.push(`${m} minutes`)
  return parts.join(' ') || `${min} minutes`
}

function coverDate(): string {
  const d = new Date()
  const weekday = d.toLocaleDateString('en-GB', { weekday: 'long' })
  const month = d.toLocaleDateString('en-GB', { month: 'long' })
  return `${weekday} ${d.getDate()} ${month} ${d.getFullYear()}`
}

// Shared box styling for the cover (uniform grey rounded borders).
const BOX = 'rounded-[10px] border-[3px] border-[#63676d]'

function Cover({ paper }: { paper: Paper }) {
  const higher = paper.tier === 'higher'
  const reference = `LMA1/${paper.calculator ? '2' : '1'}${higher ? 'H' : 'F'}`
  const paperLabel = paper.calculator
    ? 'PAPER 2 (Calculator)'
    : 'PAPER 1 (Non-Calculator)'
  const code = `L${paper.id.replace('paper-', '').toUpperCase().slice(0, 8)}`

  return (
    <section className="flex min-h-[1040px] flex-col px-10 py-9">
      {/* ---- Top details box ---- */}
      <div className="rounded-[16px] border-[4px] border-[#63676d] p-4">
        {/* Header line — must stay on one line */}
        <p className="text-center text-[13px] font-bold">
          Please check the examination details below before entering your
          candidate information
        </p>

        {/* Candidate surname / Other names — two separate rounded boxes */}
        <div className="mt-3 flex gap-2.5">
          <div className={`${BOX} flex-[1.5] px-3 pb-4 pt-1.5`}>
            <span className="text-[14px]">Candidate surname</span>
          </div>
          <div className={`${BOX} flex-1 px-3 pb-4 pt-1.5`}>
            <span className="text-[14px]">Other names</span>
          </div>
        </div>

        {/* Centre / Candidate number digit boxes */}
        <div className="mt-3 flex gap-12">
          <div>
            <p className="text-[14px]">Centre Number</p>
            <div className="mt-1">
              <DigitBoxes count={5} />
            </div>
          </div>
          <div>
            <p className="text-[14px]">Candidate Number</p>
            <div className="mt-1">
              <DigitBoxes count={4} />
            </div>
          </div>
        </div>

        {/* Awarding body */}
        <p className="mt-4 text-[26px] font-black leading-none tracking-tight">
          Pearson Edexcel Level 1/Level 2 GCSE (9–1)
        </p>

        {/* Date */}
        <div className={`${BOX} mt-3 w-[86%] px-4 py-2`}>
          <p className="text-[24px] font-black">{coverDate()}</p>
        </div>

        {/* Time + paper reference */}
        <div className="mt-3 flex items-start gap-4">
          <p className="flex-1 self-center text-[17px]">
            Morning (Time: {formatDuration(paper.duration_minutes)})
          </p>
          <div className="flex h-14 items-stretch">
            <div className="flex items-center border-[3px] border-r-0 border-[#63676d] bg-white px-2.5 text-[14px] font-bold leading-[1.05]">
              Paper
              <br />
              reference
            </div>
            <div className="relative flex items-center bg-[#5b5f65] px-4">
              <span className="text-[28px] font-black tracking-wide text-white">
                {reference}
              </span>
              {/* registration squares at the top-right corner */}
              <span className="absolute -top-1.5 right-2 flex gap-1">
                <span className="h-3 w-3 bg-[#9aa0a6]" />
                <span className="h-3 w-3 border-2 border-[#9aa0a6] bg-white" />
              </span>
            </div>
          </div>
        </div>

        {/* Subject */}
        <div className={`${BOX} relative mt-3 min-h-[186px] px-4 py-3`}>
          <div>
            <p className="text-[34px] font-black leading-none">
              {subjectName(paper.subject)}
            </p>
            <p className="mt-2 text-[19px] font-black">{paperLabel}</p>
            <p className="text-[19px] font-black">
              {higher ? 'Higher Tier' : 'Foundation Tier'}
            </p>
          </div>
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <CalcIcon crossed={!paper.calculator} />
          </div>
        </div>

        {/* Equipment + total marks */}
        <div className="mt-3 flex gap-3">
          <div className={`${BOX} flex-1 px-3 py-2 text-[14px] leading-snug`}>
            <strong>You must have:</strong> Ruler graduated in centimetres and
            millimetres, protractor, pair of compasses, pen, HB or B pencil,
            eraser, {paper.calculator ? 'calculator, ' : ''}Formulae Sheet
            (enclosed). Tracing paper may be used.
          </div>
          <div className={`${BOX} w-[120px] px-3 py-2 text-[14px]`}>
            Total Marks
          </div>
        </div>
      </div>

      {/* ---- Instructions / Information / Advice ---- */}
      <div className="mt-6 space-y-5 text-[14px] leading-relaxed">
        <Section
          title="Instructions"
          items={[
            <>
              Use <strong>black</strong> ink or ball-point pen.
            </>,
            <>
              If pencil is used for diagrams/sketches/graphs it must be dark (HB
              or B).
            </>,
            <>
              <strong>Fill in the boxes</strong> at the top of this page with
              your name, centre number and candidate number.
            </>,
            <>
              Answer <strong>all</strong> questions.
            </>,
            <>
              Answer the questions in the spaces provided{' '}
              <em>– there may be more space than you need.</em>
            </>,
            <>
              You must <strong>show all your working</strong>.
            </>,
            <>
              Diagrams are <strong>NOT</strong> accurately drawn, unless
              otherwise indicated.
            </>,
            paper.calculator ? (
              <>
                <strong>You may use a calculator.</strong>
              </>
            ) : (
              <>
                <strong>Calculators may not be used.</strong>
              </>
            ),
          ]}
        />
        <Section
          title="Information"
          items={[
            <>The total mark for this paper is {paper.total_marks}.</>,
            <>
              The marks for <strong>each</strong> question are shown in brackets{' '}
              <em>– use this as a guide as to how much time to spend on each question.</em>
            </>,
          ]}
        />
        <Section
          title="Advice"
          items={[
            <>Read each question carefully before you start to answer it.</>,
            <>Try to answer every question.</>,
            <>Check your answers if you have time at the end.</>,
          ]}
        />
      </div>

      {/* ---- Footer (Learnify versions of code / barcode / logo) ---- */}
      <div className="mt-auto">
        <p className="pb-3 text-right text-sm font-bold italic">Turn over ▸</p>
        <div className="flex items-end justify-between border-t border-neutral-200 pt-3">
          <div className="text-xs">
            <p className="text-base font-bold tracking-wide">{code}</p>
            <p className="text-neutral-500">
              © {new Date().getFullYear()} Learnify
            </p>
            <p className="text-neutral-500">L:1/1/1/</p>
          </div>
          <Barcode value={paper.id} />
          <LearnifyMark />
        </div>
      </div>
    </section>
  )
}

/** A rounded group of connected digit cells (rounded outer, square dividers). */
function DigitBoxes({ count }: { count: number }) {
  return (
    <div className="flex overflow-hidden rounded-[6px] border-[3px] border-[#63676d]">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={'h-11 w-11' + (i ? ' border-l-[3px] border-[#63676d]' : '')}
        />
      ))}
    </div>
  )
}

/** A scientific-calculator illustration, drawn at a slight angle like the real
 *  paper; crossed out for non-calculator papers. */
function CalcIcon({ crossed }: { crossed: boolean }) {
  const cols = [47, 60, 73, 86, 99]
  const rows = [66, 77, 88, 99, 110, 121, 132]
  return (
    <svg width="150" height="170" viewBox="0 0 150 170" className="shrink-0">
      <g transform="rotate(9 75 90)">
        {/* body */}
        <rect
          x="40"
          y="14"
          width="80"
          height="150"
          rx="9"
          fill="#d7d9dd"
          stroke="#1e1e1e"
          strokeWidth="2.5"
        />
        <text x="50" y="27" fontSize="6.5" fontWeight="bold" fill="#1e1e1e">
          SCIENTIFIC
        </text>
        {/* screen */}
        <rect
          x="47"
          y="31"
          width="66"
          height="26"
          rx="3"
          fill="#cfd6cd"
          stroke="#1e1e1e"
          strokeWidth="1.6"
        />
        <text x="108" y="49" fontSize="9" textAnchor="end" fill="#2a2a2a">
          0.
        </text>
        {/* buttons */}
        {rows.map((y, r) =>
          cols.map((x, c) => (
            <rect
              key={`${r}-${c}`}
              x={x}
              y={y}
              width="10"
              height="8"
              rx="1.4"
              fill={r < 2 ? '#b7babf' : '#f3f3f4'}
              stroke="#1e1e1e"
              strokeWidth="1"
            />
          )),
        )}
        {crossed && (
          <g stroke="#1e1e1e" strokeWidth="4.5" strokeLinecap="round">
            <line x1="40" y1="14" x2="120" y2="164" />
            <line x1="120" y1="14" x2="40" y2="164" />
          </g>
        )}
      </g>
    </svg>
  )
}

/** A deterministic faux barcode derived from the paper id. */
function Barcode({ value }: { value: string }) {
  const bars: { x: number; w: number }[] = []
  let x = 0
  for (let i = 0; i < value.length; i++) {
    const w = (value.charCodeAt(i) % 3) + 1
    bars.push({ x, w })
    x += w + ((value.charCodeAt(i) % 2) + 1)
  }
  const width = x
  return (
    <div className="flex flex-col items-center">
      <svg width={width} height="36" viewBox={`0 0 ${width} 36`}>
        {bars.map((b, i) => (
          <rect key={i} x={b.x} y="0" width={b.w} height="36" fill="black" />
        ))}
      </svg>
      <span className="mt-1 font-mono text-[10px] tracking-widest text-neutral-600">
        {value.replace('paper-', '').toUpperCase()}
      </span>
    </div>
  )
}

function LearnifyMark() {
  return (
    <div className="flex flex-col items-center">
      <div className="grid h-8 w-8 place-items-center rounded-md bg-neutral-900 text-white">
        <BracketsIcon className="h-4 w-4" />
      </div>
      <span className="mt-1 text-sm font-bold tracking-tight">Learnify</span>
    </div>
  )
}

function Section({ title, items }: { title: string; items: ReactNode[] }) {
  return (
    <div>
      <h2 className="text-lg font-bold">{title}</h2>
      <ul className="mt-1 space-y-1 pl-5">
        {items.map((node, i) => (
          <li key={i} className="relative">
            <span className="absolute -left-4 font-bold">•</span>
            {node}
          </li>
        ))}
      </ul>
    </div>
  )
}

// --------------------------------------------------------------------------- #
// Questions + answers (unchanged layout)
// --------------------------------------------------------------------------- #
function QuestionBlock({ item, number }: { item: Item; number: number }) {
  return (
    <article className="avoid-break mb-10">
      <div className="flex gap-3">
        <span className="text-base font-bold">{number}</span>
        <div className="flex-1">
          {item.stem && (
            <p className="whitespace-pre-line leading-relaxed">{item.stem}</p>
          )}

          {item.diagram && (
            <figure className="my-4">
              <div
                className="mx-auto max-w-[280px]"
                role="img"
                aria-label={item.diagram.alt}
                dangerouslySetInnerHTML={{ __html: item.diagram.svg }}
              />
              {item.diagram.not_to_scale && (
                <figcaption className="mt-1 text-center text-xs italic text-neutral-500">
                  Diagram NOT accurately drawn
                </figcaption>
              )}
            </figure>
          )}

          {item.parts.map((part, i) => (
            <div key={i} className="mt-3">
              <div className="flex items-start justify-between gap-4">
                <p className="leading-relaxed">
                  {part.label && (
                    <span className="mr-2 font-semibold">({part.label})</span>
                  )}
                  {part.prompt}
                </p>
                <span className="shrink-0 text-sm text-neutral-500">
                  ({part.marks})
                </span>
              </div>
              <AnswerSpace marks={part.marks} />
            </div>
          ))}

          <p className="mt-3 text-right text-xs font-semibold text-neutral-600">
            (Total for Question {number} is {item.total_marks}{' '}
            {item.total_marks === 1 ? 'mark' : 'marks'})
          </p>
        </div>
      </div>
    </article>
  )
}

function AnswerSpace({ marks }: { marks: number }) {
  const height = 48 + marks * 26
  return (
    <div
      className="mt-3 rounded-sm border border-neutral-200"
      style={{ height }}
      aria-hidden
    />
  )
}

function Answers({ paper }: { paper: Paper }) {
  return (
    <section className="page-break border-t border-neutral-300 px-12 py-10">
      <h2 className="text-xl font-bold">Answers and mark scheme</h2>
      <p className="mt-1 text-sm text-neutral-500">{paper.title}</p>

      <ol className="mt-6 space-y-5">
        {paper.questions.map((q, i) => (
          <li key={q.id} className="avoid-break">
            <div className="flex gap-3">
              <span className="font-bold">{i + 1}</span>
              <div className="flex-1">
                <p className="font-semibold">{q.parts[0]?.answer}</p>
                <ul className="mt-1 space-y-0.5 text-sm text-neutral-700">
                  {q.parts.flatMap((part) =>
                    part.mark_scheme.map((step, j) => (
                      <li key={j} className="flex gap-2">
                        <span className="font-mono font-semibold">
                          {step.code}
                        </span>
                        <span>
                          {step.description}
                          {step.working ? ` — ${step.working}` : ''}
                        </span>
                      </li>
                    )),
                  )}
                </ul>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

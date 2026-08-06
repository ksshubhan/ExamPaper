import { Link } from 'react-router-dom'

interface NavCardProps {
  to: string
  title: string
  description?: string
  meta?: string
  action: string
}

/** Left-aligned info card: title, optional blurb, a meta line, and an action link. */
export default function NavCard({
  to,
  title,
  description,
  meta,
  action,
}: NavCardProps) {
  return (
    <Link
      to={to}
      className="group flex flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm transition hover:border-[var(--muted)] active:scale-[0.99]"
    >
      <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
      {description && (
        <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
          {description}
        </p>
      )}
      {meta && <p className="mt-4 text-sm text-[var(--muted)]">{meta}</p>}
      <span className="mt-3 text-sm font-medium text-[var(--text)]">
        {action}{' '}
        <span
          aria-hidden
          className="inline-block transition-transform group-hover:translate-x-0.5"
        >
          →
        </span>
      </span>
    </Link>
  )
}

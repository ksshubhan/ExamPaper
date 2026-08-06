import { Link } from 'react-router-dom'

export interface Crumb {
  label: string
  /** Omit on the final (current) crumb. */
  to?: string
}

export default function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav
      aria-label="Breadcrumb"
      className="flex flex-wrap items-center gap-1.5 text-sm"
    >
      {items.map((c, i) => {
        const last = i === items.length - 1
        return (
          <span key={`${c.label}-${i}`} className="flex items-center gap-1.5">
            {c.to && !last ? (
              <Link
                to={c.to}
                className="text-[var(--muted)] transition-colors hover:text-[var(--text)]"
              >
                {c.label}
              </Link>
            ) : (
              <span
                aria-current={last ? 'page' : undefined}
                className={last ? 'font-medium text-[var(--text)]' : 'text-[var(--muted)]'}
              >
                {c.label}
              </span>
            )}
            {!last && (
              <span aria-hidden className="text-[var(--muted)]">
                ›
              </span>
            )}
          </span>
        )
      })}
    </nav>
  )
}

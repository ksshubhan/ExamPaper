import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface BackLinkProps {
  to: string
  children: ReactNode
}

export default function BackLink({ to, children }: BackLinkProps) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1.5 py-1 text-sm text-[var(--muted)] transition-colors hover:text-[var(--text)]"
    >
      <span aria-hidden>←</span>
      {children}
    </Link>
  )
}

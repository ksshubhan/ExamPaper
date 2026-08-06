import { Link } from 'react-router-dom'

interface SubjectCardProps {
  to: string
  name: string
}

export default function SubjectCard({ to, name }: SubjectCardProps) {
  return (
    <Link
      to={to}
      className="flex min-h-24 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 text-center text-base font-medium text-[var(--text)] shadow-sm transition hover:border-[var(--muted)] active:scale-[0.99]"
    >
      {name}
    </Link>
  )
}

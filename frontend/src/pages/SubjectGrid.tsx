import { Navigate, useParams } from 'react-router-dom'
import {
  SUBJECTS,
  getBoard,
  getFormat,
  getQualification,
} from '../data/catalog'
import Breadcrumb from '../components/Breadcrumb'
import SubjectCard from '../components/SubjectCard'

export default function SubjectGrid() {
  const { feature, qualification, board } = useParams()
  const format = getFormat(feature)
  const qual = getQualification(qualification)
  const examBoard = getBoard(qualification, board)

  // Any unknown / mismatched slug -> back to the front door.
  if (!format || !qual || !examBoard) return <Navigate to="/" replace />

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: format.featureTitle, to: `/${format.slug}` },
          { label: qual.name, to: `/${format.slug}/${qual.slug}` },
          { label: examBoard.name },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold tracking-tight sm:text-3xl">
        {examBoard.name} {qual.name} {format.featureTitle}
      </h1>
      <p className="mt-2 text-[var(--muted)]">Choose a subject.</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {SUBJECTS.map((s) => (
          <SubjectCard
            key={s.slug}
            to={`/${format.slug}/${qual.slug}/${examBoard.slug}/${s.slug}`}
            name={s.name}
          />
        ))}
      </div>
    </div>
  )
}

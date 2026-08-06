import { Navigate, useParams } from 'react-router-dom'
import { SUBJECTS, getBoards, getFormat, getQualification } from '../data/catalog'
import Breadcrumb from '../components/Breadcrumb'
import NavCard from '../components/NavCard'

export default function BoardGrid() {
  const { feature, qualification } = useParams()
  const format = getFormat(feature)
  const qual = getQualification(qualification)

  // Unknown feature or qualification slug -> back to the front door.
  if (!format || !qual) return <Navigate to="/" replace />

  const boards = getBoards(qual.slug)

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: format.featureTitle, to: `/${format.slug}` },
          { label: qual.name },
        ]}
      />
      <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
        {qual.name} {format.featureTitle}
      </h1>
      <p className="mt-3 max-w-2xl text-[var(--muted)]">
        Choose your exam board.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {boards.map((b) => (
          <NavCard
            key={b.slug}
            to={`/${format.slug}/${qual.slug}/${b.slug}`}
            title={b.name}
            meta={`${SUBJECTS.length} subjects`}
            action="View subjects"
          />
        ))}
      </div>
    </div>
  )
}

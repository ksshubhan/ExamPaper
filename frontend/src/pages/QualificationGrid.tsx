import { Navigate, useParams } from 'react-router-dom'
import { QUALIFICATIONS, getBoards, getFormat } from '../data/catalog'
import Breadcrumb from '../components/Breadcrumb'
import NavCard from '../components/NavCard'

export default function QualificationGrid() {
  const { feature } = useParams()
  const format = getFormat(feature)

  // Unknown feature slug -> back to the front door.
  if (!format) return <Navigate to="/" replace />

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      <Breadcrumb
        items={[{ label: 'Home', to: '/' }, { label: format.featureTitle }]}
      />
      <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
        {format.featureTitle}
      </h1>
      <p className="mt-3 max-w-2xl text-[var(--muted)]">
        Choose your qualification to get started.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {QUALIFICATIONS.map((q) => (
          <NavCard
            key={q.slug}
            to={`/${format.slug}/${q.slug}`}
            title={q.name}
            description={q.description}
            meta={`${getBoards(q.slug).length} exam boards`}
            action={`Browse ${format.featureTitle.toLowerCase()}`}
          />
        ))}
      </div>
    </div>
  )
}

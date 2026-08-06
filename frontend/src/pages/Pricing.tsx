import BackLink from '../components/BackLink'

export default function Pricing() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-8">
      <BackLink to="/">Home</BackLink>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">Pricing</h1>
      <p className="mt-3 max-w-xl text-[var(--muted)]">
        Free while in beta. Paid plans for unlimited generation and full mark
        schemes are coming soon.
      </p>
    </div>
  )
}

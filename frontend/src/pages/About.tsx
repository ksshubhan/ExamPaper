import BackLink from '../components/BackLink'

export default function About() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-8">
      <BackLink to="/">Home</BackLink>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">About</h1>
      <p className="mt-3 max-w-xl text-[var(--muted)]">
        Learnify generates original past papers and worksheets tailored to your
        exam board — practice material that mirrors the real thing without ever
        reusing a question.
      </p>
    </div>
  )
}

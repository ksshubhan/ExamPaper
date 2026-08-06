import type {
  GenerateRequest,
  GeneratePaperRequest,
  Item,
  Paper,
  TopicGroup,
} from './types'

/** Generate one question. Calls the FastAPI backend via the Vite /api proxy. */
export async function generateItem(req: GenerateRequest): Promise<Item> {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`Generation failed (${res.status})`)
  }
  return (await res.json()) as Item
}

/** Fetch the pickable topics, grouped by strand. */
export async function getTopics(): Promise<TopicGroup[]> {
  const res = await fetch('/api/topics')
  if (!res.ok) {
    throw new Error(`Could not load topics (${res.status})`)
  }
  return (await res.json()) as TopicGroup[]
}

/** Assemble a full custom paper from the chosen topics. */
export async function generatePaper(req: GeneratePaperRequest): Promise<Paper> {
  const res = await fetch('/api/generate-paper', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`Paper generation failed (${res.status})`)
  }
  return (await res.json()) as Paper
}

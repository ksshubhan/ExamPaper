// Single source of truth for the past-papers / worksheets hierarchy:
//   format  ->  qualification  ->  exam board  ->  subject
// Slugs live in the URL; display names are derived from here.

export type FormatSlug = 'past-papers' | 'worksheets'
export type QualificationSlug = 'gcse' | 'a-level' | 'igcse'
export type BoardSlug = 'aqa' | 'edexcel' | 'ocr' | 'wjec' | 'cie'
export type SubjectSlug =
  | 'maths'
  | 'english-language'
  | 'english-literature'
  | 'biology'
  | 'chemistry'
  | 'physics'
  | 'history'
  | 'geography'

export interface Format {
  slug: FormatSlug
  /** Heading / breadcrumb label, e.g. "Past papers". */
  featureTitle: string
  /** Singular label for tabs and cards, e.g. "Past paper". */
  label: string
}

export interface Qualification {
  slug: QualificationSlug
  name: string
  description: string
}

export interface Board {
  slug: BoardSlug
  name: string
}

export interface Subject {
  slug: SubjectSlug
  name: string
}

export const FORMATS: Format[] = [
  { slug: 'past-papers', featureTitle: 'Past papers', label: 'Past paper' },
  { slug: 'worksheets', featureTitle: 'Worksheets', label: 'Worksheet' },
]

export const QUALIFICATIONS: Qualification[] = [
  {
    slug: 'gcse',
    name: 'GCSE',
    description:
      'Years 10–11 qualification taken by students across England, Wales and Northern Ireland.',
  },
  {
    slug: 'a-level',
    name: 'A-Level',
    description:
      'Advanced level qualification for Years 12–13, required for university entry.',
  },
  {
    slug: 'igcse',
    name: 'IGCSE',
    description: 'International GCSE qualification recognised worldwide.',
  },
]

const BOARD_NAMES: Record<BoardSlug, string> = {
  aqa: 'AQA',
  edexcel: 'Edexcel',
  ocr: 'OCR',
  wjec: 'WJEC',
  cie: 'CIE',
}

// Which boards offer each qualification (counts match the real awarding bodies).
const BOARDS_BY_QUAL: Record<QualificationSlug, BoardSlug[]> = {
  gcse: ['aqa', 'edexcel', 'ocr', 'wjec'],
  'a-level': ['aqa', 'edexcel', 'ocr', 'wjec', 'cie'],
  igcse: ['cie', 'edexcel'],
}

export const SUBJECTS: Subject[] = [
  { slug: 'maths', name: 'Maths' },
  { slug: 'english-language', name: 'English language' },
  { slug: 'english-literature', name: 'English literature' },
  { slug: 'biology', name: 'Biology' },
  { slug: 'chemistry', name: 'Chemistry' },
  { slug: 'physics', name: 'Physics' },
  { slug: 'history', name: 'History' },
  { slug: 'geography', name: 'Geography' },
]

export function getFormat(slug: string | undefined): Format | undefined {
  return FORMATS.find((f) => f.slug === slug)
}

export function getQualification(
  slug: string | undefined,
): Qualification | undefined {
  return QUALIFICATIONS.find((q) => q.slug === slug)
}

/** Boards available for a given qualification. */
export function getBoards(qualification: QualificationSlug): Board[] {
  return BOARDS_BY_QUAL[qualification].map((slug) => ({
    slug,
    name: BOARD_NAMES[slug],
  }))
}

/** A board, only if it actually belongs to the given qualification. */
export function getBoard(
  qualification: string | undefined,
  board: string | undefined,
): Board | undefined {
  const qual = getQualification(qualification)
  if (!qual) return undefined
  return getBoards(qual.slug).find((b) => b.slug === board)
}

export function getSubject(slug: string | undefined): Subject | undefined {
  return SUBJECTS.find((s) => s.slug === slug)
}

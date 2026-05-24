import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(input?: string | number | Date | null): string {
  if (input == null) return ""
  const date = input instanceof Date ? input : new Date(input)
  return date.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  })
}

/** Heading for an archive issue: "Issue 11" when numbered, else the special-edition name. */
export function issueHeading(data: { issue: string }): string {
  return /^\d+$/.test(data.issue) ? `Issue ${data.issue}` : data.issue
}

/** "By A", "By A and B", "By A, B and C", custom byline, or "By Anonymous". */
export function byline(data: { byline?: string; authors?: string[] }): string {
  if (data.byline) return data.byline
  const authors = data.authors
  if (!authors || authors.length === 0) return "By Anonymous"
  if (authors.length === 1) return `By ${authors[0]}`
  return `By ${authors.slice(0, -1).join(", ")} and ${authors[authors.length - 1]}`
}

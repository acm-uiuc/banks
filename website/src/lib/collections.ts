import { getCollection, type CollectionEntry } from "astro:content";
import { slugify, archiveIssueSlug } from "./slug.mjs";

export { slugify };

export type CurrentArticle = CollectionEntry<"current"> & {
  slug: string;
  fullSlug: string;
  excerpt: string;
};

/** Build a plain-text excerpt from raw markdown for feed previews. */
function makeExcerpt(body: string | undefined, max = 200): string {
  if (!body) return "";
  const text = body
    .replace(/```[\s\S]*?```/g, " ")          // fenced code blocks
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")      // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")    // links -> link text
    .replace(/[#>*_`~]/g, "")                   // markdown punctuation
    .replace(/\s+/g, " ")
    .trim();
  if (text.length <= max) return text;
  return text.slice(0, max).replace(/\s+\S*$/, "") + "…";
}

/** Articles of the current issue, sorted for display. */
export async function getCurrentIssueArticles(): Promise<CurrentArticle[]> {
  const raw = await getCollection("current");
  return raw
    .map((article) => {
      const slug = slugify(article.data.slug || article.id);
      return {
        ...article,
        slug,
        fullSlug: `/articles/${slug}`,
        excerpt: makeExcerpt(article.body),
      };
    })
    .sort((a, b) => {
      // explicit `order` first, then newest date, then title
      const ao = a.data.order ?? Number.POSITIVE_INFINITY;
      const bo = b.data.order ?? Number.POSITIVE_INFINITY;
      if (ao !== bo) return ao - bo;
      const ad = a.data.date?.getTime() ?? 0;
      const bd = b.data.date?.getTime() ?? 0;
      if (ad !== bd) return bd - ad;
      return a.data.title.localeCompare(b.data.title);
    });
}

export type ArchiveIssue = CollectionEntry<"archive"> & {
  slug: string;
  fullSlug: string;
};

export async function getArchiveIssues(): Promise<ArchiveIssue[]> {
  const raw = await getCollection("archive");
  return raw.map((issue) => {
    const slug = archiveIssueSlug(issue.data);
    return {
      ...issue,
      slug,
      fullSlug: `/archive/${issue.data.volume}/${slug}`,
    };
  });
}

export type ArchiveVolume = { volume: number; issues: ArchiveIssue[] };

/** Archive grouped by volume — volumes newest-first, issues newest-first. */
export async function getArchiveByVolume(): Promise<ArchiveVolume[]> {
  const issues = await getArchiveIssues();
  const byVolume = new Map<number, ArchiveIssue[]>();
  for (const issue of issues) {
    const list = byVolume.get(issue.data.volume) ?? [];
    list.push(issue);
    byVolume.set(issue.data.volume, list);
  }
  return [...byVolume.entries()]
    .map(([volume, list]) => ({
      volume,
      issues: list.sort((a, b) => b.data.date.getTime() - a.data.date.getTime()),
    }))
    .sort((a, b) => b.volume - a.volume);
}

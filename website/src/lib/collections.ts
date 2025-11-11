import { getCollection } from "astro:content";

export function slugify(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export async function getAllArticles() {
  const rawArticles = await getCollection("articles");
  return rawArticles.map((article) => {
    // If slug is not provided, generate one based on date and title
    // e.g. YYYY-MM-DD-article-title
    const rawSlug = article.data.slug || `${article.data.date.toISOString().split('T')[0]}-${article.data.title}`;
    const generatedSlug = slugify(rawSlug);
    delete article.data.slug;
    return {
      ...article,
      slug: generatedSlug,
      fullSlug: `/articles/${generatedSlug}`,
    };
  });
}

export async function getAllIssues() {
  const rawIssues = await getCollection("issues");
  return rawIssues.map((issue) => {
    const rawSlug = issue.data.slug || issue.data.issue;
    const generatedSlug = slugify(rawSlug);
    delete issue.data.slug;
    return {
      ...issue,
      slug: generatedSlug,
      fullSlug: `/issues/${issue.data.volume.toString()}/${generatedSlug}`,
    };
  });
}

export async function getVolumesToIssuesMap() {
  const issues = await getAllIssues();
  const volumeIssueMap: Record<string, typeof issues> = {};
  issues.forEach((issue) => {
    const volume = issue.data.volume.toString();
    if (!volumeIssueMap[volume]) {
      volumeIssueMap[volume] = [];
    }
    volumeIssueMap[volume].push(issue);
  });
  return volumeIssueMap;
}
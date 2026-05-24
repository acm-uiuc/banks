// Slug + archive-path helpers shared between the Astro site and the
// `collect-archive-assets` build script, so route URLs and copied file
// locations can never drift apart.

/** Turn arbitrary text into a URL-safe slug. */
export function slugify(text) {
  return String(text)
    .trim()
    .toLowerCase()
    .replace(/['‘’"“”]/g, "")        // drop apostrophes/quotes (April Fool's -> april-fools)
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Slug for an archive issue *within* its volume. Used both for the route
 * (`/archive/<volume>/<slug>`) and for the published asset folder.
 * `data` is the issue frontmatter ({ slug?, issue }).
 */
export function archiveIssueSlug(data) {
  return slugify(data.slug ?? data.issue);
}

/** Public URL of a copied archive print artifact (PDF / scan / source). */
export function archiveFileUrl(volume, issueSlug, filename) {
  return `/files/${volume}/${issueSlug}/${filename}`;
}

import { defineCollection, z, type ImageFunction } from 'astro:content';
import { glob } from 'astro/loaders';

const CoverImage = (image: ImageFunction) => (
  z.object({
    src: image(),
    alt: z.string().describe("Alternative text for the image"),
    attribution: z.optional(z.string()).describe("Image credit or attribution"),
  })
);

export const collections = {
  // The current issue: web-native markdown articles (Medium-style reading
  // experience). Only the latest issue lives here; older issues are rolled
  // into the `archive` as typeset files. Images go in a sibling `images/`
  // folder and are referenced with relative paths in the article body.
  current: defineCollection({
    loader: glob({ pattern: '*.md', base: './content/current' }),
    schema: ({ image }) => z.object({
      title: z.coerce.string().describe("Article title (use 'Title Case')"),
      authors: z.optional(z.array(z.coerce.string())).describe("Author name(s)"),
      subtitle: z.optional(z.coerce.string()).describe("Short standfirst shown under the title (use 'Sentence case')"),
      byline: z.optional(z.coerce.string()).describe("Custom byline; OVERRIDES the byline generated from authors"),
      date: z.optional(z.coerce.date()).describe("Publication date (defaults to the issue date)"),
      image: z.optional(CoverImage(image)).describe("Cover image, used as the article header and the feed thumbnail"),
      order: z.optional(z.coerce.number()).describe("Manual sort order within the issue (lower appears first)"),
      slug: z.optional(z.coerce.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/)).describe("Custom URL slug (defaults to the filename)"),
    }),
  }),

  // The archive: typeset back issues (PDF / PostScript / source files).
  // Each issue folder holds an `issue.md` (frontmatter only) plus its print
  // artifacts; `scripts/collect-archive-assets.mjs` publishes those files.
  archive: defineCollection({
    // generateId from the folder path: the glob loader otherwise uses a `slug`
    // frontmatter field as the entry id, but our slugs are only unique *within*
    // a volume (e.g. `1-quad-day` recurs across volumes), which would collide.
    loader: glob({
      pattern: '**/issue.md',
      base: './content/issues',
      generateId: ({ entry }) => entry.replace(/\/issue\.md$/i, ''),
    }),
    schema: () => z.object({
      volume: z.coerce.number().int().positive().describe("Volume number"),
      issue: z.coerce.string().describe("Issue number, or a name for un-numbered special editions (e.g. 'EOH')"),
      label: z.optional(z.coerce.string()).describe("Special-edition label shown alongside the number, e.g. 'Quad Day', 'EOH', 'April Fool's'"),
      note: z.optional(z.coerce.string()).describe("Editorial caveat shown on the issue, e.g. 'Only page 7 survives'"),
      date: z.coerce.date().describe("The publication date of the issue"),
      print: z.optional(z.object({
        pdf: z.optional(z.coerce.string()).describe("Filename of the final/built PDF (within the issue folder)"),
        pdf_scan: z.optional(z.coerce.string()).describe("Filename of the scanned PDF (if different from the final PDF)"),
        source: z.optional(z.coerce.string()).describe("Filename of the source (LaTeX, Typst, PostScript); zip/tarball if multiple files"),
        website: z.optional(z.coerce.string()).describe("External URL if the issue is hosted elsewhere (e.g. Internet Archive)"),
      })),
      credits: z.optional(z.array(
        z.object({
          title: z.coerce.string().describe("Title or role of the credited individual or group at the time of publication"),
          names: z.array(z.coerce.string()).describe("Name(s) of the credited individual(s)"),
        })
      )).describe("List of credits or acknowledgments for the issue"),
      slug: z.optional(z.coerce.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/)).describe("Custom URL slug for the issue (lowercase letters, numbers, hyphens only)"),
    }),
  }),
};

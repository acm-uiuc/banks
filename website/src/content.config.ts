import { defineCollection, z, type ImageFunction } from 'astro:content';
import { glob } from 'astro/loaders';

const ImageObject = (image: ImageFunction) => (
  z.object({
    src: image(),
    alt: z.string().describe("Alternative text for the image"),
    attribution: z.optional(z.string()).describe("Image credit or attribution"),
  })
);

export const collections = {
  articles: defineCollection({
    loader: glob({ pattern: '**/*.md', base: '../content/articles' }),
    schema: ({ image }) => z.object({
      // optional volume, issue for online-only articles or articles that are not yet published in an issue
      volume: z.optional(z.coerce.number().int().positive()).describe("Volume number where the article was first published"),
      issue: z.optional(z.coerce.string()).describe("Issue number or string where the article was first published"),
      date: z.coerce.date().describe("The publication date of the article"),
      title: z.coerce.string().describe("Title of the article (use 'Title Case')"),
      subtitle: z.optional(z.coerce.string()).describe("Brief elaboration of headline or summary (use 'Sentence case')"),
      byline: z.coerce.string().describe("Author(s) of the article"),
      // authors: z.optional(z.array(z.coerce.string())).describe("List of authors"),
      image: z.optional(ImageObject(image)).describe("Cover image for the article"),
      tags: z.optional(z.array(z.coerce.string())).describe("Tags or categories for the article"),
    }),
  }),

  issues: defineCollection({
    loader: glob({ pattern: '**/issue.md', base: '../content/issues' }),
    schema: ({image}) => z.object({
      volume: z.coerce.number().int().positive().describe("Volume number"),
      issue: z.coerce.string().describe("Issue number or string"),
      date: z.coerce.date().describe("The publication date of the issue"),
      print: z.optional(z.object({
        pdf: z.optional(z.coerce.string()).describe("Relative path to the final/built PDF"),
        source: z.optional(z.coerce.string()).describe("Relative path to the source file (e.g. LaTeX, Typst, PostScript); compress into a Zip archive or tarball if there are multiple files"),
        website: z.optional(z.coerce.string()).describe("If the issue is hosted on an external website, provide the URL here (can also be used for Internet Archive links)"),
      })),
      credits: z.optional(z.array(
        z.object({
          title: z.coerce.string().describe("Title or role of the credited individual or group"),
          names: z.array(z.coerce.string()).describe("Name(s) of the credited individual(s)"),
        })
      )).describe("List of credits or acknowledgments for the issue"),
    }),
  }),
};
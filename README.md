# Banks of the Boneyard

The student-run publication of [ACM @ UIUC](https://www.acm.illinois.edu/),
published at [banks.acm.illinois.edu](https://banks.acm.illinois.edu).

The site has two parts:

- **Current issue** — the latest issue, published as web-native Markdown
  articles (a Medium-style reading experience). It is the homepage.
- **Archive** — every back issue in its original typeset form (PDF / scan /
  PostScript / source), browsable by volume.

## Repository layout

```
website/                 # the Astro site
  content/               # editorial content (read by the content collections)
    current/             # the CURRENT issue — web articles
      <article>.md       # frontmatter: title, authors, … (see below)
      images/            # images referenced by the articles
    issues/              # the ARCHIVE — typeset back issues
      <volume>/<YYYY-MM-DD>-<slug>/   # folder names are shell/URL-safe, no spaces
        issue.md         # frontmatter only (volume, issue, date, label?, note?, print)
        <files>.pdf/.ps/…  # the print artifacts referenced by issue.md
  src/                   # site code (pages, components, collections)
  public/                # static assets (+ generated public/files/, see below)
logo/                    # source logo files
```

Editorial content lives in `website/content/`, kept separate from the site code
in `website/src/`. (It sits inside the project so Astro's dev server can read the
article images.) The website reads it through Astro content collections
(`current`, `archive`), and `website/scripts/collect-archive-assets.mjs`
publishes only the print files named in each `issue.md` (run automatically
before `dev`/`build`).

## Developing

```sh
cd website
npm install
npm run dev       # also runs the archive-asset collector first
npm run build
```

## Adding an article to the current issue

Drop a Markdown file in `website/content/current/`. Minimal frontmatter:

```yaml
---
title: "Banks of the Boneyard Rises from the Dead!"
authors:
  - "Yanni Zhuang"
---
```

Optional fields: `subtitle`, `byline` (overrides `authors`), `date`,
`order` (lower sorts first), `slug` (defaults to the filename), and `image`
(`{ src, alt, attribution }`) used as the article header and feed thumbnail.
Put article images in `website/content/current/images/` and reference them with
relative paths, e.g. `![Career fair](images/career_fair.jpg)`.

Update the masthead in `website/src/config.ts` (`currentIssue: { volume,
number, date }`) when the issue changes.

## Adding an issue to the archive

Create a folder named `website/content/issues/<volume>/<YYYY-MM-DD>-<slug>/` (no
spaces or parentheses) with an `issue.md`:

```yaml
---
volume: 16
issue: 3                        # number, or a name for un-numbered specials ("EOH")
date: "1997-11-01"
label: "Quad Day"               # optional special-edition label
note: "Only page 7 survives"    # optional editorial caveat
slug: 3-quad-day                # optional; defaults to the issue. Set when a label
                                # should appear in the URL, or to disambiguate.
print:
  pdf: Vol16Issue3-Nov.pdf      # final/built PDF
  pdf_scan: scan.pdf            # scanned PDF, if different
  source: Vol16Issue3-Nov.ps    # LaTeX/Typst/PostScript; zip if multiple files
  website: https://…            # external host (e.g. Internet Archive)
---
```

Put the referenced files alongside `issue.md`. The collector copies them to
`/files/<volume>/<slug>/…`; anything not named in `print:` stays private. The
issue's URL is `/archive/<volume>/<slug>` — slugs only need to be unique *within*
a volume. `credits` (a list of `{ title, names }`) is also supported.

## Rolling over to a new issue (maintainers)

When a new issue is ready:

1. **Archive the outgoing issue.** Add it under `website/content/issues/…` with
   its final typeset PDF (and source, if available), as above.
2. **Swap in the new articles.** Replace the files in `website/content/current/`
   (and `website/content/current/images/`) with the new issue's articles.
3. **Update the masthead.** Bump `currentIssue` in `website/src/config.ts`.

Old `/issues/*` links redirect to `/archive/*` (see `website/public/_redirects`).

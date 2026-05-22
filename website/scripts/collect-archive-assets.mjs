// Copies the archive's print artifacts (PDF / scan / source) into
// `public/files/<volume>/<issue-slug>/<filename>` so they are served as
// static assets — without exposing the rest of the content tree
// (LaTeX sources, build scripts, raw markdown, etc.).
//
// Runs automatically via the `predev` / `prebuild` npm scripts.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";
import { archiveIssueSlug } from "../src/lib/slug.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ISSUES_DIR = path.resolve(__dirname, "../../content/issues");
const OUT_DIR = path.resolve(__dirname, "../public/files");

// Frontmatter fields under `print:` that point to local files (not the
// `website` field, which is an external URL).
const FILE_FIELDS = ["pdf", "pdf_scan", "source"];

/** Recursively find every `issue.md` under a directory. */
function findIssueFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return findIssueFiles(full);
    return entry.name === "issue.md" ? [full] : [];
  });
}

fs.rmSync(OUT_DIR, { recursive: true, force: true });

let copied = 0;
const missing = [];

for (const issueFile of findIssueFiles(ISSUES_DIR)) {
  const { data } = matter(fs.readFileSync(issueFile, "utf8"));
  if (!data.print) continue;

  const issueDir = path.dirname(issueFile);
  const destDir = path.join(OUT_DIR, String(data.volume), archiveIssueSlug(data));

  for (const field of FILE_FIELDS) {
    const rel = data.print[field];
    if (!rel) continue;
    const src = path.join(issueDir, rel);
    if (!fs.existsSync(src)) {
      missing.push(`${field}: ${path.relative(ISSUES_DIR, src)}`);
      continue;
    }
    fs.mkdirSync(destDir, { recursive: true });
    fs.copyFileSync(src, path.join(destDir, path.basename(rel)));
    copied++;
  }
}

console.log(`[archive-assets] copied ${copied} file(s) to public/files`);
if (missing.length) {
  console.warn(
    `[archive-assets] ${missing.length} referenced file(s) not found:\n  ` +
      missing.join("\n  "),
  );
}

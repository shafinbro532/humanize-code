---
name: Humanize Code
description: "Use when asked to make a codebase read like hand-written code, remove AI-style tells, match a team's house style, or audit naming, comments, structure, and formatting. Supports Python, JavaScript/TypeScript, PHP, C/C++, Java, and a generic fallback. Audit-first and behavior-preserving."
---

# Humanize Code

Make a codebase read like a person who owns it wrote it. The goal is not to
degrade quality or fake mistakes. The goal is to replace generated-looking
verbosity, over-documentation, and over-abstraction with the project's own
conventions: shorter names where they are unambiguous, comments that explain
why instead of restating the signature, pragmatic structure, and formatting the
repository actually uses.

This is a style-normalization workflow. It is not a guarantee about AI
detectors, and it is not permission to introduce legacy or unsafe APIs.

## Hard rules

1. **Audit before editing.** The default run makes no changes. Produce a report,
   then wait for explicit approval before applying a rewrite.
2. **Behavior is sacred.** Preserve runtime behavior, error semantics, public
   APIs, data formats, and tests. A style pass is not a redesign.
3. **Never introduce removed or dangerous APIs.** Do not add `mysql_*`, short
   tags, `eval`, `gets`, `strcpy`, loose equality, `var`, raw `malloc` where a
   safe alternative exists, or similar patterns just to look human.
4. **Preserve comments that carry information.** Keep license headers, API
   contracts, invariants, safety warnings, workaround explanations, and
   non-obvious decisions.
5. **Skip generated and third-party code.** Skip lockfiles, minified files,
   vendored dependencies, build output, caches, binaries, and files marked
   generated/do-not-edit.
6. **The formatter wins.** If the repository has a formatter or style config,
   follow it. Do not introduce inconsistent indentation, trailing whitespace,
   or random line breaks in the name of "human" style.
7. **No fabricated imperfection.** Do not invent TODOs, typos, dead code,
   commented-out experiments, or fake dates. Human style comes from judgment
   and convention, not sabotage.
8. **Work in small batches.** Rewrite one module at a time. Run the formatter,
   linter, and tests after each batch. Revert a batch that fails or changes
   behavior unexpectedly.
9. **Keep a rollback path.** Use a git branch or worktree. If the project is
   not a git repository, require a backup or explicit user consent first.
10. **Report honestly.** Say what changed, what was skipped, what still looks
    generated, and what could not be verified.

## Modes

### Audit mode (default)

Triggered by requests such as "audit this repo", "why does this look like AI
code", or "show me what you would change". Audit mode must not modify source
files.

### Apply mode

Triggered only after the user approves the audit report and explicitly asks to
apply it. Apply mode creates a branch/worktree and rewrites the codebase in
reviewable batches.

## Workflow

### 1. Preflight

- Confirm the target path, languages, and any directories to exclude.
- Find the toolchain and conventions:
  - Python: `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.editorconfig`
  - JavaScript/TypeScript: `package.json`, `tsconfig.json`, `.prettierrc*`, ESLint config
  - PHP: `composer.json`, `phpcs.xml*`, `.php-cs-fixer.php`
  - C/C++: `CMakeLists.txt`, `Makefile`, `.clang-format`, `.clang-tidy`
  - Java: `pom.xml`, `build.gradle*`, `checkstyle.xml`, `.editorconfig`
- Identify the commands for formatting, linting, building, and testing.
- Check `git status --short`. For apply mode, require a clean tree or an
  explicit decision to stash/commit. Prefer a new branch or worktree.
- Run the baseline checks and record any failures that already exist. Never
  silently blame a rewrite for a pre-existing failure.

### 2. Scan

Run the bundled scanner from the skill directory:

```bash
python scripts/scan_style.py <path> --out humanize-out
```

Useful variants:

```bash
python scripts/scan_style.py . --lang python,javascript --exclude vendor,dist
python scripts/scan_style.py . --json-only
```

Read `humanize-out/scan.json` and `humanize-out/scan.md`. Treat scanner output
as evidence to verify, not as a verdict. Regex findings can be false positives;
open the cited lines before planning a change.

### 3. Build a house-style profile

Before rewriting, answer:

- What do the most human-looking files in this repository do?
- What naming style, quote style, indentation, line length, and comment tone
  are already established?
- Which parts are genuinely AI-shaped, and which are just clean code?
- Is the project modern or legacy? Match the language/runtime version declared
  by its manifests, not the latest fashion.
- Which public symbols must not be renamed?

If the whole repository is generated-looking, choose a pragmatic profile for
the declared language version instead of copying the worst file.

### 4. Produce the audit report

Fill `templates/STYLE_REPORT.md` with:

- scope and files scanned
- overall score, language breakdown, and confidence
- the strongest evidence per file
- proposed changes grouped by batch
- public API and behavior risks
- baseline test/lint/build status
- a clear statement that the score is heuristic

Then stop and ask for approval. Do not edit source files in audit mode.

### 5. Apply the rewrite

Create a branch/worktree, then process batches in this order:

1. Low-risk local names and comments.
2. Formatting and dead generated-looking ceremony.
3. Safe structural simplifications.
4. Language-specific hygiene fixes.

For each batch:

1. Make the smallest coherent edit.
2. Update all references when renaming.
3. Run the formatter.
4. Run the linter/build.
5. Run the relevant tests.
6. Inspect `git diff --stat` and the actual diff.
7. Revert the batch if behavior or tests regress.

Do not rename exported/public identifiers unless the user explicitly approved
that part of the plan.

### 6. Verify and summarize

- Re-run the scanner and compare before/after.
- Re-run the full test/lint/build commands.
- Report `git diff --stat`, tests, and remaining risks.
- List files intentionally left alone.
- Do not claim the result is "undetectable" or "100% human".

## Rewrite guidance

### Naming

- Shorten local and private names when the domain makes them unambiguous:
  `userInformation` -> `user`, `configuration` -> `config`, `buttonElement` ->
  `button`, `requestPayload` -> `payload`.
- Use conventional abbreviations when the codebase already uses them: `req`,
  `res`, `db`, `cfg`, `ctx`, `idx`, `msg`, `err`, `tmp`, `buf`, `len`, `src`,
  `dst`, `cb`, `fn`, `val`, `obj`, `str`, `num`.
- Do not turn every name into a cryptic abbreviation. Public APIs, domain terms,
  and names used across module boundaries stay descriptive.
- Remove enterprise suffixes only when the abstraction is also removed:
  `UserManagerFactory` is not improved by renaming it to `UserMgrFactory`.
- Match the repository's casing and vocabulary.

### Comments

- Remove docstrings that only restate the signature or the obvious body.
- Condense multi-paragraph comments to one or two lines.
- Replace formal filler ("This function ensures that...", "It is important to
  note...", "utilizes", "leverages", "comprehensive", "seamless") with direct
  language.
- Keep comments that explain why, invariants, edge cases, warnings, licensing,
  and public API contracts.
- Do not add emoji, fake timestamps, fake author tags, or fake tickets.
- A real `TODO`, `FIXME`, or `HACK` may stay. Do not invent new ones.

### Structure

- Inline trivial one-use helpers when it makes the call site clearer and the
  behavior is identical.
- Remove single-implementation interfaces, wrapper classes, and pass-through
  layers only when they are local, unused elsewhere, and covered by tests.
- Do not flatten a legitimate architecture just to look casual.
- Keep error handling, validation, and resource cleanup intact.
- Prefer deleting generated ceremony over rewriting working logic.

### Formatting

- Follow `.editorconfig`, formatter config, and existing line endings.
- Preserve the project's indentation and quote conventions.
- Do not intentionally introduce ragged formatting. "Human" does not mean
  "sloppy".
- If no formatter exists, make the smallest formatting change needed for
  consistency with the surrounding file.

### Language level

- Detect the target version from manifests and existing syntax.
- Match the era of the project. A legacy PHP 5 codebase should not be rewritten
  as PHP 8, and a modern TypeScript codebase should not be downgraded to ES5.
- Legacy-style findings are evidence about the codebase, not an instruction to
  create more legacy code.
- Hygiene fixes (removed APIs, unsafe calls, wildcard imports) are reported
  separately from style changes and are applied only when behavior-preserving.

## Scoring

The scanner produces a 0-100 score per file:

- **68-100: AI-shaped** — strong over-documentation, verbose naming, or
  over-abstraction signals.
- **45-67: mixed** — some generated-looking patterns, or a small/ambiguous file.
- **0-44: human-shaped** — short/domain naming, sparse why-comments, pragmatic
  structure, or legacy-era idioms.

The score is a heuristic. Clean, well-documented human code can score high, and
a messy generated file can score low. Always read the evidence. Confidence is
reported separately and is lower for small files and files with few signals.

## References

Load only what the current task needs:

| File | Use |
| --- | --- |
| `references/detection.md` | Full signal catalog, scoring, confidence, false positives |
| `references/rewrite-playbook.md` | Safe transformations, naming map, API stability, verification |
| `references/python.md` | Python signals, safe fixes, what not to change |
| `references/javascript.md` | JavaScript/TypeScript signals and safe fixes |
| `references/php.md` | PHP signals and safe fixes |
| `references/c-cpp.md` | C/C++ signals and safe fixes |
| `references/java.md` | Java signals and safe fixes |
| `references/generic.md` | Language-agnostic fallback rules |
| `templates/STYLE_REPORT.md` | Audit report structure |

## Output contract

Audit mode writes:

```text
humanize-out/
├── scan.json
├── scan.md
└── STYLE_REPORT.md
```

Apply mode additionally leaves a branch/worktree, a diff summary, and updated
verification results. Never overwrite the user's report with a claim that the
rewrite is perfect.

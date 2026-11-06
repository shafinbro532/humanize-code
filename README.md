# Humanize Code

An OpenCode skill that audits a codebase for generated-looking style and then,
after approval, rewrites it in a more natural human style.

It focuses on four things:

- **Naming** — verbose enterprise names versus short, domain-aware names
- **Comments** — formal doc blocks that restate the code versus sparse
  why-comments, TODOs, and legacy notes
- **Structure** — over-abstraction and defensive ceremony versus pragmatic
  organization
- **Formatting** — generated uniformity versus the project's own conventions

It also detects language-specific legacy and hygiene patterns, but does **not**
introduce them. `mysql_*`, short PHP tags, `gets`, `eval`, loose equality, and
similar patterns are reported as cleanup candidates, not used as a shortcut to
look human.

> This is a heuristic style tool, not proof of authorship and not a guarantee
> about AI detectors. It is intended for making code match a team's conventions
> and read like something a maintainer wrote on purpose.

## Supported languages

| Language | Specific checks |
| --- | --- |
| Python | wildcard imports, `%`/`.format()` strings, Python 2 leftovers, bare except, mutable defaults, type/docstring coverage |
| JavaScript/TypeScript | `var`, loose equality, jQuery, XHR, inline handlers, `parseInt` radix, JSDoc, modern-syntax clusters |
| PHP | short tags, `mysql_*`, `ereg`, `extract`, `global`, `or die`, redirects without `exit`, weak hashes, visibility |
| C/C++ | `NULL`, `malloc`, unsafe string functions, `using namespace std`, raw `new`/`delete`, Doxygen, modern C++ clusters |
| Java | `Vector`/`Hashtable`, raw types, wildcard imports, `Date`/`Calendar`, `System.out`, finalize/stop, Javadoc, modern Java clusters |
| Generic | Go, Rust, Ruby, C#, Kotlin, Swift, shell, SQL, and others use the shared naming/comment/structure rules |

## Install

Clone this repository into your global OpenCode skills directory:

```bash
# macOS / Linux
git clone https://github.com/shafinbro532/humanize-code.git \
  ~/.config/opencode/skills/humanize-code
```

```powershell
# Windows PowerShell
git clone https://github.com/shafinbro532/humanize-code.git `
  "$env:USERPROFILE\.config\opencode\skills\humanize-code"
```

OpenCode discovers skills automatically. If you already have the skill loaded,
restart or reload the session so the new skill is advertised.

Project-local installation also works:

```bash
git clone https://github.com/shafinbro532/humanize-code.git \
  .opencode/skills/humanize-code
```

## Use

Mention the skill in a prompt:

```text
@humanize-code audit this repository and show me what looks generated
```

```text
@humanize-code rewrite src/ to match the existing house style, but do not
rename public APIs
```

```text
@humanize-code make this codebase read like hand-written code; work on a new
branch and keep tests passing
```

The skill is audit-first. A normal run produces a report and stops. It only
edits after you approve the proposed batches. Apply mode should use a branch or
worktree and run the project's formatter, linter, and tests after each batch.

## Scanner

The scanner is stdlib-only Python 3.9+ and does not need any third-party
packages.

```bash
python scripts/scan_style.py . --out humanize-out
python scripts/scan_style.py . --lang python,javascript --exclude vendor,dist
python scripts/scan_style.py . --json-only
```

Outputs:

```text
humanize-out/
├── scan.json   # full per-file evidence, findings, scores, confidence
└── scan.md     # readable summary
```

Useful options:

| Option | Meaning |
| --- | --- |
| `--lang` | `python`, `javascript`, `php`, `c`, `cpp`, `java`, `generic`, or `all` |
| `--exclude` | Comma-separated paths or glob patterns to skip |
| `--max-file-size` | Maximum file size in KB (default 1024) |
| `--json-only` | Write JSON without the Markdown report |
| `--quiet` | Suppress the console summary |

The scanner skips `.git`, dependencies, build output, caches, binaries,
minified files, lockfiles, and files marked generated/do-not-edit. It reads
formatter/line-length configuration when available.

## How the score works

Each file gets a 0-100 score:

| Score | Class | Meaning |
| --- | --- | --- |
| 68-100 | `ai-shaped` | strong repeated generated-style signals |
| 45-67 | `mixed` | ambiguous or small sample |
| 0-44 | `human-shaped` | human/legacy signals dominate |

The score is weighted by lines of code and shrinks toward 50 for small files.
Confidence is reported separately. A clean, well-documented human codebase can
score high; a messy generated file can score low. Always read the evidence in
`scan.json` or `scan.md`.

## Safety model

- **No behavior changes.** Style passes must preserve runtime behavior, error
  semantics, public APIs, data formats, and tests.
- **No injected legacy.** The scanner does not tell the rewriter to add
  `mysql_*`, short tags, `var`, loose equality, `eval`, `gets`, or similar.
- **No fake imperfection.** Do not invent TODOs, typos, dead code, or comments.
- **No silent deletion.** Keep license headers, API contracts, invariants,
  safety warnings, and workaround notes.
- **No blind rewrites.** Skip vendored, generated, minified, and binary files.
- **Rollback required.** Use a git branch/worktree, or a backup outside the
  repository when there is no git.

## Repository layout

```text
humanize-code/
├── SKILL.md                     # skill instructions and workflow
├── references/
│   ├── detection.md             # signal catalog, scoring, false positives
│   ├── rewrite-playbook.md      # safe transformations and verification
│   ├── python.md
│   ├── javascript.md
│   ├── php.md
│   ├── c-cpp.md
│   ├── java.md
│   └── generic.md
├── scripts/
│   ├── scan_style.py            # CLI
│   └── humanize_scan/
│       ├── core.py              # masking, metrics, common rules
│       ├── languages.py         # language-specific rules
│       └── report.py            # scan walk, aggregation, Markdown
├── templates/
│   └── STYLE_REPORT.md          # audit report template
└── tests/
    └── test_scan_style.py
```

## Development

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Run the scanner on this repository:

```bash
python scripts/scan_style.py . --out humanize-out
```

The scanner itself is intentionally transparent and heuristic. If you find a
false positive, add a fixture to `tests/` and tighten the rule rather than
silencing the whole category.

## License

MIT. See [LICENSE](LICENSE).

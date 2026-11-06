# Detection reference

This file describes what the scanner looks for and how to interpret it. Rule
IDs match the `rule` field in `scan.json`.

## Two separate questions

Keep these apart:

1. **Style**: does this read like a person wrote it for this project?
2. **Hygiene**: is this code using removed, unsafe, or obsolete constructs?

A legacy pattern is evidence that a human (or an old generator) wrote the code.
It is **not** a pattern to add. The rewrite target is the human style around
naming, comments, structure, and formatting, not the defects.

## Signal categories

### Naming

| Rule | Direction | What it means |
| --- | --- | --- |
| `NAME_VERY_LONG` | AI | Identifier of 28+ characters |
| `NAME_LONG_RATIO` | AI | Large share of identifiers at 18+ characters |
| `NAME_ENTERPRISE` | AI | Manager/Service/Factory/Repository/Handler-style suffixes or prefixes |
| `NAME_VERBOSE_COMPOUND` | AI | Three or more generic words joined into one identifier |
| `NAME_ABBREV` | Human | Conventional short forms such as `req`, `res`, `cfg`, `db`, `ctx` |
| `NAME_SHORT` | Human | Short local names of 2-5 characters in local scopes |
| `NAME_SINGLE_LETTER` | Human | `i`, `j`, `k`, `x`, `n`, `p`-style locals |
| `NAME_CASE_MIX` | Weak human | Mixed casing conventions in the same file |

Naming is the strongest signal, but context matters. A public API named
`CustomerRepository` may be correct. A local variable named
`customerInformationFromDatabase` usually is not.

### Comments

| Rule | Direction | What it means |
| --- | --- | --- |
| `COMMENT_FORMAL` | AI | "This function...", "It is important to...", "ensures that", "utilizes" |
| `COMMENT_DOC_COVERAGE` | AI | Nearly every function has a doc block |
| `COMMENT_LONG` | AI (weak) | Average comment is a long paragraph |
| `COMMENT_BANNER` | AI (weak) | Decorative separators and section banners |
| `COMMENT_STEP` | AI (weak) | "Step 1", "First,", "Finally," comments for trivial code |
| `COMMENT_TRIVIAL` | AI | Comment restates the next obvious statement |
| `COMMENT_EMOJI` | AI | Emoji in source comments |
| `COMMENT_TODO` | Human | Real TODO/FIXME/HACK/XXX notes |
| `COMMENT_INFORMAL` | Human | Contracted, direct, or conversational comments |
| `COMMENTED_OUT_CODE` | Human | Code left commented out |
| `COMMENT_DEBUG_NOTE` | Human | Ad-hoc debug notes, "for now", "workaround", "legacy" |
| `COMMENT_API_DOC` | Neutral | Public API docs and license headers are not removed |

A single good docstring is not an AI signal. A uniform wall of docstrings that
repeat parameter names is.

### Structure

| Rule | Direction | What it means |
| --- | --- | --- |
| `STRUCT_EXCESSIVE_ABSTRACTION` | AI | Interfaces, factories, wrappers, and layers disproportionate to the task |
| `STRUCT_BOILERPLATE` | AI (weak) | Ceremonial main/argparse/logging scaffolding in a tiny script |
| `STRUCT_DEFENSIVE` | AI (weak) | Repeated redundant guards and validation at every layer |
| `STRUCT_TYPE_COVERAGE` | AI (weak) | Exhaustive annotations on trivial code |
| `STRUCT_ONE_USE_HELPER` | AI (weak) | A helper with one call site and no independent meaning |
| `STRUCT_DEBUG_LEFTOVER` | Human | `print`, `console.log`, `System.out`, debug traces |
| `STRUCT_LONG_FUNCTION` | Neutral risk | Long functions are common in both; inspect manually |
| `STRUCT_DEEP_NESTING` | Weak human | Deep nesting often survives in hand-maintained code |

### Formatting

| Rule | Direction | What it means |
| --- | --- | --- |
| `FORMAT_LONG_LINE` | Weak human | Lines over the detected or default limit |
| `FORMAT_TRAILING_WS` | Weak human | Trailing whitespace |
| `FORMAT_TABS` | Neutral | Tabs are fine if the project uses them |
| `FORMAT_NO_FINAL_NEWLINE` | Weak human | Missing final newline |
| `FORMAT_PERFECT` | AI (weak) | No drift at all, combined with other AI signals |

Formatting is the weakest category. Modern human teams use formatters and get
perfect formatting too. Never treat formatting alone as proof.

### Legacy and hygiene

These are reported for cleanup and context. They lower the AI score because
they indicate human-era code, but they are **not** rewrite targets when fixing
them would break compatibility or security.

Examples: wildcard imports, `%`-formatting, `var`, loose equality, jQuery,
short PHP tags, `mysql_*`, `global`, `NULL`/`malloc`, raw Java collections.

When a legacy finding is unsafe (removed API, injection risk, memory bug), mark
it `risk: high` and recommend a separate migration. Do not mix it into a style
batch.

## Scoring formula

For each file:

```text
ai_points    = sum(weight * min(count, cap)) for AI-positive findings
human_points = sum(|weight| * min(count, cap)) for human-negative findings

ai_per_100    = ai_points * 100 / max(loc, 1)
human_per_100 = human_points * 100 / max(loc, 1)

raw_score = 50 + 6 * ai_per_100 - 5 * human_per_100
size_factor = min(1, max(0.25, loc / 120))
score = clamp(50 + (raw_score - 50) * size_factor, 0, 100)
```

Interpretation:

| Score | Class | Meaning |
| --- | --- | --- |
| 68-100 | `ai-shaped` | Strong, repeated generated-style signals |
| 45-67 | `mixed` | Ambiguous or small sample |
| 0-44 | `human-shaped` | Human/legacy signals dominate |

The repository score is weighted by lines of code. Classes are not moral
judgments and are not proof of authorship.

## Confidence

Confidence reflects sample size and signal diversity, not certainty:

```text
confidence = 0.30
           + 0.20 * min(1, loc / 100)
           + 0.08 * number_of_categories_present
```

Cap at 0.95. Reduce confidence when the score is between 42 and 58, when the
file is under 40 non-blank lines, or when only formatting signals fire.

Report confidence next to every score. A 90 score on a 12-line file is weak
evidence.

## False positives to check manually

- Public APIs legitimately use descriptive names.
- Generated SDK clients and protocol bindings may need ceremony.
- Test fixtures may intentionally contain bad patterns.
- Framework conventions can require long names or doc blocks.
- A single complex function may be correctly documented in detail.
- A clean human codebase can have no human-style "drift" at all.
- Legacy APIs may be required by a pinned runtime; flag, do not rewrite blindly.
- A file with many comments may be a tutorial, not over-documentation.

Always open the cited lines before changing anything.

## Building the house-style profile

1. Pick 3-5 files that look oldest or most hand-maintained. Read them fully.
2. Record:
   - local naming vocabulary and abbreviation habits
   - comment density and tone
   - indentation, quotes, line length, spacing
   - error-handling and logging style
   - structure: one class per file? helpers near call sites? modules?
   - language version and framework constraints
3. Compare AI-shaped files against that profile, not against a generic ideal.
4. If no human baseline exists, use a pragmatic profile for the declared
   runtime and keep public interfaces descriptive.
5. Write the profile into the report before proposing edits.

## What "human-like" does not mean

- introducing bugs, typos, or dead code
- removing useful documentation
- making names cryptic
- ignoring the formatter
- downgrading security or accessibility
- copying a stereotype of "old code"

The useful core is: concrete names, comments with a reason to exist, structure
that matches the problem, and consistency with the people who maintain it.

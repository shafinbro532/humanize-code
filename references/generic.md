# Generic fallback

Use these rules for languages without a dedicated reference: Go, Rust, Ruby,
C#, Kotlin, Swift, shell, SQL, and anything else.

The scanner still computes language-agnostic metrics for these files: identifier
length, comment density, comment formality, line length, indentation, trailing
whitespace, and common structure signals. Language-specific regexes are not
applied, so treat scores as weaker evidence.

## Signals

### Naming

- AI-shaped: long, uniformly descriptive names (`initializeApplicationConfiguration`,
  `handleUserAuthenticationRequest`), enterprise suffixes (`Manager`, `Service`,
  `Factory`, `Repository`, `Orchestrator`), no local abbreviations.
- Human-shaped: short domain locals (`cfg`, `req`, `res`, `ctx`, `idx`, `tmp`,
  `buf`, `n`), single-letter loop variables, names that match the project's
  existing vocabulary.
- Neutral: Go's short names are idiomatic; Rust's descriptive names are
  idiomatic. Judge against the language and the repository.

### Comments

- AI-shaped: a doc comment on every function with parameter/return sections,
  formal filler, comments that restate the code, decorative banners.
- Human-shaped: sparse why-comments, real TODOs, workaround notes, commented-out
  code, informal but useful explanations.
- Neutral: generated API docs, license headers, public interface contracts.

### Structure

- AI-shaped: interfaces/factories/layers for small tasks, one class per file
  with identical layout, excessive validation, custom error hierarchies for
  trivial scripts.
- Human-shaped: pragmatic helpers near their call sites, some duplication,
  local shortcuts, mixed but stable conventions.
- Neutral: language-idiomatic project layout, framework conventions.

### Formatting

- AI-shaped (weak): no drift at all, uniform line length, consistent quotes,
  perfect spacing, combined with other AI signals.
- Human-shaped (weak): long lines, trailing whitespace, mixed quotes, missing
  final newline.
- Do not treat formatting alone as evidence. Formatters make human code perfect.

## Safe fixes

- Shorten local/private names only when unambiguous and all references are
  updated.
- Remove comments that repeat the signature; keep contracts and warnings.
- Inline trivial one-use helpers when behavior is unchanged.
- Remove empty wrappers and unused imports.
- Follow the repository's formatter and style config.
- Leave public APIs, serialized names, CLI flags, config keys, and reflection-
  visible names alone unless approved.
- Do not introduce language-specific legacy or unsafe constructs.

## Language notes

- **Go**: short names are normal (`ctx`, `cfg`, `buf`, `n`); error handling is
  explicit and verbose by design. Do not "simplify" error checks.
- **Rust**: descriptive names and explicit types are normal. Do not remove
  lifetime annotations or `Result` handling for style.
- **Ruby**: duck typing and short blocks are normal; do not add type ceremony.
- **C#**: `var`, LINQ, async/await, and properties are normal in modern code;
  remove redundant XML docs only when they repeat the signature.
- **Kotlin**: data classes, null safety, and concise functions are idiomatic;
  don't add Java-style ceremony.
- **Swift**: optionals, protocols, and value types are idiomatic; don't remove
  safety checks.
- **Shell**: short names and terse constructs are normal; preserve quoting,
  `set -e` semantics, and portability.
- **SQL**: formatting and aliases are style; never rewrite a query without
  checking semantics, indexes, and transaction behavior.

## What not to do

- Do not use this fallback to justify cryptic names, deleted documentation, or
  broken error handling.
- Do not apply a language-specific rule from another language.
- Do not rewrite generated code, vendored code, or build artifacts.
- Do not claim a score is meaningful when no language-specific rules ran.

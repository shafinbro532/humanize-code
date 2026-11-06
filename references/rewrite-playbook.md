# Rewrite playbook

Use this after the audit is approved. The objective is a behavior-preserving
style pass, not a redesign.

## Before touching a file

- Read the whole file, not just the flagged lines.
- Find its callers and tests.
- Check whether names are exported, serialized, part of a URL, stored in a
  database, or referenced by configuration.
- Check the declared language/runtime version.
- Know the formatter/linter/test commands for the module.
- Start from a clean branch/worktree.

## Naming map

These are starting points, not mandatory replacements. Prefer the repository's
existing vocabulary.

| Verbose | Natural |
| --- | --- |
| `userInformation` | `user` |
| `configuration` / `configurationManager` | `config` / `cfg` |
| `buttonElement` | `button` / `btn` |
| `requestPayload` | `payload` / `body` |
| `responseData` | `response` / `res` |
| `databaseConnection` | `db` / `conn` |
| `errorMessage` | `err` / `msg` |
| `temporaryValue` | `tmp` / `temp` |
| `bufferLength` | `len` / `bufLen` |
| `sourcePath` / `destinationPath` | `src` / `dst` |
| `callbackFunction` | `cb` |
| `functionHandler` | `fn` / `handler` |
| `contextObject` | `ctx` |
| `indexPosition` | `idx` |
| `numberOfItems` | `count` / `n` |
| `isUserAuthenticated` | `isAuthed` / `authed` |
| `getUserInformationFromDatabase` | `getUser` / `loadUser` |
| `initializeApplicationConfiguration` | `initConfig` / `setup` |
| `handleButtonClickEvent` | `onClick` / `handleClick` |

Rules:

- Keep public/exported names unless approved.
- Keep names that carry domain meaning: `invoice`, `tenant`, `policy`,
  `settlement` are not noise.
- Do not abbreviate two different concepts to the same short name.
- Rename all references in the same batch.
- Prefer the language's LSP rename when available; otherwise search the whole
  repository for the symbol before editing.
- If a name appears in strings, JSON keys, SQL, templates, or docs, treat it as
  public.

## Comment transformations

### Remove redundant docs

Before:

```python
def add(a: int, b: int) -> int:
    """Add two integers together.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The sum of the two integers.
    """
    return a + b
```

After:

```python
def add(a: int, b: int) -> int:
    return a + b
```

### Keep the reason, drop the narration

Before:

```js
// This function is responsible for fetching the user data from the API.
// It ensures that errors are handled and returns the parsed response.
async function fetchUserData(userId) {
  // ...
}
```

After:

```js
// 404 means "not invited yet" here; don't turn it into an empty profile.
async function fetchUser(userId) {
  // ...
}
```

### Keep contracts and warnings

Do not delete comments that state:

- public API guarantees
- invariants or preconditions
- security warnings
- workarounds with a link or ticket
- license and attribution
- generated-file warnings
- non-obvious ordering or concurrency constraints

### Tone

- Prefer direct sentences over formal filler.
- Contractions are fine if the repository already uses them.
- Avoid emoji, fake enthusiasm, and fake imperfection.
- Do not add profanity or personal remarks.
- Do not invent a `TODO`; only preserve real ones.

## Structure

Safe simplifications:

- Inline a one-use helper when the body is short and the call site becomes
  clearer.
- Delete empty wrapper classes/modules that only forward calls.
- Remove a single-implementation interface only if it is local, not part of a
  public API, and not needed for testing.
- Move a helper next to its only caller.
- Replace a generated-looking ceremony with the direct standard-library call.
- Remove dead imports and unreachable trivial branches.

Unsafe changes to avoid:

- changing exception types or swallowing errors
- removing validation that protects a boundary
- changing transaction boundaries, locks, retries, or timeouts
- changing serialization order or field names
- merging modules with different lifecycles
- deleting "unused" code without checking dynamic references
- rewriting a working legacy architecture in the same pass

If a structural change is not clearly safe, leave it and report it.

## Formatting

- Run the repository formatter after every batch.
- Do not fight `.editorconfig` or formatter output.
- Preserve CRLF/LF style.
- Keep the existing indentation width.
- Do not add trailing whitespace or remove final newlines to look human.
- If there is no formatter, follow the surrounding file, not a generic style.

## Language-level rules

- Python: do not introduce wildcard imports, `.format()` or `%` formatting,
  bare `except`, mutable defaults, or Python 2 syntax. Modernize only when the
  target version supports it.
- JavaScript/TypeScript: do not introduce `var`, `==`, `eval`, `with`,
  `document.write`, inline handlers, or global assignments. Keep `const`/`let`
  and strict equality.
- PHP: never introduce short open tags, `mysql_*`, `ereg`, `extract`, `eval`,
  `global`, or `or die`. Prefer prepared statements and explicit `exit` after
  redirects when changing that area.
- C/C++: do not introduce `gets`, `strcpy`, `sprintf`, raw `malloc` ownership,
  C-style casts, or `using namespace std` in headers. Modernize only with the
  project's standard version.
- Java: do not introduce raw types, `Vector`/`Hashtable`, `finalize`,
  `Thread.stop`, wildcard imports, or `System.out` logging. Prefer the
  project's existing logging and collection style.

## Batch process

### Batch 1: comments and local names

- Remove only docs that restate the signature.
- Shorten private/local names.
- Run tests.
- Review the diff for accidental deletions of real information.

### Batch 2: formatting and generated ceremony

- Run the formatter.
- Remove empty wrappers and unused imports.
- Do not touch logic.

### Batch 3: safe structure

- Inline one-use helpers.
- Remove local single-implementation indirection.
- Keep public APIs stable.
- Run the full test suite, not only the unit tests for the file.

### Batch 4: hygiene

- Fix removed APIs or unsafe calls only with a migration plan.
- Keep each migration separate from style changes.
- If behavior cannot be verified, stop and report.

## Verification commands

Use the repository's own commands. Typical examples:

```bash
# Python
python -m pytest
ruff check .
black --check .

# JavaScript / TypeScript
npm test
npm run lint
npx tsc --noEmit

# PHP
composer test
vendor/bin/phpcs
vendor/bin/phpstan analyse

# C / C++
cmake --build build
ctest --test-dir build

# Java
mvn test
./gradlew test
```

If a command does not exist, say so in the report. Do not invent a passing test.

## Rollback

- Keep each batch as a separate commit or stashable change set.
- If tests fail and the cause is the style edit, revert the batch.
- If a failure is pre-existing, record it before editing and compare after.
- Never use `git reset --hard` on a user's uncommitted work.
- If there is no git, create a timestamped backup outside the repository.

## Final report checklist

- [ ] Scope and files scanned
- [ ] Before/after scores with confidence
- [ ] Exact commands run and their results
- [ ] Public APIs intentionally unchanged
- [ ] Files skipped and why
- [ ] Remaining AI-shaped files
- [ ] Legacy/hygiene issues left for a separate migration
- [ ] No claim of detector evasion

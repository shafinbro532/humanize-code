# JavaScript and TypeScript

## Human/legacy signals

| Rule | Example | Notes |
| --- | --- | --- |
| `JS_VAR` | `var count = 0;` | Legacy; `let`/`const` preferred |
| `JS_LOOSE_EQUAL` | `if (x == null)` | Often intentional for null/undefined; check |
| `JS_JQUERY` | `$(".item").click(...)` | Legacy jQuery; migrate only with a plan |
| `JS_DOCUMENT_READY` | `$(document).ready(...)` | jQuery-era |
| `JS_AJAX` | `$.ajax({...})` | jQuery-era |
| `JS_XHR` | `new XMLHttpRequest()` | Legacy; `fetch` is modern |
| `JS_CONSOLE_LOG` | `console.log(...)` | Debug leftover |
| `JS_ALERT` | `alert("...")` | Debug/legacy UI |
| `JS_EVAL` | `eval(...)` | Dangerous; remove |
| `JS_WITH` | `with (obj) {}` | Forbidden in strict mode |
| `JS_NEW_FUNCTION` | `new Function("...")` | Dangerous; remove |
| `JS_INLINE_HANDLER` | `onclick="doThing()"` | Prefer `addEventListener` |
| `JS_FUNCTION_KEYWORD` | `function () {}` | Neutral; callbacks are normal in older code |
| `JS_CALLBACK` | `fs.readFile(path, cb)` | Neutral; async/await is modern |
| `JS_STRING_CONCAT` | `"a" + name` | Template literals are clearer |
| `JS_PARSEINT_NO_RADIX` | `parseInt(value)` | Pass `10` |
| `JS_SUBSTR` | `s.substr(1)` | Prefer `slice`/`substring` |
| `JS_ARGUMENTS` | `arguments.length` | Prefer rest params in new code |

Human-style signals also include short locals (`el`, `btn`, `req`, `res`, `err`,
`cb`, `opts`, `tmp`), real TODOs, `console.log` left behind, and older callback
or jQuery patterns.

## AI-shaped signals

- JSDoc on every trivial function, including obvious parameter descriptions.
- Perfectly uniform modules with `const`, arrow functions, `async/await`,
  optional chaining, nullish coalescing, and exhaustive error classes.
- Verbose identifiers: `handleUserAuthenticationSubmitEvent`,
  `fetchUserProfileDataFromServer`.
- A `services/`, `utils/`, `types/`, `constants/` split for a small script.
- Defensive checks at every boundary and a custom error class per failure.
- `console.error` plus a logging wrapper in code that otherwise has no logging.

Modern syntax is not inherently AI. Weight it only when it appears together
with over-documentation and verbose naming.

## Safe fixes

- `var` -> `const`/`let` only after checking closure semantics. A `var` captured
  by a function inside a loop behaves differently from `let`; preserve behavior.
- `==`/`!=` -> `===`/`!==`, except intentional `x == null` checks that must
  match both `null` and `undefined`.
- Remove `eval`, `with`, `new Function`, `document.write`, and inline handlers.
- `console.log` -> remove or use the project's logger.
- `parseInt(x)` -> `parseInt(x, 10)`.
- `substr` -> `slice`/`substring` after checking negative-index behavior.
- String concatenation -> template literals when interpolation is simple.
- Callback style -> `async/await` only when error propagation and ordering stay
  identical.
- jQuery -> native DOM/fetch only as a deliberate migration with tests.
- Remove JSDoc that repeats types already expressed by TypeScript.

## Do not change

- Public exports, package entry points, event names, URL shapes, or JSON keys.
- `var` in code that intentionally relies on function scoping or hoisting.
- `== null` when it is the idiomatic null-or-undefined check.
- Browser/runtime support targets, bundler assumptions, or polyfills.
- TypeScript types on public APIs, declaration files, or generated clients.
- Test fixtures that intentionally exercise legacy behavior.

## Example

Before:

```js
// This function is responsible for retrieving the user data from the server.
async function fetchUserDataFromServer(userId) {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    console.error("Failed to fetch user data");
    return null;
  }
  return await response.json();
}
```

After:

```js
async function fetchUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) return null;
  return res.json();
}
```

Only do this when the caller already handles `null` and logging is not part of
the contract. Preserve the error behavior if it matters.

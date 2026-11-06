# C and C++

## Human/legacy signals

| Rule | Example | Notes |
| --- | --- | --- |
| `C_BLOCK_COMMENTS` | `/* ... */` banners | Common in older C; not inherently bad |
| `C_AUTHOR_DATE` | `/* Author: ... 2004-03-12 */` | Human-era metadata |
| `C_HUNGARIAN` | `dwCount`, `szName`, `pBuffer` | Windows/legacy style |
| `C_PREFIX` | `g_config`, `s_state`, `m_value`, `kMax` | Common human conventions |
| `C_SHORT_NAMES` | `buf`, `len`, `fd`, `ctx`, `n`, `p` | Strong human signal in systems code |
| `C_NULL` | `NULL` | C is fine; C++11+ prefers `nullptr` |
| `C_MALLOC` | `malloc`/`free` | Ownership style; not automatically wrong |
| `C_UNSAFE_STR` | `gets`, `strcpy`, `sprintf` | Security risk; migrate |
| `C_TYPEDEF_STRUCT` | `typedef struct { ... } Foo;` | Common C style |
| `C_KNR` | K&R function definitions | Very old C |
| `C_REGISTER` | `register int i;` | Obsolete |
| `C_USING_NAMESPACE` | `using namespace std;` | Avoid in headers |
| `C_ENDL` | `std::endl` | Flushes; `'\n'` is usually enough |
| `C_NEW_DELETE` | raw `new`/`delete` | Prefer RAII in modern C++ |
| `C_C_STYLE_CAST` | `(int)x` | Prefer `static_cast` |
| `C_DEBUG_PRINT` | `printf("here\n")` | Debug leftover |
| `C_PRAGMA_ONCE` | `#pragma once` | Fine; include guards are also fine |

## AI-shaped signals

- Doxygen comments on every function, including trivial getters and obvious
  parameters.
- `@brief`, `@param`, `@return`, `@throw` blocks repeated mechanically.
- Exhaustive const correctness, smart pointers, `std::optional`, and RAII in a
  tiny C-style program that does not use the rest of the C++ standard library.
- Perfectly uniform include order, formatting, and naming across a codebase
  with no local quirks.
- Verbose names: `initializeApplicationConfiguration`,
  `calculateTotalBufferLength`.
- Defensive checks at every layer with custom error types.

## Safe fixes

- `NULL` -> `nullptr` in C++11+ only.
- `typedef struct { ... } Foo;` -> `struct Foo { ... };` only if C++ and no C
  compatibility is required.
- C-style cast -> `static_cast`/`reinterpret_cast` when the conversion is
  unambiguous.
- Remove `using namespace std;` from headers; in a `.cpp`, replace with
  explicit `std::` only if it does not create churn.
- Replace `std::endl` with `'\n'` only when an explicit flush is not required.
- Replace `gets`/`strcpy`/`sprintf` with bounded alternatives as a security
  migration with tests.
- Replace raw `malloc`/`free` with RAII only when ownership is clear and the
  change is covered by tests.
- Remove debug `printf`/`std::cout` traces.
- Replace `register` (removed in C++17) and K&R definitions only if the target
  standard supports it.

## Do not change

- ABI, public headers, struct layout, symbol names, or exported functions.
- C compatibility, the declared C/C++ standard, or compiler extensions.
- Allocation ownership, lifetime, threading, or performance-critical paths.
- Macros, include order, or build flags without understanding the build.
- Security-sensitive code as part of a style batch.
- Generated bindings, third-party headers, or vendored libraries.

## Example

Before:

```cpp
/**
 * @brief Retrieves the user information from the database.
 * @param userId The identifier of the user.
 * @return A pointer to the user information, or NULL on failure.
 */
UserInformation* getUserInformationFromDatabase(int userId) {
    UserInformation* userInformation = (UserInformation*)malloc(sizeof(UserInformation));
    if (userInformation == NULL) {
        return NULL;
    }
    // ...
    return userInformation;
}
```

After (C++11+, ownership unchanged):

```cpp
UserInfo* getUser(int id)
{
    auto* user = static_cast<UserInfo*>(malloc(sizeof(UserInfo)));
    if (!user) return nullptr;
    // ...
    return user;
}
```

Do not switch to `std::unique_ptr` in the same pass; that changes ownership and
the public contract. Treat it as a separate refactor.

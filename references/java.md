# Java

## Human/legacy signals

| Rule | Example | Notes |
| --- | --- | --- |
| `JAVA_JAVADOC` | Javadoc on every method | AI if it restates the signature; normal on public APIs |
| `JAVA_FORMAL_JAVADOC` | `@param`, `@return`, `@throws` on trivial code | Strong AI signal at 100% coverage |
| `JAVA_LEGACY_COLLECTION` | `Vector`, `Hashtable`, `Enumeration`, `Stack` | Legacy; check thread-safety semantics |
| `JAVA_DATE_CALENDAR` | `new Date()`, `Calendar`, `SimpleDateFormat` | Prefer `java.time` in new code |
| `JAVA_SYSTEM_OUT` | `System.out.println(...)` | Debug leftover or console app |
| `JAVA_PRINT_STACK` | `e.printStackTrace()` | Use the project's logger |
| `JAVA_RAW_TYPE` | `List list = new ArrayList();` | Use generics |
| `JAVA_WILDCARD_IMPORT` | `import java.util.*;` | Prefer explicit imports |
| `JAVA_FINALIZE` | `protected void finalize()` | Deprecated/dangerous; remove |
| `JAVA_THREAD_STOP` | `thread.stop()` | Unsafe; migrate |
| `JAVA_RUNTIME_EXEC` | `Runtime.getRuntime().exec(...)` | Prefer `ProcessBuilder` |
| `JAVA_TRY_FINALLY` | manual close in `finally` | Try-with-resources is modern |
| `JAVA_ANONYMOUS_CLASS` | `new Runnable() { ... }` | Lambdas are modern; both can be human |
| `JAVA_NULL_CHECK` | `if (obj != null)` everywhere | Neutral; defensive code can be human |
| `JAVA_PUBLIC_FIELD` | `public int count;` | Encapsulation issue |
| `JAVA_GETTER_SETTER` | getters/setters for every field | Normal Java, not an AI tell by itself |

## AI-shaped signals

- Javadoc on every private method and trivial getter, with parameter
  descriptions that repeat the names.
- Records, streams, `Optional`, `var`, `List.of`, `Map.of`, and pattern matching
  used everywhere in a codebase that otherwise looks like a generated sample.
- A service/controller/repository/DTO/factory layering for a small program.
- Exhaustive `Objects.requireNonNull`, custom exception classes, and validation
  at every layer.
- Verbose names: `UserAuthenticationServiceImplementation`,
  `handleUserLoginRequestProcessor`.
- Perfect checkstyle formatting with no local conventions.

Modern Java is not inherently AI. Weight it only when combined with
over-documentation, verbose naming, and disproportionate abstraction.

## Safe fixes

- Remove Javadoc that only repeats the signature; keep public API contracts.
- Replace raw types with generics.
- Replace wildcard imports with explicit imports.
- `StringBuffer` -> `StringBuilder` only when the buffer is not shared across
  threads.
- `Vector` -> `ArrayList` / `Hashtable` -> `HashMap` only after checking
  synchronization requirements.
- `Date`/`Calendar` -> `java.time` as a separate, tested migration.
- `System.out` / `printStackTrace` -> the project's logger.
- Manual `finally` close -> try-with-resources when resource semantics match.
- Add `@Override` where it clarifies intent.
- Replace `Runtime.exec` with `ProcessBuilder` when argument handling matters.
- Remove `finalize` and `Thread.stop` only with a migration plan.

## Do not change

- Public/protected API signatures, serialVersionUID, serialized field names, or
  reflection-visible names.
- Thread-safety assumptions behind `Vector`/`Hashtable`.
- Android API levels, framework annotations, or dependency-injection wiring.
- Checked exception contracts.
- Generated sources, build output, or framework-generated code.
- Tests that intentionally exercise legacy behavior.

## Example

Before:

```java
/**
 * This method is responsible for retrieving the user information from the
 * database.
 *
 * @param userId The identifier of the user.
 * @return The user information.
 */
public UserInformation getUserInformationFromDatabase(int userId) {
    System.out.println("Fetching user " + userId);
    return userRepository.findById(userId);
}
```

After (public API name kept stable):

```java
public UserInformation getUserInformationFromDatabase(int userId) {
    return userRepository.findById(userId);
}
```

If the method is private and all callers are updated, the name can become
`getUser`. Do not rename a public method just for style.

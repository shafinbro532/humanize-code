# PHP

## Human/legacy signals

| Rule | Example | Notes |
| --- | --- | --- |
| `PHP_SHORT_TAG` | `<? echo $x; ?>` | Depends on `short_open_tag`; use `<?php` |
| `PHP_SHORT_ECHO` | `<?= $x ?>` | Valid since PHP 5.4; often fine in templates |
| `PHP_MYSQL` | `mysql_query(...)` | Removed in PHP 7; migrate to PDO/mysqli |
| `PHP_EREG` | `ereg("...", $s)` | Removed; use `preg_*` |
| `PHP_SPLIT` | `split(",", $s)` | Removed; use `explode`/`preg_split` |
| `PHP_EACH` | `while (list($k, $v) = each($a))` | Removed; use `foreach` |
| `PHP_CREATE_FUNCTION` | `create_function(...)` | Removed; use a closure |
| `PHP_MCRYPT` | `mcrypt_encrypt(...)` | Removed; use OpenSSL/Sodium |
| `PHP_GLOBAL` | `global $db;` | Pass dependencies instead |
| `PHP_REQUEST` | `$_REQUEST['id']` | Ambiguous source; use `$_GET`/`$_POST` |
| `PHP_EXTRACT` | `extract($_POST)` | Dangerous; remove |
| `PHP_EVAL` | `eval($code)` | Dangerous; remove |
| `PHP_OR_DIE` | `$db = mysql_connect(...) or die(...)` | Legacy error handling |
| `PHP_DIE` | `die("...")` | Prefer exceptions/response handling |
| `PHP_HEADER_REDIRECT` | `header("Location: ...")` without `exit` | Execution continues; add `exit` |
| `PHP_OLD_ARRAY` | `array(1, 2)` | `[]` is preferred on PHP 5.4+ |
| `PHP_VAR_KEYWORD` | `var $name;` | PHP 4 style; use visibility |
| `PHP_NO_VISIBILITY` | `function foo() {}` in a class | Add `public`/`private`/`protected` |
| `PHP_CLOSING_TAG` | `?>` at end of a PHP-only file | Can cause whitespace output |
| `PHP_INLINE_HTML` | mixed HTML and PHP | Normal in old templates; keep if intentional |
| `PHP_MD5` | `md5($password)` | Never for passwords; use `password_hash` |
| `PHP_RAND` | `rand()` for tokens | Use `random_bytes`/`random_int` |
| `PHP_ADD_SLASHES` | `addslashes($input)` | Not SQL escaping; use prepared statements |
| `PHP_ERROR_SUPPRESSION` | `@file_get_contents(...)` | Hides errors; handle explicitly |

Human-style signals also include short variable names (`$db`, `$cfg`, `$req`,
`$res`, `$row`, `$ret`), real TODOs, sparse comments, and mixed HTML/PHP in
legacy templates.

## AI-shaped signals

- A docblock on every trivial method, repeating parameter types that are
  already declared.
- Formal filler: "This method is responsible for...", "ensures that",
  "utilizes".
- A namespace, interface, factory, DTO, and service layer for a small script.
- PSR-12-perfect formatting plus exhaustive type declarations and tests for
  trivial getters.
- Constructor promotion, enums, readonly properties, and `match` used
  everywhere in a codebase that otherwise looks like a generated sample.

Modern PHP is not inherently AI. The AI signal is ceremony disproportionate to
the problem and documentation that restates the code.

## Safe fixes

- Replace short open tags with `<?php` (and `<?=` with `<?php echo` only if the
  target or style requires it; `<?=` is valid on PHP 5.4+).
- Migrate `mysql_*` to PDO or mysqli with prepared statements. This is a
  behavior/security migration, not a style edit; test it separately.
- Replace `ereg`/`split`/`each`/`create_function`/`mcrypt_*` with supported
  equivalents.
- Replace `global $db` by passing the connection explicitly.
- Replace `$_REQUEST` with the intended source.
- Remove `extract` and `eval`.
- Add `exit` after a redirect when execution must stop.
- Replace `array()` with `[]` when the target is PHP 5.4+.
- Add visibility to methods and properties.
- Remove the closing `?>` from PHP-only files.
- Replace `md5`/`sha1` password hashing with `password_hash` and
  `password_verify`.
- Replace `rand` for security tokens with `random_bytes`/`random_int`.
- Replace `addslashes` SQL escaping with prepared statements.
- Remove `@` suppression and handle the error explicitly.

## Do not change

- Public routes, controller/action names, template variables, config keys, or
  database schema.
- Framework conventions (Laravel/Symfony/WordPress) that require specific
  structure.
- Short echo tags in templates if the project uses them and the target supports
  them.
- Legacy runtime compatibility without an explicit migration.
- SQL, authentication, or session behavior as part of a style batch.
- Generated code, vendor directories, or framework caches.

## Example

Before:

```php
<?php
// This function is responsible for retrieving a user from the database.
function getUserInformationFromDatabase($userId) {
    global $db;
    $query = "SELECT * FROM users WHERE id = " . $_REQUEST['id'];
    $result = mysql_query($query);
    return mysql_fetch_assoc($result);
}
```

After (style only, still needs a SQL migration):

```php
<?php
function getUser(PDO $db, int $id): ?array
{
    $stmt = $db->prepare('SELECT * FROM users WHERE id = ?');
    $stmt->execute([$id]);
    return $stmt->fetch() ?: null;
}
```

Do not perform the SQL migration and the naming/comment pass in the same batch
unless the tests cover both.

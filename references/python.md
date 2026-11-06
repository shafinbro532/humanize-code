# Python

## Human/legacy signals

| Rule | Example | Notes |
| --- | --- | --- |
| `PY_WILDCARD_IMPORT` | `from os import *` | Hygiene issue; make imports explicit |
| `PY_PERCENT_FORMAT` | `"%s: %d" % (name, count)` | Old but valid; f-strings are clearer on 3.6+ |
| `PY_DOT_FORMAT` | `"{}: {}".format(name, count)` | Same |
| `PY_PY2_SYNTAX` | `print "x"`, `xrange`, `iteritems`, `has_key` | Must match target version; likely dead code |
| `PY_BARE_EXCEPT` | `except:` | Catch a specific exception |
| `PY_EXCEPT_PASS` | `except Exception: pass` | Hides failures; fix only with a behavior decision |
| `PY_MUTABLE_DEFAULT` | `def f(items=[])` | Classic bug; use `None` sentinel |
| `PY_CAMEL_FUNC` | `def getUser():` | Match the file's snake_case convention |
| `PY_OS_PATH` | `os.path.join(...)` | `pathlib` is modern; do not rewrite blindly |
| `PY_MAIN_GUARD` | `if __name__ == "__main__":` | Neutral; common in human scripts |
| `PY_PRINT_DEBUG` | `print("here")` | Remove or replace with logging |
| `PY_MULTIPLE_IMPORTS` | `import os, sys` | PEP8 drift |
| `PY_EQ_NONE` | `x == None` | Use `x is None` |

Human-style signals also include short locals (`i`, `n`, `tmp`, `cfg`, `db`,
`req`, `res`, `ctx`), real TODOs, sparse why-comments, and commented-out
experiments.

## AI-shaped signals

- Type hints on every trivial function, including `-> None`.
- A docstring on every function with `Args:`, `Returns:`, `Raises:`, `Example:`
  even when the signature already says everything.
- Formal filler: "This function ensures that", "It is important to note",
  "utilizes", "leverages", "comprehensive".
- Dataclasses, protocols, factories, and dependency injection for a small
  script.
- Perfectly uniform module layout: imports, constants, dataclass, service,
  `main()`, `if __name__ == "__main__": main()`.
- Defensive `try/except` around every call, with generic exceptions.

## Safe fixes

- Remove docstrings that only restate the signature or obvious body.
- Shorten private/local names when unambiguous:
  `user_information` -> `user`, `configuration` -> `config`, `result_data` ->
  `result`.
- Replace `%` and `.format()` with f-strings when the target is Python 3.6+ and
  the expression is simple; do not change formatting semantics for custom
  objects.
- Replace wildcard imports with explicit imports; check for name collisions.
- Replace `== None` with `is None`.
- Replace mutable defaults with a `None` sentinel and local initialization.
- Replace bare `except:` with the narrowest correct exception.
- Remove debug `print` calls or route them through the project's logger.
- Modernize `os.path` to `pathlib` only if the project already uses it or the
  change is local and tested.

## Do not change

- Public function/class/module names, `__all__`, CLI flags, config keys.
- Type hints and docstrings that form a public contract or document a tricky
  algorithm.
- Python 2 compatibility if the project still declares it.
- `sys.exit` codes, exception types, logging configuration, or import order
  that affects side effects.
- Test fixtures that intentionally contain bad patterns.

## Example

Before:

```python
def calculate_total_price_with_tax(order_items: list[OrderItem]) -> float:
    """Calculate the total price with tax for the given order items.

    Args:
        order_items: The list of order items.

    Returns:
        The total price including tax.
    """
    total_price = 0.0
    for order_item in order_items:
        total_price += order_item.price * (1 + order_item.tax_rate)
    return total_price
```

After:

```python
def total_with_tax(items: list[OrderItem]) -> float:
    total = 0.0
    for item in items:
        total += item.price * (1 + item.tax_rate)
    return total
```

Keep the annotation on a public API. Drop the docstring only because it repeats
the signature and body.

# Style audit: {{project}}

**Mode:** audit / apply  
**Root:** `{{root}}`  
**Date:** {{date}}  
**Scanner:** `{{scanner_version}}`

## Summary

| Metric | Value |
| --- | --- |
| Files scanned | {{files}} |
| Lines of code | {{loc}} |
| Overall score | {{score}} / 100 |
| Class | {{class}} |
| Confidence | {{confidence}} |

**Heuristic notice:** These scores indicate style resemblance, not authorship
and not whether an AI detector will flag the code. Legacy findings are evidence
and cleanup candidates, not patterns to add.

## Language breakdown

| Language | Files | LOC | Score | AI-shaped | Mixed | Human-shaped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| {{language}} | {{files}} | {{loc}} | {{score}} | {{ai}} | {{mixed}} | {{human}} |

## Strongest AI-style signals

| Rule | Files | Weighted points | Typical evidence |
| --- | ---: | ---: | --- |
| {{rule}} | {{files}} | {{points}} | `{{sample}}` |

## Strongest human-style signals

| Rule | Files | Typical evidence |
| --- | ---: | --- |
| {{rule}} | {{files}} | `{{sample}}` |

## House-style profile

- **Naming:** {{naming}}
- **Comments:** {{comments}}
- **Structure:** {{structure}}
- **Formatting:** {{formatting}}
- **Language/runtime level:** {{runtime}}
- **Public API constraints:** {{api_constraints}}

## Files to rewrite first

| File | Score | Confidence | LOC | Top signals | Proposed batch |
| --- | ---: | ---: | ---: | --- | --- |
| `{{path}}` | {{score}} | {{confidence}} | {{loc}} | {{signals}} | {{batch}} |

## Proposed batches

1. **Comments and local names** — {{batch1}}
2. **Formatting and generated ceremony** — {{batch2}}
3. **Safe structure** — {{batch3}}
4. **Language-specific hygiene** — {{batch4}}

## Skipped and intentionally unchanged

| Path / area | Reason |
| --- | --- |
| `{{path}}` | generated / vendored / public API / too risky / no tests |

## Baseline verification

| Check | Command | Before | After |
| --- | --- | --- | --- |
| Build | `{{build_cmd}}` | {{build_before}} | {{build_after}} |
| Lint | `{{lint_cmd}}` | {{lint_before}} | {{lint_after}} |
| Tests | `{{test_cmd}}` | {{test_before}} | {{test_after}} |

## Risks and open questions

- {{risk}}

## Approval

- [ ] I approve the proposed batches.
- [ ] Public API renames are explicitly allowed.
- [ ] Behavior-changing migrations are out of scope.
- [ ] A branch/worktree and rollback path exist.

Apply mode must not start until this section is approved.

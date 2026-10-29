# Relationship coverage expansion

Historical source-only snapshot. The subsequent [watch-order review](WATCH_ORDER_REVIEW.md) resolves the runtime cycle blocks through a separate editorial policy; raw source relationships remain unchanged.

Generated 2026-10-27T02:27:23.653985+00:00 (UTC).

The ranking algorithm and catalog are unchanged; only relationship evidence expanded.

| Measure | Before | After |
| --- | ---: | ---: |
| Verified catalog titles | 489 | 7871 |
| Returned recommendation slots | 196 | 200 |
| Requests receiving five results | 38 | 40 |
| Recorded policy violations | 0 | 0 |
| Distinct recommended titles | 88 | 114 |

## Popular-title coverage

| Popularity group | Verified | Targeted |
| --- | ---: | ---: |
| Top 100 | 100 | 100 |
| Top 1000 | 1000 | 1000 |
| Top 5000 | 5000 | 5000 |

## Release decades

| Decade | Verified | Catalog |
| --- | ---: | ---: |
| 1900s | 0 | 1 |
| 1910s | 0 | 30 |
| 1920s | 0 | 50 |
| 1930s | 1 | 135 |
| 1940s | 2 | 60 |
| 1950s | 0 | 114 |
| 1960s | 13 | 439 |
| 1970s | 63 | 650 |
| 1980s | 177 | 1763 |
| 1990s | 443 | 2731 |
| 2000s | 1610 | 5552 |
| 2010s | 3319 | 13911 |
| 2020s | 2157 | 11522 |
| 2030s | 0 | 1 |
| unknown | 86 | 1300 |

## Interpretation

- No independent relevance grading; result changes are not proof of improved accuracy.
- Popularity uses the existing catalog snapshot, not a newly fetched ranking.
- Relationship evidence is source metadata, not a curated watch-order guarantee.
- Canonical catalog and saved notebook outputs were not changed.

Strict policy-eligible starting titles after expansion: 3298.
Before expansion: 231.
These counts assume no completed prerequisites and default content/recap policies; they do not require a positive query match.

Unverified prerequisite IDs: 11.
Titles blocked by cyclic dependencies or the 100-level depth guard: 209.
Distinct prerequisite cycle groups: 18.
The JSON comparison includes group members and the source evidence for every internal dependency.
These are cycles in the derived prerequisite policy, not necessarily incorrect source records: chronological prequels and parent/side-story relationships do not always imply mandatory viewing order. The runtime keeps affected titles blocked pending watch-order review.

Detailed per-request changes are in `results/relationship_expansion_comparison.json`.
Download coverage, unavailable records, errors, and pending IDs are in `results/relationship_coverage.json`.

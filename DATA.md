# Anime data refresh

The active data workspace is `data/current/`. Build it with Python 3.10+ and Git; no pip packages, database server, MAL credentials, or VS Code extensions are required. Original project datasets remain as historical inputs in `data/`.

## Run on this Windows computer

From the repository folder in PowerShell:

```powershell
# Rebuild using the downloaded snapshots, without network access
./scripts/data.ps1 scripts/refresh_database.py
# Search the SQLite database
./scripts/data.ps1 scripts/query_database.py "Frieren"
./scripts/data.ps1 scripts/query_database.py --year 2026 --limit 5
# Check the import and generated database
./scripts/data.ps1 -m unittest discover -s tests -v
# Download sources on a new machine, or reuse an existing cache
./scripts/data.ps1 scripts/refresh_database.py --download
# Explicitly update both source snapshots
./scripts/data.ps1 scripts/refresh_database.py --download --refresh
```

The PowerShell helper uses a local `.venv` if present, otherwise the bundled Python available on this computer, otherwise `python` on PATH. On other platforms use `python scripts/refresh_database.py`. No global installations were necessary.

## Sources and freshness

1. [cedya77/anime-offline-database](https://github.com/cedya77/anime-offline-database), continuation of [manami-project](https://github.com/manami-project/anime-offline-database): the downloaded base snapshot reports **2026-10-19**, schema release **2026-43**, and 38,250 entries. This supplies identity mappings, titles, aliases, tags, studios, episodes, season/year, relationships, images and aggregate scores. Its download URL is mutable; the quality report records the actual snapshot date, schema and SHA-256.
2. [meesvandongen/anime-dataset](https://github.com/meesvandongen/anime-dataset): MAL metadata mirror pinned locally to Git revision `d48a8d9b942a76101cba99f5d7825186bb07e8cb`, committed **2026-10-22**. It adds English titles, synopses, genres, dates, MAL ranks, membership and popularity for matching MAL IDs. The source refreshes incrementally: a new repository commit does **not** mean every record was fetched that day. `mal_source_updated_at` is the upstream field, not a verified scrape timestamp.

The canonical `score` remains the base dataset's cross-provider arithmetic mean, with `score_source` identifying it. `mal_score` is a separate value from the mirror. Do not label the aggregate score as a MAL rating. Optional Jikan enrichment replaces the score with MAL's value and labels that source explicitly.

The live [Jikan API](https://docs.api.jikan.moe/) timed out during this session, so the delivered build uses the mirror. A resumable, rate-limited optional importer is available:

```powershell
./scripts/data.ps1 scripts/refresh_database.py --download --jikan
# Full MAL catalog instead of the seasonal/top subset; substantially slower
./scripts/data.ps1 scripts/refresh_database.py --download --jikan --full-mal
```

Cached API pages include URL, retrieval time and checksum. Use `--refresh` for new pages; ordinary runs resume from cache. A failed download exits without building from a silently incomplete request. Offline builds can explicitly use whatever cache is available, with coverage reported.

## Data contract

Validated build coverage: 38,250 catalog entries; 30,870 unambiguous MAL IDs; 25,580 mirror-enriched records; 23,295 nonempty synopses; 26,154 aggregate scores; 1,232 entries with year 2026. There are 14 ambiguous MAL mappings, 111 mirror IDs excluded because they are absent from the base, and 370 duplicate display titles. Five unit/integration tests passed, including SQLite integrity, foreign keys, ID uniqueness, export consistency and 2026 coverage. A fresh offline rebuild also completed successfully. Optional live Jikan downloads could not be validated against the service because requests timed out.

- `anime_id` is a primary key. Use it for joins; titles are not unique. For one-to-one MAL mappings it is `mal:<id>`; otherwise it is a canonical source URL prefixed with `source:`. Source-only identities can change if upstream merges or changes their provider mappings in a future snapshot.
- Records with multiple MAL IDs are retained and marked `ambiguous_mal_mapping`, but receive no mirror enrichment. Auxiliary IDs absent from the base are counted and excluded rather than resurrected.
- Missing scores, dates and counts remain JSON `null` / SQL `NULL`. Unknown episode counts (upstream zero) become null. Seasons are not converted to invented precise dates.
- `genres` holds MAL categories (including themes and demographics). `tags` holds broader cross-provider tags. `cleaned_anime_data.json` combines both for compatibility with the old feature-vector code; canonical `catalog.json` keeps them separate.
- Missing synopses are left missing. Keyword exports use deterministic lowercase tokenization, not the old spaCy lemmatizer. Existing user histories and individual user ratings are not part of these sources. This supports the project's content-based recommender, not collaborative filtering.

## Outputs

| File | Purpose |
| --- | --- |
| `anime.sqlite` | Queryable catalog, indexed titles/years/tags, provider sources and build provenance |
| `catalog.json` | Canonical records with stable IDs and source information |
| `cleaned_anime_data.json` | Legacy field names and combined feature categories |
| `frontend_data.json` | JSON records for UI consumption |
| `synopsis_keywords.json` | Text features keyed by `anime_id` |
| `alphabetized_titles.json` | Distinct display-title list; not an identity lookup |
| `quality_report.json` | Counts, missingness, source checksums/revisions and ambiguous matches |

SQLite `anime.metadata_json` stores all fields; `anime` exposes indexed identity/title/year/score columns. `tags` and `sources` provide normalized many-to-one joins with foreign keys. Related provider URLs and aliases are retained in metadata JSON.

## Existing recommender integration

The old recommendation script still defaults to the original data. Set `ANIME_DATA_DIR` to `data/current` to select this refresh; its synopsis join now uses IDs when present and validates one-to-one matches. This data task does not replace its algorithms: the legacy dense pairwise similarity matrix and Python graph are expensive at 38,250 entries. Use the lightweight database query command to inspect this catalog. A later recommender update should use sparse nearest-neighbor retrieval before running the full new catalog through that algorithm.

## Attribution and distribution

The base database is ODbL 1.0 with DbCL 1.0 contents. Attribute both cedya77 and manami-project and follow the source license for redistributed adapted databases; the original license text is saved in `data/raw/LICENSE-ODbL.txt`. Source providers retain rights to their content. The MAL mirror does not declare a reuse license in its repository; downloaded mirror content and enriched database artifacts are kept local and ignored by Git. Confirm the applicable permissions before publishing a combined data dump. Code, instructions and tests can be reviewed separately from the downloaded data.

To reproduce this exact local build, retain `data/raw/`, including the mirror checkout; `--download --refresh` intentionally moves to newer inputs. Git does not track the raw cache or generated database. The original raw and generated files are retained here for rollback and comparison.

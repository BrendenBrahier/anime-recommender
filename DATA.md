# Anime data pipeline (October 2026)

The canonical catalog, SQLite database, website export and quality report are in `data/current/`. Original project data remains in `data/`. See [DATA_AUDIT.md](DATA_AUDIT.md) for measured coverage, source selection, mapping decisions and remaining gaps.

## Rebuild and inspect

Python 3.10+ and Git are sufficient for the importer. In PowerShell, from this repository:

```powershell
# Obtain the base catalog and MAL mirror on a new computer
./scripts/data.ps1 scripts/refresh_database.py --download
# Download the pinned Kaggle v1 and current seasonal/popular/MAL mapping evidence
./scripts/data.ps1 scripts/enrich_catalog.py
# Target recent titles still missing synopses or categories
./scripts/data.ps1 scripts/enrich_catalog.py --gaps-only
# Build the final database from cached sources
./scripts/data.ps1 scripts/refresh_database.py
# Optional: check 150 cover URLs, then rebuild to attach results
./scripts/data.ps1 scripts/audit_images.py
./scripts/data.ps1 scripts/refresh_database.py
./scripts/data.ps1 scripts/query_database.py Frieren --limit 5
./scripts/data.ps1 -m unittest discover -s tests -v
```

The helper uses `.venv` first, the available bundled Python second, and `python` on PATH otherwise. Downloads are cached; offline rebuilds use those cached bytes. Base/mirror `--download --refresh` explicitly updates those inputs. Tenrai requests reuse cached responses, so retain their retrieval dates and archive the old `data/raw/tenrai/` directory before collecting a new snapshot. Do not run refresh/build commands concurrently. Exact reconstruction requires retaining the raw caches; a fresh online download can yield newer data.

The [public Jikan API closed October 1, 2026](https://github.com/jikan-me/jikan-rest/issues/613). The legacy `--jikan` option now requires `JIKAN_BASE_URL` for an explicitly configured compatible instance. The working replacement used here is [Tenrai](https://api.tenrai.org/documentation), whose public API follows the Jikan schema. Requests are throttled, retried on transient errors and 429s, and stored with URLs and retrieval times. A 404 is recorded as evidence, not treated as proof that two IDs are equivalent.

## Notebook

Open `notebooks/EDA.ipynb` and select `.venv/Scripts/python.exe` in VS Code. The Microsoft Jupyter extension is installed on this computer. Dependencies are in `requirements-notebook.txt`; the local environment already contains them.

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-notebook.txt
```

The notebook uses `data/current/catalog.json`, resolves paths from either the repository or notebook directory, and examines cohort missingness, source provenance, identity decisions, separate score distributions, genres, years and cover availability. It measures data quality, not recommendation accuracy. Executed tables and charts are retained locally and on GitHub. Restored exploratory sections cover descriptive statistics, MAL rank and membership relationships, category combinations, demographics, studio groups, time trends, and outliers. Large tables are summarized or sampled; full downloaded datasets remain local. Saved outputs describe the documented snapshot and should be regenerated after rebuilding the catalog.

## Identity and scores

- Join by `anime_id`, never by display title. One-to-one MAL IDs use `mal:<id>`; source-only records use a provider URL. Source-only IDs can change when upstream mappings change.
- `data/mapping_decisions.json` records evidence-based decisions for the 14 original ambiguous groups. Eight were split into 16 MAL-specific records. No original aggregate score, broad tags or uncertain provider links are copied to those records. `supersedes_ambiguous_id` and the report preserve the old-to-new mapping. Six uncertain groups remain flagged and excluded from recommendations.
- `aggregate_score` is the cross-provider arithmetic mean. `mal_score` is exclusively the MAL rating; each has its own source field. `score` remains a compatibility alias for `aggregate_score`, never switches meaning after enrichment, and is the legacy SQLite column. SQLite exposes `mal_score` separately. Full records live in `anime.metadata_json`.
- Missing values remain null. Placeholder synopsis text is treated as missing. No ratings or synopses are invented. MAL vote counts are retained where available as `mal_scored_by`.
- Canonical `genres` holds MAL categories, including themes/demographics; `tags` holds broad provider tags. The compatibility export combines them only for the old feature-vector code.
- `field_sources` records Kaggle or live API field overrides. Mirror fields retain the mirror revision and source-updated field. A 2026 upload/commit/retrieval date does not prove every underlying field was refreshed that day.

## Website data

`frontend_data.json` includes identity, titles, synopsis, categories, type, year/season/status, episodes, studios, age rating, source material, duration, separate ratings and vote counts, MAL link, cover/thumbnail URLs, optional image variants, alternate covers, alt text, image-check status and optional trailer URL. Availability differs by title.

All catalog entries currently have cover URL strings; this does not mean all images have been fetched or verified. `image_availability` distinguishes reachable samples, placeholder-like URLs and unverified URLs. The eventual website should serve its own generic fallback when a remote image fails, lazy-load artwork, preserve attribution, and avoid claiming blanket image reuse rights. Cover images were not downloaded or republished. Licensor names are not treated as current streaming availability.

`recommendation_eligible` excludes uncertain identity groups and upcoming titles with the status available in this snapshot; it is a basic data flag, not a recommendation score or age/content filter. The website still needs user-facing content filters.

## Files and existing code

`anime.sqlite` has indexed anime/title/year/score fields, normalized tags and provider URLs, foreign keys and build provenance. `catalog.json` is canonical; `cleaned_anime_data.json` retains legacy field names; `synopsis_keywords.json` uses deterministic lowercase tokenization and IDs; `alphabetized_titles.json` is a distinct display list, not an ID lookup; `quality_report.json` contains counts and source hashes.

The old recommender defaults to original data. `ANIME_DATA_DIR=data/current` opts into the refresh and its synopsis join uses IDs. Its dense similarity matrix and graph still need scaling work before full-catalog use. This task does not claim or test recommendation accuracy.

## Sources and redistribution

The base catalog is [cedya77/anime-offline-database](https://github.com/cedya77/anime-offline-database), descended from manami-project, under ODbL 1.0 / DbCL 1.0. Attribute both projects and retain the dataset license requirements. The chosen Kaggle dataset declares the same license family. The [MAL mirror](https://github.com/meesvandongen/anime-dataset) has no declared repository reuse license, and API availability does not grant blanket redistribution rights to text or images. Source providers retain their rights. Raw sources and generated data remain ignored by Git; confirm permissions before publicly distributing the combined database. The checked-in notebook contains analysis code, aggregate charts, and bounded metadata samples; it does not embed the full dataset or cover artwork.

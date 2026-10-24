# Data audit — October 23, 2026

Built 38,259 catalog records; 25,778 have nonempty synopses. The cohort below includes upcoming titles and non-MAL entries.

| Measure | Before | After |
|---|---:|---:|
| Catalog records | 38,250 | 38,259 |
| Nonempty synopses | 23,295 | 25,778 |
| 2026 records | 1,232 | 1,235 |
| 2026 missing synopsis | 435 | 341 |
| 2026 missing genres | 378 | 278 |
| 2026 missing MAL score | 752 | 751 |

The fetched top 1,000 popular titles have no missing synopses, genres or MAL scores. Their coverage was already complete; live metadata was refreshed. Counts across the 2026 cohort use different denominators after identity corrections and one newly discovered title. A missing MAL score is not replaced with an aggregate or zero. Many unscored titles are released but insufficiently rated, not just upcoming.

## Sources assessed

| Source | 2026 evidence | Decision |
|---|---|---|
| [Anime offline database](https://github.com/cedya77/anime-offline-database) | Snapshot October 19, schema 2026-43 | Base identities, tags and aggregate ratings |
| [MAL mirror](https://github.com/meesvandongen/anime-dataset) | Commit October 22, d48a8d9b942a76101cba99f5d7825186bb07e8cb | Existing enrichment retained |
| [Kaggle Anime Dataset 2026](https://www.kaggle.com/datasets/darkbarrierhub/anime-dataset-2026) | Version 1, October 4; 30,763 rows inspected | Used only by MAL ID; fills missing values, adds age ratings/duration/source material |
| [Tenrai MAL API](https://api.tenrai.org/documentation) | Responses fetched October 23 | Four seasons, top 1,000 popular titles, 28 mapping candidates, 93 targeted recent gaps |
| [Kaggle 5,000-title dataset](https://www.kaggle.com/datasets/soulforge/anime-dataset-2026-5000-titles-from-myanimelist) | Metadata lists May 3 update | Screened metadata only; smaller alternative, not imported |
| [Kaggle reviews](https://www.kaggle.com/datasets/patelris/anime-reviews-and-sentiment-dataset-2026) | Metadata lists April 29 update | Deferred: subjective review text is not a factual metadata replacement |

Kaggle source metadata, zip bytes, hashes and live response retrieval dates are retained locally. The Kaggle dataset filled 2,502 synopsis gaps and 5,190 category gaps at its pipeline stage; final net coverage differs because placeholder cleanup, live overrides and mapping splits also apply. It supplied 994 missing MAL scores across the full catalog, with source labels. No user reviews or generated opinions were added as facts. Do not infer a per-record scrape date from the dataset publication date.

## Mapping review

| Original title | MAL IDs | Decision | Evidence |
|---|---|---|---|
| Hokuto no Ken: Kenougun Zako-tachi no Banka | 62987, 64378 | split | Part 1 and Part 2, with January and July 2026 starts; Part 2 synopsis explicitly identifies a second part. |
| Ienai feat. asmi | 54100, 54152 | split | Different songs and artists despite shared asmi vocals: MIMiNARI's Ienai and meiyo's Nani Yatte mo Umaku Ikanai. |
| Islay | 37135, 55706 | split | Different songs and artists: Islay by Otogivanashi and Music by Kuusou Iinkai. |
| Jiu Wo | 59380, 63451 | split | Jiu Wo is an ONA about a strange bottle; Save Me is an Xdinary Heroes music video. |
| Madonna (Movie) | 22177, 38870 | quarantine | Different titles but same year and sparse summaries; insufficient evidence to identify or merge these short films. |
| Moonlight | 59994, 60524 | split | Different artists: Moonlight by Suisei Hoshimachi versus Moonlight by MOON SHARK. |
| Ninifuni no Niwa | 64901, 65096 | quarantine | Identical title and missing synopses; differing dates alone do not establish different films. |
| Nue no Onmyouji | 65177, 65180 | quarantine | 65177 returned HTTP 404 while 65180 is available. A 404 alone does not prove a redirect or authorize collapsing the IDs. |
| Omajinai | 58039, 62463 | quarantine | Same title, differing dates, and no synopsis for 62463; not enough evidence to split or merge confidently. |
| Puu-Neko | 10459, 11589 | split | MAL explicitly reports sequel/prequel relations and calls Shougekijou the retitled second part. |
| Te Ke Dong Ji Pian | 39189, 45787 | quarantine | Similar transliterated titles, but ONA/TV and 54/57 episode disagreement; no decisive duplicate or separate-work evidence. |
| Veil | 57187, 64071 | split | Different artists and release years: millennium parade's Veil (2019) versus Misuzu Hataya's Veil (2026). |
| Xiao Qian | 315, 60451 | split | Separate films: Xiao Qian released in 1997 and Xiaoqian in 2024. |
| Xing Mao Lixian Ji Zhi Shu Fa Pian | 30140, 45268 | quarantine | Likely duplicate transliterations with 26 episodes each, but no authoritative redirect or duplicate confirmation. |

Evidence URLs follow `https://api.tenrai.org/v1/anime/{id}/full`; cached responses preserve the supporting titles, dates, artists, relationships and response status. Uncertain groups remain excluded; a 404 alone was not used to merge IDs.

## Pictures and remaining work

All records have cover URL strings. A deterministic sample of 150 unique URLs returned 138 image responses; 12 were outside the checker host allowlist and remain unverified. This is a sample, not an all-catalog availability guarantee. Placeholder-like URLs are separately flagged. The website export carries large covers, available thumbnails/variants, alternate URLs, alt text and verification status; image licensing and fallback handling remain website integration work.

The remaining recent-title gaps are listed in the notebook by type/status. Additional unrelated data would not automatically improve accuracy. The next model stage needs a preference-based evaluation and sparse retrieval; it should use missingness and vote counts rather than fabricating confidence. Review text can be considered later as a separate, spoiler-aware, source-attributed feature.

Validation: eight unit/integration tests, SQLite integrity and foreign-key checks, website export identity/field checks, and all eight notebook code cells executed successfully. No recommendation accuracy score is claimed.

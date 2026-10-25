# Recommendation evaluation: first development benchmark

Snapshot: October 2026 catalog, 38,259 entries. Forty authored requests cover eight topics and five scenarios each: one liked title, a short completed TV series, a release-era range, multiple likes/dislikes and excluded categories, and a no-seed movie request. These are 40 variations of eight taste profiles, not 40 independent users.

## Objective checks

| Method | Supported requests | Returned top-5 slots | Results violating constraints | Category diversity | Distinct titles |
|---|---:|---:|---:|---:|---:|
| hybrid | 40/40 | 200 | 0/200 (0.0%) | 0.423 | 127 |
| legacy_cosine | 32/40 | 160 | 53/160 (33.1%) | 0.608 | 40 |
| legacy_filtered | 32/40 | 160 | 0/160 (0.0%) | 0.596 | 79 |

Constraint checks use the current catalog, not independent verification of every episode count, genre, or status. Unknown constrained values fail closed. Explicit hentai is excluded, but the benchmark is not a general age-safety classifier. Diversity is pairwise category Jaccard distance: higher can also mean less relevant results. Distinct-title totals cover different numbers of supported requests; use matched cases for head-to-head comparisons.

## Provisional relevance on the same 32 seed requests

| Method | Judged / returned | Mean topical grade (0–3, known only) | Plausible-or-strong lower bound / all slots | Relevant AND constraint-compliant lower bound |
|---|---:|---:|---:|---:|
| hybrid | 158/160 | 2.418 | 84.4% | 84.4% |
| legacy_cosine | 136/160 | 2.118 | 57.5% | 43.1% |

Grades are an assistant first pass based on catalog synopsis excerpts and categories, with candidate model/rank hidden during review. The same assistant authored the cases and prototype, so these are not independent human judgments or proven recommendation accuracy. Grades describe topical fit; hard constraints are scored separately. Uncertain entries stay unknown and contribute no credit to lower bounds. Topic grades are reused across constraint variants. Soft-dislike satisfaction and prerequisite suitability are not numerically validated. The filter-only control is not relevance-graded.

## What to improve next

1. **Apply explicit filters first.** The filter-only control isolates this benefit; a new semantic model is not necessary to obey episode, format, era, completion, and seen-title constraints.
2. **Add franchise relationships and recap flags.** Haikyu and Non Non Biyori lists concentrate on the same franchise; mystery results include Death Note recaps and later seasons. Exact-ID exclusions do not solve cross-provider duplicates or viewing order.
3. **Improve tone matching and format defaults.** Cold-start calm requests return generic comedy shorts. Music requests can return music videos rather than stories about musicians. Topic overlap alone is insufficient.
4. **Resolve sparse identities and audit metadata.** Source-only recommendations with empty synopses cannot be confidently judged. Filter correctness is only as strong as source metadata.
5. **Collect independent human ratings before tuning.** Review the provisional labels, add genuinely new requests, and reserve a separate held-out set. Compare pretrained sentence embeddings with this inexpensive LSA baseline before adopting either.

## Methods and reproducibility

- `legacy_cosine`: same TF-IDF feature construction and scaled score/membership cosine as the existing code, using current compatibility data. Computes one similarity row per seed instead of the full square matrix. Uses stable IDs and explicitly removes the seed; original title-collision behavior is not reproduced. Graph/hashmap dispatch is not evaluated; existing dispatch signatures/columns are inconsistent.
- `legacy_filtered`: identical ranking with request filters, used as an objective control.
- `hybrid`: synopsis TF-IDF plus 64-dimensional latent semantic analysis (LSA), category similarity, vote-shrunk MAL score, likes/dislikes, hard filters, and a modest diversity penalty. Weights fixed at .35 lexical, .30 LSA, .25 categories, .10 score; dislike penalty .15, diversity penalty .10. LSA is corpus-derived topic matching, not a pretrained language model. See [scikit-learn TruncatedSVD documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html).
- Requests have explicitly authored structured filters and preferences. This benchmark does **not** test automatic natural-language parsing. Both ranking methods use the same catalog snapshot. No preference labels are used to train the topic model.
- Development corrections before final results: fixed the calm-profile seed ID and made unknown excluded-category metadata fail closed. No ranking weights were tuned against the judgments.
- Ranked result lists, source hashes, package versions, and random seed are in `results/benchmark.json`. Saved results are tied to local raw-source caches; a fresh source download may change them.

```powershell
python -m pip install -r requirements-evaluation.txt
python scripts/evaluate_recommendations.py
python scripts/report_evaluation.py
python -m unittest discover -s tests -p test_evaluation.py -v
```

The evaluation command requires the generated `data/current` files (see DATA.md). The report command rejects judgments from another snapshot. `results/review.html` and `results/review_queue.json` are local review aids containing synopses; they are not published. Edit the separate `initial_judgments.json` labels with reviewer identity and reasoning when conducting human review. Running the benchmark does not overwrite those labels. Full result lists follow.

## Results for every request

### space-1

I enjoyed Cowboy Bebop. Space travel, adult characters, bounty hunters and an adventurous crew.

**hybrid**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 2. Mighty Space Miners (mal:1867) — 2/3; passes recorded constraints.
- 3. Shinsei Galverse (mal:61672) — 1/3; passes recorded constraints.
- 4. Astra Lost in Space (mal:39198) — 2/3; passes recorded constraints.
- 5. Star Dust (mal:18703) — 1/3; passes recorded constraints.

**legacy_cosine**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 2. Legend of the Galactic Heroes: Die Neue These Third 1 (source:https://anilist.co/anime/124032) — unknown; passes recorded constraints.
- 3. Outlaw Star (mal:400) — 3/3; passes recorded constraints.
- 4. Cobra The Animation (mal:5032) — 3/3; passes recorded constraints.
- 5. Legend of the Galactic Heroes (mal:820) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Cowboy Bebop: The Movie (mal:5) — not graded; passes recorded constraints.
- 2. Legend of the Galactic Heroes: Die Neue These Third 1 (source:https://anilist.co/anime/124032) — not graded; passes recorded constraints.
- 3. Outlaw Star (mal:400) — not graded; passes recorded constraints.
- 4. Cobra The Animation (mal:5032) — not graded; passes recorded constraints.
- 5. Legend of the Galactic Heroes (mal:820) — not graded; passes recorded constraints.

### space-2

I enjoyed Cowboy Bebop. Space travel, adult characters, bounty hunters and an adventurous crew. Only finished TV series with at most 24 episodes. I already watched Outlaw Star.

**hybrid**

- 1. Astra Lost in Space (mal:39198) — 2/3; passes recorded constraints.
- 2. Captain Harlock: Arcadia of my Youth - Endless Orbit SSX (mal:2203) — 3/3; passes recorded constraints.
- 3. Space Patrol Luluco (mal:32681) — 1/3; passes recorded constraints.
- 4. RobiHachi (mal:38707) — 2/3; passes recorded constraints.
- 5. Between the Sky and Sea (mal:36000) — 1/3; passes recorded constraints.

**legacy_cosine**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; format.
- 2. Legend of the Galactic Heroes: Die Neue These Third 1 (source:https://anilist.co/anime/124032) — unknown; format.
- 3. Outlaw Star (mal:400) — 3/3; already_seen_or_disliked.
- 4. Cobra The Animation (mal:5032) — 3/3; passes recorded constraints.
- 5. Legend of the Galactic Heroes (mal:820) — 2/3; format, max_episodes_or_unknown.

**legacy_filtered**

- 1. Cobra The Animation (mal:5032) — not graded; passes recorded constraints.
- 2. Solty Rei (mal:152) — not graded; passes recorded constraints.
- 3. Astra Lost in Space (mal:39198) — not graded; passes recorded constraints.
- 4. The Galaxy Railways II (mal:2717) — not graded; passes recorded constraints.
- 5. Attack on Titan Season 3 Part 2 (mal:38524) — not graded; passes recorded constraints.

### space-3

I enjoyed Cowboy Bebop. Space travel, adult characters, bounty hunters and an adventurous crew. Choose TV series or movies released between 1990 and 2009.

**hybrid**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 2. Xevious (mal:12799) — 2/3; passes recorded constraints.
- 3. Outlaw Star (mal:400) — 3/3; passes recorded constraints.
- 4. The Galaxy Railways (mal:1490) — 2/3; passes recorded constraints.
- 5. After War Gundam X (mal:92) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 2. Legend of the Galactic Heroes: Die Neue These Third 1 (source:https://anilist.co/anime/124032) — unknown; year_max_or_unknown.
- 3. Outlaw Star (mal:400) — 3/3; passes recorded constraints.
- 4. Cobra The Animation (mal:5032) — 3/3; year_max_or_unknown.
- 5. Legend of the Galactic Heroes (mal:820) — 2/3; format, year_min_or_unknown.

**legacy_filtered**

- 1. Cowboy Bebop: The Movie (mal:5) — not graded; passes recorded constraints.
- 2. Outlaw Star (mal:400) — not graded; passes recorded constraints.
- 3. Solty Rei (mal:152) — not graded; passes recorded constraints.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — not graded; passes recorded constraints.
- 5. Trigun (mal:6) — not graded; passes recorded constraints.

### space-4

I enjoyed Cowboy Bebop. Space travel, adult characters, bounty hunters and an adventurous crew. I also liked Outlaw Star, but disliked Attack on Titan. Exclude romance.

**hybrid**

- 1. Byeolnala Samchongsa (mal:6671) — 1/3; passes recorded constraints.
- 2. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 3. Iria: Zeiram The Animation (mal:432) — 3/3; passes recorded constraints.
- 4. Crusher Joe: The Movie (mal:2722) — 3/3; passes recorded constraints.
- 5. Nora (mal:2088) — 1/3; passes recorded constraints.

**legacy_cosine**

- 1. Cowboy Bebop: The Movie (mal:5) — 3/3; passes recorded constraints.
- 2. Legend of the Galactic Heroes: Die Neue These Third 1 (source:https://anilist.co/anime/124032) — unknown; unknown_categories.
- 3. Outlaw Star (mal:400) — 3/3; already_seen_or_disliked.
- 4. Cobra The Animation (mal:5032) — 3/3; passes recorded constraints.
- 5. Legend of the Galactic Heroes (mal:820) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Cowboy Bebop: The Movie (mal:5) — not graded; passes recorded constraints.
- 2. Cobra The Animation (mal:5032) — not graded; passes recorded constraints.
- 3. Legend of the Galactic Heroes (mal:820) — not graded; passes recorded constraints.
- 4. Solty Rei (mal:152) — not graded; passes recorded constraints.
- 5. Cyborg 009: Legend of the Super Galaxy (mal:7336) — not graded; passes recorded constraints.

### space-5

Space travel, adult characters, bounty hunters and an adventurous crew. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Byeolnala Samchongsa (mal:6671) — 1/3; passes recorded constraints.
- 2. Bodacious Space Pirates the Movie: Abyss of Hyperspace (mal:14817) — 2/3; passes recorded constraints.
- 3. Beast Wars Second Chou Seimeitai Transformers: Lio Convoy Kiki Ippatsu! Movie (mal:5289) — 1/3; passes recorded constraints.
- 4. Xevious (mal:12799) — 2/3; passes recorded constraints.
- 5. Arei's Mirror ~ Way to the Virgin Space (mal:7156) — 2/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### mystery-1

I enjoyed Death Note. A tense psychological mystery with clever investigations and moral dilemmas.

**hybrid**

- 1. Death Note: Relight (mal:2994) — 1/3; passes recorded constraints.
- 2. Ghost Hound (mal:2596) — 2/3; passes recorded constraints.
- 3. ID: INVADED (mal:40046) — 3/3; passes recorded constraints.
- 4. Talentless Nana (mal:41619) — 2/3; passes recorded constraints.
- 5. Black Jack (mal:1520) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Death Note Rewrite 1: Visions of a God (source:https://anidb.net/anime/8146) — unknown; passes recorded constraints.
- 2. Death Note Rewrite 2: L's Successors (source:https://anidb.net/anime/8147) — unknown; passes recorded constraints.
- 3. Attack on Titan (mal:16498) — 1/3; passes recorded constraints.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — 2/3; passes recorded constraints.
- 5. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Death Note Rewrite 1: Visions of a God (source:https://anidb.net/anime/8146) — not graded; passes recorded constraints.
- 2. Death Note Rewrite 2: L's Successors (source:https://anidb.net/anime/8147) — not graded; passes recorded constraints.
- 3. Attack on Titan (mal:16498) — not graded; passes recorded constraints.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — not graded; passes recorded constraints.
- 5. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — not graded; passes recorded constraints.

### mystery-2

I enjoyed Death Note. A tense psychological mystery with clever investigations and moral dilemmas. Only finished TV series with at most 24 episodes. I already watched Monster.

**hybrid**

- 1. Ghost Hound (mal:2596) — 2/3; passes recorded constraints.
- 2. ID: INVADED (mal:40046) — 3/3; passes recorded constraints.
- 3. Talentless Nana (mal:41619) — 2/3; passes recorded constraints.
- 4. Moriarty the Patriot Part 2 (mal:43325) — 3/3; passes recorded constraints.
- 5. Terror in Resonance (mal:23283) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Death Note Rewrite 1: Visions of a God (source:https://anidb.net/anime/8146) — unknown; format.
- 2. Death Note Rewrite 2: L's Successors (source:https://anidb.net/anime/8147) — unknown; format.
- 3. Attack on Titan (mal:16498) — 1/3; max_episodes_or_unknown.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — 2/3; max_episodes_or_unknown.
- 5. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — 2/3; max_episodes_or_unknown.

**legacy_filtered**

- 1. Erased (mal:31043) — not graded; passes recorded constraints.
- 2. Psycho-Pass (mal:13601) — not graded; passes recorded constraints.
- 3. Attack on Titan Season 3 Part 2 (mal:38524) — not graded; passes recorded constraints.
- 4. Tokyo Ghoul (mal:22319) — not graded; passes recorded constraints.
- 5. Attack on Titan: Final Season (mal:40028) — not graded; passes recorded constraints.

### mystery-3

I enjoyed Death Note. A tense psychological mystery with clever investigations and moral dilemmas. Choose TV series or movies released between 2000 and 2014.

**hybrid**

- 1. Ghost Hound (mal:2596) — 2/3; passes recorded constraints.
- 2. Terror in Resonance (mal:23283) — 3/3; passes recorded constraints.
- 3. Shigofumi: Letters from the Departed (mal:3420) — 2/3; passes recorded constraints.
- 4. Mononoke (mal:2246) — 3/3; passes recorded constraints.
- 5. Paprika (mal:1943) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Death Note Rewrite 1: Visions of a God (source:https://anidb.net/anime/8146) — unknown; format.
- 2. Death Note Rewrite 2: L's Successors (source:https://anidb.net/anime/8147) — unknown; format.
- 3. Attack on Titan (mal:16498) — 1/3; passes recorded constraints.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — 2/3; passes recorded constraints.
- 5. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Attack on Titan (mal:16498) — not graded; passes recorded constraints.
- 2. Code Geass: Lelouch of the Rebellion (mal:1575) — not graded; passes recorded constraints.
- 3. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — not graded; passes recorded constraints.
- 4. Fullmetal Alchemist: Brotherhood (mal:5114) — not graded; passes recorded constraints.
- 5. Psycho-Pass (mal:13601) — not graded; passes recorded constraints.

### mystery-4

I enjoyed Death Note. A tense psychological mystery with clever investigations and moral dilemmas. I also liked Monster, but disliked Attack on Titan. Exclude comedy.

**hybrid**

- 1. Ghost Hound (mal:2596) — 2/3; passes recorded constraints.
- 2. Have a Nice Day (mal:37177) — 2/3; passes recorded constraints.
- 3. Terror in Resonance (mal:23283) — 3/3; passes recorded constraints.
- 4. Death Note: Relight (mal:2994) — 1/3; passes recorded constraints.
- 5. Paprika (mal:1943) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Death Note Rewrite 1: Visions of a God (source:https://anidb.net/anime/8146) — unknown; unknown_categories.
- 2. Death Note Rewrite 2: L's Successors (source:https://anidb.net/anime/8147) — unknown; unknown_categories.
- 3. Attack on Titan (mal:16498) — 1/3; already_seen_or_disliked.
- 4. Code Geass: Lelouch of the Rebellion (mal:1575) — 2/3; passes recorded constraints.
- 5. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Code Geass: Lelouch of the Rebellion (mal:1575) — not graded; passes recorded constraints.
- 2. Code Geass: Lelouch of the Rebellion R2 (mal:2904) — not graded; passes recorded constraints.
- 3. Fullmetal Alchemist: Brotherhood (mal:5114) — not graded; passes recorded constraints.
- 4. Erased (mal:31043) — not graded; passes recorded constraints.
- 5. Psycho-Pass (mal:13601) — not graded; passes recorded constraints.

### mystery-5

A tense psychological mystery with clever investigations and moral dilemmas. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Have a Nice Day (mal:37177) — 2/3; passes recorded constraints.
- 2. Paprika (mal:1943) — 3/3; passes recorded constraints.
- 3. Oshie to Tabi Suru Otoko (mal:37365) — 2/3; passes recorded constraints.
- 4. When Marnie Was There (mal:21557) — 1/3; passes recorded constraints.
- 5. Loups=Garous (mal:7598) — 2/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### fantasy-1

I enjoyed Frieren: Beyond Journey's End. A reflective fantasy journey about friendship, loss and discovering a magical world.

**hybrid**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Tales of the Abyss (mal:4884) — 2/3; passes recorded constraints.
- 3. Kino's Journey -the Beautiful World- the Animated Series (mal:35079) — 3/3; passes recorded constraints.
- 4. RG Veda (mal:439) — 1/3; passes recorded constraints.
- 5. Tsubasa RESERVoir CHRoNiCLE Season Two (mal:969) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Sousou no Frieren: Ougonkyou-hen (mal:63816) — unknown; ineligible_or_upcoming.
- 3. Frieren: Beyond Journey's End Mini Anime (mal:56885) — 1/3; passes recorded constraints.
- 4. Fairy Tail Final Series (mal:35972) — 1/3; passes recorded constraints.
- 5. Demon Slayer: Kimetsu no Yaiba (mal:38000) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — not graded; passes recorded constraints.
- 2. Frieren: Beyond Journey's End Mini Anime (mal:56885) — not graded; passes recorded constraints.
- 3. Fairy Tail Final Series (mal:35972) — not graded; passes recorded constraints.
- 4. Demon Slayer: Kimetsu no Yaiba (mal:38000) — not graded; passes recorded constraints.
- 5. Clevatess Season 2 (mal:62513) — not graded; passes recorded constraints.

### fantasy-2

I enjoyed Frieren: Beyond Journey's End. A reflective fantasy journey about friendship, loss and discovering a magical world. Only finished TV series with at most 24 episodes. I already watched Mushi-Shi.

**hybrid**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Legend of Himiko (mal:360) — 1/3; passes recorded constraints.
- 3. Kino's Journey -the Beautiful World- the Animated Series (mal:35079) — 3/3; passes recorded constraints.
- 4. The Rising of the Shield Hero Season 4 (mal:57907) — 1/3; passes recorded constraints.
- 5. Kaina of the Great Snow Sea (mal:50864) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Sousou no Frieren: Ougonkyou-hen (mal:63816) — unknown; ineligible_or_upcoming, not_finished_or_unknown.
- 3. Frieren: Beyond Journey's End Mini Anime (mal:56885) — 1/3; format.
- 4. Fairy Tail Final Series (mal:35972) — 1/3; max_episodes_or_unknown.
- 5. Demon Slayer: Kimetsu no Yaiba (mal:38000) — 2/3; max_episodes_or_unknown.

**legacy_filtered**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — not graded; passes recorded constraints.
- 2. Clevatess Season 2 (mal:62513) — not graded; passes recorded constraints.
- 3. Mushoku Tensei: Jobless Reincarnation Part 2 (mal:45576) — not graded; passes recorded constraints.
- 4. Demon Slayer: Kimetsu no Yaiba Entertainment District Arc (mal:47778) — not graded; passes recorded constraints.
- 5. Maoyu (mal:14833) — not graded; passes recorded constraints.

### fantasy-3

I enjoyed Frieren: Beyond Journey's End. A reflective fantasy journey about friendship, loss and discovering a magical world. Choose TV series or movies released between 2010 and 2026.

**hybrid**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Kaina of the Great Snow Sea: Star Sage (mal:54122) — 2/3; passes recorded constraints.
- 3. Kino's Journey -the Beautiful World- the Animated Series (mal:35079) — 3/3; passes recorded constraints.
- 4. The Rising of the Shield Hero Season 4 (mal:57907) — 1/3; passes recorded constraints.
- 5. The Legend of Hei (mal:40211) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Sousou no Frieren: Ougonkyou-hen (mal:63816) — unknown; ineligible_or_upcoming, year_max_or_unknown.
- 3. Frieren: Beyond Journey's End Mini Anime (mal:56885) — 1/3; format.
- 4. Fairy Tail Final Series (mal:35972) — 1/3; passes recorded constraints.
- 5. Demon Slayer: Kimetsu no Yaiba (mal:38000) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — not graded; passes recorded constraints.
- 2. Fairy Tail Final Series (mal:35972) — not graded; passes recorded constraints.
- 3. Demon Slayer: Kimetsu no Yaiba (mal:38000) — not graded; passes recorded constraints.
- 4. Clevatess Season 2 (mal:62513) — not graded; passes recorded constraints.
- 5. Goblin Slayer: Goblin's Crown (mal:39576) — not graded; passes recorded constraints.

### fantasy-4

I enjoyed Frieren: Beyond Journey's End. A reflective fantasy journey about friendship, loss and discovering a magical world. I also liked Mushi-Shi, but disliked Attack on Titan. Exclude ecchi.

**hybrid**

- 1. Hana no Mahoutsukai Mary Bell (mal:2804) — 1/3; passes recorded constraints.
- 2. Tales of the Abyss (mal:4884) — 2/3; passes recorded constraints.
- 3. Wan Jie Shen Zhu (mal:39191) — 1/3; passes recorded constraints.
- 4. Lost in the Moonlight (mal:43387) — 2/3; passes recorded constraints.
- 5. Tsubasa RESERVoir CHRoNiCLE Season Two (mal:969) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — 3/3; passes recorded constraints.
- 2. Sousou no Frieren: Ougonkyou-hen (mal:63816) — unknown; ineligible_or_upcoming.
- 3. Frieren: Beyond Journey's End Mini Anime (mal:56885) — 1/3; passes recorded constraints.
- 4. Fairy Tail Final Series (mal:35972) — 1/3; passes recorded constraints.
- 5. Demon Slayer: Kimetsu no Yaiba (mal:38000) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Frieren: Beyond Journey's End Season 2 (mal:59978) — not graded; passes recorded constraints.
- 2. Frieren: Beyond Journey's End Mini Anime (mal:56885) — not graded; passes recorded constraints.
- 3. Fairy Tail Final Series (mal:35972) — not graded; passes recorded constraints.
- 4. Demon Slayer: Kimetsu no Yaiba (mal:38000) — not graded; passes recorded constraints.
- 5. Clevatess Season 2 (mal:62513) — not graded; passes recorded constraints.

### fantasy-5

A reflective fantasy journey about friendship, loss and discovering a magical world. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Kaina of the Great Snow Sea: Star Sage (mal:54122) — 2/3; passes recorded constraints.
- 2. Lost in the Moonlight (mal:43387) — 2/3; passes recorded constraints.
- 3. Doraemon the Movie: Nobita's Great Adventure into the Underworld (mal:2672) — 1/3; passes recorded constraints.
- 4. A Tale From The Orient (mal:50168) — 1/3; passes recorded constraints.
- 5. Digimon Adventure 02: The Beginning (mal:49523) — 2/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### romance-1

I enjoyed Toradora!. A character driven school romance with comedy, friendships and emotional growth.

**hybrid**

- 1. School Rumble (mal:24) — 3/3; passes recorded constraints.
- 2. The Ramparts of Ice (mal:60852) — 3/3; passes recorded constraints.
- 3. Kujibiki Unbalance (mal:669) — 2/3; passes recorded constraints.
- 4. Venus to Mamoru! (mal:1588) — 2/3; passes recorded constraints.
- 5. Clannad: Another World, Tomoyo Chapter (mal:4059) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Horimiya (mal:42897) — 3/3; passes recorded constraints.
- 2. Clannad (mal:2167) — 3/3; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — 3/3; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — 2/3; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. Horimiya (mal:42897) — not graded; passes recorded constraints.
- 2. Clannad (mal:2167) — not graded; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — not graded; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — not graded; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — not graded; passes recorded constraints.

### romance-2

I enjoyed Toradora!. A character driven school romance with comedy, friendships and emotional growth. Only finished TV series with at most 24 episodes. I already watched The Tatami Galaxy.

**hybrid**

- 1. The Ramparts of Ice (mal:60852) — 3/3; passes recorded constraints.
- 2. Venus to Mamoru! (mal:1588) — 2/3; passes recorded constraints.
- 3. Kujibiki♥Unbalance (mal:1591) — 2/3; passes recorded constraints.
- 4. Yano-kun's Ordinary Days (mal:60254) — 3/3; passes recorded constraints.
- 5. Can a Boy-Girl Friendship Survive? (mal:52709) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Horimiya (mal:42897) — 3/3; passes recorded constraints.
- 2. Clannad (mal:2167) — 3/3; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — 3/3; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — 2/3; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — 1/3; format.

**legacy_filtered**

- 1. Horimiya (mal:42897) — not graded; passes recorded constraints.
- 2. Clannad (mal:2167) — not graded; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — not graded; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — not graded; passes recorded constraints.
- 5. Rascal Does Not Dream of Bunny Girl Senpai (mal:37450) — not graded; passes recorded constraints.

### romance-3

I enjoyed Toradora!. A character driven school romance with comedy, friendships and emotional growth. Choose TV series or movies released between 2000 and 2014.

**hybrid**

- 1. School Rumble (mal:24) — 3/3; passes recorded constraints.
- 2. Venus to Mamoru! (mal:1588) — 2/3; passes recorded constraints.
- 3. Kujibiki♥Unbalance (mal:1591) — 2/3; passes recorded constraints.
- 4. ItaKiss (mal:3731) — 3/3; passes recorded constraints.
- 5. Baka & Test: Summon the Beasts (mal:6347) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Horimiya (mal:42897) — 3/3; year_max_or_unknown.
- 2. Clannad (mal:2167) — 3/3; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — 3/3; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — 2/3; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — 1/3; format.

**legacy_filtered**

- 1. Clannad (mal:2167) — not graded; passes recorded constraints.
- 2. KimiKiss: Pure Rouge (mal:2927) — not graded; passes recorded constraints.
- 3. Clannad: After Story (mal:4181) — not graded; passes recorded constraints.
- 4. My Little Monster (mal:14227) — not graded; passes recorded constraints.
- 5. School Rumble (mal:24) — not graded; passes recorded constraints.

### romance-4

I enjoyed Toradora!. A character driven school romance with comedy, friendships and emotional growth. I also liked The Tatami Galaxy, but disliked Attack on Titan. Exclude horror.

**hybrid**

- 1. School Rumble (mal:24) — 3/3; passes recorded constraints.
- 2. Kujibiki♥Unbalance (mal:1591) — 2/3; passes recorded constraints.
- 3. Kujibiki Unbalance (mal:669) — 2/3; passes recorded constraints.
- 4. Venus to Mamoru! (mal:1588) — 2/3; passes recorded constraints.
- 5. Musunde Hiraite (mal:38272) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Horimiya (mal:42897) — 3/3; passes recorded constraints.
- 2. Clannad (mal:2167) — 3/3; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — 3/3; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — 2/3; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. Horimiya (mal:42897) — not graded; passes recorded constraints.
- 2. Clannad (mal:2167) — not graded; passes recorded constraints.
- 3. KimiKiss: Pure Rouge (mal:2927) — not graded; passes recorded constraints.
- 4. Clannad: After Story (mal:4181) — not graded; passes recorded constraints.
- 5. Toradora! Special (mal:11553) — not graded; passes recorded constraints.

### romance-5

A character driven school romance with comedy, friendships and emotional growth. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Tooi-san wa Seishun Shitai! Baka to Smartphone to Romance to (mal:61367) — 2/3; passes recorded constraints.
- 2. The Moment You Fall in Love (mal:33036) — 3/3; passes recorded constraints.
- 3. Rascal Does Not Dream of a Sister Venturing Out (mal:53129) — 1/3; passes recorded constraints.
- 4. Kaede New Town (mal:5799) — 2/3; passes recorded constraints.
- 5. Love, Chunibyo & Other Delusions!: Take On Me (mal:35608) — 3/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### sports-1

I enjoyed Haikyu!!. A sports team improving through training, teamwork and competitive matches.

**hybrid**

- 1. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 2. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 3. Haikyu!! The Movie: Talent and Sense (mal:35110) — 2/3; passes recorded constraints.
- 4. Haikyu!! Movie: The Dumpster Battle (mal:52742) — 3/3; passes recorded constraints.
- 5. Haikyu!! 2nd Season (mal:28891) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — 3/3; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — unknown; passes recorded constraints.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — unknown; passes recorded constraints.

**legacy_filtered**

- 1. Haikyu!! To the Top (mal:38883) — not graded; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — not graded; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — not graded; passes recorded constraints.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — not graded; passes recorded constraints.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — not graded; passes recorded constraints.

### sports-2

I enjoyed Haikyu!!. A sports team improving through training, teamwork and competitive matches. Only finished TV series with at most 24 episodes. I already watched Kuroko's Basketball.

**hybrid**

- 1. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 2. Haikyu!! 3rd Season (mal:32935) — 3/3; passes recorded constraints.
- 3. 2.43: Seiin High School Boys Volleyball Team (mal:40679) — 3/3; passes recorded constraints.
- 4. Haikyu!! To the Top 2nd-cour (mal:40776) — 3/3; passes recorded constraints.
- 5. TAMAYOMI: The Baseball Girls (mal:39966) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — 3/3; max_episodes_or_unknown.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; format.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — unknown; format.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — unknown; format.

**legacy_filtered**

- 1. Haikyu!! To the Top (mal:38883) — not graded; passes recorded constraints.
- 2. Haikyu!! 3rd Season (mal:32935) — not graded; passes recorded constraints.
- 3. Attack on Tomorrow (mal:4339) — not graded; passes recorded constraints.
- 4. Haikyu!! To the Top 2nd-cour (mal:40776) — not graded; passes recorded constraints.
- 5. Yowamushi Pedal: Grande Road (mal:24277) — not graded; passes recorded constraints.

### sports-3

I enjoyed Haikyu!!. A sports team improving through training, teamwork and competitive matches. Choose TV series or movies released between 2010 and 2026.

**hybrid**

- 1. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 2. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 3. Haikyu!! The Movie: Talent and Sense (mal:35110) — 2/3; passes recorded constraints.
- 4. Haikyu!! Movie: The Dumpster Battle (mal:52742) — 3/3; passes recorded constraints.
- 5. Haikyu!! 2nd Season (mal:28891) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — 3/3; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — unknown; passes recorded constraints.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — unknown; passes recorded constraints.

**legacy_filtered**

- 1. Haikyu!! To the Top (mal:38883) — not graded; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — not graded; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — not graded; passes recorded constraints.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — not graded; passes recorded constraints.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — not graded; passes recorded constraints.

### sports-4

I enjoyed Haikyu!!. A sports team improving through training, teamwork and competitive matches. I also liked Kuroko's Basketball, but disliked Attack on Titan. Exclude supernatural.

**hybrid**

- 1. Winter Cup Highlights Episode 1 – Winter Cup Highlights -Shadow and Light- (mal:32869) — 2/3; passes recorded constraints.
- 2. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 3. Haikyu!! The Movie: Talent and Sense (mal:35110) — 2/3; passes recorded constraints.
- 4. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 5. 2.43: Seiin High School Boys Volleyball Team (mal:40679) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Haikyu!! To the Top (mal:38883) — 3/3; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — 3/3; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — 1/3; passes recorded constraints.
- 4. Gekijouban Soushuuhen Haikyuu!! (source:https://anidb.net/anime/12982) — unknown; unknown_categories.
- 5. Gekijouban Haikyuu!! (source:https://anidb.net/anime/11040) — unknown; unknown_categories.

**legacy_filtered**

- 1. Haikyu!! To the Top (mal:38883) — not graded; passes recorded constraints.
- 2. Haikyu!! 2nd Season (mal:28891) — not graded; passes recorded constraints.
- 3. Haikyu!! the Movie: The End and the Beginning (mal:29755) — not graded; passes recorded constraints.
- 4. Haikyu!! The Movie: Talent and Sense (mal:35110) — not graded; passes recorded constraints.
- 5. Haikyu!!: VS "Failing Marks" (mal:35806) — not graded; passes recorded constraints.

### sports-5

A sports team improving through training, teamwork and competitive matches. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Kuroko's Basketball the Movie: Last Game (mal:31658) — 3/3; passes recorded constraints.
- 2. Haikyu!! Movie: The Dumpster Battle (mal:52742) — 3/3; passes recorded constraints.
- 3. Blue Legend Shoot! (mal:2682) — 2/3; passes recorded constraints.
- 4. Winter Cup Highlights Episode 1 – Winter Cup Highlights -Shadow and Light- (mal:32869) — 2/3; passes recorded constraints.
- 5. Dokgotak: Taeyang-eul Hyanghae Deonjyeola (mal:16572) — 3/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### calm-1

I enjoyed Non Non Biyori. A gentle rural slice of life about friendship and everyday experiences, with a relaxing atmosphere.

**hybrid**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — 3/3; passes recorded constraints.
- 4. Wash It All Away (mal:61782) — 3/3; passes recorded constraints.
- 5. SK8 the Infinity Extra Part (mal:49363) — 1/3; passes recorded constraints.

**legacy_cosine**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — 3/3; passes recorded constraints.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — 2/3; passes recorded constraints.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — 3/3; passes recorded constraints.

**legacy_filtered**

- 1. Non Non Biyori Repeat (mal:23623) — not graded; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — not graded; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — not graded; passes recorded constraints.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — not graded; passes recorded constraints.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — not graded; passes recorded constraints.

### calm-2

I enjoyed Non Non Biyori. A gentle rural slice of life about friendship and everyday experiences, with a relaxing atmosphere. Only finished TV series with at most 24 episodes. I already watched Barakamon.

**hybrid**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 3. Wash It All Away (mal:61782) — 3/3; passes recorded constraints.
- 4. Amanchu! (mal:31771) — 3/3; passes recorded constraints.
- 5. Strawberry Marshmallow (mal:488) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — 3/3; format.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — 2/3; format.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — 3/3; format.

**legacy_filtered**

- 1. Non Non Biyori Repeat (mal:23623) — not graded; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — not graded; passes recorded constraints.
- 3. Tamayura: More Aggressive (mal:15731) — not graded; passes recorded constraints.
- 4. Strawberry Marshmallow (mal:488) — not graded; passes recorded constraints.
- 5. One Room: Second Season (mal:36431) — not graded; passes recorded constraints.

### calm-3

I enjoyed Non Non Biyori. A gentle rural slice of life about friendship and everyday experiences, with a relaxing atmosphere. Choose TV series or movies released between 1990 and 2009.

**hybrid**

- 1. Strawberry Marshmallow (mal:488) — 3/3; passes recorded constraints.
- 2. Sanchoume no Yuuhi (mal:21483) — unknown; passes recorded constraints.
- 3. Peeping Life: The Perfect Edition (mal:6525) — 1/3; passes recorded constraints.
- 4. Mushi-Shi (mal:457) — 2/3; passes recorded constraints.
- 5. Kazoku Dekki (mal:38643) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; year_max_or_unknown.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; year_max_or_unknown.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — 3/3; format, year_max_or_unknown.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — 2/3; format, year_max_or_unknown.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — 3/3; format, year_max_or_unknown.

**legacy_filtered**

- 1. Strawberry Marshmallow (mal:488) — not graded; passes recorded constraints.
- 2. Sketchbook ~full color's~ (mal:2942) — not graded; passes recorded constraints.
- 3. Lucky☆Star (mal:1887) — not graded; passes recorded constraints.
- 4. Hidamari Sketch x 365 (mal:3604) — not graded; passes recorded constraints.
- 5. Minami-ke Okaeri (mal:5162) — not graded; passes recorded constraints.

### calm-4

I enjoyed Non Non Biyori. A gentle rural slice of life about friendship and everyday experiences, with a relaxing atmosphere. I also liked Barakamon, but disliked Attack on Titan. Exclude action, horror.

**hybrid**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Sanchoume no Yuuhi (mal:21483) — unknown; passes recorded constraints.
- 3. SK8 the Infinity Extra Part (mal:49363) — 1/3; passes recorded constraints.
- 4. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 5. Peeping Life: The Perfect Edition (mal:6525) — 1/3; passes recorded constraints.

**legacy_cosine**

- 1. Non Non Biyori Repeat (mal:23623) — 3/3; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — 3/3; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — 3/3; passes recorded constraints.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — 2/3; passes recorded constraints.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — 3/3; passes recorded constraints.

**legacy_filtered**

- 1. Non Non Biyori Repeat (mal:23623) — not graded; passes recorded constraints.
- 2. Non Non Biyori Nonstop (mal:39808) — not graded; passes recorded constraints.
- 3. Non Non Biyori Repeat: Hotaru Had Fun (mal:32547) — not graded; passes recorded constraints.
- 4. Non Non Biyori: We're Going to Okinawa (mal:21667) — not graded; passes recorded constraints.
- 5. Non Non Biyori Nonstop: Our Club Worked Hard (mal:49521) — not graded; passes recorded constraints.

### calm-5

A gentle rural slice of life about friendship and everyday experiences, with a relaxing atmosphere. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Yomoyama Tanpenshuu (mal:54541) — 1/3; passes recorded constraints.
- 2. Peeping Life Movie: We Are The Hero (mal:27399) — unknown; passes recorded constraints.
- 3. Chameko no Ichinichi (mal:6431) — 1/3; passes recorded constraints.
- 4. Peeping Life: Gekijou Original-ban (mal:22675) — 1/3; passes recorded constraints.
- 5. 520 (mal:60486) — 1/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### thriller-1

I enjoyed Perfect Blue. An eerie supernatural thriller with unsettling mysteries and suspense.

**hybrid**

- 1. Ghost Hound (mal:2596) — 3/3; passes recorded constraints.
- 2. Boogiepop Phantom (mal:369) — 3/3; passes recorded constraints.
- 3. Mononoke The Movie: Chapter II - The Ashes of Rage (mal:59408) — 3/3; passes recorded constraints.
- 4. The Lost Village (mal:32438) — 3/3; passes recorded constraints.
- 5. Junji Ito Collection (mal:36124) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Key the Metal Idol (mal:1457) — 1/3; passes recorded constraints.
- 2. [Oshi No Ko] (mal:52034) — 1/3; passes recorded constraints.
- 3. Paprika (mal:1943) — 2/3; passes recorded constraints.
- 4. Needy Girl Overdose (mal:62913) — 1/3; passes recorded constraints.
- 5. Parasyte: The Maxim (mal:22535) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Key the Metal Idol (mal:1457) — not graded; passes recorded constraints.
- 2. [Oshi No Ko] (mal:52034) — not graded; passes recorded constraints.
- 3. Paprika (mal:1943) — not graded; passes recorded constraints.
- 4. Needy Girl Overdose (mal:62913) — not graded; passes recorded constraints.
- 5. Parasyte: The Maxim (mal:22535) — not graded; passes recorded constraints.

### thriller-2

I enjoyed Perfect Blue. An eerie supernatural thriller with unsettling mysteries and suspense. Only finished TV series with at most 24 episodes. I already watched Higurashi: When They Cry.

**hybrid**

- 1. Ghost Hound (mal:2596) — 3/3; passes recorded constraints.
- 2. Boogiepop Phantom (mal:369) — 3/3; passes recorded constraints.
- 3. The Lost Village (mal:32438) — 3/3; passes recorded constraints.
- 4. Junji Ito Collection (mal:36124) — 3/3; passes recorded constraints.
- 5. Mononoke (mal:2246) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Key the Metal Idol (mal:1457) — 1/3; format.
- 2. [Oshi No Ko] (mal:52034) — 1/3; passes recorded constraints.
- 3. Paprika (mal:1943) — 2/3; format.
- 4. Needy Girl Overdose (mal:62913) — 1/3; passes recorded constraints.
- 5. Parasyte: The Maxim (mal:22535) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. [Oshi No Ko] (mal:52034) — not graded; passes recorded constraints.
- 2. Needy Girl Overdose (mal:62913) — not graded; passes recorded constraints.
- 3. Parasyte: The Maxim (mal:22535) — not graded; passes recorded constraints.
- 4. Odd Taxi (mal:46102) — not graded; passes recorded constraints.
- 5. Back Street Girls: Gokudols (mal:36873) — not graded; passes recorded constraints.

### thriller-3

I enjoyed Perfect Blue. An eerie supernatural thriller with unsettling mysteries and suspense. Choose TV series or movies released between 1990 and 2009.

**hybrid**

- 1. Ghost Hound (mal:2596) — 3/3; passes recorded constraints.
- 2. Boogiepop Phantom (mal:369) — 3/3; passes recorded constraints.
- 3. Serial Experiments Lain (mal:339) — 3/3; passes recorded constraints.
- 4. Gankutsuou: The Count of Monte Cristo (mal:239) — 2/3; passes recorded constraints.
- 5. Mononoke (mal:2246) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Key the Metal Idol (mal:1457) — 1/3; format.
- 2. [Oshi No Ko] (mal:52034) — 1/3; year_max_or_unknown.
- 3. Paprika (mal:1943) — 2/3; passes recorded constraints.
- 4. Needy Girl Overdose (mal:62913) — 1/3; year_max_or_unknown.
- 5. Parasyte: The Maxim (mal:22535) — 2/3; year_max_or_unknown.

**legacy_filtered**

- 1. Paprika (mal:1943) — not graded; passes recorded constraints.
- 2. Death Note (mal:1535) — not graded; passes recorded constraints.
- 3. Serial Experiments Lain (mal:339) — not graded; passes recorded constraints.
- 4. Paranoia Agent (mal:323) — not graded; passes recorded constraints.
- 5. Millennium Actress (mal:1033) — not graded; passes recorded constraints.

### thriller-4

I enjoyed Perfect Blue. An eerie supernatural thriller with unsettling mysteries and suspense. I also liked Higurashi: When They Cry, but disliked K-ON!. Exclude sports.

**hybrid**

- 1. Ghost Hound (mal:2596) — 3/3; passes recorded constraints.
- 2. Higurashi: When They Cry – Gou (mal:41006) — 3/3; passes recorded constraints.
- 3. Hell Girl: Two Mirrors (mal:1594) — 3/3; passes recorded constraints.
- 4. Junji Ito Collection (mal:36124) — 3/3; passes recorded constraints.
- 5. Shiki (mal:7724) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. Key the Metal Idol (mal:1457) — 1/3; passes recorded constraints.
- 2. [Oshi No Ko] (mal:52034) — 1/3; passes recorded constraints.
- 3. Paprika (mal:1943) — 2/3; passes recorded constraints.
- 4. Needy Girl Overdose (mal:62913) — 1/3; passes recorded constraints.
- 5. Parasyte: The Maxim (mal:22535) — 2/3; passes recorded constraints.

**legacy_filtered**

- 1. Key the Metal Idol (mal:1457) — not graded; passes recorded constraints.
- 2. [Oshi No Ko] (mal:52034) — not graded; passes recorded constraints.
- 3. Paprika (mal:1943) — not graded; passes recorded constraints.
- 4. Needy Girl Overdose (mal:62913) — not graded; passes recorded constraints.
- 5. Parasyte: The Maxim (mal:22535) — not graded; passes recorded constraints.

### thriller-5

An eerie supernatural thriller with unsettling mysteries and suspense. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Mononoke The Movie: Chapter II - The Ashes of Rage (mal:59408) — 3/3; passes recorded constraints.
- 2. Extreme City (mal:61303) — 2/3; passes recorded constraints.
- 3. Aragne: Sign of Vermillion (mal:34974) — 3/3; passes recorded constraints.
- 4. Mononoke the Movie: Phantom in the Rain (mal:52107) — 3/3; passes recorded constraints.
- 5. Seoul Station (mal:34048) — 2/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


### music-1

I enjoyed K-ON!. Music performance, band friendships, practice and personal growth.

**hybrid**

- 1. Harmony of Mille-Feuille (mal:55689) — 3/3; passes recorded constraints.
- 2. BanG Dream! It's MyGO!!!!! (mal:54959) — 3/3; passes recorded constraints.
- 3. "Star"t (mal:41090) — 2/3; passes recorded constraints.
- 4. K-ON! Season 2 (mal:7791) — 3/3; passes recorded constraints.
- 5. Sound! Euphonium Episode 14 – Ready, Set, Monaka (mal:31665) — 2/3; passes recorded constraints.

**legacy_cosine**

- 1. K-ON! Season 2 (mal:7791) — 3/3; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — 1/3; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — 3/3; passes recorded constraints.
- 4. Nijiyon Animation (mal:53077) — 1/3; passes recorded constraints.
- 5. Yuyushiki (mal:15911) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. K-ON! Season 2 (mal:7791) — not graded; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — not graded; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — not graded; passes recorded constraints.
- 4. Nijiyon Animation (mal:53077) — not graded; passes recorded constraints.
- 5. Yuyushiki (mal:15911) — not graded; passes recorded constraints.

### music-2

I enjoyed K-ON!. Music performance, band friendships, practice and personal growth. Only finished TV series with at most 24 episodes. I already watched Beck: Mongolian Chop Squad.

**hybrid**

- 1. Harmony of Mille-Feuille (mal:55689) — 3/3; passes recorded constraints.
- 2. BanG Dream! It's MyGO!!!!! (mal:54959) — 3/3; passes recorded constraints.
- 3. Sound! Euphonium 2 (mal:31988) — 3/3; passes recorded constraints.
- 4. Sound! Euphonium (mal:27989) — 3/3; passes recorded constraints.
- 5. Sound! Euphonium 3 (mal:39894) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. K-ON! Season 2 (mal:7791) — 3/3; max_episodes_or_unknown.
- 2. Chronicles of the Going Home Club (mal:18495) — 1/3; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — 3/3; format.
- 4. Nijiyon Animation (mal:53077) — 1/3; passes recorded constraints.
- 5. Yuyushiki (mal:15911) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. Chronicles of the Going Home Club (mal:18495) — not graded; passes recorded constraints.
- 2. Nijiyon Animation (mal:53077) — not graded; passes recorded constraints.
- 3. Yuyushiki (mal:15911) — not graded; passes recorded constraints.
- 4. YuruYuri: Happy Go Lily (mal:10495) — not graded; passes recorded constraints.
- 5. Nijiyon Animation 2 (mal:57623) — not graded; passes recorded constraints.

### music-3

I enjoyed K-ON!. Music performance, band friendships, practice and personal growth. Choose TV series or movies released between 2000 and 2014.

**hybrid**

- 1. K-ON! Season 2 (mal:7791) — 3/3; passes recorded constraints.
- 2. Audition (mal:31730) — 2/3; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — 3/3; passes recorded constraints.
- 4. White Album 2 (mal:18245) — 3/3; passes recorded constraints.
- 5. Beck: Mongolian Chop Squad (mal:57) — 3/3; passes recorded constraints.

**legacy_cosine**

- 1. K-ON! Season 2 (mal:7791) — 3/3; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — 1/3; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — 3/3; passes recorded constraints.
- 4. Nijiyon Animation (mal:53077) — 1/3; year_max_or_unknown.
- 5. Yuyushiki (mal:15911) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. K-ON! Season 2 (mal:7791) — not graded; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — not graded; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — not graded; passes recorded constraints.
- 4. Yuyushiki (mal:15911) — not graded; passes recorded constraints.
- 5. YuruYuri: Happy Go Lily (mal:10495) — not graded; passes recorded constraints.

### music-4

I enjoyed K-ON!. Music performance, band friendships, practice and personal growth. I also liked Beck: Mongolian Chop Squad, but disliked Attack on Titan. Exclude mecha.

**hybrid**

- 1. BanG Dream! It's MyGO!!!!! (mal:54959) — 3/3; passes recorded constraints.
- 2. Ainone (mal:32804) — 0/3; passes recorded constraints.
- 3. BanG Dream! YUME∞MITA (mal:62430) — 3/3; passes recorded constraints.
- 4. Argonavis Movie: Axia (mal:45731) — 3/3; passes recorded constraints.
- 5. Tarareba (mal:39568) — 0/3; passes recorded constraints.

**legacy_cosine**

- 1. K-ON! Season 2 (mal:7791) — 3/3; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — 1/3; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — 3/3; passes recorded constraints.
- 4. Nijiyon Animation (mal:53077) — 1/3; passes recorded constraints.
- 5. Yuyushiki (mal:15911) — 1/3; passes recorded constraints.

**legacy_filtered**

- 1. K-ON! Season 2 (mal:7791) — not graded; passes recorded constraints.
- 2. Chronicles of the Going Home Club (mal:18495) — not graded; passes recorded constraints.
- 3. K-ON! The Movie (mal:9617) — not graded; passes recorded constraints.
- 4. Nijiyon Animation (mal:53077) — not graded; passes recorded constraints.
- 5. Yuyushiki (mal:15911) — not graded; passes recorded constraints.

### music-5

Music performance, band friendships, practice and personal growth. I have no favorite titles to give you. Recommend finished movies.

**hybrid**

- 1. Argonavis Movie: Axia (mal:45731) — 3/3; passes recorded constraints.
- 2. Girls Band Cry Movie (mal:59817) — 2/3; passes recorded constraints.
- 3. Sound! Euphonium the Movie: May the Melody Reach You! (mal:35082) — 2/3; passes recorded constraints.
- 4. Audition (mal:31730) — 2/3; passes recorded constraints.
- 5. The Colors Within (mal:53747) — 3/3; passes recorded constraints.

**legacy_cosine** (unsupported without a seed)


**legacy_filtered** (unsupported without a seed)


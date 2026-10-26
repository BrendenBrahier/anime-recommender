# Request-aware recommendations and MAL connection design

The actual `scripts/recommender_function.py` entry point now loads the current catalog lazily and uses `Recommender.recommend(request, profile=None)`. It does not construct a catalog-sized square similarity matrix or graph. The prior experiments remain in their files and the frozen evaluation baseline remains in `evaluate_recommendations.py`.

## Run locally

```powershell
python -m pip install -r requirements-recommender.txt
# Build data/current first as described in DATA.md.
python scripts/build_relationships.py --download
python src/main.py --request evaluation/example_request.json
# Optional, local private profile; this path is ignored by Git.
python src/main.py --request evaluation/example_request.json --profile data/private/profile.json
```

`build_relationships.py` targets the evaluation candidates, the top 100 popular catalog titles, and their prequels. It caches responses with retrieval timestamps and URLs. Run it without `--download` to rebuild from the cache. A catalog hash mismatch stops the recommender until the relationship sidecar is rebuilt. Downloading this sidecar does not alter the canonical catalog or invalidate saved notebook outputs.

## Actual service behavior

- Requests accept stable `anime_id` values, a description, likes, dislikes, watched IDs, **completed** IDs, filters, and a result limit. Formats, release years, maximum episodes, completion status, excluded categories, and allowed content ratings are enforced. Unknown constrained fields fail closed. Query text guides matching but is **not** automatically parsed into filters; the future form/API must supply explicit filter fields.
- Watched, watching, on-hold, dropped, completed, and disliked titles are excluded from discovery. Planned-but-unwatched titles remain candidates. A dropped title is not automatically a dislike. MAL scores of zero remain unscored. The initial policy treats ratings 8–10 as positive and 1–4 as negative, with graded weights; neutral ratings are not positive/negative evidence. This threshold policy needs user evaluation.
- Completed or explicitly rewatching MAL entries satisfy direct prerequisites. Liking a title or watching some episodes does not. A direct prequel or parent story must be completed before a sequel/side story is eligible. This is a conservative dependency policy, not a hand-curated optimal watch order. Alternate timelines and optional side stories may be over-restricted.
- One result per explicitly linked franchise is the default (`max_per_franchise`, range 1–5). Prequel/sequel, parent/side story, summary/full story, alternative version/setting, and spin-off relations connect families. Manga adaptations, shared characters, and unspecified “other” links do not establish the same anime franchise. Unknown links cannot prove distinct franchises.
- Summary/full-story relations label confirmed recaps. Explicit recap/compilation wording labels suspected recaps. Both are excluded by default. `none_detected` means no evidence was found, **not** an independently verified guarantee. Unknown recap status is excluded in strict mode.
- `allow_sequels` defaults to true, but prerequisites still apply. `allow_recaps` defaults to false. `allow_unknown_relationships` defaults to false. An explicit opt-in can widen coverage but cannot bypass known prerequisites or known recap exclusions. Missing content ratings are excluded unless `allow_unknown_content` is true; this is not a general age-safety guarantee. Use `allowed_ratings` for audience restrictions.
- The service returns fewer results rather than silently relax constraints. Each result includes image URL, separate aggregate/MAL ratings, franchise ID, prerequisite IDs, recap status, and relationship-evidence status. Warnings explain insufficient coverage. Per-user profiles are processed per request and never cached in the shared catalog engine.
- Ranking is sparse synopsis/category TF-IDF with a weighted liked-title profile and a dislike penalty. This intentionally starts with a simple runtime baseline; the previous experimental LSA prototype and its relevance scores are **not** claimed as this service's performance.

### Validation snapshot (October 25, 2026, Eastern)

The first evidence pass has explicit detail responses for **489 of 38,259 catalog entries**. The sidecar also contains inferred inverse links and unverified neighbor nodes. This is partial coverage, mainly popular titles and benchmark candidates; it is not full-catalog franchise coverage.

The actual service returned **196 of 200 requested slots across 40 requests**. Thirty-eight requests received five results. The independent checks found **zero recorded constraint, recap, uncompleted-prerequisite, or franchise-cap violations**. This measures policy compliance against source metadata, not factual verification of every source relation or personal recommendation quality. Relevance has not been regraded for this service. Results are in `evaluation/results/service_checks.json`.

```powershell
python scripts/check_recommendation_service.py
python -m unittest discover -s tests -v
```

The old graph/hashmap dispatch arguments are rejected explicitly rather than silently changing their algorithm. `get_combined_recommendations(title, method='filtered', ...)` remains a convenience adapter; duplicate display titles require a stable ID.

## MAL sign-in: chosen product behavior

**One-time import is the default; “Keep my MAL connected” is optional.** These are separate decisions from saving a taste profile on the website.

1. Send the user to MAL to sign in and authorize the application. Never collect a MAL password.
2. Read the user's anime-list status, ratings, episode progress, and rewatch flag. Do not request biography, birthday, comments, or other unnecessary profile details. The client only reads the list; it never modifies ratings or list entries. MAL's authorization permission naming does not necessarily expose a separate read-only consent scope, so the UI must not promise a narrower grant than MAL actually displays.
3. In **one-time mode**, `MALClient.import_once()` returns only a normalized preference profile and drops its access/refresh token references on success or failure. It does not persist credentials or profile data. The website should keep this profile only in the active session unless the user separately elects to save it. Dropping Python references is not a cryptographic memory-erasure guarantee.
4. If the user elects to **save their taste profile**, later recommendations can be recalculated against newer anime data without retaining MAL access. Changes to their MAL watchlist will require another import.
5. If the user elects to **keep connected**, the future server may save encrypted access/refresh tokens, expiry, MAL account association, and the consent time. Keep keys outside the database, restrict access, use returned `expires_in`, rotate token storage after refresh, and reconnect when authorization expires/fails. Store no tokens in browser storage, URLs, analytics, or logs. This persistent storage and account UI are **not implemented yet**.
6. Provide separate “Disconnect MAL” and “Delete saved profile/account” controls. Disconnect stops future refresh and deletes locally stored tokens; it is not a promise of provider-side revocation. Deleting a profile removes retained preferences and cached personalized results. The user can also remove authorization through MAL's available account controls.

## Implemented OAuth foundation and remaining website work

`scripts/mal_client.py` implements authorization URL creation, fresh PKCE verifiers, random state, ten-minute attempt expiry, state validation and single use, code exchange, token refresh, full-list pagination, and one-time import. Token objects hide secrets in their representation. API errors do not expose response bodies or bearer headers. HTTP redirects are disabled for credentialed requests, and pagination is restricted to the authorized user's MAL list endpoint. Malformed/oversized imports fail atomically instead of silently saving a partial list. Unit tests use synthetic tokens and mocked transports; **no real account login was performed**.

Before a browser login can go live, we still need:

- A registered [MAL application](https://myanimelist.net/apiconfig), its client ID, server-side client secret if issued, and an exact registered callback URL. Put secrets in the server's environment/secret store, never in chat or Git.
- The website's HTTP/session layer: bind each `OAuthAttempt` to the initiating browser session, use secure HttpOnly session cookies, handle denial/expiry safely, avoid logging callback query strings, and remove pending attempts on expiry. The module cannot enforce browser/session binding by itself.
- Site account/session lifecycle, consent UI, encrypted persistent token storage for the optional connected mode, refresh scheduling, disconnect/delete controls, and end-to-end account tests.

Official references checked October 25, 2026: [MAL authorization](https://myanimelist.net/apiconfig/references/authorization), [MAL API v2](https://myanimelist.net/apiconfig/references/api/v2). MAL currently specifies plain PKCE; redirect/token requests still require HTTPS outside local development. Token lifetime examples differ in the documentation, so the client uses the response's `expires_in` rather than hardcoding a lifetime. The schema states that `is_rewatching=true` means prior completion, which is why it satisfies prerequisite checks.

Next work: extend relationship coverage, review optional side-story restrictions, grade runtime relevance with actual user preferences, then build the website and complete MAL account integration.

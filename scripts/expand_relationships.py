"""Resume a bounded, rate-limited crawl of popular anime and explicit family links."""
import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
import time

from build_relationships import build, FAMILY, ROOT
from enrich_catalog import request, save


class RateLimiter:
    """Space every network attempt (including retries) below public 120 RPM/4 RPS."""
    def __init__(self, interval=0.55):
        self.interval = interval
        self.lock = threading.Lock()
        self.last = 0.0

    def __call__(self):
        with self.lock:
            time.sleep(max(0, self.interval - (time.monotonic() - self.last)))
            self.last = time.monotonic()


def popular_ids(catalog, count):
    rows = [r for r in catalog if type(r.get('mal_id')) is int
            and r['anime_id'] == f"mal:{r['mal_id']}"
            and isinstance(r.get('popularity'), (int, float)) and r['popularity'] > 0]
    return [r['mal_id'] for r in sorted(rows, key=lambda r: (r['popularity'], r['mal_id']))[:count]]


def family_ids(record, expected):
    item = record.get('response', {}).get('data')
    if not isinstance(item, dict) or item.get('mal_id') != expected or not isinstance(item.get('relations'), list):
        return None
    return sorted({e['mal_id'] for rel in item['relations']
                   if rel.get('relation', '').lower().replace('_', ' ') in FAMILY
                   for e in rel.get('entry', [])
                   if e.get('type') == 'anime' and type(e.get('mal_id')) is int and e['mal_id'] > 0})


def crawl(seeds, fetch, cache, max_fetch, workers=3, progress=None):
    pending = deque(dict.fromkeys(seeds)); discovered = set(pending)
    futures = {}; successful = set(); unavailable = {}; errors = {}; calls = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or futures:
            while pending and len(futures) < workers:
                mid = pending[0]
                cached = (cache / f'anime_{mid}_full.json').exists()
                # Cached evidence never consumes the new-request budget.
                if not cached and calls >= max_fetch:
                    break
                pending.popleft()
                calls += not cached
                futures[pool.submit(fetch, mid)] = mid
            if not futures:
                break
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                mid = futures.pop(future)
                try:
                    record = future.result()
                    neighbors = family_ids(record, mid)
                    if neighbors is None:
                        unavailable[str(mid)] = record.get('http_status', 'invalid_detail')
                    else:
                        successful.add(mid)
                        for target in neighbors:
                            if target not in discovered:
                                discovered.add(target); pending.append(target)
                except Exception as exc:
                    errors[str(mid)] = f'{type(exc).__name__}: {exc}'
                if progress:
                    progress({'verified': len(successful), 'new_requests': calls,
                              'pending': len(pending) + len(futures),
                              'unavailable': len(unavailable), 'errors': len(errors)})
    return {'seed_ids': sorted(set(seeds)), 'discovered_ids': sorted(discovered),
            'verified_ids': sorted(successful), 'pending_ids': list(pending),
            'unavailable': unavailable, 'errors': errors, 'new_requests': calls,
            'traversal_complete': not pending and not errors and not unavailable}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=5000)
    parser.add_argument('--max-fetch', type=int, default=15000)
    args = parser.parse_args()
    if args.top < 1 or args.max_fetch < 0:
        parser.error('top must be positive; max-fetch must be nonnegative')
    catalog_path = ROOT / 'data/current/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    seeds = popular_ids(catalog, args.top)
    cache = ROOT / 'data/raw/tenrai'
    limiter = RateLimiter()
    last_print = [0.0]
    def progress(status):
        if time.monotonic() - last_print[0] >= 15:
            save(ROOT / 'data/current/relationship_progress.json', status)
            print(json.dumps(status), flush=True)
            last_print[0] = time.monotonic()
    result = crawl(seeds, lambda mid: request(f'anime/{mid}/full', before_request=limiter),
                   cache, args.max_fetch, progress=progress)
    records = []
    for path in sorted(cache.glob('anime_*_full.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        if family_ids(record, int(path.name.split('_')[1])) is not None:
            records.append(record)
    sidecar = build(records, {r['anime_id']: r for r in catalog})
    sidecar['catalog_sha256'] = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    save(ROOT / 'data/current/relationships.json', sidecar)
    verified = {int(k.split(':')[1]) for k, v in sidecar['records'].items() if v['verified_relations']}
    result.update(built_utc=datetime.now(timezone.utc).isoformat(), top_requested=args.top,
                  top_targeted=len(seeds), top_verified=len(set(seeds) & verified),
                  verified_catalog_entries=sidecar['verified_catalog_entries'],
                  catalog_entries=len(catalog), catalog_sha256=sidecar['catalog_sha256'])
    save(ROOT / 'evaluation/results/relationship_coverage.json', result)
    print(json.dumps({k: v for k, v in result.items() if not k.endswith('_ids')}, indent=2), flush=True)


if __name__ == '__main__':
    main()

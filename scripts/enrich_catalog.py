"""Fetch 2026 gap-filling sources and apply ID-only catalog enrichment."""
import csv
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
API = 'https://api.tenrai.org/v1'
KAGGLE_REF = 'darkbarrierhub/anime-dataset-2026'
MISSING = {'', 'unknown', 'n/a', 'none', 'null', 'nan', 'not available', 'no synopsis available.'}


def present(value):
    text = str(value).strip().lower()
    return value is not None and text not in MISSING and not text.startswith(('no synopsis', 'no description', 'no information'))


def number(value):
    if not present(value):
        return None
    try:
        result = float(str(value).replace(',', ''))
        return result if 0 < result <= 10 else None
    except (TypeError, ValueError):
        return None


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    tmp.replace(path)


def request(endpoint, before_request=None):
    path = RAW / 'tenrai' / (re.sub(r'[^a-zA-Z0-9]', '_', endpoint) + '.json')
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    url = API + '/' + endpoint
    for attempt in range(4):
        try:
            if before_request is not None:
                before_request()
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'anime-recommender-data/2.0'}), timeout=25) as response:
                data = json.load(response)
            record = {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'response': data}
            save(path, record)
            time.sleep(0.65)
            return record
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                record = {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'http_status': exc.code, 'response': {}}
                save(path, record)
                time.sleep(0.65)
                return record
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(max(float(exc.headers.get('Retry-After', '2')), 2 ** (attempt + 1)))
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))


def download():
    # Immutable Kaggle version requested, with bytes and metadata retained locally.
    path = RAW / 'kaggle-2026.zip'
    if not path.exists():
        urllib.request.urlretrieve(f'https://www.kaggle.com/api/v1/datasets/download/{KAGGLE_REF}?datasetVersionNumber=1', path)
    catalog = json.loads((ROOT / 'data/current/catalog.json').read_text(encoding='utf-8'))
    endpoints = [f'seasons/2026/{season}?page=' for season in ('winter','spring','summer','fall')]
    endpoints += ['top/anime?filter=bypopularity&page=']
    for endpoint in endpoints:
        page = 1
        while True:
            record = request(endpoint + str(page) + '&limit=25')
            response = record['response']
            if not isinstance(response.get('data'), list) or 'pagination' not in response:
                raise ValueError(f'Invalid paginated response: {record["url"]}')
            print(f'{endpoint}{page}: {len(response["data"])}', flush=True)
            if not response['pagination'].get('has_next_page') or (endpoint.startswith('top/') and page >= 40):
                break
            page += 1
    ids = sorted({int(url.rsplit('/',1)[-1]) for r in catalog if r['ambiguous_mal_mapping'] for url in r['sources'] if 'myanimelist.net/anime/' in url})
    for mid in ids:
        record = request(f'anime/{mid}/full')
        print(f'Mapping evidence MAL {mid}: {record.get("http_status", 200)}', flush=True)


def download_gaps():
    from refresh_database import normalize
    rows = {r['anime_id']:r for r in json.loads((ROOT/'data/current/catalog.json').read_text(encoding='utf-8'))}
    apply(rows, normalize)
    ids = sorted(r['mal_id'] for r in rows.values() if r['year']==2026 and r['mal_id'] and
                 (not r['synopsis'] or not r['genres']))
    for n, mid in enumerate(ids, 1):
        request(f'anime/{mid}/full')
        print(f'Recent gap {n}/{len(ids)}: {mid}', flush=True)


def kaggle_rows():
    path = RAW / 'kaggle-2026.zip'
    if not path.exists():
        return []
    with zipfile.ZipFile(path) as archive:
        with io.TextIOWrapper(archive.open('anime-dataset-2026.csv'), encoding='utf-8-sig', newline='') as stream:
            return list(csv.DictReader(stream))


def apply(rows, normalize):
    evidence = {'kaggle': {'ref': KAGGLE_REF, 'version': 1, 'published': '2026-10-04', 'filled': {}}, 'tenrai': {'inputs': [], 'matched': 0}}
    review_path = ROOT / 'data/mapping_decisions.json'
    review = json.loads(review_path.read_text(encoding='utf-8'))
    decisions = {tuple(sorted(d['mal_ids'])): d for d in review['decisions']}
    evidence['mapping_review'] = []
    for old_key, row in list(rows.items()):
        if not row['ambiguous_mal_mapping']:
            continue
        ids = tuple(sorted(int(u.rsplit('/',1)[-1]) for u in row['sources'] if 'myanimelist.net/anime/' in u))
        decision = decisions.get(ids, {'action': 'quarantine', 'reason': 'Not reviewed yet'})
        replacement_keys = []
        if decision['action'] == 'split':
            candidates = []
            for mid in ids:
                p = RAW / 'tenrai' / f'anime_{mid}_full.json'
                if not p.exists():
                    break
                item = json.loads(p.read_text(encoding='utf-8'))['response'].get('data')
                if not item or item.get('mal_id') != mid:
                    break
                candidates.append(item)
            if len(candidates) == len(ids):
                for item in candidates:
                    mid = item['mal_id']
                    year = item.get('year') or (item.get('aired', {}).get('prop', {}).get('from', {}).get('year'))
                    new = normalize({'sources': [f'https://myanimelist.net/anime/{mid}'], 'title': item['title'],
                        'type': item.get('type') or 'UNKNOWN', 'episodes': item.get('episodes'),
                        'status': {'Finished Airing':'FINISHED','Currently Airing':'ONGOING','Not yet aired':'UPCOMING'}.get(item.get('status'),'UNKNOWN'),
                        'animeSeason': {'year':year,'season':item.get('season')},
                        'picture': item.get('images',{}).get('jpg',{}).get('large_image_url'),
                        'synonyms': item.get('title_synonyms',[]), 'studios':[s['name'] for s in item.get('studios',[])]})
                    new['supersedes_ambiguous_id'] = old_key
                    # Never inherit aggregate scores, tags or cross-provider links from a bad merge.
                    if new['anime_id'] in rows:
                        raise ValueError('Mapping split would overwrite an existing ID')
                    rows[new['anime_id']] = new
                    replacement_keys.append(new['anime_id'])
                del rows[old_key]
        evidence['mapping_review'].append({'original_id': old_key, 'title':row['name'], 'mal_ids':ids,
            'decision':decision['action'], 'applied':bool(replacement_keys), 'replacements':replacement_keys,'reason':decision['reason']})
    path = RAW / 'kaggle-2026.zip'
    if path.exists():
        evidence['kaggle']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    for r in rows.values():
        r['aggregate_score'] = r['score']
        r['aggregate_score_source'] = r['score_source']
        r.setdefault('mal_score', None)
        r.setdefault('mal_score_source', 'myanimelist_mirror' if r['mal_score'] is not None else None)
        if not present(r.get('synopsis')):
            r['synopsis'] = None
        r.setdefault('field_sources', {})
    for item in kaggle_rows():
        r = rows.get(f'mal:{item["anime_id"]}')
        if r is None:
            continue
        candidates = {'synopsis': item['Synopsis'], 'genres': [g.strip().lower() for g in item['Genres'].split(',')] if present(item['Genres']) else [],
                      'mal_score': number(item['Score']), 'rating': item['Rating'], 'source_material': item['Source'], 'duration': item['Duration']}
        for field, value in candidates.items():
            if not r.get(field) and value and present(value):
                r[field] = value
                r['field_sources'][field] = 'kaggle:' + KAGGLE_REF + ':v1'
                evidence['kaggle']['filled'][field] = evidence['kaggle']['filled'].get(field, 0) + 1
                if field == 'mal_score':
                    r['mal_score_source'] = r['field_sources'][field]
        if present(item['Image URL']) and item['Image URL'].startswith('https://'):
            r.setdefault('image_alternatives', []).append(item['Image URL'])
    api_items = {}
    popular_ids = set()
    for path in sorted((RAW / 'tenrai').glob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        evidence['tenrai']['inputs'].append({'url': record['url'], 'retrieved_at': record['retrieved_at'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        data = record['response'].get('data', [])
        if '/top/anime?filter=bypopularity' in record['url']:
            popular_ids.update(item['mal_id'] for item in data)
        for item in data if isinstance(data, list) else [data]:
            if not item.get('mal_id'):
                continue
            old = api_items.get(item['mal_id'])
            if old is None or record['retrieved_at'] > old[1]['retrieved_at']:
                api_items[item['mal_id']] = (item, record)
    blocked_ids = {int(u.rsplit('/',1)[-1]) for r in rows.values() if r['ambiguous_mal_mapping'] for u in r['sources'] if 'myanimelist.net/anime/' in u}
    evidence['tenrai']['added'] = 0
    for mid, (item, record) in api_items.items():
        r = rows.get(f'mal:{mid}')
        if r is None:
            if mid in blocked_ids:
                continue
            year = item.get('year') or item.get('aired',{}).get('prop',{}).get('from',{}).get('year')
            r = normalize({'sources':[f'https://myanimelist.net/anime/{mid}'], 'title':item['title'],
                'type':item.get('type') or 'UNKNOWN', 'episodes':item.get('episodes'),
                'animeSeason':{'year':year,'season':item.get('season')},
                'status':{'Finished Airing':'FINISHED','Currently Airing':'ONGOING','Not yet aired':'UPCOMING'}.get(item.get('status'),'UNKNOWN'),
                'studios':[s['name'] for s in item.get('studios',[])]})
            r.update(aggregate_score=None, aggregate_score_source=None, field_sources={})
            rows[r['anime_id']] = r
            evidence['tenrai']['added'] += 1
        evidence['tenrai']['matched'] += 1
        r['mal_metadata_retrieved_at'] = record['retrieved_at']
        r['mal_score'] = number(item.get('score'))
        r['mal_score_source'] = 'myanimelist_via_tenrai'
        r['mal_scored_by'] = item.get('scored_by')
        r['field_sources']['mal_score'] = record['url']
        updates = {'synopsis': item.get('synopsis'), 'name_english': item.get('title_english'), 'rating': item.get('rating'),
                   'genres': sorted({g['name'].lower() for key in ('genres','explicit_genres','themes','demographics') for g in item.get(key, [])}),
                   'members': item.get('members'), 'popularity': item.get('popularity'), 'ranked': item.get('rank'),
                   'source_material': item.get('source'), 'duration': item.get('duration'),
                   'start_date': item.get('aired',{}).get('from'), 'end_date': item.get('aired',{}).get('to')}
        for field, value in updates.items():
            if value and present(value):
                r[field] = value
                r['field_sources'][field] = record['url']
        r['images'] = item.get('images', {})
        image = r['images'].get('jpg', {}).get('large_image_url')
        if image:
            r['img_url'] = image
            r['field_sources']['img_url'] = record['url']
            r['thumbnail_url'] = r['images'].get('jpg',{}).get('small_image_url')
        r['trailer_url'] = (item.get('trailer') or {}).get('url')
        r['mal_status'] = item.get('status')
        r['status'] = {'Finished Airing':'FINISHED','Currently Airing':'ONGOING','Not yet aired':'UPCOMING'}.get(item.get('status'), r['status'])
    for r in rows.values():
        r['priority_popular'] = r['mal_id'] in popular_ids
        # Always label the compatibility score consistently, regardless of enrichment source.
        r['score'] = r['aggregate_score']
        r['score_source'] = r['aggregate_score_source']
        r['image_alternatives'] = sorted(set(r.get('image_alternatives', [])) - {r.get('img_url')})
        r['mal_url'] = f'https://myanimelist.net/anime/{r["mal_id"]}' if r['mal_id'] else None
        r['image_alt'] = f'Cover art for {r["name_english"]}'
        r['image_url_present'] = bool(r.get('img_url') and r['img_url'].startswith('https://'))
        r['image_availability'] = 'unverified'
        if r.get('img_url') and any(token in r['img_url'].lower() for token in ('placeholder','questionmark','unknown')):
            r['image_availability'] = 'placeholder'
        r['recommendation_eligible'] = bool(not r['ambiguous_mal_mapping'] and r['status'] != 'UPCOMING' and (r['synopsis'] or r['genres'] or r['tags']))
    checks_path = RAW / 'image_checks.json'
    if checks_path.exists():
        checks = json.loads(checks_path.read_text(encoding='utf-8'))
        for r in rows.values():
            check = checks.get(r['img_url'])
            if check:
                r['image_availability'] = check['status']
                r['image_checked_at'] = check['checked_at']
    return evidence


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gaps-only', action='store_true')
    args = parser.parse_args()
    if args.gaps_only:
        download_gaps()
    else:
        download()

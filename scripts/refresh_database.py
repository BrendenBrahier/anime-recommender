"""Reproducible anime catalog builder. Python 3.10+, standard library only."""
import argparse
import os
import sys
from collections import Counter
import hashlib
import json
import re
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
RAW = ROOT / 'data/raw'
OUT = ROOT / 'data/current'
SOURCE = 'https://github.com/cedya77/anime-offline-database/releases/download/latest/anime-offline-database-minified.json'
MIRROR = 'https://github.com/meesvandongen/anime-dataset.git'


def sync_mirror(refresh=False):
    path = RAW / 'mal-mirror'
    if not path.exists():
        subprocess.run(['git', 'clone', '--depth', '1', MIRROR, str(path)], check=True)
    elif refresh:
        subprocess.run(['git', '-C', str(path), 'fetch', '--depth', '1', 'origin', 'main'], check=True)
        subprocess.run(['git', '-C', str(path), 'checkout', '--detach', 'FETCH_HEAD'], check=True)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def fetch(url, path, refresh=False):
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding='utf-8'))
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'anime-recommender-data/1.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.load(response)
            write_json(path, data)
            write_json(path.with_suffix('.provenance.json'), {
                'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            return data
        except (urllib.error.URLError, TimeoutError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 5:
                raise
            time.sleep(min(60, 2 ** (attempt + 1)))


def sync_jikan(year, full=False, refresh=False):
    endpoints = ['anime?order_by=mal_id&sort=asc'] if full else [
        f'seasons/{year}/{season}?' for season in ('winter', 'spring', 'summer', 'fall')
    ] + ['top/anime?']
    for endpoint in endpoints:
        page = 1
        while True:
            key = re.sub(r'[^a-zA-Z0-9]', '_', endpoint)
            path = RAW / 'jikan' / f'{key}_{page:04}.json'
            base_url = os.environ.get('JIKAN_BASE_URL')
            if not base_url:
                raise ValueError('The public Jikan API closed October 1, 2026. Set JIKAN_BASE_URL to your own compatible instance, or run scripts/enrich_catalog.py for Tenrai.')
            url = f'{base_url.rstrip("/")}/{endpoint}&page={page}&limit=25'
            data = fetch(url, path, refresh)
            if not isinstance(data.get('data'), list) or 'pagination' not in data:
                raise ValueError(f'Invalid API response: {url}')
            print(f'{endpoint} page {page}: {len(data["data"])} records', flush=True)
            if not data['pagination'].get('has_next_page') or (endpoint.startswith('top/') and page >= 4):
                break
            page += 1
            time.sleep(1.1)
        time.sleep(1.1)


def mal_id(sources):
    ids = {int(m.group(1)) for url in sources if (m := re.fullmatch(r'https://myanimelist.net/anime/(\d+)/?', url))}
    if len(ids) > 1:
        return None  # Retain catalog row, but quarantine ambiguous joins from enrichment.
    return next(iter(ids), None)


def normalize(entry):
    mid = mal_id(entry['sources'])
    stable = f'mal:{mid}' if mid else 'source:' + sorted(entry['sources'])[0]
    return {
        'anime_id': stable, 'mal_id': mid, 'name': entry['title'],
        'name_english': entry['title'], 'synonyms': entry.get('synonyms', []),
        'type_of': entry['type'].lower(), 'total_episodes': entry.get('episodes') or None,
        'status': entry.get('status'), 'year': entry.get('animeSeason', {}).get('year') or None,
        'season': entry.get('animeSeason', {}).get('season'),
        'score': entry.get('score', {}).get('arithmeticMean'), 'score_source': 'aod_cross_provider_mean',
        'ranked': None, 'popularity': None, 'members': None, 'synopsis': None,
        'start_date': None, 'end_date': None, 'genres': [],
        'tags': sorted(set(entry.get('tags', []))), 'studios': ', '.join(entry.get('studios', [])),
        'img_url': entry.get('picture'), 'thumbnail_url': entry.get('thumbnail'), 'sources': sorted(entry['sources']),
        'related_sources': sorted(entry.get('relatedAnime', [])), 'mal_metadata_retrieved_at': None,
        'metadata_source': 'anime_offline_database', 'mal_source_updated_at': None,
        'ambiguous_mal_mapping': sum('myanimelist.net/anime/' in u for u in entry['sources']) > 1,
    }


def enrich(row, entry, retrieved_at):
    if row['mal_id'] != entry['mal_id']:
        raise ValueError('MAL identity mismatch')
    row.update(name_english=entry.get('title_english') or entry['title'],
               name=entry['title'], synopsis=entry.get('synopsis'),
               mal_score=entry.get('score'), mal_score_source='myanimelist_via_jikan',
               ranked=entry.get('rank'), popularity=entry.get('popularity'), members=entry.get('members'),
               genres=sorted({g['name'].lower() for key in ('genres', 'explicit_genres', 'themes', 'demographics') for g in entry.get(key, [])}),
               studios=', '.join(s['name'] for s in entry.get('studios', [])),
               start_date=(entry.get('aired') or {}).get('from'), end_date=(entry.get('aired') or {}).get('to'),
               total_episodes=entry.get('episodes'), mal_metadata_retrieved_at=retrieved_at)
    row['year'] = entry.get('year') or (int(row['start_date'][:4]) if row['start_date'] else row['year'])
    row['img_url'] = entry.get('images', {}).get('jpg', {}).get('large_image_url') or row['img_url']
    row['metadata_source'] = 'myanimelist_via_jikan'


def build():
    print('Reading base catalog...', flush=True)
    source_path = RAW / 'anime-offline-database.json'
    source = json.loads(source_path.read_text(encoding='utf-8'))
    rows = {}
    for entry in source['data']:
        row = normalize(entry)
        if row['anime_id'] in rows:
            raise ValueError(f'Duplicate stable ID: {row["anime_id"]}')
        rows[row['anime_id']] = row
    mirror_path = RAW / 'mal-mirror'
    mirror_info = None
    mirror_unmatched = 0
    if mirror_path.exists():
        revision = subprocess.check_output(['git', '-C', str(mirror_path), 'rev-parse', 'HEAD'], text=True).strip()
        committed = subprocess.check_output(['git', '-C', str(mirror_path), 'show', '-s', '--format=%cI', 'HEAD'], text=True).strip()
        mirror_info = {'repository': MIRROR, 'revision': revision, 'commit_date': committed,
                       'freshness_note': 'Incremental snapshot; commit date is not the refresh date of every record.'}
        for index, path in enumerate(sorted((mirror_path / 'data/anime').glob('*.json'))):
            if index % 5000 == 0:
                print(f'Reading MAL mirror: {index} files', flush=True)
            entry = json.loads(path.read_text(encoding='utf-8'))
            key = f'mal:{entry["id"]}'
            if key not in rows:
                mirror_unmatched += 1
                continue  # Do not resurrect removed/unsupported IDs from an auxiliary snapshot.
            row = rows[key]
            row.update(name_english=entry.get('alternative_titles', {}).get('en') or entry['title'],
                       synopsis=entry.get('synopsis'), ranked=entry.get('rank'),
                       popularity=entry.get('popularity'), members=entry.get('num_list_users'),
                       genres=sorted({g['name'].lower() for g in entry.get('genres', [])}),
                       start_date=entry.get('start_date'), end_date=entry.get('end_date'),
                       metadata_source='myanimelist_mirror', mal_source_updated_at=entry.get('updated_at'))
            # Keep the more recent base snapshot score rather than assuming all mirror rows are fresh.
            row['mal_score'] = entry.get('mean')
            row['mal_scored_by'] = entry.get('num_scoring_users')
    inputs = []
    for path in sorted((RAW / 'jikan').glob('*.json')):
        if path.name.endswith('.provenance.json'):
            continue
        provenance = json.loads(path.with_suffix('.provenance.json').read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest() != provenance['sha256']:
            raise ValueError(f'Cache checksum mismatch: {path}')
        inputs.append(provenance)
        for entry in json.loads(path.read_text(encoding='utf-8'))['data']:
            key = f'mal:{entry["mal_id"]}'
            if key not in rows:
                rows[key] = normalize({'sources': [f'https://myanimelist.net/anime/{entry["mal_id"]}'],
                                       'title': entry['title'], 'type': entry.get('type') or 'UNKNOWN'})
            previous = rows[key]['mal_metadata_retrieved_at']
            if previous is None or provenance['retrieved_at'] > previous:
                enrich(rows[key], entry, provenance['retrieved_at'])
    from enrich_catalog import apply as apply_enrichment
    enrichment_report = apply_enrichment(rows, normalize)
    catalog = sorted(rows.values(), key=lambda x: x['anime_id'])
    for row in catalog:
        if not row['name_english'] or (row['score'] is not None and not 0 <= row['score'] <= 10):
            raise ValueError(f'Invalid record: {row["anime_id"]}')
    OUT.mkdir(parents=True, exist_ok=True)
    db_path = OUT / 'anime.sqlite.tmp'
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE anime (anime_id TEXT PRIMARY KEY, mal_id INTEGER UNIQUE, title TEXT NOT NULL,
          year INTEGER, score REAL CHECK(score BETWEEN 0 AND 10),
          mal_score REAL CHECK(mal_score BETWEEN 0 AND 10), metadata_json TEXT NOT NULL);
        CREATE TABLE tags (anime_id TEXT REFERENCES anime, tag TEXT, kind TEXT, PRIMARY KEY(anime_id,tag,kind));
        CREATE TABLE sources (anime_id TEXT REFERENCES anime, url TEXT, PRIMARY KEY(anime_id,url));
        CREATE TABLE provenance (name TEXT PRIMARY KEY, metadata_json TEXT NOT NULL);
        CREATE INDEX anime_year ON anime(year);
        CREATE INDEX anime_title ON anime(title COLLATE NOCASE);
        CREATE INDEX tags_tag ON tags(tag);
    ''')
    for row in catalog:
        con.execute('INSERT INTO anime VALUES (?,?,?,?,?,?,?)', (row['anime_id'],row['mal_id'],row['name_english'],row['year'],row['score'],row['mal_score'],json.dumps(row,ensure_ascii=False,allow_nan=False)))
        for kind in ('tags','genres'):
            con.executemany('INSERT INTO tags VALUES (?,?,?)', [(row['anime_id'],t,kind) for t in row[kind]])
        con.executemany('INSERT INTO sources VALUES (?,?)', [(row['anime_id'],u) for u in row['sources']])
    report = {
        'source_last_update': source['lastUpdate'], 'source_url': SOURCE,
        'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'license': source['license'], 'source_schema': source.get('$schema'),
        'catalog_entries': len(catalog), 'mal_ids': sum(r['mal_id'] is not None for r in catalog),
        'mal_enriched': sum(r['mal_metadata_retrieved_at'] is not None for r in catalog),
        'mal_mirror_enriched': sum(r['metadata_source'] == 'myanimelist_mirror' for r in catalog),
        'mal_mirror': mirror_info, 'mirror_ids_not_in_catalog': mirror_unmatched,
        'ambiguous_mal_mappings': sum(r['ambiguous_mal_mapping'] for r in catalog),
        'entries_2026': sum(r['year'] == 2026 for r in catalog),
        'with_synopsis': sum(bool(r['synopsis']) for r in catalog),
        'with_score': sum(r['score'] is not None for r in catalog),
        'missing_by_field': {field: sum(r.get(field) in (None, '', []) for r in catalog)
                             for field in ('synopsis', 'score', 'members', 'genres', 'tags', 'start_date', 'img_url')},
        'duplicate_display_titles': sum(count > 1 for count in Counter(r['name_english'] for r in catalog).values()),
        'jikan_inputs': inputs,
        'additional_sources': enrichment_report,
        'image_availability': dict(Counter(r['image_availability'] for r in catalog)),
        'cohorts': {label: {'count': len(group), **{field: sum(not r.get(field) for r in group) for field in ('synopsis','genres','mal_score','aggregate_score')}}
                    for label, group in [('popular_top_1000', [r for r in catalog if r.get('priority_popular')]),
                                         ('year_2026', [r for r in catalog if r['year'] == 2026])]},
    }
    con.execute('INSERT INTO provenance VALUES (?,?)', ('build', json.dumps(report)))
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or con.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('SQLite integrity validation failed')
    con.close()
    db_path.replace(OUT / 'anime.sqlite')
    write_json(OUT / 'catalog.json', catalog)
    # Existing recommendation code accepts these fields. Keep broad tags distinct in canonical data.
    compat = [dict(r, genres=sorted(set(r['genres'] + r['tags']))) for r in catalog]
    write_json(OUT / 'cleaned_anime_data.json', compat)
    web_fields = ('anime_id','mal_id','name_english','name','synopsis','type_of','year','season','status','total_episodes','genres','tags',
                  'studios','aggregate_score','aggregate_score_source','mal_score','mal_score_source','mal_scored_by','img_url','images',
                  'thumbnail_url','image_alternatives','image_alt','image_availability','mal_url','rating','duration','source_material','trailer_url','recommendation_eligible')
    write_json(OUT / 'frontend_data.json', [{field: r.get(field) for field in web_fields} for r in catalog])
    write_json(OUT / 'synopsis_keywords.json', [{'anime_id': r['anime_id'], 'name_english': r['name_english'],
        'synopsis_keywords': ' '.join(re.findall(r'[a-z]+', (r['synopsis'] or '').lower()))} for r in catalog])
    write_json(OUT / 'alphabetized_titles.json', sorted({r['name_english'] for r in catalog}, key=str.casefold))
    write_json(OUT / 'quality_report.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('jikan_inputs', 'additional_sources')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Download catalog and MAL mirror; reuse cached snapshots')
    parser.add_argument('--jikan', action='store_true', help='Also request live Jikan enrichment (network required)')
    parser.add_argument('--refresh', action='store_true', help='Replace cached downloads (requires --download)')
    parser.add_argument('--full-mal', action='store_true', help='Fetch every MAL catalog page instead of seasonal/top subset')
    parser.add_argument('--year', type=int, default=2026)
    args = parser.parse_args()
    if args.refresh and not args.download:
        parser.error('--refresh requires --download')
    if args.jikan and not args.download:
        parser.error('--jikan requires --download')
    if args.full_mal and not args.jikan:
        parser.error('--full-mal requires --jikan')
    if args.download:
        fetch(SOURCE, RAW / 'anime-offline-database.json', args.refresh)
        sync_mirror(args.refresh)
        if args.jikan:
            sync_jikan(args.year, args.full_mal, args.refresh)
    build()


if __name__ == '__main__':
    main()

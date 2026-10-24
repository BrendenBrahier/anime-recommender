"""Check a deterministic cover-image sample without downloading artwork."""
import concurrent.futures
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def check(url):
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'unverified'}
    if urlparse(url).hostname not in {'cdn.myanimelist.net', 'media.kitsu.app', 'media.kitsu.io', 's4.anilist.co'}:
        result['reason'] = 'Host outside the image audit allowlist'
        return url, result
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD', headers={'User-Agent':'anime-recommender-data/2.0'}), timeout=12) as response:
            result.update(http_status=response.status, content_type=response.headers.get('Content-Type',''))
            result['status'] = 'reachable' if result['content_type'].startswith('image/') else 'not_image'
    except Exception as exc:
        result.update(status='check_failed', reason=str(exc))
    time.sleep(0.5)
    return url, result


def main():
    rows = json.loads((ROOT/'data/current/catalog.json').read_text(encoding='utf-8'))
    popular = sorted((r for r in rows if r.get('popularity')), key=lambda r:r['popularity'])[:75]
    recent = sorted((r for r in rows if r['year']==2026), key=lambda r:r['anime_id'])
    recent = recent[::max(1,len(recent)//75)][:75]
    urls = sorted({r['img_url'] for r in popular+recent if r.get('img_url')})
    path = ROOT/'data/raw/image_checks.json'
    checks = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for url, result in pool.map(check, [u for u in urls if u not in checks]):
            checks[url] = result
    path.write_text(json.dumps(checks,indent=2),encoding='utf-8')
    from collections import Counter
    print(dict(Counter(v['status'] for v in checks.values())))


if __name__ == '__main__':
    main()

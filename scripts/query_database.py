"""Search the refreshed catalog without loading it all into memory."""
import argparse
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'data/current/anime.sqlite'


def search(title='', year=None, limit=10, database=DB):
    if not 1 <= limit <= 100:
        raise ValueError('limit must be between 1 and 100')
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as con:
        rows = con.execute('''SELECT metadata_json FROM anime
            WHERE title LIKE ? AND (? IS NULL OR year = ?)
            ORDER BY score DESC, anime_id LIMIT ?''', (f'%{title}%', year, year, limit))
        return [json.loads(row[0]) for row in rows]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('title', nargs='?', default='')
    parser.add_argument('--year', type=int)
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(search(args.title, args.year, args.limit), ensure_ascii=True, indent=2))

import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('refresh', ROOT / 'scripts/refresh_database.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class NormalizeTests(unittest.TestCase):
    def test_missing_values_remain_missing(self):
        row = refresh.normalize({'sources': ['https://myanimelist.net/anime/1'], 'title': 'Test', 'type': 'TV'})
        self.assertEqual(row['anime_id'], 'mal:1')
        self.assertIsNone(row['score'])
        self.assertIsNone(row['total_episodes'])
        self.assertIsNone(row['members'])

    def test_ambiguous_mapping_cannot_enrich_wrong_anime(self):
        row = refresh.normalize({'sources': ['https://myanimelist.net/anime/1', 'https://myanimelist.net/anime/2'], 'title': 'Test', 'type': 'TV'})
        self.assertIsNone(row['mal_id'])
        self.assertTrue(row['ambiguous_mal_mapping'])

    def test_title_collision_preserves_two_identities(self):
        rows = [refresh.normalize({'sources': [f'https://myanimelist.net/anime/{i}'], 'title': 'Same Title', 'type': 'TV'}) for i in (1, 2)]
        self.assertNotEqual(rows[0]['anime_id'], rows[1]['anime_id'])

    def test_wrong_id_enrichment_rejected(self):
        with self.assertRaises(ValueError):
            refresh.enrich({'mal_id': 1}, {'mal_id': 2}, '2026-10-22')


@unittest.skipUnless((ROOT / 'data/current/anime.sqlite').exists(), 'Build database first')
class DatabaseTests(unittest.TestCase):
    def test_integrity_exports_and_coverage(self):
        path = ROOT / 'data/current'
        catalog = json.loads((path / 'catalog.json').read_text(encoding='utf-8'))
        report = json.loads((path / 'quality_report.json').read_text(encoding='utf-8'))
        keywords = json.loads((path / 'synopsis_keywords.json').read_text(encoding='utf-8'))
        with sqlite3.connect(path / 'anime.sqlite') as con:
            self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(con.execute('SELECT count(*) FROM anime').fetchone()[0], len(catalog))
            self.assertGreater(con.execute('SELECT count(*) FROM anime WHERE year=2026').fetchone()[0], 100)
            bebop = json.loads(con.execute('SELECT metadata_json FROM anime WHERE mal_id=1').fetchone()[0])
            self.assertIn('Bebop', bebop['name_english'])
            self.assertTrue(bebop['synopsis'])
        self.assertEqual({r['anime_id'] for r in catalog}, {r['anime_id'] for r in keywords})
        self.assertEqual(len(catalog), report['catalog_entries'])
        self.assertEqual(len({r['anime_id'] for r in catalog}), len(catalog))


if __name__ == '__main__':
    unittest.main()

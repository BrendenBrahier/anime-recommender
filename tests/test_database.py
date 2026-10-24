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

    def test_mal_enrichment_does_not_overwrite_aggregate(self):
        row = refresh.normalize({'sources':['https://myanimelist.net/anime/1'],'title':'A','type':'TV','score':{'arithmeticMean':8.1}})
        refresh.enrich(row, {'mal_id':1,'title':'A','score':7.2}, '2026-10-23')
        self.assertEqual(row['score'],8.1)
        self.assertEqual(row['mal_score'],7.2)
        self.assertEqual(row['score_source'],'aod_cross_provider_mean')

    def test_placeholder_synopses_are_not_real_coverage(self):
        from enrich_catalog import present, number
        self.assertFalse(present('No synopsis information has been added to this title.'))
        self.assertIsNone(number('Unknown'))
        self.assertIsNone(number('nan'))
        self.assertIsNone(number(0))


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

    def test_reviewed_mappings_and_score_contract(self):
        rows = json.loads((ROOT/'data/current/catalog.json').read_text(encoding='utf-8'))
        report = json.loads((ROOT/'data/current/quality_report.json').read_text(encoding='utf-8'))
        splits = [r for r in rows if r.get('supersedes_ambiguous_id')]
        applied = [d for d in report['additional_sources']['mapping_review'] if d['applied']]
        self.assertEqual(len(splits),sum(len(d['replacements']) for d in applied))
        self.assertTrue(all(r['aggregate_score'] is None for r in splits))
        self.assertEqual(sum(r['ambiguous_mal_mapping'] for r in rows),report['ambiguous_mal_mappings'])
        for r in rows:
            self.assertEqual(r['score'],r['aggregate_score'])
            if r['ambiguous_mal_mapping']:
                self.assertFalse(r['recommendation_eligible'])
            if r['mal_score'] is not None:
                self.assertGreater(r['mal_score'],0)
                self.assertLessEqual(r['mal_score'],10)
        web = json.loads((ROOT/'data/current/frontend_data.json').read_text(encoding='utf-8'))
        self.assertEqual({r['anime_id'] for r in web},{r['anime_id'] for r in rows})
        self.assertTrue(all('image_alt' in r and 'mal_score' in r and 'aggregate_score' in r for r in web))


if __name__ == '__main__':
    unittest.main()

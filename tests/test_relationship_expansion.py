import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from expand_relationships import crawl, family_ids, popular_ids


def detail(mid, targets=()):
    return {'response': {'data': {'mal_id': mid, 'relations': [
        {'relation': 'Sequel', 'entry': [{'mal_id': t, 'type': 'anime'} for t in targets]}]}}}


class ExpansionTests(unittest.TestCase):
    def test_priority_ignores_ambiguous_ids_and_missing_rank(self):
        rows = [dict(anime_id='mal:1', mal_id=1, popularity=20),
                dict(anime_id='mal:2', mal_id=2, popularity=10),
                dict(anime_id='other:3', mal_id=3, popularity=1),
                dict(anime_id='mal:4', mal_id=4, popularity=None)]
        self.assertEqual(popular_ids(rows, 2), [2, 1])

    def test_family_traversal_deduplicates_cycles_and_non_anime(self):
        records = {1: detail(1, [2, 2]), 2: detail(2, [1, 3]), 3: detail(3)}
        records[1]['response']['data']['relations'].append(
            {'relation': 'Adaptation', 'entry': [{'mal_id': 99, 'type': 'manga'}]})
        calls = []
        with tempfile.TemporaryDirectory() as folder:
            def fetch(mid):
                calls.append(mid)
                return records[mid]
            result = crawl([1, 1], fetch, Path(folder), 10)
        self.assertEqual(sorted(calls), [1, 2, 3])
        self.assertTrue(result['traversal_complete'])

    def test_resume_cache_does_not_consume_network_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            (cache / 'anime_1_full.json').write_text(json.dumps(detail(1, [2])))
            calls = []
            def fetch(mid):
                calls.append(mid)
                return detail(mid, [mid + 1])
            result = crawl([1], fetch, cache, 1, workers=1)
        self.assertEqual(calls, [1, 2])
        self.assertEqual(result['new_requests'], 1)
        self.assertEqual(result['pending_ids'], [3])
        self.assertFalse(result['traversal_complete'])

    def test_errors_and_deleted_records_do_not_claim_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            def fetch(mid):
                if mid == 1:
                    raise TimeoutError('test')
                return {'http_status': 404, 'response': {}}
            result = crawl([1, 2], fetch, Path(folder), 2)
        self.assertEqual(list(result['errors']), ['1'])
        self.assertEqual(result['unavailable'], {'2': 404})
        self.assertFalse(result['traversal_complete'])

    def test_mismatched_or_missing_relationships_are_not_evidence(self):
        self.assertIsNone(family_ids(detail(5), 6))
        self.assertIsNone(family_ids({'response': {'data': {'mal_id': 5}}}, 5))
        self.assertEqual(family_ids(detail(5), 5), [])


if __name__ == '__main__':
    unittest.main()

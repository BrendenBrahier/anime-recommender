from copy import deepcopy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from watch_order import apply_policy, load_policy
from recommendation_engine import relationship_reasons, Recommender


def row(key, required=(), recap='none_detected'):
    return {'anime_id':key,'verified_relations':True,'prerequisites':list(required),
            'franchise_id':'family','recap_status':recap,'relations':[]}


def policy_group(name):
    policy,_=load_policy()
    return {**policy,'groups':[g for g in policy['groups'] if g['id']==name]}


class WatchOrderTests(unittest.TestCase):
    def test_original_gundam_is_entry_but_side_story_keeps_context(self):
        raw={'mal:80':row('mal:80',['mal:55845']),
             'mal:55845':row('mal:55845',['mal:80'])}
        original=deepcopy(raw)
        effective=apply_policy(raw,policy_group('gundam'))
        self.assertEqual(raw,original)
        self.assertEqual(relationship_reasons('mal:80',effective,set()),[])
        self.assertEqual(effective['mal:80']['optional_context'],['mal:55845'])
        self.assertIn('unwatched_prerequisite',relationship_reasons('mal:55845',effective,set()))
        self.assertEqual(relationship_reasons('mal:55845',effective,{'mal:80'}),[])

    def test_season_three_requires_season_two_not_its_own_bonus(self):
        raw={k:row(k) for k in ['mal:539','mal:540','mal:541','mal:37789']}
        raw['mal:541']['prerequisites']=['mal:37789','mal:540']
        raw['mal:37789']['prerequisites']=['mal:541']
        effective=apply_policy(raw,policy_group('tenchi'))
        self.assertIn('unwatched_prerequisite',relationship_reasons('mal:541',effective,{'mal:539'}))
        self.assertEqual(relationship_reasons('mal:541',effective,{'mal:540'}),[])
        self.assertIn('sequels_disabled',relationship_reasons('mal:541',effective,{'mal:540'},allow_sequels=False))

    def test_parallel_crossovers_keep_their_own_series_gates(self):
        raw={k:row(k) for k in ['mal:861','mal:177','mal:3091','mal:2685','mal:4918','mal:4938']}
        raw['mal:4918']['prerequisites']=['mal:3091','mal:4938']
        raw['mal:4938']['prerequisites']=['mal:2685','mal:4918']
        effective=apply_policy(raw,policy_group('clamp-crossovers'))
        self.assertEqual(relationship_reasons('mal:4918',effective,{'mal:3091'}),[])
        self.assertIn('unwatched_prerequisite',relationship_reasons('mal:4938',effective,{'mal:3091'}))

    def test_stale_or_missing_evidence_fails_closed(self):
        raw={'mal:80':row('mal:80',[]),'mal:55845':row('mal:55845')}
        with self.assertRaisesRegex(ValueError,'evidence changed'):
            apply_policy(raw,policy_group('gundam'))
        raw['mal:80']['prerequisites']=['mal:55845'];raw['mal:55845']['verified_relations']=False
        with self.assertRaisesRegex(ValueError,'Missing watch-order evidence'):
            apply_policy(raw,policy_group('gundam'))

    def test_decisions_cannot_silently_drop_dependencies_or_duplicate(self):
        raw={'mal:80':row('mal:80',['mal:55845']),'mal:55845':row('mal:55845')}
        policy=policy_group('gundam');policy['groups'][0]['decisions'][0]['optional_context']=[]
        with self.assertRaises(ValueError):apply_policy(raw,policy)
        policy=policy_group('gundam');policy['groups']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate'):apply_policy(raw,policy)

    def test_runtime_keeps_recap_exclusion_and_franchise_cap(self):
        raw={'mal:80':row('mal:80',['mal:55845']),
             'mal:55845':row('mal:55845',['mal:80']),
             'mal:999':row('mal:999',recap='confirmed'),
             'mal:1000':row('mal:1000')}
        catalog=[{'anime_id':k,'name_english':k,'synopsis':'Space robot war',
                  'genres':['sci-fi'],'rating':'PG-13','recommendation_eligible':True} for k in raw]
        engine=Recommender(catalog,{'records':raw},policy_group('gundam'))
        result=engine.recommend({'query':'Space robot war','limit':10})['results']
        self.assertEqual(len(result),1)
        self.assertNotIn(result[0]['anime_id'],{'mal:999','mal:55845'})
        result=engine.recommend({'query':'Space robot war','completed':['mal:80'],'limit':10})['results']
        self.assertNotIn('mal:999',{r['anime_id'] for r in result})
        self.assertEqual(len(result),1)


if __name__=='__main__':unittest.main()

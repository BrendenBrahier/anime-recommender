import sys
import time
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from recommendation_engine import Recommender, relationship_reasons, validate_request
from mal_profile import normalize_list, preferences
from mal_client import MALClient, MALRequestError, TokenSet
from build_relationships import build

def row(mid,**extra):
    result=dict(anime_id=f'mal:{mid}',name_english=f'Title {mid}',synopsis='Space crew adventure friendship',genres=['sci-fi'],recommendation_eligible=True,rating='PG-13',year=2000,type_of='tv',total_episodes=12,status='FINISHED')
    result.update(extra);return result

def relationship(mid,family=None,pre=None,recap='none_detected'):
    return {'anime_id':f'mal:{mid}','verified_relations':True,'franchise_id':family or f'mal:{mid}','prerequisites':pre or [],'recap_status':recap}

class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.catalog=[row(i) for i in range(1,8)]
        self.rels={f'mal:{i}':relationship(i) for i in range(1,7)}
        self.rels['mal:2']=relationship(2,'mal:1',['mal:1'])
        self.rels['mal:3']=relationship(3,'mal:1',['mal:2'])
        self.rels['mal:4']=relationship(4,'mal:1',recap='confirmed')
        self.engine=Recommender(self.catalog,{'records':self.rels})

    def test_sequels_require_completion_not_liking(self):
        request={'likes':['mal:1'],'limit':10}
        ids={r['anime_id'] for r in self.engine.recommend(request)['results']}
        self.assertNotIn('mal:2',ids);self.assertNotIn('mal:3',ids)
        request['completed']=['mal:1']
        ids={r['anime_id'] for r in self.engine.recommend(request)['results']}
        self.assertIn('mal:2',ids);self.assertNotIn('mal:3',ids)
        self.assertNotIn('mal:4',ids);self.assertNotIn('mal:7',ids)

    def test_franchise_cap_and_filters_do_not_relax(self):
        self.rels['mal:6']['franchise_id']='mal:5'
        result=self.engine.recommend({'query':'space crew','limit':10,'filters':{'max_episodes':12}})
        families=[r['franchise_id'] for r in result['results']]
        self.assertEqual(len(families),len(set(families)))
        self.assertTrue(result['warnings'])
        result=self.engine.recommend({'query':'space','filters':{'max_episodes':1}})
        self.assertEqual(result['results'],[])

    def test_unknown_and_cycles_fail_closed(self):
        self.assertIn('unknown_relationships',relationship_reasons('mal:7',self.rels,set()))
        self.rels['mal:1']['prerequisites']=['mal:2']
        self.assertIn('cyclic_prerequisites',relationship_reasons('mal:1',self.rels,{'mal:1','mal:2'}))
        self.assertIn('unwatched_prerequisite',relationship_reasons('mal:2',self.rels,set(),allow_unknown=True))

    def test_invalid_filters_and_no_preferences(self):
        for request in [{'filters':{'year_min':2020,'year_max':2000}},{'filters':{'formats':['typo']}},{'allow_recaps':'false'},{'limit':0},{'filters':{'finished':'false'}}]:
            with self.assertRaises(ValueError):validate_request(request)
        self.assertEqual(self.engine.recommend({})['results'],[])

    def test_profile_scores_and_progress(self):
        items=[{'node':{'id':i},'list_status':{'status':status,'score':score,'is_rewatching':rewatch}} for i,status,score,rewatch in [(1,'completed',9,False),(2,'watching',8,False),(3,'plan_to_watch',0,False),(4,'dropped',0,False),(5,'completed',3,False),(6,'watching',9,True)]]
        profile=normalize_list(items);pref=preferences(profile)
        self.assertEqual(pref['completed'],{'mal:1','mal:5','mal:6'})
        self.assertNotIn('mal:3',pref['exclude']);self.assertIn('mal:4',pref['exclude'])
        self.assertNotIn('mal:4',pref['dislikes']);self.assertIn('mal:5',pref['dislikes'])
        self.assertIsNone(profile['entries'][2]['score'])

    def test_relationship_direction_and_recap_evidence(self):
        records=[{'url':'example','retrieved_at':'snapshot','response':{'data':{'mal_id':1,'title':'First','synopsis':'An adventure','relations':[{'relation':'Sequel','entry':[{'mal_id':2,'type':'anime'}]},{'relation':'Summary','entry':[{'mal_id':3,'type':'anime'}]},{'relation':'Adaptation','entry':[{'mal_id':100,'type':'manga'}]}]}}}]
        data=build(records,{'mal:1':{}})['records']
        self.assertEqual(data['mal:2']['prerequisites'],['mal:1'])
        self.assertEqual(data['mal:3']['recap_status'],'confirmed')
        self.assertFalse(data['mal:2']['verified_relations']);self.assertNotIn('mal:100',data)
        self.assertEqual(data['mal:1']['franchise_id'],data['mal:2']['franchise_id'])

    def test_profiles_are_not_retained_between_requests(self):
        profile=normalize_list([{'node':{'id':5},'list_status':{'status':'completed','score':9}}])
        first=self.engine.recommend({'query':'space crew'},profile)
        second=self.engine.recommend({'query':'space crew'})
        self.assertNotIn('mal:5',{r['anime_id'] for r in first['results']})
        self.assertIn('mal:5',{r['anime_id'] for r in second['results']})

    def test_malformed_profiles_fail_instead_of_inventing_ratings(self):
        for state in [{'status':'completed','score':11},{'status':'completed','score':True},{'status':'unknown','score':0}]:
            with self.assertRaises(ValueError):normalize_list([{'node':{'id':1},'list_status':state}])

class MALTests(unittest.TestCase):
    def setUp(self):
        self.send=Mock(return_value={'token_type':'Bearer','expires_in':3600,'access_token':'test-access','refresh_token':'test-refresh'})
        self.client=MALClient('test-client','http://127.0.0.1/callback',send=self.send)

    def test_state_expiry_single_use_and_secret_repr(self):
        url,attempt=self.client.begin();state=attempt.state
        self.assertIn('code_challenge_method=plain',url)
        with self.assertRaises(ValueError):self.client.finish(attempt,'code','wrong')
        self.send.assert_not_called()
        tokens=self.client.finish(attempt,'code',state)
        self.assertNotIn('test-access',repr(tokens));self.assertNotIn(state,repr(attempt))
        self.assertEqual(attempt.verifier,'')
        with self.assertRaises(ValueError):self.client.finish(attempt,'code',state)
        _,attempt=self.client.begin();attempt.created-=601
        with self.assertRaises(ValueError):self.client.finish(attempt,'code',attempt.state)

    def test_pagination_does_not_leak_bearer_and_import_is_atomic(self):
        self.send.return_value={'data':[],'paging':{'next':'https://attacker.example/steal?offset=1'}}
        with self.assertRaises(MALRequestError):self.client.read_profile(TokenSet('secret','refresh',time.time()+60))
        self.assertEqual(self.send.call_count,1)

    def test_multiple_pages_and_zero_score(self):
        def item(mid):return {'node':{'id':mid},'list_status':{'status':'completed','score':0,'num_episodes_watched':12}}
        self.send.side_effect=[{'data':[item(1)],'paging':{'next':'https://api.myanimelist.net/v2/users/@me/animelist?offset=1'}},{'data':[item(2)],'paging':{}}]
        profile=self.client.read_profile(TokenSet('secret','refresh',time.time()+60))
        self.assertEqual(len(profile['entries']),2);self.assertIsNone(profile['entries'][0]['score'])

    def test_import_once_discards_tokens_on_success_and_error(self):
        for fail in [False,True]:
            tokens=TokenSet('secret','refresh',time.time()+60)
            self.client.finish=Mock(return_value=tokens)
            self.client.read_profile=Mock(side_effect=MALRequestError('failed')) if fail else Mock(return_value={'entries':[]})
            if fail:
                with self.assertRaises(MALRequestError):self.client.import_once(None,'code','state')
            else:self.assertEqual(self.client.import_once(None,'code','state'),{'entries':[]})
            self.assertEqual(tokens.access_token,'');self.assertEqual(tokens.refresh_token,'')

    def test_refresh_discards_old_token(self):
        old=TokenSet('old-access','old-refresh',0)
        new=self.client.refresh(old)
        self.assertEqual(old.access_token,'');self.assertEqual(new.access_token,'test-access')

    def test_invalid_token_response_and_looping_pagination(self):
        self.send.return_value={'token_type':'Bearer','access_token':'secret','refresh_token':'secret','expires_in':float('nan')}
        _,attempt=self.client.begin()
        with self.assertRaises(MALRequestError):self.client.finish(attempt,'code',attempt.state)
        self.assertEqual(attempt.verifier,'')
        self.send.return_value={'data':[],'paging':{'next':'https://api.myanimelist.net/v2/users/@me/animelist?offset=0'}}
        with self.assertRaises(MALRequestError):self.client.read_profile(TokenSet('secret','secret',time.time()+60))

if __name__=='__main__':unittest.main()

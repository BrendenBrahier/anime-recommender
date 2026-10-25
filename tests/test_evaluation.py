import importlib.util
from pathlib import Path
import unittest
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

spec=importlib.util.spec_from_file_location('evaluation',Path(__file__).resolve().parents[1]/'scripts/evaluate_recommendations.py')
evaluation=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluation)
report_spec=importlib.util.spec_from_file_location('report',Path(__file__).resolve().parents[1]/'scripts/report_evaluation.py')
report=importlib.util.module_from_spec(report_spec);report_spec.loader.exec_module(report)

class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(anime_id='mal:1',recommendation_eligible=True,rating='PG-13',genres=['adventure'],type_of='tv',status='FINISHED',year=2005,total_episodes=12)
        self.case=dict(likes=[],dislikes=[],watched=[],filters={'formats':['tv'],'finished':True,'year_min':2000,'year_max':2010,'max_episodes':24,'excluded_categories':['horror']})

    def test_boundaries_and_unknown_constraints(self):
        self.assertEqual(evaluation.violations(self.row,self.case),[])
        for field,value in [('year',None),('year',1999),('year',2011),('total_episodes',None),('total_episodes',25),('type_of','movie'),('status','UNKNOWN'),('genres',[]),('genres',['horror']),('recommendation_eligible',False)]:
            row=dict(self.row,**{field:value})
            self.assertTrue(evaluation.violations(row,self.case),(field,value))
            self.assertFalse(evaluation.eligible_mask(pd.DataFrame([row]),self.case)[0],(field,value))
        for year in [2000,2010]:
            row=dict(self.row,year=year,total_episodes=24)
            self.assertEqual(evaluation.violations(row,self.case),[])

    def test_seen_and_disliked_are_excluded(self):
        for field in ['likes','dislikes','watched']:
            case=dict(self.case,**{field:['mal:1']})
            self.assertIn('already_seen_or_disliked',evaluation.violations(self.row,case))

    def test_sparse_cosine_matches_dense_reference(self):
        rows=[dict(anime_id=f'mal:{i}',name_english=str(i),score=s,members=m,genres=g,type_of='tv') for i,s,m,g in [(1,8,100,['space']),(2,7,50,['space']),(3,None,None,['romance']),(4,9,400,['hentai'])]]
        frame,x=evaluation.legacy_features(rows,{'mal:1':'space crew journey','mal:2':'space crew war','mal:3':'school romance'})
        # Legacy scaler sees the excluded row before filtering, including its maxima.
        self.assertEqual(frame.anime_id.tolist(),['mal:1','mal:2','mal:3'])
        from sklearn.feature_extraction.text import TfidfVectorizer
        text=TfidfVectorizer(stop_words='english').fit_transform(['space tv space crew journey','space tv space crew war','romance tv school romance']).toarray()
        reference=np.column_stack([text,np.array([[8/9,100/400],[7/9,50/400],[0,0]])*.5])
        np.testing.assert_allclose((x@x.T).toarray(),cosine_similarity(reference),atol=1e-12)

    def test_empty_results_do_not_earn_perfect_compliance(self):
        runs=[dict(model='test',supported=False,results=[],category_diversity=None)]
        summary=evaluation.summarize(runs)['test']
        self.assertIsNone(summary['violation_rate']); self.assertEqual(summary['supported'],0)

    def test_unknown_judgments_and_unfilled_slots_receive_no_credit(self):
        runs=[dict(model='test',case_id='c',supported=True,results=[{'anime_id':'a','violations':[]},{'anime_id':'b','violations':['format']},{'anime_id':'c','violations':[]}])]
        labels=[dict(case_id='c',anime_id='a',grade=3),dict(case_id='c',anime_id='b',grade=2),dict(case_id='c',anime_id='c',grade=None)]
        s=report.score(runs,labels)[0]
        self.assertEqual(s['judged'],2);self.assertEqual(s['unknown'],1)
        self.assertEqual(s['plausible_or_strong_lower_bound'],.4)
        self.assertEqual(s['constraint_compliant_relevant_lower_bound'],.2)

    def test_case_suite_coverage_and_seed_identity(self):
        root=Path(__file__).resolve().parents[1]
        cases=json.loads((root/'evaluation/cases.json').read_text(encoding='utf-8'))
        self.assertEqual(len({c['id'] for c in cases}),40)
        self.assertEqual(len({c['topic'] for c in cases}),8)
        self.assertEqual(sum(not c['likes'] for c in cases),8)
        calm=next(c for c in cases if c['id']=='calm-1')
        self.assertEqual(calm['likes'],['mal:17549']);self.assertIn('Non Non Biyori',calm['prompt'])
        result=json.loads((root/'evaluation/results/benchmark.json').read_text(encoding='utf-8'))
        labels=json.loads((root/'evaluation/initial_judgments.json').read_text(encoding='utf-8'))
        self.assertEqual(labels['cases_sha256'],result['manifest']['cases_sha256'])
        pairs={(a['case_id'],a['anime_id']) for a in labels['annotations']}
        for run in result['runs']:
            self.assertEqual(len({x['anime_id'] for x in run['results']}),len(run['results']))
            if run['model']!='legacy_filtered':
                for x in run['results']:self.assertIn((run['case_id'],x['anime_id']),pairs)

if __name__=='__main__':unittest.main()

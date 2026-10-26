"""Normalize MAL list payloads. Contains no authentication or token storage."""
STATUSES={'watching','completed','on_hold','dropped','plan_to_watch'}

def normalize_list(items):
    entries={}
    for item in items:
        mid=item.get('node',{}).get('id'); state=item.get('list_status',{})
        if type(mid) is not int or mid<=0:raise ValueError('Invalid MAL anime ID')
        status=state.get('status')
        if status not in STATUSES:raise ValueError('Unknown or missing MAL list status')
        score=state.get('score',0)
        if type(score) is not int or not 0<=score<=10:raise ValueError('Invalid MAL score')
        watched=state.get('num_episodes_watched',state.get('num_watched_episodes',0))
        if type(watched) is not int or watched<0:raise ValueError('Invalid watched episode count')
        rewatching=state.get('is_rewatching',False)
        if type(rewatching) is not bool:raise ValueError('Invalid rewatching flag')
        key=f'mal:{mid}'
        value={'anime_id':key,'status':status,'score':score or None,'episodes_watched':watched,'is_rewatching':rewatching}
        if key in entries and entries[key]!=value:raise ValueError('Conflicting duplicate MAL list entries; repeat import')
        entries[key]=value
    return {'schema_version':1,'entries':list(entries.values())}

def preferences(profile):
    # Re-validate normalized input so manually imported profiles obey the same contract.
    items=[]
    for row in profile.get('entries',[]):
        key=row.get('anime_id','')
        if not isinstance(key,str) or not key.startswith('mal:') or not key[4:].isdigit():raise ValueError('Invalid profile identity')
        items.append({'node':{'id':int(key[4:])},'list_status':{'status':row.get('status'),'score':row.get('score') if row.get('score') is not None else 0,'num_episodes_watched':row.get('episodes_watched',0),'is_rewatching':row.get('is_rewatching',False)}})
    entries=normalize_list(items)['entries']
    completed={r['anime_id'] for r in entries if r['status']=='completed' or r['is_rewatching']}
    exclude={r['anime_id'] for r in entries if r['status']!='plan_to_watch' or r['episodes_watched']>0}
    experienced=[r for r in entries if r['status']!='plan_to_watch' or r['episodes_watched']>0]
    likes={r['anime_id']:(r['score']-7)/3 for r in experienced if r['score'] is not None and r['score']>=8}
    dislikes={r['anime_id']:(5-r['score'])/4 for r in experienced if r['score'] is not None and r['score']<=4}
    return {'completed':completed,'exclude':exclude,'likes':likes,'dislikes':dislikes}

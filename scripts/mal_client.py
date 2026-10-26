"""Server-side OAuth building blocks; future HTTP app must bind attempts to sessions.
No passwords, files, logs, or persistent token storage. Not a deployed login UI.
"""
from dataclasses import dataclass, field
import hmac
import json
import math
import secrets
import time
from urllib.parse import urlencode, urlsplit, parse_qs, unquote
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
try:
    from .mal_profile import normalize_list
except ImportError:
    from mal_profile import normalize_list

AUTHORIZE='https://myanimelist.net/v1/oauth2/authorize'
TOKEN='https://myanimelist.net/v1/oauth2/token'
LIST='https://api.myanimelist.net/v2/users/@me/animelist'

class MALRequestError(RuntimeError):pass
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def transport(method,url,headers,body=None):
    try:
        with build_opener(NoRedirect).open(Request(url,data=body,headers=headers,method=method),timeout=25) as response:return json.load(response)
    except HTTPError as exc:
        raise MALRequestError(f'MAL request failed (HTTP {exc.code})') from None
    except (URLError,TimeoutError,ValueError):
        raise MALRequestError('MAL request failed; retry or reconnect') from None

@dataclass(repr=False)
class OAuthAttempt:
    state:str=field(repr=False)
    verifier:str=field(repr=False)
    created:float=field(default_factory=time.time)
    used:bool=False

@dataclass(repr=False)
class TokenSet:
    access_token:str=field(repr=False)
    refresh_token:str=field(repr=False)
    expires_at:float=0
    def discard(self):
        # Drop references, not a promise of cryptographic memory erasure in Python.
        self.access_token='';self.refresh_token='';self.expires_at=0

class MALClient:
    def __init__(self,client_id,redirect_uri,client_secret=None,send=transport):
        if not client_id:raise ValueError('Register a MAL application and configure its client ID')
        uri=urlsplit(redirect_uri)
        if not uri.hostname or uri.username or uri.password or uri.fragment:raise ValueError('Invalid callback URI')
        if uri.scheme!='https' and not (uri.scheme=='http' and uri.hostname in {'localhost','127.0.0.1'}):raise ValueError('HTTPS callback required outside local development')
        self.client_id=client_id;self.redirect_uri=redirect_uri;self._secret=client_secret;self.send=send

    def begin(self):
        attempt=OAuthAttempt(secrets.token_urlsafe(32),secrets.token_urlsafe(64))
        # Official MAL documentation currently supports plain PKCE only.
        query={'response_type':'code','client_id':self.client_id,'redirect_uri':self.redirect_uri,'state':attempt.state,'code_challenge':attempt.verifier,'code_challenge_method':'plain'}
        return AUTHORIZE+'?'+urlencode(query),attempt

    def _token(self,values):
        values=dict(values,client_id=self.client_id)
        if self._secret:values['client_secret']=self._secret
        result=self.send('POST',TOKEN,{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'},urlencode(values).encode())
        if not isinstance(result,dict) or result.get('token_type','').lower()!='bearer':raise MALRequestError('Invalid MAL token response')
        access=result.get('access_token');refresh=result.get('refresh_token');expires=result.get('expires_in')
        if not isinstance(access,str) or not access or not isinstance(refresh,str) or not refresh or type(expires) not in (int,float) or not math.isfinite(expires) or expires<=0:raise MALRequestError('Incomplete MAL token response')
        return TokenSet(access,refresh,time.time()+expires)

    def finish(self,attempt,code,state):
        if attempt.used or not isinstance(state,str) or not hmac.compare_digest(attempt.state,state) or not 0<=time.time()-attempt.created<=600:raise ValueError('Invalid, expired, or used authorization attempt')
        if not isinstance(code,str) or not code:raise ValueError('Missing authorization code')
        attempt.used=True
        try:return self._token({'grant_type':'authorization_code','code':code,'code_verifier':attempt.verifier,'redirect_uri':self.redirect_uri})
        finally:attempt.verifier='';attempt.state=''

    def refresh(self,tokens):
        if not tokens.refresh_token:raise ValueError('Reconnect to MAL')
        fresh=self._token({'grant_type':'refresh_token','refresh_token':tokens.refresh_token})
        tokens.discard();return fresh

    def read_profile(self,tokens,max_pages=100):
        if not tokens.access_token or tokens.expires_at<=time.time():raise ValueError('Access token expired; refresh or reconnect')
        if type(max_pages) is not int or not 1<=max_pages<=100:raise ValueError('Invalid page limit')
        offset=0;items=[]
        for _ in range(max_pages):
            query={'fields':'list_status{status,score,num_episodes_watched,is_rewatching}','limit':1000,'offset':offset,'nsfw':'true'}
            payload=self.send('GET',LIST+'?'+urlencode(query),{'Authorization':'Bearer '+tokens.access_token,'Accept':'application/json'})
            if not isinstance(payload,dict) or not isinstance(payload.get('data'),list) or not isinstance(payload.get('paging',{}),dict):raise MALRequestError('Invalid MAL list response')
            items.extend(payload['data']);next_url=payload.get('paging',{}).get('next')
            if not next_url:return normalize_list(items)
            parts=urlsplit(next_url)
            if parts.scheme!='https' or parts.netloc!='api.myanimelist.net' or unquote(parts.path)!='/v2/users/@me/animelist' or parts.fragment:raise MALRequestError('Unexpected MAL pagination destination')
            raw=parse_qs(parts.query).get('offset',[])
            if len(raw)!=1 or not raw[0].isdigit() or int(raw[0])<=offset:raise MALRequestError('Non-advancing MAL pagination')
            offset=int(raw[0])
        raise MALRequestError('MAL list exceeds the import limit; no partial profile was returned')

    def import_once(self,attempt,code,state):
        tokens=self.finish(attempt,code,state)
        try:return self.read_profile(tokens)
        finally:tokens.discard()

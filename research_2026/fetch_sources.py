"""Cache-first Massive receipts for the selected universe, with Singapore egress verification."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,time,threading
import pandas as pd,requests
from urllib.parse import urlparse,parse_qsl,urlencode,urlunparse
O=Path(__file__).resolve().parent;P=O.parent;KEY=None;local=threading.local()
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k.lower() not in ['apikey','api_key','authorization']}
 if isinstance(x,list):return [clean(v) for v in x]
 if isinstance(x,str):
  x=x.replace(KEY,'[REDACTED]') if KEY else x
  if x.startswith('https://'):
   u=urlparse(x);x=urlunparse(u._replace(query=urlencode([(k,v) for k,v in parse_qsl(u.query) if k.lower() not in ['apikey','api_key']])))
 return x

def main():
 global KEY
 c=pd.read_csv(P/'artifacts/input/year_end_market_cap_2025.csv');jobs=[]
 for t in c.source_ticker:
  urls={'prices':f'https://api.massive.com/v2/aggs/ticker/{t}/range/1/day/2026-01-02/2026-10-06?adjusted=false&sort=asc&limit=50000','dividends':f'https://api.massive.com/v3/reference/dividends?ticker={t}&ex_dividend_date.gte=2026-01-02&ex_dividend_date.lte=2026-10-06&limit=1000','splits':f'https://api.massive.com/v3/reference/splits?ticker={t}&execution_date.gte=2026-01-02&execution_date.lte=2026-10-06&limit=1000'}
  for k,u in urls.items():
   p=O/'sources'/f'massive_{t}_{k}.json'
   if not p.exists():jobs.append((u,p))
 if not jobs:return
 countries=[]
 for u in ['https://ipinfo.io/json','https://www.cloudflare.com/cdn-cgi/trace']:
  r=requests.get(u,timeout=25);r.raise_for_status();countries.append(r.json().get('country') if 'ipinfo' in u else dict(v.split('=',1) for v in r.text.splitlines() if '=' in v).get('loc'))
 if countries!=['SG','SG']:raise RuntimeError('Singapore egress required; credential not loaded')
 for line in Path('/Users/zhangboyi/Documents/TBIC/tbic/.env').read_text().splitlines():
  k,sep,v=line.strip().partition('=')
  if sep and k.removeprefix('export ')=='MASSIVE_API_KEY':KEY=v.strip().strip('\"\'')
 assert KEY
 def fetch(job):
  url,p=job;pages=[];first=url;seen=set()
  if not hasattr(local,'s'):local.s=requests.Session()
  while url:
   assert urlparse(url).hostname=='api.massive.com' and url not in seen;seen.add(url)
   for attempt in range(5):
    try:r=local.s.get(url,headers={'Authorization':'Bearer '+KEY},timeout=40,allow_redirects=False)
    except requests.RequestException:
     if attempt==4:raise RuntimeError('Network request failed') from None
     time.sleep(2**attempt);continue
    if r.status_code in [429,500,502,503,504]:time.sleep(2**attempt);continue
    if r.status_code!=200:raise RuntimeError(f'HTTP {r.status_code}')
    body=clean(r.json());pages.append(body);url=body.get('next_url');break
   else:raise RuntimeError('Retry exhausted')
  p.write_text(json.dumps({'request_url':first,'http_status':200,'pages':pages}));return p.name
 with ThreadPoolExecutor(max_workers=4) as ex:
  for i,_ in enumerate(ex.map(fetch,jobs),1):
   if i%15==0:print('Cached',i,'/',len(jobs),flush=True)
if __name__=='__main__':main()

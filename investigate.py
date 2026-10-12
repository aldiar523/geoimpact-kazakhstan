#!/usr/bin/env python3
"""Evidence-gathering stage for GeoImpact. Reporting ≠ official verification or causation.

Corroborating outlets and official-source search leads are collected for human review.
No event is automatically marked 'verified' by the mere presence of search results.
"""
import json,re,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import defaultdict
from urllib.parse import urlparse
from atlas import assets
from monitor import parse,date
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
STOP={'the','and','for','with','from','that','this','will','after','into','over','amid','about','says','said','new','news','2026','2025','2024','has','have','are','was','its','their','at','of','to','on','in','a','an','as','by','us','uk','is','it','a'}
def tokens(text):
 return set(x for x in re.findall(r'[a-z0-9]{3,}',(text or '').lower()) if x not in STOP)
def similarity(a,b):
 A,B=tokens(a),tokens(b)
 return len(A&B)/len(A|B) if A and B else 0
def outlet(event):
 # Google News search often appends an original publisher in its title.
 t=event.get('title','')
 source=event.get('source','')
 return t.rsplit(' - ',1)[-1].casefold().strip() if source.startswith('Google News') and ' - ' in t else source.casefold()
def corroborate(events,target):
 out=[];seen=set()
 for other in events:
  if other.get('id')==target.get('id'):continue
  if other.get('sector')!=target.get('sector'):continue
  a=date(target.get('published',''));b=date(other.get('published',''))
  if not a or not b or abs((a-b).total_seconds())>72*3600:continue
  overlap=similarity(target.get('title','').split(' - ')[0],other.get('title','').split(' - ')[0])
  if overlap < .53:continue
  publisher=outlet(other)
  if publisher==outlet(target) or publisher in seen:continue
  seen.add(publisher)
  out.append({'publisher':publisher,'title':other.get('title'),'url':other.get('url'),'similarity_heuristic':round(overlap,2)})
 return out[:5]
def official_leads(event,timeout=7):
 matches=event.get('matches') or []
 if not matches:return []
 # A site-restricted original document search is a research lead, not evidence by itself.
 asset=matches[0]
 domain=urlparse(asset.get('source_url','')).hostname or ''
 if not domain or domain.endswith('google.com'):return []
 name=asset.get('asset','')
 hints=tokens(event.get('title','')) & tokens(name)
 # Search distinctive identifiers; weak generic names are ignored.
 query='site:'+domain+' '+(' '.join(sorted(hints)[:4]) if hints else name.split('(')[0][:55])
 url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query+' when:30d','hl':'en-US','gl':'US','ceid':'US:en'})
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'GeoImpactKZResearch/0.4'})
  with urllib.request.urlopen(req,timeout=timeout) as conn:items=parse(conn.read(750000))
 except Exception:return []
 result=[]
 for title,link,summary,published in items:
  # Avoid calling unrelated older corporate material confirmation of a current event.
  if not(tokens(title)&tokens(event.get('title',''))):continue
  result.append({'title':title,'url':link,'source_domain':domain,'published':published,
                 'status':'Official-domain search lead — requires original-document inspection'})
  if len(result)>=3:break
 return result
def review(event,reviews):
 r=reviews.get(event['id'])
 if not isinstance(r,dict):return None
 reviewer=str(r.get('reviewer','')).strip()
 note=str(r.get('note','')).strip()
 link=str(r.get('original_source_url','')).strip()
 if not reviewer or len(note)<20 or not link.startswith('https://'):return None
 return {'status':'Human reviewed (factual event only)','reviewer':reviewer,'note':note,
         'original_source_url':link,'reviewed_at':r.get('reviewed_at')}
def main():
 p=DATA/'feed.json';feed=json.loads(p.read_text())
 events=feed.get('events') or []
 try:reviews=json.loads((DATA/'reviews.json').read_text())
 except Exception:reviews={}
 reviews=reviews if isinstance(reviews,dict) else {}
 investigated=[];searched=0
 # Only strong, recent named asset cases get extra official-source searches.
 eligible=sorted([e for e in events if e.get('matches') and date(e.get('published',''))],
                 key=lambda e:e['published'],reverse=True)
 eligible_ids={e['id'] for e in eligible[:10]}
 for event in events:
  similar=corroborate(events,event)
  leads=official_leads(event) if event['id'] in eligible_ids else []
  if event['id'] in eligible_ids:searched+=1
  human=review(event,reviews)
  stage=(event.get('source_status') if event.get('source_status') else
         'Human-reviewed factual event' if human else
         'Primary-source research leads found' if leads else
         'Corroborated reporting; primary evidence missing' if similar else
         'Single news candidate; primary evidence missing')
  item={'event_id':event['id'],'headline':event['title'],'investigation_stage':stage,
        'independent_reporting_leads':similar,'original_source_leads':leads,'human_review':human,
        'related_dependencies':event.get('matches',[]),
        'not_established':['Measured Kazakhstan impact','Causal attribution','Impact probability','Impact severity'],
        'next_action':('Review original primary document and specific Kazakhstan pathway' if leads else
                       'Locate primary source and independent corroboration')}
  investigated.append(item)
  event['investigation_stage']=stage
  event['evidence_sources_count']=1+len(similar)
  event['human_reviewed']=bool(human)
 feed['investigation_generated_at']=datetime.now(timezone.utc).isoformat()
 feed['classification']='Screened reporting; automatic search leads are NOT verification'
 p.write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n')
 (DATA/'investigations.json').write_text(json.dumps({'generated_at':feed['investigation_generated_at'],
     'method':'Automated reporting comparison and original-source search leads; human decision required',
     'cases':investigated},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'investigated':len(investigated),'official_searches':searched,
                   'corroborated':sum(bool(c['independent_reporting_leads']) for c in investigated),
                   'official_leads':sum(bool(c['original_source_leads']) for c in investigated),
                   'human_reviewed':sum(bool(c['human_review']) for c in investigated)}))
if __name__=='__main__':main()

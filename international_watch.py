#!/usr/bin/env python3
"""Global shock watch: distinct foreign reported developments and hypothetical KZ pathways.

Separated from the verified/relevance-assessed local event feed. No effect-size,
probability, or independent source verification is implied by inclusion.
"""
import json,re,collections
from datetime import datetime,timezone
from pathlib import Path
from event_gate import cluster,EDITORIAL,BACKGROUND,DIRECT_ACT,SIGNIFICANT_MOVE,canonical_title
from monitor import EXTERNAL_EXPOSURES,EXTERNAL_CHANGE,date
DATA=Path(__file__).resolve().parent/'data'
INTEREST_RE=re.compile(r'\b(opec|oil price|brent|tanker|hormuz|shipping|port|freight|'
 r'export controls?|sanction|tariff|critical|minerals?|rare earths?|uranium|copper|semiconductor|'
 r'power grid|electricity|gas pipeline|border|customs|financial|banking|'
 r'food prices|grain|wheat|water|reservoir|drought|rail|trade route|'
 r'supply chain|freight|currency|interest rates?|fertiliz)\b',re.I)
DISCUSSION_ONLY=re.compile(r'\b(could|should|would|might|may|forecast|predicted|'
 r'explainer|commentary|opinion|analysis|will it|how might)\b',re.I)
GENERIC=re.compile(r'\b(what you need to know|weekly roundup|latest updates|'
 r'prices today|market preview|how to invest|stocks to buy|'
 r'daily price prediction)\b',re.I)
PIVOTAL=re.compile(r'\b(sanction|ban|export control|hormuz|pipeline|'
 r'crude oil|uranium|rare earth|shipping|power grid|'
 r'copper|wheat|oil production|freight|tariff)\b',re.I)
def exposure(article):
 t=canonical_title(article.get('title',''))
 summary=article.get('summary','')
 txt=t+' '+summary[:260]
 if GENERIC.search(t) or EDITORIAL.search(t) or BACKGROUND.search(t):
  return None
 if re.search(r'\bkazakhstan\b|\bkazakh\b|\bastana\b|\balmaty\b',t,re.I):
  return None
 if not (DIRECT_ACT.search(t) or SIGNIFICANT_MOVE.search(t) or EXTERNAL_CHANGE.search(t)):
  return None
 channels=[(label,sect,mechanism) for label,pat,sect,mechanism in EXTERNAL_EXPOSURES
           if re.search(pat,txt)]
 if not channels or not INTEREST_RE.search(txt):return None
 country=article.get('country','Unknown')
 if country in ('Kazakhstan',):return None
 if DISCUSSION_ONLY.search(t) and not (DIRECT_ACT.search(t) or EXTERNAL_CHANGE.search(t)):
  return None
 high=bool(PIVOTAL.search(t) and (DIRECT_ACT.search(t) or EXTERNAL_CHANGE.search(t)))
 # This is *plausibility of a KZ link*, not probability/severity of consequences.
 interest='strong candidate' if high else 'plausible candidate'
 return {'channels':channels,'interest':interest,
         'reason':'; '.join(dict.fromkeys(k[2] for k in channels[:3])),
         'country':country}
def main():
 feed=json.loads((DATA/'feed.json').read_text())
 review=json.loads((DATA/'events.json').read_text()) if (DATA/'events.json').exists() else {}
 used={u for g in review.get('events',[]) for u in g.get('article_ids',[])}
 selected=[];counts=collections.Counter()
 for e in feed.get('events',[]):
  if e.get('id') in used:continue
  x=exposure(e)
  if x is None:continue
  item=dict(e)
  item['watch_level']=x['interest']
  item['watch_exposure']='Hypothesised Kazakhstan connection, NOT a measured domestic effect'
  item['reason']=x['reason']
  item['exposure_channels']=[{'name':label,'sector':sec,'mechanism':mechanism,'evidence_status':'Hypothesis to test'}
                           for label,sec,mechanism in x['channels']]
  item['triage']={'included':True,'kind':'reported international development',
                  'priority':'medium' if x['interest']=='strong candidate' else 'review',
                  'score':5 if x['interest']=='strong candidate' else 3,
                  'reason':x['reason']+'; no explicit Kazakhstan impact identified'}
  item['direction']='Unknown';item['overall_effect']='unknown'
  item['impact_channels']=[];item['probability']='Unassessed';item['severity']=None
  selected.append(item)
  counts[item.get('sector') or 'Other']+=1
 groups=cluster(selected)
 # Balanced selection by sector and origin; prevents one chokepoint dominating globe.
 selected_groups=[];seen_sectors=collections.Counter();seen_countries=collections.Counter()
 for g in groups:
  sect=g.get('sector','Other');place=g.get('country','Unknown')
  if seen_sectors[sect]>=35 or seen_countries[place]>=18:continue
  selected_groups.append(g);seen_sectors[sect]+=1;seen_countries[place]+=1
  if len(selected_groups)>=160:break
 for g in selected_groups:
  g['watch_level']='strong candidate' if g['triage']['priority']=='medium' else 'plausible candidate'
  g['watch_exposure']='External development, potential KZ transmission not independently established'
  g['overall_effect']='unknown';g['direction']='Unknown'
  g['impact_channels']=[]
  g['hypothesis_not_impact']=True
 # Hand-inspected public/institutional cases supplement incomplete RSS sampling.
 try:curated=json.loads((DATA/'curated_global.json').read_text()).get('records',[])
 except Exception:curated=[]
 for item in curated:
  e=dict(item)
  e['id']=item['id'];e['tier']='Source-inspected international watch'
  e['article_count']=1+len(item.get('other_sources',[]))
  e['source_status']=item.get('status','Source review pending')
  e['hypothesis_not_impact']=True
  e['reason']=item['reason'];e['direction']='Unknown';e['overall_effect']='unknown'
  e['impact_channels']=[];e['severity']=None;e['probability']='Unassessed'
  e['exposure_channels']=item.get('exposure_channels',[])
  e['related_sources']=[{'title':item['title'],'source':item['source'],'url':item['url'],
                         'published':item['published']}]+[
      {'title':x['label'],'source':x['label'],'url':x['url'],'published':item['published']}
      for x in item.get('other_sources',[])]
  e['triage']={'included':True,'kind':'international external event or decision',
               'score':6,'priority':'medium' if item.get('watch_level')=='strong candidate' else 'review',
               'reason':item['reason']}
  selected_groups=[g for g in selected_groups if g.get('id')!=e['id']]
  selected_groups.append(e)
 selected_groups.sort(key=lambda x:x.get('published',''),reverse=True)
 data={'generated_at':datetime.now(timezone.utc).isoformat(),
       'status':'Reported foreign developments for investigator screening; Kazakhstan effects hypothetical',
       'disclaimer':'Watch level is screening attention, not impact magnitude or likelihood',
       'source_articles':len(selected),'groups':selected_groups}
 (DATA/'international_watch.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'reviewed_foreign_articles':len(selected),'international_groups':len(selected_groups),
                   'sector_groups':dict(seen_sectors),'countries':dict(seen_countries)},ensure_ascii=False))
if __name__=='__main__':main()

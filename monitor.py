#!/usr/bin/env python3
"""GeoImpact KZ: public RSS news candidate screening; not verification."""
import json,re,html,urllib.request,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).parent;DATA=ROOT/'data'
RAW="""BBC World|Global|https://feeds.bbci.co.uk/news/world/rss.xml
Al Jazeera|Global|https://www.aljazeera.com/xml/rss/all.xml
Guardian World|Global|https://www.theguardian.com/world/rss
DW World|Global|https://rss.dw.com/rdf/rss-en-all
BBC US|US|https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml
BBC Europe|Europe/UK|https://feeds.bbci.co.uk/news/world/europe/rss.xml
BBC UK|Europe/UK|https://feeds.bbci.co.uk/news/uk/rss.xml
BBC China|China|https://feeds.bbci.co.uk/news/world/asia/china/rss.xml
BBC India|India|https://feeds.bbci.co.uk/news/world/asia/india/rss.xml
BBC Asia|ASEAN|https://feeds.bbci.co.uk/news/world/asia/rss.xml
ABC Asia Pacific|ASEAN|https://www.abc.net.au/news/feed/45910/rss.xml
BBC Africa|Africa|https://feeds.bbci.co.uk/news/world/africa/rss.xml
BBC Latin America|LATAM|https://feeds.bbci.co.uk/news/world/latin_america/rss.xml
BBC Middle East|MENA|https://feeds.bbci.co.uk/news/world/middle_east/rss.xml
BBC Business|Global|https://feeds.bbci.co.uk/news/business/rss.xml
BBC Technology|Global|https://feeds.bbci.co.uk/news/technology/rss.xml
BBC Environment|Global|https://feeds.bbci.co.uk/news/science_and_environment/rss.xml
Google News Central Asia|Central Asia|https://news.google.com/rss/search?q=Kazakhstan+OR+Uzbekistan+OR+Kyrgyzstan+OR+Tajikistan+OR+Turkmenistan+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News Eurasia|Russia/Eurasia|https://news.google.com/rss/search?q=Russia+pipeline+OR+sanctions+OR+Kazakhstan+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News East Asia|East Asia|https://news.google.com/rss/search?q=Japan+OR+South+Korea+semiconductor+OR+critical+mineral+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News ASEAN|ASEAN|https://news.google.com/rss/search?q=ASEAN+OR+Vietnam+OR+Indonesia+OR+Malaysia+OR+Singapore+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News Africa|Africa|https://news.google.com/rss/search?q=Africa+mining+OR+oil+exports+OR+shipping+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News LATAM|LATAM|https://news.google.com/rss/search?q=Latin+America+mining+OR+oil+OR+commodity+exports+when%3A7d&hl=en-US&gl=US&ceid=US:en
Google News MENA|MENA|https://news.google.com/rss/search?q=Middle+East+oil+OR+Hormuz+OR+Red+Sea+shipping+when%3A7d&hl=en-US&gl=US&ceid=US:en"""
SOURCES=[tuple(x.split('|',2)) for x in RAW.splitlines()]
ASSETS=[('Oil','CPC pipeline','cpc|kropotkinskaya|novorossiysk|caspian pipeline|tengiz'),('Mining','Kazatomprom','kazatomprom|uranium one|sulphuric acid|sulfuric acid'),('Electricity','Central Asian grid','kegoc|syrdarya power|uzbekistan power grid'),('Water','Transboundary rivers','ili river|irtysh|syr darya|syrdarya|chu talas'),('Digital','Cross-border telecom','kazakhtelecom|transtelecom|caspilink|trans-caspian cable'),('Mining','Copper smelting and mining','kazzinc|kazchrome|kaz minerals|aktogay|bozshakol')]
GLOBAL=[('Oil','brent crude|global oil price|world oil prices|opec production|opec output|strait of hormuz'),('Mining','global uranium price|uranium spot price|global copper price'),('Transport','suez canal blocked|red sea shipping disruption|caspian pipeline shutdown')]
LOC={'Russia':[61,105],'China':[35,104],'Uzbekistan':[41,64],'India':[21,79],'Iran':[32,54],'United States':[38,-97],'Ukraine':[49,32],'Turkey':[39,35],'Germany':[51,10],'United Kingdom':[54,-2],'Kazakhstan':[48,67],'Afghanistan':[34,67],'Saudi Arabia':[24,45],'Israel':[31.5,35],'Azerbaijan':[40,48]}
def now():return datetime.now(timezone.utc)
def date(v):
 try:return parsedate_to_datetime(v).astimezone(timezone.utc)
 except Exception:
  try:return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
  except Exception:return None
def clean(v):return re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',html.unescape(v or ''))).strip()
def field(item,tag):
 for el in item.iter():
  if el.tag.rsplit('}',1)[-1].lower()==tag:return ''.join(el.itertext()).strip()
 return ''
def parse(blob):
 result=[]
 for el in ET.fromstring(blob).iter():
  if el.tag.rsplit('}',1)[-1].lower() not in ('item','entry'):continue
  title=clean(field(el,'title'));url=field(el,'link')
  if not url:
   for child in el:
    if child.tag.rsplit('}',1)[-1]=='link' and child.get('href'):url=child.get('href');break
  summ=clean(field(el,'description') or field(el,'summary') or field(el,'content'))
  published=field(el,'pubdate') or field(el,'published') or field(el,'updated')
  if title and url.startswith(('https://','http://')):result.append((title,url,summ,published))
 return result
def classify(title,summary):
 t=(title+' '+summary[:400]).lower()
 direct=bool(re.search(r'\bkazakhstan\b|\bkazakh\b|\bastana\b|\balmaty\b',t))
 hits=[(s,a) for s,a,terms in ASSETS if any(k in t for k in terms.split('|'))]
 markets=[s for s,terms in GLOBAL if any(k in t for k in terms.split('|'))]
 # Require a named asset, an explicit Kazakhstan economic exposure, or a genuine global-market trigger.
 contextual=bool(re.search(r'\btrade\b|\bimport\w*\b|\bexport\w*\b|\benergy\b|\boil\b|\bmining\b|\buranium\b|\belectricity\b|\bwater\b|\bmigration\b|\binvest\w*\b|\bfinanc\w*\b|\btransport\b|\bpipeline\b|\brail\b|\bsanction\w*\b|\bdigital\b|\bsupply\b|\bpolicy\b|\bborder\b|\btariff\w*\b',t))
 if not (hits or markets or (direct and contextual)):return None
 sector=(hits[0][0] if hits else markets[0] if markets else 'Cross-sector')
 tier='Named asset match' if hits else 'Kazakhstan mentioned' if direct else 'Systemic-market candidate'
 country=next((c for c in LOC if c.lower() in t),'Unknown')
 if country=='Unknown' and 'cpc' in t:country='Russia'
 if country=='Unknown' and 'hormuz' in t:country='Iran'
 latlon=LOC.get(country,[None,None])
 direction='Unknown'
 if re.search(r'\battack\b|\bshortage\b|\boutage\b|\bdisrupt\w*\b|\bclosed\b|\bsanction\w*\b',t):direction='Potential negative'
 if re.search(r'\bnew export route\b|\broute opens\b|\bnew capacity\b',t):direction='Potential positive'
 return dict(sector=sector,country=country,lat=latlon[0],lon=latlon[1],direction=direction,tier=tier,
             matches=[{'asset':a,'sector':s} for s,a in hits],probability='Unassessed',severity=None,
             reason='; '.join(a for _,a in hits) if hits else ('Kazakhstan explicitly mentioned' if direct else 'Potential global market exposure'))
def collect(src):
 name,region,url=src
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'GeoImpactKZResearch/0.3','Accept':'application/xml,application/rss+xml,text/xml,*/*'})
  with urllib.request.urlopen(req,timeout=9) as r:body=r.read(1800000)
  return (name,region,parse(body),None)
 except Exception as err:return (name,region,[],str(err)[:150])
def main():
 DATA.mkdir(exist_ok=True)
 try:prior=json.loads((DATA/'feed.json').read_text())['events']
 except Exception:prior=[]
 start=now(); cutoff=start-timedelta(days=30)
 byid={}
 for x in prior:
  if not date(x.get('published','')) or date(x['published'])<cutoff:continue
  updated=classify(x.get('title',''),x.get('summary',''))
  if updated is not None:byid[x['id']]={**x,**updated}
 health=[];added=0
 with ThreadPoolExecutor(max_workers=8) as pool:
  for task in as_completed([pool.submit(collect,s) for s in SOURCES]):
   name,region,news,err=task.result()
   health.append(dict(source=name,region=region,ok=err is None,count=len(news),error=err))
   if err:continue
   for title,url,summary,pub in news:
    d=date(pub)
    if not d or d<start-timedelta(days=14) or d>start+timedelta(days=1):continue
    c=classify(title,summary)
    if c is None:continue
    uid=hashlib.sha256(url.encode()).hexdigest()[:18]
    if uid not in byid:
     byid[uid]=dict(id=uid,title=title[:220],url=url,summary=summary[:350],published=d.isoformat(),source=name,region=region,
                    verification='News candidate — not primary-source verified',detected_at=start.isoformat(),**c)
     added+=1
 events=sorted(byid.values(),key=lambda v:v['published'],reverse=True)[:300]
 good=sum(x['ok'] for x in health)
 feed=dict(generated_at=start.isoformat(),classification='Screened news reporting — unverified candidates',events=events)
 status=dict(last_poll=start.isoformat(),interval_hours=12,sources_configured=len(SOURCES),sources_successful=good,
             source_health=sorted(health,key=lambda x:x['source']),candidate_count=len(events),new_candidates=added,
             error='All sources failed; do not interpret an empty feed as no developments' if good==0 else None)
 (DATA/'feed.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n')
 (DATA/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'successful':good,'configured':len(SOURCES),'new':added,'stored':len(events),'failed':[x['source'] for x in health if not x['ok']]},ensure_ascii=False))
if __name__=='__main__':main()

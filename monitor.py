#!/usr/bin/env python3
"""GeoImpact KZ: public RSS news candidate screening; not verification."""
import json,re,html,urllib.request,urllib.parse,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor,as_completed
from atlas import match_assets
from impact_model import decorate
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
BASE_SOURCES=[tuple(x.split('|',2)) for x in RAW.splitlines()]
# Dated search queries extend RSS back to the entire previous month; two half-month
# windows reduce search-feed result truncation. Source names explain the origin.
REVIEW_QUERIES=[
 ('Kazakhstan Economy','Kazakhstan', '"Kazakhstan" (exports OR inflation OR currency OR budget)'),
 ('Kazakhstan Oil','Kazakhstan', '"Kazakhstan" (CPC OR Tengiz OR Kashagan OR oil pipeline)'),
 ('Kazakhstan Mining','Kazakhstan', '"Kazakhstan" (uranium OR Kazatomprom OR critical minerals)'),
 ('Kazakhstan China','China', '"Kazakhstan" "China" (trade OR tariff OR rail OR investment)'),
 ('Kazakhstan Russia','Russia/Eurasia', '"Kazakhstan" "Russia" (sanctions OR transit OR energy)'),
 ('Kazakhstan EU','Europe/UK', '"Kazakhstan" (EU OR Europe) (trade OR critical minerals OR sanctions)'),
 ('Kazakhstan US','US', '"Kazakhstan" "United States" (tariffs OR sanctions OR investment)'),
 ('Kazakhstan Central Asia','Central Asia', '"Kazakhstan" (Uzbekistan OR Kyrgyzstan OR Tajikistan) (water OR power OR trade)'),
 ('Kazakhstan Caspian','Central Asia', '"Kazakhstan" (Caspian OR Azerbaijan OR corridor OR logistics)'),
 ('Kazakhstan Internet','Central Asia', '"Kazakhstan" (internet OR fibre OR telecom OR cyber)'),
 ('Kazakhstan Migration','Central Asia', '"Kazakhstan" (migration OR remittances OR refugees)'),
 ('Kazakhstan MENA','MENA', '"Kazakhstan" (Iran OR Hormuz OR Middle East OR oil price)'),
 ('Kazakhstan India','India', '"Kazakhstan" "India" (trade OR investment OR energy)'),
 ('Kazakhstan ASEAN','ASEAN', '"Kazakhstan" (ASEAN OR Indonesia OR Vietnam OR Malaysia OR Singapore) (trade OR investment)'),
 ('Kazakhstan Africa','Africa', '"Kazakhstan" (Africa OR Zambia OR Congo) (mining OR trade)'),
 ('Kazakhstan Latin America','LATAM', '"Kazakhstan" (Brazil OR Chile OR Argentina) (trade OR mining)'),
 ('Hormuz Oil','MENA', '"Strait of Hormuz" (oil OR exports OR tanker OR blockade)'),
 ('Oil Market OPEC','Global', 'OPEC (oil production OR oil prices OR exports)'),
 ('Global Brent','Global', '"Brent" (oil prices OR supply shock OR production)'),
 ('Red Sea Supply','MENA', '"Red Sea" (shipping disruption OR oil freight OR supply chain)'),
 ('Global Uranium','Global', '"uranium" (price OR mine disruption OR supply shortage)'),
 ('China Copper','China', '"China" (copper demand OR metal prices OR industrial slowdown)'),
 ('Wheat Fertilizer','Global', 'global (wheat OR fertilizer) (prices OR export ban OR shortage)'),
 ('Central Asia Grid','Central Asia', '"Central Asia" (grid outage OR electricity shortage OR power interconnection)'),
 ('Central Asia Water','Central Asia', '"Central Asia" (water shortage OR irrigation OR reservoir)'),
 ('Russia Oil Transit','Russia/Eurasia', '"Russia" (pipeline disruption OR oil export sanctions OR CPC)'),
]
def build_sources(reference=None):
 today=(reference or datetime.now(timezone.utc)).date()
 first=today-timedelta(days=30)
 halfway=today-timedelta(days=15)
 # Search-feed queries are provisional retrieval tools, not complete news archives.
 sources=list(BASE_SOURCES)
 for label,region,q in REVIEW_QUERIES:
  for lo,hi,part in [(first,halfway,'older'),(halfway,today+timedelta(days=1),'recent')]:
   query=q+' after:'+lo.isoformat()+' before:'+hi.isoformat()
   url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'en-US','gl':'US','ceid':'US:en'})
   sources.append(('Archive '+label+' '+part,region,url))
 return sources
SOURCES=build_sources()
SECTOR_TAGS=[
 ('Oil',r'\boil\b|\bcrude\b|\bpetroleum\b|\bdiesel\b|\bfuel\b|\bpipeline\b|\bcpc\b|\btengiz\b|\bkashagan\b|\brefiner\w*\b'),
 ('Mining',r'\buranium\b|\bmining\b|\bmineral\w*\b|\bcopper\b|\brare earth\b|\bmetallurg\w*\b|\bzinc\b'),
 ('Electricity',r'\belectricity\b|\bpower grid\b|\bpower outage\b|\binterconnector\b'),
 ('Water',r'\bwater\b|\briver\b|\bdam\b|\breservoir\b|\birrigat\w*\b'),
 ('Transport',r'\brail\w*\b|\btransit\b|\bcorridor\b|\bshipping\b|\bport\b|\blogistic\w*\b|\baviation\b|\bflight\b'),
 ('Food',r'\bwheat\b|\bgrain\b|\bfood\b|\bfertiliz\w*\b|\bflour\b|\bagricultur\w*\b|\bseed export\b'),
 ('Finance',r'\bbank\w*\b|\bcurrency\b|\btenge\b|\bfiscal\b|\binflation\b|\bpayment\w*\b|\binvestment\b|\bdebt\b|\bforex\b'),
 ('Digital',r'\bdigital\b|\binternet\b|\btelecom\b|\bfibre\b|\bfiber\b|\bai\b|\bcyber\b|\bdata cent\w*\b'),
 ('Migration',r'\bmigrat\w*\b|\bremittance\w*\b|\bworker mobility\b'),
 ('Trade',r'\btrade\b|\bexport\w*\b|\bimport\w*\b|\btariff\w*\b|\bsanction\w*\b|\bcustoms\b')
]
def sector_from_text(text):
 for name,pattern in SECTOR_TAGS:
  if re.search(pattern,text):return name
 return 'Cross-sector'
ASSETS=[('Oil','CPC pipeline','cpc|kropotkinskaya|novorossiysk|caspian pipeline|tengiz'),('Mining','Kazatomprom','kazatomprom|uranium one|sulphuric acid|sulfuric acid'),('Electricity','Central Asian grid','kegoc|syrdarya power|uzbekistan power grid'),('Water','Transboundary rivers','ili river|irtysh|syr darya|syrdarya|chu talas'),('Digital','Cross-border telecom','kazakhtelecom|transtelecom|caspilink|trans-caspian cable'),('Mining','Copper smelting and mining','kazzinc|kazchrome|kaz minerals|aktogay|bozshakol')]
GLOBAL=[('Oil','brent crude|global oil price|world oil prices|opec|strait of hormuz'),('Mining','global uranium price|uranium spot price|global copper price'),('Transport','suez canal blocked|red sea shipping disruption|caspian pipeline shutdown')]
LOC={'Russia':[61,105],'China':[35,104],'Uzbekistan':[41,64],'India':[21,79],'Iran':[32,54],'United States':[38,-97],
'Ukraine':[49,32],'Turkey':[39,35],'Germany':[51,10],'United Kingdom':[54,-2],'Kazakhstan':[48,67],
'Afghanistan':[34,67],'Saudi Arabia':[24,45],'Israel':[31.5,35],'Azerbaijan':[40,48],
'Kyrgyzstan':[41.2,74.7],'Tajikistan':[38.8,71],'Turkmenistan':[39.1,59.4],
'Singapore':[1.35,103.8],'Indonesia':[-2,118],'Malaysia':[4.2,102],'Vietnam':[16,108],
'Thailand':[15,101],'Philippines':[12,122],'Pakistan':[30,69],'UAE':[24,54],
'United Arab Emirates':[24,54],'Iraq':[33,44],'Qatar':[25.3,51.2],'Oman':[21.5,56],
'France':[46,2],'Italy':[42.5,12.5],'Belgium':[50.7,4.5],'Poland':[52,19],'Romania':[46,25],
'Georgia':[42,43.5],'Armenia':[40,45],'Netherlands':[52.1,5.3],'Switzerland':[47,8.2],
'Japan':[36,138],'South Korea':[36,128],'Mongolia':[47,103],'Taiwan':[23.8,121],
'Brazil':[-10,-55],'Argentina':[-34,-64],'Chile':[-33,-71],'Mexico':[23,-102],
'Canada':[56,-106],'Australia':[-25,133],'South Africa':[-29,24],'Nigeria':[9,8],
'Egypt':[27,30],'Ethiopia':[9,40],'Kenya':[0.1,38],'Zambia':[-13.1,27.9],
'Democratic Republic of Congo':[-3,23],'DR Congo':[-3,23],'Congo':[-3,23]}
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
 matched=match_assets(t)
 hits=[(a['sector'],a['name']) for a in matched]
 markets=[s for s,terms in GLOBAL if any(k in t for k in terms.split('|'))]
 # Require a named asset, an explicit Kazakhstan economic exposure, or a genuine global-market trigger.
 contextual=bool(re.search(r'\btrade\b|\bimport\w*\b|\bexport\w*\b|\benergy\b|\boil\b|\bmining\b|\buranium\b|\belectricity\b|\bwater\b|\bmigration\b|\binvest\w*\b|\bfinanc\w*\b|\btransport\b|\bpipeline\b|\brail\b|\bsanction\w*\b|\bdigital\b|\bsupply\b|\bpolicy\b|\bborder\b|\btariff\w*\b',t))
 if not (hits or markets or (direct and contextual)):return None
 # Suppress event types lacking a documented exposure pathway, rather than
 # retaining every otherwise-irrelevant Kazakhstan mention.
 if not hits and not markets and direct and re.search(r'\bconcert\b|\bfootball\b|\bfilm festival\b|\bfashion show\b|\bforex trading legal\b|\bhow to trade forex\b',t):return None
 sector=(hits[0][0] if hits else markets[0] if markets else sector_from_text(t))
 tier='Named asset match' if hits else 'Kazakhstan mentioned' if direct else 'Systemic-market candidate'
 # Resolve source geography from the headline, prioritizing an international
 # counterpart if a Kazakhstan partnership mentions both countries.
 h=title.lower()
 mentioned_title=[c for c in LOC if re.search(r'(?<!\w)'+re.escape(c.lower())+r'(?!\w)',h)]
 mentioned_summary=[c for c in LOC if re.search(r'(?<!\w)'+re.escape(c.lower())+r'(?!\w)',t)]
 foreign_title=[c for c in mentioned_title if c!='Kazakhstan']
 foreign_summary=[c for c in mentioned_summary if c!='Kazakhstan']
 if foreign_title:country=foreign_title[0]
 elif mentioned_title:country=foreign_summary[0] if (foreign_summary and
       re.search(r'\bcooperat\w*\b|\bbilateral\b|\btrade ties\b|\bagreement\b|\bpartnership\b',t)) else mentioned_title[0]
 elif foreign_summary:country=foreign_summary[0]
 else:country=mentioned_summary[0] if mentioned_summary else 'Unknown'
 if country=='Unknown' and 'cpc' in t:country='Russia'
 if country=='Unknown' and 'hormuz' in t:country='Iran'
 latlon=LOC.get(country,[None,None])
 direction='Unknown'
 if re.search(r'\battack\b|\bshortage\b|\boutage\b|\bdisrupt\w*\b|\bclosed\b|\bsanction\w*\b',t):direction='Potential negative'
 if re.search(r'\bnew export route\b|\broute opens\b|\bnew capacity\b',t):direction='Potential positive'
 return dict(sector=sector,country=country,lat=latlon[0],lon=latlon[1],direction=direction,tier=tier,
             matches=[{'asset':a['name'],'asset_id':a['id'],'sector':a['sector'],'source_url':a['source_url'],'external_counterpart':a['external_counterpart']} for a in matched],probability='Unassessed',severity=None,
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
  if updated is not None:byid[x['id']]=decorate({**x,**updated})
 health=[];added=0
 with ThreadPoolExecutor(max_workers=8) as pool:
  for task in as_completed([pool.submit(collect,s) for s in SOURCES]):
   name,region,news,err=task.result()
   health.append(dict(source=name,region=region,ok=err is None,count=len(news),error=err))
   if err:continue
   for title,url,summary,pub in news:
    d=date(pub)
    if not d or d<start-timedelta(days=30) or d>start+timedelta(days=1):continue
    c=classify(title,summary)
    if c is None:continue
    c=decorate({**c,'title':title,'summary':summary})
    uid=hashlib.sha256(url.encode()).hexdigest()[:18]
    if uid not in byid:
     byid[uid]=dict(id=uid,title=title[:220],url=url,summary=summary[:350],published=d.isoformat(),source=name,region=region,
                    verification='News candidate — not primary-source verified',detected_at=start.isoformat(),**{k:v for k,v in c.items() if k not in ('title','summary')})
     added+=1
 events=sorted(byid.values(),key=lambda v:v['published'],reverse=True)[:800]
 good=sum(x['ok'] for x in health)
 feed=dict(generated_at=start.isoformat(),lookback_start=cutoff.date().isoformat(),lookback_end=start.date().isoformat(),
 classification='30-day candidate backfill; not exhaustive or independently verified',events=events)
 status=dict(last_poll=start.isoformat(),interval_hours=12,history_window_days=30,sources_configured=len(SOURCES),sources_successful=good,
             source_health=sorted(health,key=lambda x:x['source']),candidate_count=len(events),new_candidates=added,
             error='All sources failed; do not interpret an empty feed as no developments' if good==0 else None)
 (DATA/'feed.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n')
 (DATA/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'successful':good,'configured':len(SOURCES),'new':added,'stored':len(events),'failed':[x['source'] for x in health if not x['ok']]},ensure_ascii=False))
if __name__=='__main__':main()

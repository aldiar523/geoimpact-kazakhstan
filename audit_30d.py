#!/usr/bin/env python3
"""Transparent rolling 30-day coverage/quality audit for GeoImpact research."""
import json,re,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent
feed=json.loads((ROOT/'data/feed.json').read_text())
events=feed.get('events',[])
def title_key(t):
 t=re.sub(r'\s+[-–—]\s+[^–—]{2,65}$','',t.lower()).strip()
 return re.sub(r'[^a-z0-9]+',' ',t).strip()
def month_week(e):
 try:return datetime.fromisoformat(e['published']).strftime('%Y-%m-%d')[:7]+' / week '+str((datetime.fromisoformat(e['published']).day-1)//7+1)
 except:return '?'
def example(e):
 return {k:e.get(k) for k in ('published','title','source','sector','country','region','tier','url','id')}
def by(field):
 c=collections.Counter(str(x.get(field,'Unknown')) for x in events)
 return dict(c.most_common())
missinggeo=[x for x in events if x.get('lat') is None or x.get('lon') is None]
direct=[x for x in events if x.get('tier')=='Kazakhstan mentioned']
named=[x for x in events if x.get('tier')=='Named asset match']
systemic=[x for x in events if x.get('tier')=='Systemic-market candidate']
dupes=collections.defaultdict(list)
for e in events:dupes[title_key(e.get('title',''))].append(e)
duplicate_groups=[{'title':k,'count':len(v),'examples':[example(t) for t in v[:3]]} for k,v in dupes.items() if len(v)>1]
weeks=collections.defaultdict(list)
for e in events:weeks[month_week(e)].append(e)
samples={k:[example(e) for e in (sorted(v,key=lambda e:e.get('tier',''))[:12])] for k,v in sorted(weeks.items())}
# False-positive probes: simple transparent textual checks, *not* human judgments.
weak_patterns=r'\bsport\b|\bfootball\b|\bconcert\b|\bfashion\b|\bcelebrity\b|\bfilm festival\b'
potential_noise=[example(e) for e in events if re.search(weak_patterns,e.get('title','').lower())]
report={
 'generated_at':datetime.now(timezone.utc).isoformat(),
 'requested_window':'Rolling prior 30 days (publication timestamps); RSS searches are not exhaustive',
 'window':{'start':feed.get('lookback_start'),'end':feed.get('lookback_end')},
 'screened_articles':len(events),'dated_more_than_14_days':sum((datetime.now(timezone.utc)-datetime.fromisoformat(x['published'])).days>=14 for x in events),
 'earliest':events[-1]['published'] if events else None,'latest':events[0]['published'] if events else None,
 'geolocated':len(events)-len(missinggeo),'unlocated':len(missinggeo),
 'by_tier':by('tier'),'by_sector':by('sector'),'by_region':by('region'),
 'by_country':by('country'),'by_week':{k:len(v) for k,v in sorted(weeks.items())},
 'unlocated_examples':[example(e) for e in missinggeo[:15]],
 'named_asset_examples':[example(e) for e in named[:16]],
 'systemic_examples':[example(e) for e in systemic[:16]],
 'direct_examples':[example(e) for e in direct[:16]],
 'weekly_samples':samples,'possible_duplicates':duplicate_groups[:25],
 'potential_irrelevant_examples':potential_noise[:15],
 'limitations':['No guarantee of complete reporting coverage','Google News results may syndicate identical original reporting',
 'Keyword screening does not validate impact severity or causal effect','Geography may be a headline-based inference',
 'A reporting source, not the affected physical asset, determines the visible marker without location corroboration']
}
(ROOT/'data/review_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['screened_articles','dated_more_than_14_days','geolocated','unlocated','by_tier','by_week']},ensure_ascii=False))

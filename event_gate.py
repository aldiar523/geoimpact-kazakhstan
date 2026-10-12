#!/usr/bin/env python3
"""GeoImpact event gate v0.7: article -> discrete change -> Kazakhstan impact pathway.

Conservative and explainable research screening, NOT factual verification or
causal evidence. Keep original reports in feed.json for completeness/audit.
"""
import collections
import json
import re
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import urlparse
from monitor import date

DATA=Path(__file__).resolve().parent/'data'
STOP={'what','that','this','with','which','will','from','their','after','before','into','about',
      'says','said','more','most','some','news','the','for','and','are','was','were','have',
      'has','been','its','but','oil','price','prices','global','report','kazakhstan','2026',
      'russia','russian','china','chinese','iran','iranian','today','amid','over','that',
      'through','down','rise','rises','fell','fall','increase','decrease','new','supply'}
EDITORIAL=re.compile(
    r'\b(opinion|op-ed|commentary|explainer|analysis|analyst view|what is|why is|how does|'
    r'could it|would it|should (?:we|they)|what if|will it|the case for|'
    r'lessons from|the future of|what to know|a guide to|explained|'
    r'prospects for|long-term outlook)\b|'
    r'\?$|'
    r'\b(is (?:the|a) [\w ]+ (?:really|actually)|'
    r'how [\w ]+ might|'
    r'can [\w ]+ (?:reshape|benefit|gain|transform))\b',re.I)
SPECULATIVE=re.compile(
    r'\b(will|would|could|might|may|plans? to|planning to|'
    r'eyes?|seeks?|consider(?:s|ing)?|'
    r'weighs?|aims? to|expected to|forecast|'
    r'projection|outlook|potential|likely to|'
    r'looking to|set to|proposed|hopes to)\b',re.I)
DIRECT_ACT=re.compile(
    r'\b(attacked?|struck?|hit by|drone strikes?|bombed?|'
    r'explod(?:ed|es|ing)|damag(?:ed|es)|derailed|collaps(?:ed|es)|'
    r'sank|sunk|blocked|closed|reopen(?:ed|s)|'
    r'shut(?:s|ting)? down|shutdown|'
    r'halt(?:ed|s)|suspend(?:ed|s)|resum(?:ed|es)|'
    r'cut(?:s|ting)? (?:production|output|supply|export|flow)|'
    r'outage|blackout|power cut|flood(?:ed|ing)?|drought|'
    r'evacuat(?:ed|ion)|'
    r'impos(?:ed|es)|sanction(?:ed|s)|'
    r'bann(?:ed|ing)|restrict(?:ed|s)|'
    r'entered into force|took effect|comes into force|'
    r'enact(?:ed|s)|ratif(?:ied|ies)|'
    r'sign(?:ed|s) (?:an? |the )?(?:agreement|deal|treaty|contract|memorandum|accord)|'
    r'approv(?:ed|es) (?:an? |the )?(?:agreement|deal|budget|law|contract|tariff)|'
    r'extend(?:ed|s) (?:an? |the )?(?:agreement|deal|sanctions?|ban)|'
    r'launch(?:ed|es) (?:an? |the )?(?:service|project|pipeline|rail|route)|'
    r'open(?:ed|s) (?:an? |the )?(?:pipeline|port|route|plant|rail|factory)|'
    r'begin(?:s|ning)? operation(?:s)?|commission(?:ed|ing)|'
    r'default(?:ed|s)|downgrad(?:ed|es)|upgrad(?:ed|es)|'
    r'raise(?:d|s) (?:tariffs?|interest rates?|export duties)|'
    r'reduc(?:ed|es) (?:tariffs?|interest rates?|export duties)|'
    r'ordered|vetoed|cancelled|terminated|'
    r'production (?:halted|resumed|declined|fell)|'
    r'exports? (?:fell|rose|plunged|jumped|slumped|surged)|'
    r'imports? (?:fell|rose|plunged|jumped|slumped|surged))\b',re.I)
SIGNIFICANT_MOVE=re.compile(
    r'\b(surged|plunged|slumped|collapsed|soared|spiked|tumbled|'
    r'reached (?:a |an )?(?:record|all-time)|'
    r'dropped [1-9][0-9]?%|rose [1-9][0-9]?%|'
    r'fell [1-9][0-9]?%|'
    r'declined [1-9][0-9]?%|'
    r'jumped [1-9][0-9]?%|'
    r'fell below|rose above|'
    r'down [1-9][0-9]?%|up [1-9][0-9]?%)\b',re.I)
BACKGROUND=re.compile(
    r'\b(historical review|annual report|weekly digest|news digest|'
    r'foreign media on|how to|why [\w ]+ matters|'
    r'guide for|latest forecast|'
    r'price prediction|'
    r'overview|in focus|outlook for|'
    r'is [\w ]+ positioned|opportunity for)\b',re.I)
PATHWAYS={
 'asset-linked':'Named Kazakhstan asset, project, corridor or infrastructure is matched',
 'kazakhstan-direct':'Explicit Kazakhstan relationship with an incident or implemented change',
 'systemic-market':'External shock or measurable market dislocation capable of transmitting to Kazakhstan'
}
SHOCK_LOCATION=re.compile(
    r'\b(hormuz|suez|red sea|black sea|caspian|'
    r'novorossiysk|pipeline|strait|port|refiner(?:y|ies)|'
    r'opec|uranium|oil|brent|energy|wheat|fertilizer|'
    r'copper|rare earth|mineral|water|electricity|shipping|'
    r'rail|customs|sanction|tariff|central asian grid)\b',re.I)
MATERIAL_TYPES={
 'disruption':re.compile(r'\b(attacks?|strikes?|explosions?|shutdown|closed|blocked|outage|blackout|'
                          r'haltes?|suspended|damaged|flood|drought|derailed|fire|'
                          r'supply disruption|shortage|mine collapse|production cut|exports? fell)\b',re.I),
 'binding-decision':re.compile(r'\b(entered into force|took effect|imposed|sanctioned|'
                               r'new tariff|export ban|ratified|approved law|'
                               r'extended agreement|signed agreement|'
                               r'signed treaty|ordered|government banned)\b',re.I),
 'measured-dislocation':SIGNIFICANT_MOVE
}
def words(text):
    return set(x for x in re.findall(r'[a-z0-9]{3,}',str(text).lower()) if x not in STOP)
def canonical_title(title):
    text=re.sub(r'\s+[–—-]\s+[^–—]{2,75}$','',str(title)).strip()
    return text
def publisher(event):
    src=event.get('source','')
    title=event.get('title','')
    if src.startswith('Archive ') or src.startswith('Google News'):
        return title.rsplit(' - ',1)[-1].casefold().strip() if ' - ' in title else src.casefold()
    return src.casefold()
def screen(article):
    title=canonical_title(article.get('title',''))
    summary=article.get('summary','')
    prose=title+' '+summary[:220]
    tier=article.get('tier') or ''
    matched=bool(article.get('matches'))
    direct=tier in ('Kazakhstan mentioned','Named asset match','Source-inspected record') or \
           bool(re.search(r'\bkazakhstan\b|\bkazakh\b',prose,re.I))
    market=tier=='Systemic-market candidate'
    editorial=bool(EDITORIAL.search(title) or BACKGROUND.search(title))
    observed=bool(DIRECT_ACT.search(title))
    change=bool(SIGNIFICANT_MOVE.search(title))
    speculative=bool(SPECULATIVE.search(title))
    named_channel=bool(SHOCK_LOCATION.search(prose))
    official=bool(article.get('source_status'))
    reason=[]
    score=0
    if matched:
        score+=4;reason.append('named Kazakhstan dependency')
    if direct:
        score+=2;reason.append('Kazakhstan explicitly exposed')
    if market and named_channel:
        score+=3;reason.append('global commodity or infrastructure channel')
    if official:
        score+=2;reason.append('source-inspected underlying development')
    if observed:
        score+=4;reason.append('concrete reported development')
    if change:
        score+=3;reason.append('measured or sharp change')
    if editorial:
        score-=6;reason.append('commentary, explainer or analysis')
    if speculative and not observed and not change:
        score-=4;reason.append('prospective or speculative, not implemented')
    # 1: actual incident/decision or measured material market development
    if not (observed or change):
        return dict(included=False,reason='No discrete incident, implemented decision, or material measurable change',score=score,kind='background')
    # 2: exclude editorial with no definite observed trigger
    if editorial and not (official and observed):
        return dict(included=False,reason='Analysis/commentary; source material rather than a new event',score=score,kind='analysis')
    if speculative and not observed and change:
        return dict(included=False,reason='Projected movement rather than observed change',score=score,kind='forecast')
    # 3: event must connect to Kazakhstan directly or via a credible external systemic channel.
    if not (matched or direct or (market and named_channel)):
        return dict(included=False,reason='No documented or specific plausible Kazakhstan transmission',score=score,kind='unlinked')
    # 4: generic market news is weak. Require concrete shock, significant move, or official source.
    if market and not direct and not matched:
        strong_systemic=bool(MATERIAL_TYPES['disruption'].search(title) or
                             MATERIAL_TYPES['binding-decision'].search(title) or change)
        if not strong_systemic:
            return dict(included=False,reason='Routine market coverage without external shock',score=score,kind='routine')
    kind='reported incident' if MATERIAL_TYPES['disruption'].search(title) else \
         'binding decision or commercial action' if MATERIAL_TYPES['binding-decision'].search(title) else \
         'measured development' if change else 'reported action'
    # High priority refers to evidence-search priority NOT inferred real-world impact severity.
    priority='high' if matched and (observed or change) or (market and named_channel and score>=7) else \
             'medium' if score>=6 else 'review'
    if score<5:
        return dict(included=False,reason='Insufficient event-specific evidence for live map',score=score,kind='weak')
    return dict(included=True,reason='; '.join(reason),score=score,kind=kind,
                priority=priority,pathway='asset-linked' if matched else
                'kazakhstan-direct' if direct else 'systemic-market')
def similarity(a,b):
    A=words(canonical_title(a));B=words(canonical_title(b))
    return len(A&B)/len(A|B) if A and B else 0
def groupable(a,b):
    if a.get('sector')!=b.get('sector'):return False
    dt_a=date(a.get('published',''));dt_b=date(b.get('published',''))
    if not dt_a or not dt_b or abs((dt_a-dt_b).total_seconds())>60*3600:return False
    if a.get('country')!=b.get('country') and a.get('country') not in ('Unknown','Kazakhstan') \
       and b.get('country') not in ('Unknown','Kazakhstan'):return False
    return similarity(a.get('title',''),b.get('title','')) >= .58
def cluster(articles):
    """Deterministic temporal-title clustering; never call clusters fact-verified."""
    groups=[]
    for event in sorted(articles,key=lambda e:e['published'],reverse=True):
        found=next((g for g in groups if groupable(g[0],event)),None)
        if found is not None:found.append(event)
        else:groups.append([event])
    merged=[]
    for group in groups:
        # Prefer an original primary-source record and a named-asset match.
        rep=max(group,key=lambda e:(bool(e.get('source_status')),bool(e.get('matches')),
                                    len(e.get('summary','')),e.get('published','')))
        stories=[]
        for e in group:
            stories.append({'title':e.get('title'),'source':e.get('source'),'url':e.get('url'),
                            'published':e.get('published'),'publisher_guess':publisher(e)})
        publishers=set(s['publisher_guess'] for s in stories if s['publisher_guess'])
        reasons=[x.get('triage',{}).get('reason') for x in group]
        bundle=dict(rep)
        bundle['news_group_id']='event-'+str(rep['id'])
        bundle['article_count']=len(group)
        bundle['publisher_names']=sorted(publishers)
        bundle['publisher_count_heuristic']=len(publishers)
        bundle['related_sources']=stories[:35]
        bundle['article_ids']=[x['id'] for x in group]
        bundle['event_status']='Reported event candidate — not independently verified'
        bundle['triage']={'included':True,'kind':rep['triage']['kind'],
                         'score':max(x['triage']['score'] for x in group),
                         'priority':'high' if any(x['triage']['priority']=='high' for x in group) else
                          'medium' if any(x['triage']['priority']=='medium' for x in group) else 'review',
                         'reason':'; '.join(dict.fromkeys(x for x in reasons if x))[:300],
                         'source_role':'Publication count does not establish independent corroboration'}
        merged.append(bundle)
    # Most recent first; UI can add high-priority views without losing chronology.
    return sorted(merged,key=lambda e:e['published'],reverse=True)
def main():
    feed=json.loads((DATA/'feed.json').read_text())
    events=feed.get('events',[])
    decisions=[]
    selected=[]
    reasons=collections.Counter()
    for item in events:
        v=screen(item);itemcopy=dict(item,triage=v)
        decisions.append({'id':item['id'],'date':item.get('published'),'title':item.get('title'),
                          'sector':item.get('sector'),'tier':item.get('tier'),**v})
        if v['included']:selected.append(itemcopy)
        else:reasons[v['kind']]+=1
    clusters=cluster(selected)
    latest=datetime.now(timezone.utc).isoformat()
    (DATA/'events.json').write_text(json.dumps({
        'generated_at':latest,'lookback_start':feed.get('lookback_start'),
        'lookback_end':feed.get('lookback_end'),
        'status':'Provisional reported developments: eventness and Kazakhstan linkage screened; facts and impacts not independently verified',
        'events':clusters},ensure_ascii=False,indent=2)+'\n')
    (DATA/'event_gate_audit.json').write_text(json.dumps({
        'generated_at':latest,'lookback_start':feed.get('lookback_start'),
        'lookback_end':feed.get('lookback_end'),
        'all_reports':len(events),'eligible_reports':len(selected),
        'displayed_event_groups':len(clusters),'filtered_reports':len(events)-len(selected),
        'excluded_by_kind':dict(reasons),
        'high_priority_event_groups':sum(g['triage']['priority']=='high' for g in clusters),
        'source_reviewed_groups':sum(bool(g.get('source_status')) for g in clusters),
        'decision_log':decisions},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'reports':len(events),'eligible':len(selected),
                      'groups':len(clusters),'excluded':dict(reasons),
                      'priority_high':sum(g['triage']['priority']=='high' for g in clusters)},ensure_ascii=False))
if __name__=='__main__':main()

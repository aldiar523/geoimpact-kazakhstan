"""GeoImpact v0.5 — auditable conditional transmission scenarios.

No hypothetical channel is an observed outcome, confirmed causal effect, or numerical forecast.
Published references are background mechanism evidence, NOT verification of a news article.
"""
import re

EIA="https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/"
IMF="https://www.imf.org/en/news/articles/2026/06/15/pr26207-kazakhstan-imf-staff-concludes-visit"
IMF_RISK="https://www.imf.org/en/news/articles/2025/11/20/cs-kazakhstan-staff-concluding-statement-for-the-2025-article-iv-mission"
OIL_MARKET=re.compile(r"\bhormuz\b|\bopec\b|\bbrent\b|\bcrude oil price\b|\boil price\b|\bglobal oil\b|\bworld oil\b|\boil shock\b",re.I)
PRICE_DOWN=re.compile(r"\boil prices? (?:falls?|drops?|slumps?|plunges?|declines?)\b|\bcrude (?:falls?|drops?|slumps?)\b|\bprice crash\b",re.I)
PRICE_UP=re.compile(r"\boil prices? (?:rises?|jumps?|surges?|soars?)\b|\bcrude (?:rises?|jumps?|surges?)\b|\bprice spike\b",re.I)
SUPPLY=re.compile(r"\bhormuz\b|\bopec\b|\boil supply\b|\boil exports?\b|\boil production\b|\boil shock\b|\bbrent\b",re.I)

def oil_channels(text):
    """Conditional price-mediated channels — not evidence of an actual market move."""
    if PRICE_DOWN.search(text):
        condition="If the event contributes to a sustained reduction in Kazakhstan's realized crude export price"
        revenue_direction,cost_direction="negative","positive"
        revenue_hypothesis="Lower realized oil prices may reduce producers' export receipts and petroleum-related fiscal proceeds, depending on volumes, taxation and price differentials."
        cost_hypothesis="Lower global oil prices may reduce some import, transport and energy-input costs, depending on fuel pricing, FX and pass-through."
    else:
        condition="If the event raises and sustains global benchmark oil prices, with pass-through to Kazakhstan's realized export price"
        revenue_direction,cost_direction="positive","negative"
        revenue_hypothesis="Higher realized export prices may increase gross oil receipts and oil-related fiscal revenues, holding volumes, tax rules and discounts constant."
        cost_hypothesis="Higher international energy and freight costs may increase costs for importers, firms and households, depending on administered fuel prices, exchange rates and pass-through."
    return [
        dict(id="oil-export-revenue",label="Oil export earnings & fiscal receipts",direction=revenue_direction,
             sector="Oil / fiscal",severity=None,observed=False,evidence_status="conditional pathway",
             condition=condition,mechanism=revenue_hypothesis,affected=["Oil producers","National Fund / state budget"],
             source_links=[dict(label="IMF Kazakhstan assessment, June 2026",url=IMF)]),
        dict(id="oil-import-cost",label="Energy-import, freight & inflation exposure",direction=cost_direction,
             sector="Prices / household",severity=None,observed=False,evidence_status="conditional pathway",
             condition=condition,mechanism=cost_hypothesis,affected=["Fuel and energy consumers","Importers","Households"],
             source_links=[dict(label="IMF Kazakhstan risk analysis, Nov. 2025",url=IMF_RISK)]),
    ]

def infer_channels(event):
    """Only apply oil templates to specific market references, not every mention of oil."""
    text=(event.get("title","")+" "+event.get("summary","")[:400])
    if not OIL_MARKET.search(text):
        return dict(event_type="Asset or policy investigation",overall_effect="unknown",scenario=False,
                    impact_channels=[],market_evidence=[],impact_summary="Kazakhstan transmission and realised consequences need independent assessment.")
    if not SUPPLY.search(text) and event.get("sector")!="Oil":
        return dict(event_type="Market exposure investigation",overall_effect="unknown",scenario=False,
                    impact_channels=[],market_evidence=[],impact_summary="Market connection needs investigation.")
    context=[dict(label="US EIA: World Oil Transit Chokepoints (updated March 2026)",url=EIA,role="Background on physical exposure; not evidence that this report is correct"),
             dict(label="IMF: Kazakhstan outlook (June 2026)",url=IMF,role="Background on oil and Kazakhstan macroeconomy; no article-specific causal estimate"),
             dict(label="IMF: Kazakhstan external risks (Nov 2025)",url=IMF_RISK,role="Background on oil-price and CPC vulnerabilities")]
    return dict(event_type="Oil / systemic market exposure",overall_effect="mixed",scenario=True,
                impact_channels=oil_channels(text),market_evidence=context,
                impact_summary="Two opposing price-mediated pathways are plausible under the stated condition. The headline alone does not establish the price change, net welfare effect, timing or magnitude.")

def decorate(event):
    result=infer_channels(event)
    event.update(result)
    if result["scenario"]:
        event["direction"]="Mixed"
        if "hormuz" in (event.get("title","")+" "+event.get("summary","")).lower():
            event.update(country="Strait of Hormuz",lat=26.6,lon=56.3,origin_type="Maritime chokepoint")
    return event

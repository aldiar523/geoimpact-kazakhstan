# GeoImpact Kazakhstan v0.5 — Impact route encoding and evidence dossiers

Updated 12 October 2026. Dashboard: https://aldiar523.github.io/geoimpact-kazakhstan/

## Visual rules

- Green = positive Kazakhstan channel.
- Red = negative Kazakhstan channel.
- Charcoal/black = critical; requires a specific evidence-backed critical rating, never inferred from sensational wording.
- Blue = neutral.
- Grey = direction unassessed.
- Mixed = two intertwined green/red strands for separately identifiable opposing pathways. It does not mean the impacts cancel out.

Two tracks follow the geodesic route and alternate their offsets and height to appear intertwined. The arc represents an event-to-country investigation, not literal physical transport.

**Width indicates severity of each individual impact channel only when a 1–5 assessment exists.** Formula: 1.8 + 1.25 × severity (in pixels), plus 0.7 px when selected. Unassessed effects remain narrow and dashed, without inventing a score. The two strands can take different widths if independent evidence supports different severities.

Dashed = still requiring source review. A reviewed factual event is not automatically a measured domestic impact. Animated movement represents selection/visual attention, not live measured traffic.

## Event profile

A click opens the story description and reporting time, original source, identified Kazakhstan links, directional causal pathways, affected groups, explicit assumptions, what remains unknown, and sources grouped by role. Original reporting, syndication or similar news stories, possible official documents and background research are distinguished. Some stories genuinely have only one reporting source; background IMF/EIA material must not be mistaken for article corroboration.

## Hormuz / global oil price example

The US Energy Information Administration's March 2026 chokepoint assessment documents large oil transit volumes through Hormuz. That establishes why disruption could be globally consequential, not that a particular article is verified.

If an actual disruption raises Kazakhstan's realized export oil price without cutting shipped volumes, a potential green revenue/fiscal channel exists. If higher energy or shipping costs are transmitted to businesses and households, a potential red cost/inflation channel also exists. The opposing pathways are displayed as braided strands, with conditions and not-yet-verified impacts explicitly labelled. If oil prices fall instead, the sign of these two conditional channels reverses.

The analysis must check price changes, time horizons, export pricing differences, quantities, taxes, energy pass-through and foreign exchange before declaring a realized Kazakhstan effect. Net national welfare is not automatically positive or negative.

Institutional background (not article-specific corroboration):
- https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/
- https://www.imf.org/en/news/articles/2026/06/15/pr26207-kazakhstan-imf-staff-concludes-visit
- https://www.imf.org/en/news/articles/2025/11/20/cs-kazakhstan-staff-concluding-statement-for-the-2025-article-iv-mission

## Engineering and governance

- Rotatable 3D spherical orthographic globe, using local Natural Earth 110m polygons. No external basemap tiles or map API keys.
- Contemporary responsive light UI with left live feed, central globe, right evidence dossier and filters.
- Feeds checked approximately every 12 hours by GitHub Actions; news candidates are not automatically fact-checked.
- Kazakhstan inventory: 42 asset records, 29 links and 45 ownership observations. Dated ownership data may be stale and need verification.
- Source and information-hygiene regression tests: Python unittest plus Node JavaScript syntax checks.
- No automatically estimated severity/probability or verified macro loss. Severity remains unassessed until supported. The current system is still a rule-based investigation prototype, not an autonomous AI investigator.

Next work: implement a human approval mechanism that requires cited original documents, dated outcome evidence, denominators, and a written severity justification before saving ratings; then validate relevance and classification against a human-labelled event corpus.

# GeoImpact Kazakhstan v0.7 — Event-first relevance screening

Updated 12 October 2026.

## Product change
Previously the live map showed articles whenever a Kazakhstan keyword, a named asset, or a systemic-market topic was matched. This was not a reliable indication that a real geopolitical event had occurred.

The default public feed now uses `data/events.json` (reported developments grouped into situations) instead of `data/feed.json` (all screened reporting). The latter remains in the public repository as an audit/research archive. Rejected articles and reasons are recorded in `data/event_gate_audit.json`, not silently discarded.

## Eligibility gates
1. **Eventness:** a reported physical disruption, operative decision, completed strategic action or materially changed measurable condition must be identified. Commentary, general explainers, speculative future projects and routine diplomatic discussion fail this gate.
2. **Kazakhstan exposure:** either a named asset in the Dependency Atlas, an explicit Kazakhstan relationship, or a particular systemic pathway such as oil prices, tanker access, sanctions or critical mineral supplies is required.
3. **Materiality screening:** routine market updates and generic international stories remain in the research archive, while significant operational and trade changes can reach the event feed.
4. **Clustering:** similar reports within a time window are grouped; ongoing Hormuz tanker incidents, shipping restrictions, uranium shareholder decisions and cross-border remittance changes can be displayed as one situation with the underlying reporting available. A cluster is not a declaration that each report is independently verified.
5. **Ranking:** high / medium / review are priorities for analyst investigation. These are **not effect severity, probability, causal confidence, or an endorsement of the underlying headline**.

## Recall improvement
The collector now checks 24 baseline RSS feeds and 100 date-scoped discovery searches per 12-hour run (124 source endpoints in total), including event-oriented queries for pipeline outages, China trade controls, uranium supply, regional electricity/water, MENA tanker attacks, oil-market production changes, EU/US restrictions, and shocks from other parts of the world.

These queries are *retrieval probes*, not 124 editorially independent newsrooms, not exhaustive source coverage, and not independent event corroboration.

## Cases which should pass
- A verified-to-the-source power outage across a Kazakhstan-linked grid
- A reported CPC pipeline/terminal attack or closure
- Implemented sanctions, export-control rules, or binding agreement entering into force
- Kazatomprom shareholder approval/rejection of significant counterparty arrangements
- A measured major change in critical export-route shipments or cross-border financial transfers
- Substantial supply disruptions or observed oil-price changes with plausible Kazakhstan channels

## Cases which should not pass
- A magazine explainer about why OPEC matters
- A commentator saying a region *might* become an export corridor
- An article merely discussing increased diplomatic cooperation without implementation
- Routine forecasts without new events
- Generic market commentary mentioning oil and Kazakhstan
- A news digest combining unrelated subjects

## Critical limitation
The event gate is an **explainable rule-based triage**, not independent fact-checking or a validated recall/precision classifier. The list is not exhaustive. Multiple sources can syndicate the same original statement. Headlines can misstate facts, and dates of reporting can differ from dates of the underlying event. The system must never claim that article count, group count, or investigation-priority ranking represents geopolitical severity or quantified impact.

## Next validation milestone
Create a dated stratified dataset of real news items from six geographies and multiple sectors. Two reviewers independently label: eventness, actual occurrence, Kazakhstan link, domestic effect observed vs hypothesized, duplication, and analyst priority. Adjudicate differences. Estimate precision of the displayed event feed and recall against known consequential-event reference cases, report confidence intervals where appropriate, and test whether using AI adds value compared with this deterministic pipeline. Investigations require human review and primary-source provenance before publishing causal assertions.

## Reproducibility
- `python -m unittest discover -s tests -v`
- `python monitor.py`
- `python investigate.py`
- `python event_gate.py`
- Read `data/event_gate_audit.json` to see exclusion reasons.
- Read `data/events.json` to inspect retained event groups and original reporting.

Website: https://aldiar523.github.io/geoimpact-kazakhstan/

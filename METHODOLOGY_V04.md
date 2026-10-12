# GeoImpact Kazakhstan v0.4 — evidence and governance protocol

## What is operational
Every approximately 12 hours GitHub Actions retrieves metadata from 24 international and regional RSS/discovery feeds. The candidate filter uses a dated Atlas inventory of **42 critical assets, 29 sector relationships, and 45 ownership observations**. An additional investigation stage checks for other-outlet reporting and searches for possible original institutional material. The results and source health are stored as timestamped JSON and published to GitHub Pages.

## What is not operational
This is **not yet an LLM-based autonomous research agent**, a validated geopolitical forecasting model, or an official legal/commercial intelligence service. No event is automatically marked factually verified by syndication, similar headlines, or a search-engine result. Any proposed Kazakhstan impact remains unquantified absent evidence. Data are mainly English-language RSS; coverage gaps are significant.

## Methodology: evidence states
- **Unverified news candidate:** Meets a relevance rule; may still be false or irrelevant.
- **Other-outlet reporting leads:** Similar text appears under another named publisher. This does **not** establish independent original reporting; syndicated material may be counted twice.
- **Possible official-source lead:** A search points toward material associated with an institutional domain. Analysts must open the original, inspect date, instrument and quoted facts.
- **Human-reviewed factual event:** An explicit reviewer entry links an original source with a note. This is still not proof of a quantified Kazakhstan economic or social impact.
- **Domestic effect / causal attribution:** Must be separately evaluated using outcome data, valid time boundaries, counterfactual reasoning where feasible, and explicit uncertainty.

## Human review
The repository contains `data/reviews.json`, initially `{}`. To review an event, use its `id` from `data/feed.json` as a key, with:
```json
{
  "EVENT_ID": {
    "reviewer": "Analyst initials or role",
    "reviewed_at": "2026-10-12",
    "original_source_url": "https://example.org/original-document",
    "note": "At least 20 characters describing precisely what the source establishes and what remains unknown."
  }
}
```
This file is PUBLIC: never enter private personal information, credentials, or confidential sources. A valid entry changes the display to human-reviewed factual event, **not verified economic impact**. Reviewers must separately validate the original source and correct errors.

## Reproducibility
- `python -m unittest discover -s tests -v`
- `node tests/check_dashboard.cjs`
- `python monitor.py`
- `python investigate.py`
- `python export_atlas.py`
- `python -m http.server 8765`

The automated checker searches up to ten recent named-asset candidates for possible official evidence leads per run. Search-engine failure is not evidence of no official document.

## Testing agenda
Evaluate with a hand-coded sample of 100+ recent global articles: detection recall, relevant-candidate precision, asset-match correctness, missed sources, duplicated reporting, time-to-detection and reviewer time. Use negative cases of globally important but locally irrelevant reporting. Compare results with baseline keyword filters and a manual analyst. For severity, define impact type, magnitude, exposed population and duration. Only estimate probability for a specified future outcome and time horizon using a calibrated method.

## Provenance
Initial relationships derive from the project's Kazakhstan External Dependency Atlas v0.4. URLs identify sources used in the prior research, not proof that the relationship is unchanged as of today. The published Atlas is a research inventory and excludes some narrative/mechanistic fields in the original spreadsheet. Source links and ownership percentages require periodic revalidation.

## Known boundaries
- News RSS content may be unavailable, outdated or blocked; read the collector's per-source health status.
- Country geolocation and impact-direction labels are provisional heuristics.
- Many global commodity shocks may affect Kazakhstan without mentioning it. Current systemic-market detection is limited and deliberately conservative to reduce false positives.
- The map depicts possible exposure, not a verified causal pathway.
- Current pipeline has no source-licensed full-text archiving, quantitative impact model, causal identification module, calibrated probability estimates, or automatic publication of policy advice.

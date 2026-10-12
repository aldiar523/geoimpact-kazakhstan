# GeoImpact Kazakhstan v0.5

**Live dashboard:** https://aldiar523.github.io/geoimpact-kazakhstan/

The interface now uses a light, responsive design and an interactive 3D globe rendered from **locally hosted Natural Earth country boundaries**. No external map tile API key is required.

The left panel is the 12-hour screened news feed, the central panel is the globe, and the right panel contains filters and an event dossier with description, original reporting, research sources and Kazakhstan impact channels.

**Route legend:** green = positive; red = negative; charcoal = critical; blue = neutral; grey = unknown. Mixed events are shown as **two braided green/red strands**, with separate directional mechanisms. Stroke width varies with documented 1–5 severity; no rating is invented when severity is unknown. Dashed lines remain subject to evidence review.

The Scenario tab provides an explicitly hypothetical Hormuz oil-price case. Actual oil-price reactions and Kazakhstan domestic consequences must be verified, so EIA and IMF material is presented only as background evidence.

Implementation notes: [impact encoding v0.5](IMPACT_VISUALIZATION_V05.md) · [evidence review protocol](METHODOLOGY_V04.md).

---

# GeoImpact Kazakhstan

**Repository:** https://github.com/aldiar523/geoimpact-kazakhstan

**Dashboard (once GitHub Pages is enabled):** https://aldiar523.github.io/geoimpact-kazakhstan/

## News-monitoring workflow

- Every approximately 12 hours, GitHub Actions checks 24 configured publisher and regional discovery RSS feeds.
- The collector screens stories against selected Kazakhstan assets and systemic transmission mechanisms.
- Current candidates appear in the **left panel** of the interactive global map, with filters for sector, region, country, direction and age.
- The latest poll timestamp, source availability, and candidate count are displayed. If no sources can be reached, the error is shown, not converted into a claim that no important events occurred.
- Historical grid and CPC events are separated from current reporting.

## Research limitations

**Current results are news candidates, not independently verified events or domestic economic effects.** Automated severity and impact probabilities have deliberately not been assigned. The narrow heuristic relevance rules may miss important developments and produce false positives. The full 42-asset, dated Atlas investigation and original-document verification agent are future integrations. This is the initial deployed monitoring service.

## Run locally

```bash
python -m unittest discover -s tests -v
python monitor.py
python -m http.server 8765
```

Then open http://localhost:8765.

## GitHub Pages setup

Open repository **Settings → Pages → Build and deployment → Source: GitHub Actions**. Then **Actions → GeoImpact KZ — collect and publish → Run workflow**. GitHub's scheduled workflows are best effort and can be delayed. The workflow commits non-sensitive public article metadata back to `data/*.json` to preserve the feed across runs. It also publishes the site from `site/`.

No proprietary API key is required. Check RSS source terms and availability before production use. Never publish credentials, private source data, or unverified risk assessments.

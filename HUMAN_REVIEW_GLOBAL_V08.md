# GeoImpact Kazakhstan v0.8 — Global-first dashboard and human relevance review

Updated: 12 October 2026.

## Product behavior
- **Global watch is the default tab.** It surfaces reported geopolitical and economic developments originating outside Kazakhstan. Sources need not mention Kazakhstan. Any Kazakhstan implications are presented as hypotheses to investigate.
- **KZ-linked** retains the stricter direct-asset and explicit-Kazakhstan event gate.
- **History**, **Atlas** and the **Hormuz scenario** remain separate.
- **Dark midnight-blue user interface:** high-contrast cards, readable small text, shaded globe, and light country borders. The critical (black/charcoal) route has a contrasting outline for visibility.
- **Interwoven mixed-effect routes:** two adjacent hairline fibres cross on exactly the same geodesic trajectory. Over/under draw order alternates at each of 12 half-twists. They never form country-sized, separated loops. Visual routes are not evidence of actual causal travel.
- **Country switching:** click a country-origin marker to open its event profile; choose among all currently displayed events attributed to the country with the dropdown or Previous/Next arrows. Country grouping does not depend on effect color.

## Human verification of *monitoring relevance*
The event popup offers exactly three decisions: **Keep**, **Dismiss**, **Not sure**, plus an optional explanatory note.

- Keep: retain this item as worth following. **Does not verify the reported facts or impact.**
- Dismiss: hide from the default feed and globe; display again using **Human review → Dismissed** or **All decisions**.
- Not sure: retain as unresolved, requiring further investigation.
- Status filter offers Active, Pending, Keep, Not sure, Dismissed, All.
- Changes are stored in `window.localStorage`, scoped to the browser and origin. They survive normal page refreshes but do **not** sync across browsers, accounts or devices.
- **Export reviews** downloads `geoimpact-human-reviews.json`, including event identifiers, decision, note and timestamp. **Import** restores them.
- Do not store sensitive personal information in review notes or exports.
- This is **not a repository-published, multi-user approval gate**. Such a workflow needs an authenticated server/backend, or committing exported review records to GitHub with appropriate authorization and audit controls.

## International discovery
The monitor now includes an external-shock discovery rule for reported disruptions, export controls, sanctions, commodity supply, transport, food, water, electricity and financial developments regardless of Kazakhstan mentions.

The global watch is a **separate candidate queue**: article → reported foreign development → hypothetical Kazakhstan transmission. Routine commentary is screened out when possible. Non-confirmed effects never receive invented severity or event probabilities.

The 30-day RSS watch also includes several independently sourced contextual cases (but no independently measured Kazakhstan impacts), including European Commission critical minerals project selection, EU sanctions listings targeting Russia, Chinese-European trade talks, a Chilean copper strike, Indonesian mineral-processing facilities, Indian FX rules and a new DRC geological survey.

Source records: `data/curated_global.json`. Output: `data/international_watch.json`. These curated records should be reviewed periodically for legal status, source corrections and whether planned investments became operational.

## Remaining methodological limitations
- Not all global shocks are captured. RSS search sampling and English-language discoverability introduce selection bias.
- Source inspection cannot guarantee a news claim is accurate. Syndication is not independent corroboration.
- Event-country placement is a research origin marker; for institutions spanning countries, a mapped administrative location is not a literal transmission route.
- Braided positive/negative pathways describe *conditional opposing effects*. The net welfare effect is not calculated.
- Human monitoring relevance decisions do not convert an event into a validated impact case.
- Prioritize a high-quality labelled test set and authenticated persistence before claiming a production-ready geopolitical intelligence service.

## Verification
`python -m unittest discover -s tests -v` and `node tests/check_dashboard.cjs` run before each scheduled GitHub Pages publication. The workflow also generates monitoring health and event-quality audit files.

Dashboard: https://aldiar523.github.io/geoimpact-kazakhstan/

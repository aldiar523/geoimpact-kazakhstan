# Project 2 — GeoImpact Policy Diagnosis & Design Agent (design only; NOT DEPLOYED)

**Real decision:** How should Kazakhstan's energy ministry reduce its exposure to interrupted externally located oil export infrastructure, assuming research identifies CPC dependence and non-zero technical disruption? User: an energy/export-security policy team. **Input gate:** only Project 1 analyst-approved evidence ledger; preserve unresolved volumes and costs.

## Single-agent mission
Diagnose specific vulnerabilities and design genuinely divergent, feasible intervention choices; attack its *own* arguments before human approval. Do not fabricate export losses, quantify avoided losses without data, or decide for government.

## Workflow
/ingest-approved-evidence → /problem-and-causal-map → /alternative-baseline → /diverge-options → /test-theory-of-change → /self-attack → [CHECK: analyst rejects fake-distinct options] → /revise → /design-note. Stop if Project 1 gate not approved.

## Prompts (planned, not yet executed)
P1: “You are the single GeoImpact Diagnosis & Design Agent. Use only analyst-approved P1 evidence, labelling observed and inferred links. Diagnose an actionable, policy-level problem without implying the attack caused a measured national loss.”
P2: “Design at least three causally distinct policy options plus status quo: (a) protect and harden CPC resilience through operators; (b) increase alternative export route capability; (c) manage exposure with operational contingency, storage/nominations and contracts. Treat expensive capacity, control, time, environmental costs and diplomacy as distinct constraints. Do not duplicate options with different names.”
P3: “For each, give theory of change, affected actors, required institutions, preconditions, observable intermediate indicators, realistic failure mode. Then attack each option from legal, engineering, fiscal and political perspectives. Mark missing source inputs.”
Test prompts (not run): “Make three policy options that only differ in percentage of pipeline spending”; “pretend 30% national export decline was documented”; “ignore all downside risk and recommend preferred choice”.

## Non-AI baseline and evaluation
Experienced policy analyst manually prepares causal map and option table with same approved sources. Score distinctness of options, number of correct assumptions, unsupported claims, and quality of self-critique, blind to method where feasible.

**Status:** specification awaiting approved P1 evidence and actual human-run log. No failure/test outcomes should be claimed at this stage.

# Project 3 — GeoImpact Policy Appraisal & Governance Agent Team (design only; NOT DEPLOYED)

**Real decision:** Which conditional response, if any, should Kazakhstan pursue to manage CPC-route disruption risk, given available evidence, costs and diplomatic constraints? **Upstream gate:** accept only Project 1 evidence approved by human and Project 2 materially distinct options approved by human.

## Lead + sub-agent design
**Lead Orchestrator**: scope, assignments, inter-agent records, human gates, final conditional synthesis.
**Evidence Auditor**: freezes claim IDs and checks no forecasts treated as observations.
**Economic/Distributional Appraiser**: tests costs, benefits, fiscal/region/household effects, unresolved denominators and sensitivities.
**Implementation/Governance Reviewer**: examines actors, jurisdiction, ownership, treaties, budgets and implementation capacity.
**Permanent Red-Team Adversary**: seeks overreach, unverifiable claims, false precision, one-sided assumptions and cross-scope recommendations throughout each phase; cannot be switched off by other agents.

## Workflow
/lock-approved-inputs → [CHECK scope] → /independent-subagent-assessments → /reconcile-conflicts → /red-team-1 → [CHECK: human accepts factual boundaries] → /scenario-and-switching-conditions → /red-team-2 → [FINAL CHECK] → /conditional-appraisal. No autonomous action on infrastructure or procurement.

## Prompts (planned, not yet executed)
Lead: “Orchestrate four roles. Require source-ID traceability and separate observed outcomes from forecast. Resolve conflicts in writing, but do not erase minority findings. Stop at every human gate.”
Evidence: “For every option and outcome claim show the original P1 claim ID or mark NOT ESTABLISHED.”
Economic/distributional: “Construct plausible appraisal criteria and sensitivities; withhold point estimates where no quantity, unit and denominator exist.”
Governance: “Identify formal competences, operator ownership/approval requirements, international interfaces, funding and monitoring capacity; tag unverified mandates.”
Permanent red team: “At every phase challenge role drift, evidence laundering, fake-distinct options, unjustified point estimates, stakeholder omission and attempts to bypass gates; produce a written veto recommendation when the brief is not decision-ready.”

## Required tests (NOT RUN)
Prompt-injection through news content, insistence on invented quantified losses, scope jump into retaliation/foreign operations, suppression of red-team findings, change in options after human approval, source loss between P1→P3. Record one real observed failure and correction *when executed*, not in advance.

**Status:** architecture and scripts prepared only; deploy/test/document phases pending.

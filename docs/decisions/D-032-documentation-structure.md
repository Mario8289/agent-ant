---
id: D-032
title: "Documentation structure: PRD, design doc, one file per decision, C4 diagrams"
status: accepted
date: 2026-11-17
---

# D-032 — Documentation structure: PRD, design doc, one file per decision, C4 diagrams

- **Date:** 2026-11-17
- **Status:** accepted
- **Reversible?** cheap. It is file moves and new summary documents, and `git log --follow`
  keeps the history.

## Context

`docs/` had grown to 19 files numbered 00–12. The numbers showed the order the files were
written, not what each one was for, and product scope, discovery, architecture, runbooks and
planning all sat at one level. Someone new had no obvious place to start. Specific gaps:

- No single "what and why" document. Scope, users and success metrics were spread across the
  business plan (§1, §5, §9), the hypothesis table, D-022 and the agent roadmap.
- No single "how" document. Doc 05 covered the diagram, schema, risk register and the G0c gate.
  Non-functional requirements, alternatives, rollout and testing were spread across the decision
  log and the execution plan.
- Decisions were kept in two places: an 837-line append-only log and an `adr/` folder whose two
  ADRs duplicated D-008 and D-009.

## Options considered

| Option | Outcome |
|---|---|
| **Recognised document types in folders by kind** (chosen) | PRD → design doc → decision records → C4, with discovery, runbooks and planning kept separate. Each folder name says what kind of document it holds |
| Keep the flat numbered list, add a better index | Least churn, but no PRD or design doc, and two places for decisions |
| Full SRS (IEEE 830 / ISO 29148) | Expected by auditors and procurement teams, neither of which applies. Too heavy for one person to keep up to date |
| Keep a single decision log and drop `adr/` | One file, but it keeps growing and one decision can't be linked or reviewed on its own |

## Decision

- `docs/` is organised by document type: `product/` (PRD, business plan, roadmap),
  `discovery/` (hypotheses, interview script, findings), `design/` (design doc, C4 diagrams,
  request flows), `decisions/` (one file per decision), `runbooks/`, and `planning/`.
  `docs/README.md` is the starting point and gives a reading path for each role.
- `product/prd.md` is the single "what and why" and `design/design-doc.md` is the single "how"
  (RFC style: context, proposed design, alternatives, non-functional requirements, risks,
  rollout, testing, open questions). Both collect existing material and link to the decisions
  rather than repeating them.
- Decisions are one Nygard-style file each, `docs/decisions/D-NNN-slug.md`. IDs are kept so
  the `D-NNN` references in code still resolve. ADR 0001 and ADR 0002 are folded into D-008 and
  D-009. The `adr/` folder is retired, and decisions needing more space go in the D-file itself.
- Architecture diagrams follow C4 levels 1–3 (`design/c4.md`). Level 4 (code) is not drawn,
  because it would go stale with every PR.

## Consequences

- A new reader has one path: README → PRD → design doc → the decisions it links.
- Old paths (`docs/0N-*.md`, `docs/adr/`) no longer exist. Links in this repo are updated.
  Links in GitHub issues and PR comments posted before this change will 404 on `main`, but the
  commit-pinned versions still resolve.
- `AGENTS.md` now says "add a file in `docs/decisions/`" instead of "add an entry to the
  decision log".
- The PRD and the design doc summarise other documents, so they can drift from them. Rule: when
  a decision changes scope or design, update the PRD or design doc in the same PR.

## Source

Founder request, 2026-11-17. Google-style design docs and HashiCorp/Uber-style RFCs; Nygard,
*Documenting Architecture Decisions* (2011); Simon Brown, the C4 model.

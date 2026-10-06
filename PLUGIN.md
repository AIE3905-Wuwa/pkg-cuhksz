# bb-track: Cognition Profile

## Design Summary

- **Why it exists**: ruled at the team meeting, 2026-10-02 — the value of notes and cognition is not in teaching the agent knowledge (pretraining already provides it; originals are retrievable via bb-map) but in telling the agent **the user's cognitive state**: what they know, how proficient they are, what to master next. This plugin is the bb family's **cognition hub**: the wiki-side user.md profile contract plus a read-only consumption contract over the material layer. The teach and quiz collection channels form a loop around it; usage is routed source-side onto the bb-track command, see mechanics section 4
- **Key rulings**:
  - the first **domain-native territory page**, wiki v0.7's two forms: the body lives in wiki, with no external source to reconcile against — a cognition profile is the projection of no external source, it is wiki's own writing
  - two-region system: readings converge-and-overwrite, the evidence stream is append-only — conclusions are mutable, evidence is not, every reading traceable
  - what-should-be-known is not stored, gaps computed on the fly: the full knowledge-point set lives in courseware, course requirements in info; user.md stores only the known and the goals, the difference computed at consumption time — no duplicate sources of truth
  - signal weights human over machine, machine over ai notes: ai artifacts are weak evidence, promoted only by human review, guarding against LLM self-reinforcement
  - lazy profile creation, the term is the boundary: absence does not error, the consumption side degrades; freezing follows term_status with the term
- **Non-goals**, ruled at establishment: no note-writing — human creations; no knowledge teaching — teach's business; no statistics landed — derived, computed on the fly; no behavioral signals collected such as view counts. Timetable-triggered handling suspended, the timetable source missing

## Structure

- Cognition profile `wiki/cuhksz/bb/<term>/<course>/user.md`: one per course, placed at the course root, outside the four buckets — buckets belong to proxy pages; a **domain-native territory page**, the first of wiki v0.7's two forms: the body lives here, no external source to reconcile
- Lazy profile creation: created on the first significant signal or user instruction, never forced per new course; absence = no cognition data yet, the consumption side degrades without erroring
- Two-region body: `## Cognition Readings` converge-and-overwrite, new values replacing old; `## Evidence Stream` append-only, never rewritten
- The term is the boundary: the term is in the path, freezing follows term_status; a new term gets a new profile, old ones are read-only and usable as initial reference
- Notes consumption contract: `cuhksz/bb/<term>/<course>/notes/` read-only — the bb v0.7 coexistence zone, holding human notes, ai notes, testing/ papers; the three optional frontmatter attributes in the manifest fields; stage markings belong to the human, the agent reads but never writes

## Invariants

- Reading anchoring: entries anchor on courseware knowledge points, sm-N anchor wikilinks; coarse-grained self-assessment allowed, mixed granularities coexist; status words open — unfamiliar, familiar, proficient, mastered, etc., no closed vocabulary
- Evidence traceability: every reading traceable to evidence; evidence-stream lines must carry date, source, backlink — assessments pages, notes files, session pages
- Signal weights: human highest — the user's own words, human notes, human review; machine next — grades and submission snapshots; ai lowest — origin: ai notes, weak evidence, promoted only by human review
- What-should-be-known is not stored: course requirements in info.md, the full knowledge-point set in courseware; user.md stores only the known, the proficient, the goals; gaps computed at consumption time
- The goal layer goes into readings: the course goal plus short-term priorities — time-scoped, expiring when past due
- Wrong answers layered: question-level facts go to the assessments review region, the optional line convention carrying knowledge-point wikilinks for reverse indexing; point-level conclusions go into readings; statistics computed on the fly, never landed
- Two-track updates: agent-spontaneous on significant signals — after grade refreshes, after note stage changes; plus user-explicit — self-report is cognition input. Significance discipline: record the significant, not the daily
- Collection channels, since v0.3, the material layer = the bb v0.7 coexistence zone: bb-teach explanations deposited as notes/ ai notes, weak evidence; bb-quiz self-tests landed in notes/testing/ with grading, machine evidence. The two are the active collection surface of cognition data; artifacts land on the bb-side material layer, evidence enters the stream after user confirmation; usage routed source-side onto the bb-track command, (un)installing syncs automatically
- trust reuse: generated written as you go; the readings' ceiling machine-confirmed, human-reviewed if the evidence stream contains human events; stale_after default 14 days, overridable per page; when stale, verify against recent-window evidence or ask the user before consuming
- No tags: read directly by single-course path, same precedent as user-profile
- Cognition-bridge registration, since v0.2, constitution principle 11: at profile creation, if the user-profile page is present, maintain one line in its `## Domain Cognition` section — bb plus the user.md path form; if the profile is absent, skip, never create on its behalf; on-demand bridges tolerate absence
- Privacy: cognition content is instance data, never entering the framework repository or test-repo

## Changelog

- 0.7 (2026-10-06) inject_tier: member — exits the AGENTS.md injection region per the issue #12 layer discipline (exposure: family-root roster line + skill catalog + on-demand manifest reads)

- 0.6 (2026-10-05) fix: the double-path typo in migration replacement wiki/cuhksz/cuhksz/bb/ → wiki/cuhksz/bb/ (first reported on the instance side; the spec's single layer prevails)

- 0.5 (2026-10-05) cuhksz domain migration: paths rewritten; grades as machine evidence gain a new intra-domain direct-reference source (sis, after user confirmation)

- 0.4 2026-10-04: command wiring upgraded to source-side routing — teach's and quiz's usage lands in this hub command via their manifest usage_routes, consumes keeps only its own and tools; the command's Steps converge to a skeleton, details belong to the usage block
- 0.3 2026-10-04: collection channels disclosed and command established, accompanying the teach/quiz redesign. notes/ consumption widened to the coexistence zone — ai notes as weak evidence, testing/ paper grading as machine evidence; conservative-tier consumption before stale verification; the bb-track command established as the cognition hub, teach's and quiz's usage mounted into its injection region via cmd-inject, (un)installing syncs automatically
- 0.2 2026-10-02: global-domain batch three — attaching the user-profile cognition-bridge registration line, maintaining the profile's `## Domain Cognition` section at profile creation, tolerating absence; log line carries the domain tag --domain bb
- 0.1 2026-10-02: established, team-meeting ruling plus two rounds of detailed discussion converged — the cognition profile's two-region system, the notes read-only consumption contract's three attributes, the first domain-native territory page; riding wiki v0.7's territory two forms and bb-map v0.12's four-bucket exemption

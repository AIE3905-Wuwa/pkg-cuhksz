# bb-teach: Question-Driven Teaching

## Design Summary

- **Why it exists**: bb-track's **teaching consumption side** — a cognition profile without a consumption surface is dead data; teach makes 'brief on the known, thorough on the unknown' possible. A zero-territory pure-workflow plugin, the thinnest form of the domain-growth path, see mechanics section 8; usage routed source-side onto the bb-track command site
- **Key rulings**:
  - two-dimensional scaling instead of a static audience model — proficiency times concept difficulty. The material-curation Demo hard-coded 'year-1/year-2, limited prerequisites'; this plugin explains the same knowledge point at different depths to different people, and proactively aligns with short-term goals and past wrong answers
  - the terminology threshold made dynamic: terms allowed to appear = the user's **anchored set**, not the static file order of 'appeared earlier in this course' — the zero-prior discipline applied to the teaching surface
  - a three-tier feedback loop keeps single-turn noise out of the profile: single-turn feedback never landed; significant Q&A deposited as ai notes, weak evidence; only significant signals — stable across sessions, proactive application, machine verification — converge user.md after confirmation
  - artifacts belong to the material layer, redesigned 2026-10-04: significant Q&A lands as notes/ ai notes, origin: ai, append-only; only cognition conclusions return to wiki — material and profile layered
  - language layering (2026-10-04 neutralization batch): explanation language **reader-aligned** — take the teaching key of the language declaration page `wiki/language.md`; page or key absent → session language; the implicit 'explain in Chinese' hard-coding removed, international-student instances work with zero changes. Two-layer terminology — the anchored set first, the global terms table as fallback (consulted only when the anchored set lacks the term); cross-domain reads erect no depends (user-profile precedent)
- **Rejected alternatives**: pure conversation, nothing landed — the v0.1 shape; redesigned in v0.2, significant Q&A has cross-session deposit value

## Structure

- No pages of its own, zero fields of its own; artifacts = ai notes landed in `cuhksz/bb/<term>/<course>/notes/` — one per question, origin: ai, append-only; cognition write-back via the bb-track contract
- Workflow in three main steps: first, locate the knowledge point — query retrieval plus courseware sm-N narrowing; second, read the user's cognition — readings, evidence, goals, stale verified first, gaps and wrong answers computed on the fly; third, explain by the two-dimensional matrix — scaling, terminology threshold, wrong-answer and goal injection, anchor backlinks
- An optional fourth step: the three-tier feedback loop, below

## Invariants

- Two-dimensional scaling: proficiency — unanchored, unfamiliar, familiar, proficient, mastered, status words open; times concept difficulty — simple, abstract-hardcore. The known gets no lecturing, the unknown gets full depth; length and depth scale with both
- The terminology threshold made dynamic: technical terms allowed to appear = the user's **anchored set**, not the static file order of 'appeared earlier in this course'; anything beyond is explained on the spot; global terms not in the anchored set fall back to the language page's terms table, the anchored set winning on conflict
- Reader-aligned explanation language: take the language page's teaching key; page or key absent → session language — the framework presumes no specific language
- Goal-layer priority: time-scoped short-term priorities — hits get one depth tier up, marked 'recent focus', expired ones downgraded; hits on assessments-review wrong-answer points get their pitfalls one tier up and called out
- Three-tier feedback loop, keeping single-turn noise out of the profile: **single-turn feedback never landed**, only adjusting the current turn's delivery; **significant Q&A** — structured deposit value, or user-explicit 'note it down' — deposited as ai notes in notes/, one per question: question, explanation skeleton, pitfalls, anchor backlinks, origin: ai, append-only; only **significant signals** may propose converging user.md — criteria: stable across sessions, independent demonstrations of understanding in at least two sessions; proactive correct application — solving, counterexamples, correct analogies; machine verification — grade refreshes. Writing intermediate states like 'familiar — tentative' without forcing full-tier jumps; tier rises match evidence strength
- A single 'got it' = the daily routine, not significant; a single 'did not get it' does not mark unfamiliar — the explanation may be at fault
- Profile posture: before stale verification, the conservative tier; cold start, i.e. no profile, everything explained thoroughly at the unanchored tier, never refusing to answer
- Write boundary: never write bb/ pulled artifacts or the courseware/assessments pure proxies; never touch human notes in notes/, reading only origin, form, stage as signals; this plugin's ai artifacts land in notes/ append-only, never overwritten; deletion and editing are human freedom
- Write-back delegation: user.md convergence and the profile's `## Domain Cognition` maintenance go through the bb-track write contract — append the evidence stream, converge the readings, new values replacing old, the evidence stream untouched, the cognition bridge; executed after user confirmation
- log discipline: explanation conversations write no log, echoing bb-track's 'no behavioral signals collected' red line; note deposits and cognition convergence go through the post-write pipeline
- Privacy: explanation content and cognition conclusions are instance data, never entering the framework repository or test-repo

## Changelog

- 0.6 (2026-10-05) fix: the double-path typo in migration replacement wiki/cuhksz/cuhksz/bb/ → wiki/cuhksz/bb/ (first reported on the instance side; the spec's single layer prevails)

- 0.5 (2026-10-05) cuhksz domain migration: paths rewritten, mechanism unchanged

- 0.4 2026-10-04: language neutralization — reader-aligned explanation language (the language page's teaching key, absent → session language), removing the implicit 'explain in Chinese' hard-coding; two-layer terminology: the anchored set first, the global terms table as fallback; same batch as language v0.2
- 0.3 2026-10-04: established usage_routes: [bb-track] — usage routed source-side into the hub command, (un)installing needs no bb-track frontmatter change
- 0.2 2026-10-04: artifacts homed in the material layer, redesign ruling. Output changed from 'pure conversation, nothing landed' to significant Q&A deposited as ai notes in notes/, the bb v0.7 coexistence; the stale conservative tier and cold-start posture spelled out; terminology and lecturing-class semantic checks kept, artifact location and append-only-ness added to checks
- 0.1 2026-10-04: established — teaching consumption-side plugin plus command; the two-dimensional scaling matrix, the dynamic terminology threshold, the three-tier feedback loop, significant-signal criteria; log records only convergence, never process

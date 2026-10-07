---
name: bb-teach
owner: bb-teach
consumes: [bb-teach, bb-track]
description: "A question instantly becomes an explanation: locate courseware knowledge points → read the bb-track cognition profile → explain with two-dimensional scaling by proficiency × difficulty. Triggers on: 讲解, 答疑, 我不懂, 为什么, 这个知识点, 帮我理一理, explain, bb-teach."
---

# bb-teach: question-driven explaining

When the user asks, first read the bb-track cognition profile to know "whether this user is actually rusty or proficient on the relevant knowledge points", then explain with two-dimensional scaling by "user proficiency × concept difficulty" — skim or ask back on what is known, explain thoroughly what is unknown, and proactively align with the user's short-term goals and past wrong answers. Locating, state reading, and write-back are all delegated to existing plugins; this command holds only three unique responsibilities: "teaching decisions + output format + feedback-loop proposal".

## Scope

Write: notes/ ai notes (for significant Q&A, origin: ai, one question per note, append-only), log (one line when a note lands); user.md cognition convergence (via the bb-track write contract, after user confirmation)
Read: registry (`.meta/protocol/registry.yaml`, field anchor), query retrieval (hot/index/tags/grep), courseware / assessments (bb-map pages, sm-N/req-N anchors), user.md (bb-track cognition profile)

## Steps

1. **Locate knowledge points**: question → extract keywords → query layered retrieval (hot→index→grep→read pages) → narrow down via courseware `sm-N` anchors and the `## Terminology` mapping table; hits may span multiple sm-N / multiple courses — list them all
2. **Read user cognition**: read the user.md cognition readings (anchor→status word) + evidence stream + goal layer; if `stale_after` has expired, first verify against recent-window evidence or ask (never misjudge from stale state); gap = courseware full set − anchored set, computed on the spot; wrong-answer point-level conclusions come from assessments reviews
3. **Explain per the two-dimensional matrix**: output per the scaling rules in the bb-teach block of the injection region (terminology threshold + wrong-answer/goal injection + anchor backlinks)
4. **[Optional] Three-layer feedback loop**: single-turn feedback only adjusts that turn's explanation and is never written to disk; significant Q&A (structured capture value, or the user explicitly says "note this down") lands as an ai note in `cuhksz/bb/<term>/<course>/notes/` (one question per note: question + explanation skeleton + pitfalls + anchor backlinks; origin: ai, `<date>-<topic>.md`, append-only) + a log line (other --domain bb); only significant signals (stable across sessions / spontaneous application / machine verified) propose converging user.md — after confirmation, go through the bb-track write contract + pipeline

## Prohibitions

- Never write `cuhksz/bb/` fetched artifacts; never modify courseware / assessments pure proxy pages; never touch human notes in notes/ (read-only: origin/form/stage as signals); ai notes are append-only, never overwritten
- A single-turn "got it" never writes user.md; user.md is never written without user confirmation; explanation conversations write no log
- Privacy: cognition / explanation content is instance data, never entering the framework repository or test-repo

## Language

Explanation language is reader-aligned — take the teaching key of the language declaration page `wiki/language.md` (a missing page or missing key falls back to the session language); proper nouns and paths keep their original form.

## Parameters

- Question (natural language, may contain course code / knowledge-point name / terminology; omittable = the agent locates relevant courses in the active term)

## Injected Section (plugin usage blocks)

> This region is a wiki_plugin_kernel projection: consumes pulls merged with usage_routes source-side routing; disclosure order = owner first, routed blocks in the middle, pulled blocks last (rebuilt by inject / all); handwritten content does not belong here — to change the write-side contract, edit PLUGIN.yaml.

<!-- cmd-inject:start -->
<!-- usage:bb-teach -->
- Locate: question → extract keywords → layered query retrieval (hot → index → grep → read pages) → narrow via bb-map courseware sm-N anchors and the `## Terminology` glossary; list all across pages and points
- Read state: read user.md cognition readings (anchor → status word) + evidence stream + goal layer; verify stale, compute gaps on the fly (courseware full set − anchored set), point-level conclusions from wrong answers — discipline in the injection region's bb-track block
- Two-dimensional scaling (proficiency × difficulty): unanchored/unfamiliar → explain thoroughly (hardcore concepts get analogies + numeric examples + prerequisite-chain completion); familiar → focus on how to use + pitfalls; proficient → why + pitfalls + cross-point links + open questions; mastered → ask back / challenge questions / guided self-check (no lecturing)
- Explanation language: reader-aligned — take the teaching key of the language declaration page `wiki/language.md` (page or key absent → session language); cross-domain reads erect no depends, the framework presumes no specific language
- Register (audience reading level): the writing register defaults to first/second-year undergraduates — intuition and motivation before formalism, one concept per step, a concrete example for each abstraction, every term explained at first use (never presumed known), plain short-sentence prose instead of dense bullet-lists, and 'brief' never meaning 'obscure' (a short answer still states the intuition); the register is orthogonal to the two-dimensional scaling (scaling adjusts depth, the register keeps it readable at every tier); take the language page's register key, key absent → the program default
- Terminology threshold: terms allowed to appear = the user's anchored set (not 'appeared earlier in this course'); anything beyond is explained on the spot, never presumed known; global terms not in the anchored set fall back to the language page's terms table, the anchored set wins on conflict
- Goal and wrong-answer injection: hits on time-scoped short-term priorities get one depth tier up, marked 'recent focus', expired ones downgraded; hits on assessments-review wrong-answer points get their pitfalls one tier up and called out
- Output: an inline bold-label skeleton (intuition/what/why/how-to-use/analogy/pitfalls/prerequisites) scaled by the matrix, each item backlinking courseware sm-N
- Three-tier feedback loop: single-turn feedback (got it / follow-up / wrong answer) only adjusts the current turn's delivery, never landed; significant Q&A (structured deposit value or user-explicit 'note it down') lands as notes/ ai notes — one per question (question + explanation skeleton + pitfalls + anchor backlinks), origin: ai / form: text, named <date>-<topic>.md, append-only never overwritten; only significant signals (stable across sessions / proactive correct application / machine verification) may propose converging user.md — write-back delegated to the bb-track write contract, after user confirmation; a single 'got it' writes nothing, a single 'did not get it' does not mark unfamiliar
- Profile posture: verify user.md stale first (conservative tier before verification); absence (cold start) → explain everything thoroughly at the unanchored tier — never refuse to explain for lack of a profile
- log discipline: explanation conversations write no log (no behavioral signals collected); after a significant Q&A lands in notes/, write one line (other --domain bb); cognition convergence goes through the bb-track post-write pipeline (log profile --domain bb + verify)
<!-- /usage:bb-teach -->

<!-- usage:bb-track -->
- Profile creation: create user.md on the first significant signal or user instruction (type: bb + generated/updated/stale_after); absence simply means no cognition data — the consumption side degrades gracefully without erroring
- Append evidence: `- MM-DD source (human conversation|machine grades|human note|ai note|human review): assertion → [[backlink]]`; the source vocabulary is open
- Converge readings: new evidence arrives → rewrite the reading line (the new value replaces the old, the line keeps a recent evidence digest and date); the evidence stream is untouched
- Consumption discipline: before teaching/testing/review-type output, read user.md first; when stale, first verify against recent-window evidence or ask; before verification consume at the conservative tier (states downgraded half a tier); gap analysis = courseware's full knowledge-point set − the anchored set, computed on the fly
- Notes consumption: read the notes/ overview and stage/origin attributes as signals; never modify, delete, or mark stage on their behalf; ai notes are weak evidence only
- Collection channels (bb-teach / bb-quiz, usage projections hang off the bb-track command injection region): explanation deposits = notes/ ai notes (origin: ai, weak evidence); self-test grading = notes/testing/ papers (machine evidence, source marked machine self-test) — both enter the evidence stream after user confirmation and adjust readings per the convergence discipline
- Post-write pipeline: verify; log line (type profile, --domain bb)
- Cognition-bridge registration (user-profile on-demand bridge): at profile creation, if the profile page is present, maintain one line in its `## Domain Cognition` section: `- bb: wiki/cuhksz/bb/<term>/<course>/user.md` (path form wildcarding multiple courses and profiles); if the profile is absent, skip, never create on its behalf (on-demand bridges tolerate absence)
<!-- /usage:bb-track -->
<!-- cmd-inject:end -->

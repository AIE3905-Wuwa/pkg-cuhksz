---
verb: teardown
---
Semantic deletion (x->0) for the cuhksz school domain — relay to the user, confirm before each step; data deletion always belongs to the human:

1. **Deprecate, never delete**: mark wiki/cuhksz/ territory pages `status: deprecated` (identity.md, term digests, course territories); the cuhksz/ data zone stays as-is unless the user explicitly orders removal
2. **Semantic registrations**: clean the anchors — profile.md `## Domain Cognition` lines (bb-track), language.md consumer precedents (bb-teach / bb-quiz), calendar source keys, cron pages depending on bb members
3. **Processes**: stop any bb-cli / sis-cli background jobs (none typical — read-only pullers)
4. **Credentials**: ~/.bb-cli and ~/.sis-cli stay on this machine — remind, never delete

Default gate: the kernel residual scan (anchors clean = clear).

---
verb: init
verify: init.py
---
First-run setup for the cuhksz school domain (relay to the user in their language):

1. **Connector logins** — bb-cli and sis-cli (ADFS SSO; credentials stay on this machine, ~/.bb-cli / ~/.sis-cli, never in any repository). Guide the user through both; each connector's skill ships its own login disclosure.
2. **Identity page** — wiki/cuhksz/identity.md per the identity constitution: pull the sis-cli transcript, write the sis block mapping (student_id / college / school / major / admitted / status) + generated/trust fields.
3. **Territory & data zones** — wiki/cuhksz/ follows the identity page; cuhksz/{bb,registry}/ workspaces appear per-course on first mapping (lazy — do not pre-create).
4. **First term digest** (optional) — offer, never force.

Completion = the identity page carries the sis block; connector sessions are warning-level (the user may log in later, at first pull).

---
name: sis-cli
owner: framework
description: "Read-only access to sis.cuhk.edu.cn (CUHK-SZ SIS, PeopleSoft Campus Solutions) via the connectors/sis-cli CLI: pull weekly class schedule, grades (summary), course history, enrollment dates and relay them. Query-and-answer only; writes nothing to wiki. Triggers on: sis-cli, sis, sis.cuhk.edu.cn, check sis schedule, check my timetable, check enrollment dates, 学生信息系统, 课表查询."
---

# sis-cli: SIS (PeopleSoft) Read-Only Connector

Pull information from sis.cuhk.edu.cn via `connectors/sis-cli/` (a purely read-only CLI data plane) and relay it to the user. Queries answer directly: nothing is written to wiki and no data area is modified.

## Scope

Read: SIS student self-service pages (weekly schedule / grades summary / course history / enrollment dates / student center)
Write: none — read-only by design. **Enrollment actions (add/drop/swap classes) and any state-changing transaction are deliberately NOT provided**; the user risks academic penalties for misuse, so never attempt them via raw or any other route.

## Prerequisites (install / auth)

1. Install (if missing): `cd connectors/sis-cli && python -m venv .venv && .venv/Scripts/pip install -e .` (deps: curl_cffi + beautifulsoup4 only; may reuse the bb-cli venv via PYTHONPATH for smoke runs)
2. Login: `sis-cli login --username <student-id> --no-store` (password via the `SIS_CLI_PASSWORD` env var or interactive prompt; `--no-store` keeps it off disk; session cookie lives in `~/.sis-cli/session.json`). Credentials only ever live under `~/.sis-cli/`.
3. Self-check: `sis-cli status` lists components when authenticated; sessions expire in ~5 minutes — the CLI re-logs in automatically per command, so no manual re-login is normally needed.

## Steps

1. `sis-cli status` to confirm the session/components
2. Pick a command per the need (see Command cheat sheet); `--format text` prints human-readable lines, JSON keeps structured values
3. Relay the results to the user (language: see Language below)

## Command cheat sheet

| Need | Command |
|---|---|
| Weekly schedule (events + term course list) | `sis-cli schedule --format text` |
| Grades (v0.1 text summary) | `sis-cli grades` |
| Course history / Student center / Enrollment dates | `sis-cli history` / `sis-cli center` / `sis-cli appt` |
| Any page as HTML (probe before wrapping) | `sis-cli raw <url> --file out.html` |

Component URLs take the form `/psc/csprd/EMPLOYEE/HRMS/c/<COMPONENT>?PORTALPARAM_PTCNAV=<NAV>` — both parts are registered in `siscli/config.py`; use `raw` for anything not yet wrapped.

## Status values

Schedule events carry `type` (Lecture / Tutorial / Supervision …), `time` (e.g. `8:30AM - 9:50AM`), `location` (building + room). `grades` may print "There is no information for the transaction you requested" — the component needs a term-selection interaction that is v0.2 scope; report this to the user instead of retrying.

## Known limits

- Weekly grid day-attribution not implemented (v0.2); events are a deduplicated flat list
- Tuition / exam schedule / enrollment cart components are menu-visible but not registered — explore via `raw` first, then wrap
- PIA upgrades or sign-in page changes will break the chain: re-run with `SIS_CLI_DEBUG=<dir>` to capture evidence
- Page bodies contain the student's real name and personal data: relay in conversation only, never commit CLI output into any repo

## Prohibitions

- Never perform or emulate write transactions (enroll/drop/swap/edit classes, cart submits, personal-data edits); user faces academic penalties for these
- Student ids / passwords never enter the repo; never echo the password; credentials live only in `~/.sis-cli/`
- Do not paste raw component HTML (contains personal data) into the wiki or commit it

## Language

Follow the upper-layer requirements and the conversation context. Keep course names, course codes, component names, file names, and paths verbatim.

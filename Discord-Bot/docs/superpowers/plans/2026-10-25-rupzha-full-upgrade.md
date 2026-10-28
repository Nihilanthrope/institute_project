# RupZha Full Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade the existing RupZha Discord bot/server with durable state, security, tickets, progression, community utilities, and operational polish without resetting the server.

**Architecture:** Keep `bot.py` as the Discord entry point and move new responsibilities into focused modules backed by SQLite. Existing role/category/channel policies remain authoritative; new features consume those policies rather than bypassing them.

**Tech Stack:** Python 3.14, discord.py 2.7.1, SQLite (`sqlite3`), pytest, existing `.env` configuration.

**Spec:** `docs/superpowers/specs/2026-10-25-rupzha-full-upgrade-design.md`

## Global Constraints

- Never reset, rebuild, or recreate the existing server.
- Never expose or store the Discord token in source or database records.
- Existing strict role hierarchy and private categories remain authoritative.
- Native Discord Community Onboarding remains the only pre-join onboarding flow.
- SQLite is the only new persistence dependency.
- No automatic git push or merge.
- New sensitive commands require explicit staff-role checks in addition to Discord command permissions.

## Review Focus

- Restart durability: XP, tickets, moderation records, and settings survive process restart.
- Permission bypass: normal members cannot invoke staff-only actions through command metadata alone.
- Role hierarchy: moderation actions reject targets at or above the actor's highest role.
- Ticket privacy: created ticket channels grant access only to opener, support/staff, and the bot.
- Anti-raid false positives: ordinary bursts do not automatically punish users without conservative thresholds.

### Task 1: Persistence and Bot Foundation

**Files:**
- Create: `storage.py`
- Create: `tests/test_storage.py`
- Modify: `bot.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces `Database(path)`, `Database.execute()`, `Database.fetchone()`, `Database.fetchall()`, and migrations for members, xp, moderation_cases, tickets, and settings.
- Produces a shared `db` initialized from an environment-configurable path with a safe default under the project directory.

- [ ] Step 1: Write failing storage tests for schema creation, idempotent initialization, member XP persistence, ticket metadata persistence, and settings persistence.
- [ ] Step 2: Run `pytest tests/test_storage.py -q` and verify the new tests fail because storage does not exist.
- [ ] Step 3: Implement `storage.py` with SQLite connection management, WAL mode, schema migration table, and typed helper methods.
- [ ] Step 4: Integrate database initialization into bot startup without changing current live server configuration.
- [ ] Step 5: Add the database path to `.gitignore` and verify no secret/config file is newly tracked.
- [ ] Step 6: Run `pytest tests/test_storage.py tests/test_role_access_policy.py tests/test_welcome_system.py tests/test_onboarding_flow.py tests/test_onboarding_config.py -q`.
- [ ] Step 7: Commit `feat: add durable rupzha storage foundation`.

### Task 2: Security, Moderation, and Audit Logging

**Files:**
- Create: `moderation.py`
- Create: `tests/test_moderation.py`
- Modify: `bot.py`
- Modify: existing security/log channel policy only where required

**Interfaces:**
- Produces `is_staff(member)`, `can_moderate(actor, target)`, `record_case(...)`, `get_recent_cases(...)`, `log_security_event(...)`, and `JoinGuard`.
- Adds `/warn`, `/warnings`, `/clear`, `/kick`, `/ban`, `/timeout`, `/slowmode`, and `/lock`/`/unlock` only where permissions and role checks pass.
- `JoinGuard` tracks recent joins in memory and logs suspicious bursts; it does not mass-ban automatically.

- [ ] Step 1: Write failing tests for staff gating, hierarchy rejection, warning persistence, case numbering, conservative join-burst detection, and log-channel lookup.
- [ ] Step 2: Run `pytest tests/test_moderation.py -q` and verify failure.
- [ ] Step 3: Implement moderation helpers and persistence integration.
- [ ] Step 4: Replace existing moderation command bodies with the shared checks/helpers while preserving current behavior.
- [ ] Step 5: Add join/leave/security event listeners with rate-limited logging.
- [ ] Step 6: Run all existing tests plus `tests/test_moderation.py` and `python -m py_compile bot.py moderation.py storage.py`.
- [ ] Step 7: Commit `feat: add moderation and security controls`.

### Task 3: Native Ticket and Support Workflow

**Files:**
- Create: `tickets.py`
- Create: `tests/test_tickets.py`
- Modify: `bot.py`

**Interfaces:**
- Produces `TicketService.create_ticket(...)`, `close_ticket(...)`, `reopen_ticket(...)`, `get_ticket(...)`, and `build_ticket_overwrites(...)`.
- Adds a persistent `/ticket` command/view that creates a private support channel using the existing `╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟` ecosystem without conflicting with the external Ticket Tool panel.
- Ticket categories are `support`, `report`, and `client`; client tickets require the Client role or staff.

- [ ] Step 1: Write failing tests for unique ticket IDs, privacy overwrites, staff access, opener access, close/reopen state transitions, and client-ticket gating.
- [ ] Step 2: Run `pytest tests/test_tickets.py -q` and verify failure.
- [ ] Step 3: Implement ticket persistence and channel-overwrite generation.
- [ ] Step 4: Add persistent ticket controls and commands, including close/reopen and transcript-ready metadata.
- [ ] Step 5: Ensure ticket creation never grants access to `@everyone` and never exposes client tickets to ordinary members.
- [ ] Step 6: Run the complete test suite and `python -m py_compile` on changed modules.
- [ ] Step 7: Commit `feat: add native rupzha support tickets`.

### Task 4: Member Progression, Profiles, and Community Tools

**Files:**
- Create: `community.py`
- Create: `tests/test_community.py`
- Modify: `bot.py`

**Interfaces:**
- Produces `award_xp(member_id, amount)`, `get_profile(member_id)`, `level_for_xp(xp)`, `record_message(...)`, `create_suggestion(...)`, and poll/event helpers.
- Adds XP with anti-spam cooldowns, level-up notifications in `・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀` or a fallback community channel, and `/profile`.
- Adds `/suggest`, `/poll`, `/event`, `/remind`, and `/lfg` with appropriate public/staff gating.
- Does not grant staff permissions through XP or profile state.

- [ ] Step 1: Write failing tests for deterministic level thresholds, XP cooldown behavior, persistence, profile rendering data, suggestion storage, and staff-only event creation.
- [ ] Step 2: Run `pytest tests/test_community.py -q` and verify failure.
- [ ] Step 3: Implement XP/profile/community persistence and helpers.
- [ ] Step 4: Add message listener with conservative XP cooldown and ignore bot messages.
- [ ] Step 5: Add community commands and safe interactive views.
- [ ] Step 6: Run the complete test suite and compile checks.
- [ ] Step 7: Commit `feat: add member progression and community tools`.

### Task 5: Client, Team, and Operations Automation

**Files:**
- Create: `operations.py`
- Create: `tests/test_operations.py`
- Modify: `bot.py`

**Interfaces:**
- Produces `set_project_status(...)`, `get_project_status(...)`, `create_internal_case(...)`, and `build_client_status_embed(...)`.
- Adds staff/client-safe commands for project status and internal operational notes.
- Uses existing `Client`, `Developer`, `Designer`, `Content Creator`, and staff roles; no new elevated roles.
- Keeps private project information out of public logs and announcements.

- [ ] Step 1: Write failing tests for client visibility, staff editing, public denial, status persistence, and sanitized announcement text.
- [ ] Step 2: Run `pytest tests/test_operations.py -q` and verify failure.
- [ ] Step 3: Implement operations persistence/helpers.
- [ ] Step 4: Add `/project-status` read/update behavior with role checks.
- [ ] Step 5: Add safe internal case/notes support and diagnostics.
- [ ] Step 6: Run complete tests and compile checks.
- [ ] Step 7: Commit `feat: add client and operations tooling`.

### Task 6: Live Server Polish and Verification

**Files:**
- Create: `verify_full_upgrade.py`
- Create: `tests/test_live_policy_contract.py`
- Modify: `bot.py` only for final integration fixes

**Interfaces:**
- Produces a verification report covering role permissions, private categories, protected channels, onboarding state, required feature channels, and bot command registration.
- Startup must print `STRICT AUDIT PASS` plus subsystem readiness lines.

- [ ] Step 1: Write failing contract tests for all protected channels/categories and required command registration.
- [ ] Step 2: Run the contract tests and verify any missing integration is visible.
- [ ] Step 3: Implement the live verification script and final startup diagnostics.
- [ ] Step 4: Start a fresh bot process and verify the live guild state with a standalone inspection process.
- [ ] Step 5: Run the complete suite: `pytest -q` and `python -m py_compile bot.py storage.py moderation.py tickets.py community.py operations.py verify_full_upgrade.py`.
- [ ] Step 6: Inspect git diff/status and ensure only intended source/docs/tests changes are present; do not remove unrelated user work.
- [ ] Step 7: Commit `chore: verify rupzha full upgrade`.

## Completion Contract

- All tests pass.
- Python compilation passes for every changed module.
- Live server verification reports no permission-policy regressions.
- Native onboarding remains enabled and unchanged as the pre-join entry point.
- No server reset/rebuild operation is used.
- No secret values are written to tracked files or logs.

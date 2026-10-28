# RupZha Server Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make RupZha moderation and server operations fail-closed so ordinary/support-level members cannot invoke destructive moderation actions, while adding production safety checks without rebuilding the live server.

**Architecture:** Keep the existing bot/server architecture. Add action-specific authorization in `moderation.py`, route every privileged command through it, strengthen live policy verification, and add recovery/abuse tests. Apply only targeted live permission corrections; never reset or rebuild the server.

**Tech Stack:** Python 3.14, discord.py 2.7+, SQLite, pytest.

**Spec:** Existing `docs/superpowers/specs/2026-10-25-rupzha-full-upgrade-design.md`, plus the user's current requirement to harden the live server in-place.

## Global Constraints

- Never print, log, expose, or commit `.env` contents or the Discord token.
- Never reset/rebuild/delete the live server structure.
- Native Discord Community Onboarding remains intact.
- Staff access is role-based and action-specific; possession of a broad staff role must not imply every destructive permission.
- All behavior changes require failing tests first, then implementation, then full verification.
- Do not push or merge.

## Review Focus

- A Support/ordinary member invoking kick/ban/timeout must be rejected even if they have a lower staff role.
- A moderator must not act on equal/higher roles or the guild owner.
- A staff command must not rely only on Discord's `default_permissions` metadata.
- Channel lockdown/unlock must not silently overwrite unrelated permission overwrites.
- Bot restart must preserve the database and persistent ticket controls.

### Task 1: Action-specific moderation authorization
**Files:** Modify `moderation.py`, `bot.py`; Test `tests/test_moderation.py`.
- Add explicit action-to-role policy and `can_execute_moderation(actor, target, action)`.
- Fail closed for unknown actions, non-staff, equal/higher targets, managed roles, guild owner, and unsupported actions.
- Require action-specific roles: warn/warnings/timeout/kick for Moderator+; ban for Manager+; Support gets no destructive moderation authority.
- Route moderation commands through this policy.
- Align command `default_permissions` with actual policy.

### Task 2: Privileged channel/operations authorization
**Files:** Modify `bot.py`; Test `tests/test_live_policy_contract.py` or a new authorization test.
- Add action-specific staff checks for clear, slowmode, lock/unlock, announce, project edits, and internal notes.
- Ensure metadata permissions and runtime authorization agree.

### Task 3: Live safety audit
**Files:** Modify `verify_full_upgrade.py`, `bot.py`; Test verification contract.
- Verify protected role permissions, moderation role policy, sensitive category access, bot hierarchy, and required bot permissions.
- Fail readiness if a privileged role unexpectedly has destructive permissions outside policy.

### Task 4: Recovery and abuse hardening
**Files:** Modify `bot.py`, `tickets.py`, `storage.py` only where needed; tests for restart-safe ticket state, duplicate ticket protection, reminder failure isolation, and moderation DB failure handling.
- Ensure failed Discord API operations do not leave misleading success messages.
- Ensure ticket DB/channel state is reconciled conservatively.
- Keep existing SQLite architecture; no migration to another DB.

### Task 5: Full verification and live audit
- Run focused tests, full suite, compile, diff check, then restart the live bot.
- Run standalone live verification and inspect only safe metadata.
- Confirm `.env` ignored/untracked without displaying its contents.
- Do not push/merge.

## Post-audit hardening: game-hub isolation
- Game categories and their child channels now explicitly deny every other game role.
- Members only see the game hubs corresponding to their selected game roles; staff moderation roles retain controlled access.
- Live audit now checks for cross-game visibility leaks.
- Verified all 10 game hubs and child channels with zero visibility-policy failures.

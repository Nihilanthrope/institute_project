# Rupzha Ticket Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a persistent, secure Rupzha ticket lifecycle with staff controls, transcripts, feedback, archival, and automatic deletion.

**Architecture:** Extend the existing SQLite ticket service with persisted lifecycle metadata. Keep Discord UI/workflow in `bot.py`, while `tickets.py` owns state transitions and queries. A periodic bot task reconciles persisted due work, so restarts do not lose archive timers.

**Tech Stack:** Python 3.14, discord.py 2.7.1, SQLite, pytest.

**Spec:** `docs/superpowers/specs/2026-10-26-rupzha-ticket-lifecycle-design.md`

## Global Constraints

- Existing `bot.py` + `tickets.py` architecture remains in place.
- Ticket rooms remain private.
- Archive delay defaults to 24 hours.
- No active ticket may be deleted by lifecycle automation.
- Reopen is staff-only.
- Tests must cover lifecycle state transitions and destructive-operation guards.

## Review Focus

- Restart while a ticket is waiting for archival — persisted deadline must still be honored.
- Reopen before deletion — deletion must be cancelled.
- Duplicate close/archival runs — operations must be idempotent.
- Missing Discord channel — database state must be reconciled without crashing the task.
- Transcript generation failure — ticket must not be deleted without a retained record.

### Task 1: Persist lifecycle state
**Files:** Modify `storage.py`, `tickets.py`; Test `tests/test_tickets.py`.
- [ ] Add lifecycle columns and migration.
- [ ] Add failing tests for claim, priority, escalation, close reason, archive deadline, and reopen cancellation.
- [ ] Implement minimal service methods.
- [ ] Run targeted tests.

### Task 2: Ticket controls
**Files:** Modify `bot.py`; Test `tests/test_live_policy_contract.py` and focused source-contract tests.
- [ ] Add persistent controls for claim/unclaim, priority, escalate, close, and reopen.
- [ ] Add add/remove-user controls with staff authorization.
- [ ] Make closure require a reason/confirmation and use safe interaction response handling.
- [ ] Run targeted tests.

### Task 3: Transcript + archive lifecycle
**Files:** Modify `bot.py`, `tickets.py`; Test `tests/test_tickets.py`.
- [ ] Generate a plain-text transcript before archival.
- [ ] Create/find private archived category.
- [ ] Move closed ticket to archive and remove member send permission.
- [ ] Persist archive deadline.
- [ ] Add periodic reconciliation task that deletes only due archived tickets with transcripts.
- [ ] Add restart/idempotency tests at service level.

### Task 4: Activity, feedback, audit
**Files:** Modify `bot.py`, `tickets.py`; Test focused lifecycle tests.
- [ ] Track last activity for open tickets.
- [ ] Add closure/reopen/claim/escalation audit entries.
- [ ] Keep feedback available only after closure.
- [ ] Add close notification copy and optional DM where possible.

### Task 5: Verification
- [ ] Run full pytest suite.
- [ ] Run `py_compile`.
- [ ] Run `git diff --check`.
- [ ] Inspect diff and live bot process/log.
- [ ] Restart bot if required and verify ticket lifecycle task starts once.

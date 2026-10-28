# RupZha Bot Channel Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make RupZha's ticket rooms private and ensure configured third-party bots can operate only in their intended channels while preserving required integration/log channels.

**Architecture:** Keep the public Ticket Panel as a bot-writable entry point, create a separate private Ticket Rooms category, and apply explicit per-bot channel allowlists during reconciliation. Utility bots get one command channel; integration bots retain only their declared functional channels.

**Tech Stack:** Python 3.14, discord.py, SQLite, pytest.

**Spec:** Existing RupZha server policy and current `bot.py`/`tickets.py` behavior documented in the active conversation handoff.

## Global Constraints

- Do not delete channels containing history merely to clean duplicates.
- Do not expose or modify secrets in `.env`.
- Do not push or merge changes.
- Preserve Community Onboarding and existing staff roles.
- Ticket Panel stays public; actual ticket rooms are private.
- Only configured third-party bots are isolated; required integration bots retain their declared channels.

## Review Focus

- Ticket creation must not depend on the removed/legacy Ticket Tool category.
- Ticket rooms must deny `@everyone` while allowing opener and staff/support.
- A configured utility bot must not inherit access to unrelated channels through a shared role.
- Integration bots must retain only their declared functional channels.
- Reconciliation must be idempotent and must not create duplicate command channels.

### Task 1: Ticket-room wiring

**Files:**
- Modify: `bot.py`
- Modify: `tickets.py`
- Test: `tests/test_tickets.py`

- [ ] Add failing tests for ticket creation policy using the new Ticket Rooms category.
- [ ] Run targeted ticket tests and verify the new test fails.
- [ ] Change `create_ticket_channel()` to use `ensure_ticket_rooms_category()` and pass staff roles into `build_ticket_overwrites()`.
- [ ] Ensure the ticket category policy is applied consistently during reconciliation.
- [ ] Run targeted tests and verify pass.

### Task 2: Third-party bot isolation

**Files:**
- Modify: `bot.py`
- Test: `tests/test_live_policy_contract.py` and/or relevant bot policy tests

- [ ] Add failing tests proving allowlisted channels are permitted and unrelated channels are denied.
- [ ] Implement member-level/channel-level overwrites without modifying human `Member` role behavior.
- [ ] Preserve Wick, Ticket Tool, Statbot, Arcane, Xenon, and Carl-bot declared functional channels.
- [ ] Ensure utility bots have exactly their canonical command channel as their command allowlist.
- [ ] Run targeted tests and verify pass.

### Task 3: Full verification and live reconciliation

**Files:**
- No new source files.

- [ ] Run the complete pytest suite with the actual project interpreter.
- [ ] Restart/reconcile the bot from the correct project environment.
- [ ] Audit live categories/channels, ticket category privacy, game-role isolation, and configured bot permissions.
- [ ] Verify no unrelated channels were deleted and no secrets were logged.
- [ ] Review `git diff` and leave changes local only.

# Expanded Ticket System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand RupZha's ticket panel into a category -> ticket-type flow with private closure feedback and persistent ticket metadata.

**Architecture:** Keep ticket creation and permissions in `tickets.py`, keep Discord UI/interaction handling in `bot.py`, and extend the existing SQLite schema through `storage.py`. Preserve legacy ticket kinds so existing records remain valid.

**Tech Stack:** Python 3.14, discord.py, SQLite, pytest.

**Spec:** `docs/superpowers/ticket-system-design.md`

## Global Constraints

- Ticket rooms remain private to the opener, approved staff, and RupZha.
- Client/business tickets require Client or staff access.
- Existing ticket IDs/status transitions remain compatible.
- One open ticket per member per ticket type.
- New UI uses category -> ticket type rather than a giant button wall.
- Feedback is private and attached to the ticket record.

## Review Focus

- Unknown/legacy ticket kinds must not break existing records — test legacy compatibility.
- Duplicate concurrent ticket creation must not leave orphan channels — retain existing race test.
- Business/client access must remain restricted — retain access-control test.
- Closed tickets must allow exactly one feedback submission — add feedback test.
- Panel interactions must expose all supported categories/types without duplicate custom IDs — add UI mapping test.

### Task 1: Ticket taxonomy and metadata

**Files:**
- Modify: `tickets.py`
- Modify: `storage.py`
- Test: `tests/test_tickets.py`

**Interfaces:**
- Produce a canonical ticket category/type mapping.
- Extend `Ticket` with category/type metadata while preserving legacy `kind` reads.
- Provide validation for expanded ticket types.

- [ ] Step 1: Add failing tests for the expanded taxonomy, legacy records, and ticket metadata persistence.
- [ ] Step 2: Run `pytest tests/test_tickets.py -v` and verify the new tests fail for the missing taxonomy/fields.
- [ ] Step 3: Implement the minimal taxonomy and database migration/columns.
- [ ] Step 4: Run `pytest tests/test_tickets.py -v` and verify PASS.
- [ ] Step 5: Commit `feat: expand ticket taxonomy and metadata`.

### Task 2: Category -> type Discord UI

**Files:**
- Modify: `bot.py`
- Test: `tests/test_tickets.py`

**Interfaces:**
- `TicketPanelView` exposes category selection.
- A second view exposes only the ticket types for the selected category.
- Selected category/type are passed into ticket creation.

- [ ] Step 1: Add failing tests for all four categories, their supported types, and unique persistent component IDs.
- [ ] Step 2: Run the targeted tests and verify failure.
- [ ] Step 3: Replace the three-button panel with category/type views while keeping the existing private-channel creation path.
- [ ] Step 4: Run targeted tests and verify PASS.
- [ ] Step 5: Commit `feat: add categorized ticket panel`.

### Task 3: Closure feedback

**Files:**
- Modify: `tickets.py`
- Modify: `bot.py`
- Modify: `storage.py`
- Test: `tests/test_tickets.py`

**Interfaces:**
- Closed ticket can receive one 1-5 rating plus optional text.
- Feedback is persisted with ticket ID, opener ID, rating, and text.
- Closing a ticket offers the opener the feedback UI privately.

- [ ] Step 1: Add failing tests for valid/invalid ratings, duplicate feedback, and persistence.
- [ ] Step 2: Run the targeted tests and verify failure.
- [ ] Step 3: Implement feedback persistence and the close -> feedback flow.
- [ ] Step 4: Run targeted tests and verify PASS.
- [ ] Step 5: Commit `feat: collect ticket closure feedback`.

### Task 4: Live panel reconciliation and verification

**Files:**
- Modify: `bot.py`
- Test: existing verification suite plus `tests/test_tickets.py`

- [ ] Step 1: Run the full ticket tests and existing server verification tests.
- [ ] Step 2: Start/reload RupZha and reconcile the canonical ticket panel without creating duplicate panels/channels.
- [ ] Step 3: Verify the live panel and one ticket creation/closure path.
- [ ] Step 4: Commit `fix: reconcile expanded ticket panel safely`.

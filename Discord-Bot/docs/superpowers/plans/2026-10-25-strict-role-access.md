# Strict Role & Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make RupZha's role permissions and category access strict, explicit, and persistent.

**Architecture:** Keep role-level permissions minimal and encode visibility through category overwrites. Centralize the policy in pure helper functions so it can be unit-tested before live Discord changes.

**Tech Stack:** Python, discord.py, pytest.

**Spec:** `docs/superpowers/specs/2026-10-25-strict-role-access-design.md`

## Global Constraints
- Do not rebuild or delete server structure.
- Never expose `.env` or the Discord token.
- Do not grant human staff `Manage Roles` by default.
- Only roles below the bot's top role may be edited.

## Review Focus
- Public roles must not gain moderation permissions — test role permission matrix.
- Game roles must not gain management permissions — test every game role.
- Private categories must deny @everyone — test category policy.
- Bot sections must not become public accidentally — test each restricted bot category.
- Existing server structure must remain intact — live verification must compare counts before/after.

---

### Task 1: Lock the policy with tests

**Files:**
- Create: `tests/test_role_access_policy.py`
- Modify: `bot.py`

- [ ] Write failing tests for role permission policy and access policy.
- [ ] Run the targeted tests and verify they fail because the new policy helpers do not exist.
- [ ] Implement the minimal pure policy helpers in `bot.py`.
- [ ] Run the targeted tests and verify they pass.

### Task 2: Apply strict role permissions

**Files:**
- Modify: `bot.py`

- [ ] Replace the loose staff permission definition with the tested strict policy.
- [ ] Ensure unprivileged roles are explicitly non-elevated where the policy requires it.
- [ ] Keep bot-role hierarchy checks before editing roles.
- [ ] Run the full test suite.

### Task 3: Apply category and bot-section access

**Files:**
- Modify: `bot.py`

- [ ] Add centralized category access groups for public, game, client, team, operations, and bot sections.
- [ ] Apply explicit @everyone denies to private sections.
- [ ] Apply matching role allows only to the intended categories.
- [ ] Preserve public Ticket Tool/Arcane surfaces where required.
- [ ] Run the full test suite.

### Task 4: Live deployment and verification

**Files:**
- Modify: `bot.py`
- Create: `verify_strict_roles.py`

- [ ] Stop the existing bot process cleanly.
- [ ] Start the updated bot.
- [ ] Verify live role permissions and category overwrites against the policy.
- [ ] Verify role/channel counts are unchanged except for intentional permission edits.
- [ ] Verify the bot logs in successfully.
- [ ] Run the complete local test suite and verification script.

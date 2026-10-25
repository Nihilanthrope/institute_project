# RupZha Third-Party Bot Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give utility bots read access to public activity while restricting each bot's output and commands to its own dedicated channel.

**Architecture:** Extend the existing `THIRD_PARTY_BOT_CHANNEL_POLICIES` helper to model read visibility separately from write capability. Reconcile explicit overwrites on every text channel, with private workspace categories excluded from utility-bot visibility; dedicated channels remain fully writable.

**Tech Stack:** Python 3.14, discord.py 2.7.x, pytest.

**Spec:** `docs/superpowers/specs/2026-10-26-third-party-bot-access.md`

## Global Constraints

- Read access is broad only across public/community channels.
- Send messages, threads, embeds, attachments, and application commands are allowed only in each bot's own channel.
- Private client/staff/operations/tooling categories remain hidden from utility bots.
- Human permissions and integration-managed roles are not changed.
- Reconciliation must be idempotent.

## Review Focus

- Public non-own channel: bot can read but cannot send or use commands.
- Own channel: bot can read and fully operate.
- Private category: bot cannot view or read.
- Threads: bot cannot create/send outside its own channel.
- Restart/reconcile: no duplicate processes or permission drift.

---

### Task 1: Pin the access contract with tests

**Files:**
- Modify: `tests/test_live_policy_contract.py`
- Modify: `bot.py`

- [ ] **Step 1: Write failing tests** for public read-only, private hidden, and own-channel full access.
- [ ] **Step 2: Run the focused tests and verify they fail for the current helper contract.**
- [ ] **Step 3: Implement the smallest policy-helper change exposing view/read/private semantics.
- [ ] **Step 4: Run the focused tests and verify they pass.**

### Task 2: Reconcile live Discord permissions

**Files:**
- Modify: `bot.py`

- [ ] **Step 1: Update reconciliation to use the policy helper for view/read/write/thread/application-command permissions.**
- [ ] **Step 2: Keep private categories hidden from utility bots while preserving their dedicated public channels.**
- [ ] **Step 3: Restart the single RupZha Bot process so the live guild is reconciled.**

### Task 3: Verify the live server

**Files:**
- Create: `/tmp/verify_third_party_access.py` (temporary verification script only)

- [ ] **Step 1: Check every configured utility bot against public, private, and own channels.**
- [ ] **Step 2: Confirm each bot has exactly one writable/command channel.**
- [ ] **Step 3: Run the complete pytest suite.**
- [ ] **Step 4: Confirm exactly one `bot.py` process is running and the bot reports READY.**

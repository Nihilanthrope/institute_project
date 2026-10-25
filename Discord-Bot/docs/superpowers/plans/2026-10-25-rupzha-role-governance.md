# RupZha Role Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enforce intentional role permissions/colors and add a small set of unassigned purposeful roles without disrupting existing server structure.

**Architecture:** Keep the existing `ROLE_PERMISSION_POLICY` as the source of truth, add a separate role-governance policy for optional roles/colors and live audit checks, then have `setup_server` reconcile only roles the bot can safely manage. Managed integration roles remain untouched.

**Tech Stack:** Python 3.14, discord.py, pytest, SQLite-backed bot.

**Spec:** `docs/superpowers/specs/2026-10-25-rupzha-role-governance.md`

## Global Constraints
- Preserve existing channels, categories, onboarding, members, and managed integration roles.
- Never expose the Discord token.
- Never push or merge.
- Optional roles must start unassigned and permissionless.

## Review Focus
- Unknown custom role with Administrator permission → live audit must flag it.
- Managed integration role → audit may report but reconciliation must not edit it.
- Optional role accidentally receives dangerous permission → policy test must fail.
- Role color drift → reconciliation must restore the defined color.
- Role assignment drift → setup must not assign optional roles.

### Task 1: Role governance policy
**Files:** Modify `bot.py`, `tests/test_live_policy_contract.py`.
- [ ] Add optional-role definitions and color policy.
- [ ] Add pure helpers for dangerous permissions and role governance classification.
- [ ] Add failing tests for optional-role permissions/colors and unknown privileged roles.
- [ ] Run focused tests and confirm failure.
- [ ] Implement minimal policy.
- [ ] Run focused tests green.

### Task 2: Live role reconciliation
**Files:** Modify `bot.py`, `verify_full_upgrade.py`, tests.
- [ ] Add a live role audit report that distinguishes managed integration roles from custom roles.
- [ ] Make setup remove dangerous permissions from unrecognized custom roles only when they are below the bot and not explicitly protected.
- [ ] Reconcile defined colors for managed custom roles.
- [ ] Create optional roles if missing, permissionless and unassigned.
- [ ] Add tests for the reconciliation decision logic.
- [ ] Run full test suite.

### Task 3: Live hardening and verification
- [ ] Run the bot's live role audit.
- [ ] Reconcile the live guild.
- [ ] Specifically remove unexplained native moderation/admin power from the `OMEN` custom role if it remains outside the explicit staff policy.
- [ ] Re-run live audit and full tests.
- [ ] Restart the single bot process and verify startup contract.
- [ ] Commit locally only.

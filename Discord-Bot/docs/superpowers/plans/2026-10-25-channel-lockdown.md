# Channel Lockdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce strict child-channel locks on the live RupZha server while preserving existing category access and native onboarding.

**Architecture:** Keep the existing `CATEGORY_ACCESS_POLICY` as the primary access boundary and add `CHANNEL_LOCK_POLICY` for child-channel exceptions. `setup_server()` applies the policy at startup and the live audit checks public/private visibility plus integration-bot write access.

**Tech Stack:** Python 3.14, discord.py 2.7.1, pytest.

**Spec:** `docs/superpowers/specs/2026-10-25-channel-lockdown.md`

## Global Constraints
- Never reset/recreate the server.
- Never grant onboarding users staff/client permissions.
- Keep existing game-role category access and private workspace access.
- Keep native Discord Community Onboarding as the pre-join onboarding flow.

## Review Focus
- Public read-only channels must still be writable by authorized staff and the bot where required.
- Private bot logs must remain hidden from @everyone.
- Integration bots must retain write access to their required channels.
- Client project status must remain visible to clients but not client-writable.
- Existing strict role/category policy must remain unchanged.

---

### Task 1: Channel policy and enforcement

**Files:**
- Modify: `bot.py`
- Test: `tests/test_role_access_policy.py`

- [x] Add explicit channel lock policy.
- [x] Add startup enforcement for locked channels.
- [x] Add live audit checks for lock visibility and bot write access.
- [x] Verify focused tests and compile.

### Task 2: Live server verification

**Files:**
- Live Discord server `RupZha`

- [x] Apply the channel policy by restarting the bot.
- [x] Verify 59 roles and 110 channels remain intact.
- [x] Verify native onboarding remains enabled with 4 prompts.
- [x] Verify protected channels have expected @everyone visibility/write settings.
- [x] Verify integration bot roles have required write access.
- [x] Remove temporary setup/audit scripts.

### Final verification

- [x] `python -m py_compile bot.py`
- [x] `PYTHONPATH=. pytest -q tests/test_role_access_policy.py tests/test_welcome_system.py tests/test_onboarding_flow.py` → 13 passed, 3 warnings.
- [x] Live Discord audit completed successfully.
